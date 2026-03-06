from __future__ import annotations
"""
PHASE 8: SYNTHETIC SERMON GENERATOR
======================================
Generate sermons in the authentic voice of each preacher, grounded in
their intellectual DNA, rhetorical patterns, and theological commitments.

WHAT IT DOES:
1. Loads the voice profile for the selected preacher (from Phase 7)
2. Takes inputs: scripture readings, liturgical date, current events
3. Retrieves the most relevant real sermon excerpts (RAG)
4. Generates a sermon that authentically captures the preacher's voice
5. Includes proper intellectual references from their influence set

THIS IS NOT:
- A replacement for real preaching (obviously)
- A claim that AI can do what these preachers do
- Something to publish without attribution

THIS IS:
- A fascinating exploration of what makes each voice distinctive
- A tool for studying homiletic patterns
- A way to engage with a preacher's theology interactively
- A prototype for what "personalized AI theology" could look like

RUN: python 08_generate_sermon.py
"""

import json
import anthropic
import chromadb
from sentence_transformers import SentenceTransformer
from config import (
    DATA_DIR, CHROMA_DIR, EMBEDDING_MODEL,
    ANTHROPIC_API_KEY, CLAUDE_MODEL, RAG_TOP_K, PREACHERS
)

REFERENCE_DIR = DATA_DIR / "references"
CONTEXT_DIR = DATA_DIR / "context"

GENERATION_PROMPT = """You are generating a synthetic sermon in the voice and style of {preacher}, 
a preacher at Saint John's Episcopal Cathedral in Denver, Colorado.

## VOICE PROFILE
{voice_profile}

## INTELLECTUAL REFERENCES THIS PREACHER WOULD USE
Draw from these thinkers and traditions that {preacher} frequently cites:
{reference_summary}

## ADJACENT THINKERS (use sparingly, as fresh references)
{adjacent_voices}

## LITURGICAL CONTEXT
Date: {date}
Occasion: {occasion}
Scripture Readings: {readings}

## CURRENT EVENTS CONTEXT
{current_events}

## REAL SERMON EXCERPTS (for voice calibration)
These are actual excerpts from {preacher}'s sermons. Match this voice:
{real_excerpts}

## INSTRUCTIONS
Generate a sermon (~1200-1800 words) that:
1. Sounds authentically like {preacher} — match their vocabulary, sentence rhythm, 
   rhetorical moves, and relationship with the congregation
2. Engages seriously with the scripture readings
3. References 2-3 thinkers from their known influence set naturally
4. Connects to current events the way this preacher would
5. Has a clear theological argument, not just inspirational fluff
6. Includes their characteristic touches (humor if they use it, pastoral 
   warmth if that's their style, scholarly depth if that's their approach)
7. Feels like something you'd actually hear at Saint John's on a Sunday morning

Begin the sermon now. Do not include a title or metadata — just the sermon text 
as it would be spoken from the pulpit."""


def load_voice_profile(preacher: str) -> dict | None:
    """Load the voice profile for a preacher."""
    profiles_path = REFERENCE_DIR / "voice_profiles.json"
    if not profiles_path.exists():
        return None
    with open(profiles_path) as f:
        profiles = json.load(f)
    return profiles.get(preacher)


def get_relevant_excerpts(preacher: str, topic: str, collection, embedder) -> str:
    """Retrieve real sermon excerpts relevant to the topic."""
    query_embedding = embedder.encode([topic]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=RAG_TOP_K,
        where={"preacher": preacher},
    )

    excerpts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        excerpts.append(f"[{meta['date']}] {doc[:500]}")

    return "\n\n".join(excerpts) if excerpts else "No excerpts available."


def interactive_generate():
    """Interactive sermon generation session."""
    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in environment or config.py")
        return

    # Load resources
    print("Loading resources...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = chroma_client.get_collection("sermons")
        embedder = SentenceTransformer(EMBEDDING_MODEL)
        has_rag = True
        print(f"  Sermon database: {collection.count()} chunks loaded")
    except Exception:
        has_rag = False
        print("  Warning: No sermon index found. Generating without RAG.")

    # Check for voice profiles
    profiles_path = REFERENCE_DIR / "voice_profiles.json"
    if profiles_path.exists():
        with open(profiles_path) as f:
            profiles = json.load(f)
        print(f"  Voice profiles: {', '.join(profiles.keys())}")
    else:
        profiles = {}
        print("  Warning: No voice profiles found. Run 07_intellectual_dna.py first.")
        print("  Generating with basic style matching only.")

    print()
    print("=" * 60)
    print("  SYNTHETIC SERMON GENERATOR")
    print("  Saint John's Cathedral, Denver")
    print("=" * 60)
    print()

    # Select preacher
    available = list(PREACHERS.keys())
    print("Available preachers:")
    for i, name in enumerate(available, 1):
        has_profile = " (voice profile loaded)" if name in profiles else ""
        print(f"  {i}. {name}{has_profile}")

    while True:
        try:
            choice = input(f"\nSelect preacher (1-{len(available)}): ").strip()
            preacher = available[int(choice) - 1]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Try again.")

    print(f"\nSelected: {preacher}")

    # Get inputs
    print("\nProvide the following (or press Enter to skip):")
    occasion = input("  Liturgical occasion (e.g., 'Third Sunday in Lent'): ").strip()
    readings = input("  Scripture readings (e.g., 'Luke 15:1-10, Romans 8:28-39'): ").strip()
    date = input("  Date (e.g., '2026-03-15'): ").strip() or "upcoming Sunday"
    current_events = input("  Current events to address (or Enter to skip): ").strip()
    theme = input("  Any specific theme to explore? ").strip()

    if not occasion:
        occasion = "A Sunday in Ordinary Time"
    if not readings:
        readings = "To be determined by the preacher"
    if not current_events:
        current_events = "No specific current events provided."

    # Build the prompt
    profile = profiles.get(preacher, {})
    influence_map = profile.get("influence_map", {})

    voice_profile_text = influence_map.get("generative_prompt_seed", 
        f"Match the general style of an Episcopal preacher at a major urban cathedral.")

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

    # Get real excerpts via RAG
    search_topic = f"{occasion} {readings} {theme}".strip()
    real_excerpts = ""
    if has_rag:
        real_excerpts = get_relevant_excerpts(preacher, search_topic, collection, embedder)

    prompt = GENERATION_PROMPT.format(
        preacher=preacher,
        voice_profile=voice_profile_text,
        reference_summary=ref_summary or "Not yet analyzed",
        adjacent_voices=adjacent or "Not yet analyzed",
        date=date,
        occasion=occasion,
        readings=readings,
        current_events=current_events,
        real_excerpts=real_excerpts or "Not available",
    )

    print(f"\nGenerating sermon in the voice of {preacher}...")
    print("─" * 60)

    # Generate with streaming for a nice experience
    with client.messages.stream(
        model=CLAUDE_MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        full_text = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text

    print()
    print("─" * 60)
    print(f"\nWord count: {len(full_text.split())}")

    # Offer to save
    save = input("\nSave this sermon? (y/n): ").strip().lower()
    if save == "y":
        output_dir = DATA_DIR / "generated_sermons"
        output_dir.mkdir(exist_ok=True)
        filename = f"{date}_{preacher.replace(' ', '_')}_{occasion.replace(' ', '_')[:30]}.json"
        output = {
            "preacher": preacher,
            "date": date,
            "occasion": occasion,
            "readings": readings,
            "current_events": current_events,
            "theme": theme,
            "sermon_text": full_text,
            "generated_at": __import__("datetime").datetime.now().isoformat(),
            "model": CLAUDE_MODEL,
        }
        with open(output_dir / filename, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Saved to {output_dir / filename}")


if __name__ == "__main__":
    interactive_generate()
