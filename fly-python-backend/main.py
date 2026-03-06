"""
FastAPI backend for the Saint John's Cathedral Sermon Bot.

Endpoints:
  POST /query    — RAG chat: embed query -> search ChromaDB -> stream Claude response
  GET  /search   — Semantic search: embed query -> search ChromaDB -> return ranked results
  POST /generate — Sermon generation: load voice profile -> RAG -> stream Claude response
  GET  /health   — Health check
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
CHROMA_DIR = DATA_DIR / "chroma_db"
REFERENCE_DIR = DATA_DIR / "references"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
RAG_TOP_K = 8

SYSTEM_PROMPT = """You are the Saint John's Cathedral Sermon Bot — an AI assistant \
trained on sermons from Saint John's Cathedral in Denver, Colorado.

Your knowledge comes from sermon transcripts by the cathedral's clergy, including \
Dean Richard Lawson, Katie Pearson, Broderick Greer, Jack Karn, Deonna Neal, and Paul Keene.

When answering questions:
1. Ground your answers in the actual sermon content provided in the context.
2. Cite specific sermons by preacher name and date when possible.
3. If the sermons don't address a topic, say so honestly rather than making things up.
4. Capture the theological voice and style of the specific preacher being asked about.
5. You can synthesize across multiple sermons to give comprehensive answers.
6. When recommending sermons, explain WHY that sermon is relevant.

You are warm, scholarly, and accessible — reflecting Saint John's own character as \
a community that "says its prayers but does not take itself too seriously."
"""

GENERATION_PROMPT = """You are generating a synthetic sermon in the voice and style of {preacher}, \
a preacher at Saint John's Episcopal Cathedral in Denver, Colorado.

## VOICE PROFILE
{voice_profile}

## INTELLECTUAL REFERENCES THIS PREACHER WOULD USE
{reference_summary}

## ADJACENT THINKERS (use sparingly)
{adjacent_voices}

## LITURGICAL CONTEXT
Occasion: {occasion}
Scripture Readings: {readings}

## CURRENT EVENTS CONTEXT
{current_events}

## REAL SERMON EXCERPTS (for voice calibration)
{real_excerpts}

## INSTRUCTIONS
Generate a sermon (~1200-1800 words) that:
1. Sounds authentically like {preacher}
2. Engages seriously with the scripture readings
3. References 2-3 thinkers from their known influence set naturally
4. Connects to current events the way this preacher would
5. Has a clear theological argument
6. Includes their characteristic touches

Begin the sermon now. Do not include a title or metadata."""

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(title="SJC Sermon Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global resources (loaded once at startup)
# ---------------------------------------------------------------------------
embedder: SentenceTransformer | None = None
collection = None
claude_client: anthropic.Anthropic | None = None
voice_profiles: dict = {}


@app.on_event("startup")
async def startup():
    global embedder, collection, claude_client, voice_profiles

    print("Loading embedding model...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    print("Loading ChromaDB...")
    if CHROMA_DIR.exists():
        chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            collection = chroma.get_collection("sermons")
            print(f"  Loaded {collection.count()} sermon chunks")
        except Exception:
            print("  WARNING: No 'sermons' collection found in ChromaDB")
    else:
        print(f"  WARNING: ChromaDB directory not found at {CHROMA_DIR}")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        claude_client = anthropic.Anthropic(api_key=api_key)
        print("  Claude API connected")
    else:
        print("  WARNING: No ANTHROPIC_API_KEY set")

    profiles_path = REFERENCE_DIR / "voice_profiles.json"
    if profiles_path.exists():
        with open(profiles_path) as f:
            data = json.load(f)
        voice_profiles = data if isinstance(data, dict) else {}
        print(f"  Voice profiles loaded: {list(voice_profiles.get('profiles', voice_profiles).keys())}")

    print("Startup complete!")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class GenerateRequest(BaseModel):
    preacher: str
    occasion: str
    readings: str
    theme: str = ""
    current_events: str = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def format_context(results: dict) -> tuple[str, list[dict]]:
    """Format retrieved chunks into context text and source metadata."""
    context_parts = []
    sources = []
    seen = set()

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_parts.append(
            f"--- Sermon Excerpt ---\n"
            f"Preacher: {meta['preacher']}\n"
            f"Date: {meta['date']}\n"
            f"Title: {meta['title']}\n"
            f"Content:\n{doc}\n"
        )
        key = f"{meta['date']}_{meta['preacher']}"
        if key not in seen:
            seen.add(key)
            date_str = meta["date"]
            title = meta["title"]
            slug = f"{date_str}-{title}".lower()
            slug = "".join(c if c.isalnum() or c in " -" else "" for c in slug)
            slug = "-".join(slug.split())
            sources.append({
                "title": title,
                "date": date_str,
                "preacher": meta["preacher"],
                "slug": slug,
                "excerpt": doc[:200],
            })

    return "\n".join(context_parts), sources


def slugify(text: str) -> str:
    return "-".join(
        "".join(c if c.isalnum() or c in " -" else "" for c in text.lower()).split()
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "embedder_loaded": embedder is not None,
        "collection_loaded": collection is not None,
        "claude_connected": claude_client is not None,
        "voice_profiles": list(voice_profiles.get("profiles", voice_profiles).keys()),
    }


@app.post("/query")
async def query_chat(req: ChatRequest):
    if not collection or not embedder:
        raise HTTPException(503, "Search index not loaded")
    if not claude_client:
        raise HTTPException(503, "Claude API not configured")

    # Embed the query and search
    query_embedding = embedder.encode([req.message]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=RAG_TOP_K,
    )

    context_text, sources = format_context(results)

    # Build messages
    messages = list(req.history)
    user_msg = (
        f"Here are relevant sermon excerpts from Saint John's Cathedral:\n\n"
        f"{context_text}\n\n"
        f"Based on these sermon excerpts, please answer this question:\n"
        f"{req.message}"
    )
    messages.append({"role": "user", "content": user_msg})

    async def stream():
        with claude_client.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as response:
            for text in response.text_stream:
                yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"

        yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/search")
async def search(q: str, n: int = 20):
    if not collection or not embedder:
        raise HTTPException(503, "Search index not loaded")

    query_embedding = embedder.encode([q]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n,
    )

    items = []
    seen = set()
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        key = f"{meta['date']}_{meta['preacher']}"
        if key in seen:
            continue
        seen.add(key)

        date_str = meta["date"]
        title = meta["title"]

        items.append({
            "title": title,
            "date": date_str,
            "preacher": meta["preacher"],
            "slug": slugify(f"{date_str} {title}"),
            "excerpt": doc[:300],
            "score": round(1 - dist, 4),
        })

    return {"query": q, "results": items}


@app.post("/generate")
async def generate_sermon(req: GenerateRequest):
    if not claude_client:
        raise HTTPException(503, "Claude API not configured")

    # Load voice profile
    profiles_data = voice_profiles.get("profiles", voice_profiles)
    profile = profiles_data.get(req.preacher, {})
    influence_map = profile.get("influence_map", {})

    voice_profile_text = influence_map.get(
        "generative_prompt_seed",
        "Match the general style of an Episcopal preacher at a major urban cathedral.",
    )

    ref_summary = ""
    agg = profile.get("aggregated_references", {})
    if agg.get("top_thinkers"):
        ref_summary = ", ".join(name for name, _ in agg["top_thinkers"][:10])

    adjacent = ""
    if influence_map.get("adjacent_voices"):
        adjacent = "\n".join(
            f"- {v.get('name', v) if isinstance(v, dict) else v}"
            for v in influence_map["adjacent_voices"][:5]
        )

    # RAG excerpts
    real_excerpts = "Not available."
    if collection and embedder:
        search_topic = f"{req.occasion} {req.readings} {req.theme}".strip()
        query_embedding = embedder.encode([search_topic]).tolist()
        try:
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=RAG_TOP_K,
                where={"preacher": req.preacher},
            )
            excerpts = []
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                excerpts.append(f"[{meta['date']}] {doc[:500]}")
            if excerpts:
                real_excerpts = "\n\n".join(excerpts)
        except Exception:
            pass

    prompt = GENERATION_PROMPT.format(
        preacher=req.preacher,
        voice_profile=voice_profile_text,
        reference_summary=ref_summary or "Not yet analyzed",
        adjacent_voices=adjacent or "Not yet analyzed",
        occasion=req.occasion,
        readings=req.readings,
        current_events=req.current_events or "No specific current events provided.",
        real_excerpts=real_excerpts,
    )

    async def stream():
        with claude_client.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        ) as response:
            for text in response.text_stream:
                yield f"data: {json.dumps({'type': 'text', 'content': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
