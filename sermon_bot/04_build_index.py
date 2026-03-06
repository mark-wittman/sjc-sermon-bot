"""
PHASE 4: BUILD THE SEARCH INDEX
=================================
Chunks transcripts, generates embeddings, and stores them in ChromaDB.

WHAT THIS DOES (in plain English):
1. CHUNKING: Each sermon transcript is 2000-5000 words. That's too big
   to search effectively. We split each transcript into ~200-word chunks
   with some overlap so we don't lose context at the boundaries.

2. EMBEDDING: Each chunk gets converted into a "vector" — a list of 384
   numbers that represent the *meaning* of the text. Similar meanings
   produce similar numbers. This is what makes semantic search work.

3. INDEXING: We store all chunks + vectors in ChromaDB, a lightweight
   database optimized for this kind of search. When you ask a question
   later, the bot converts your question to a vector too, then finds
   the sermon chunks whose vectors are most similar.

RUN: python 04_build_index.py
"""

import json
import chromadb
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from config import (
    TRANSCRIPT_DIR, CHROMA_DIR, CATALOG_PATH,
    CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL
)


def load_transcripts() -> list[dict]:
    """Load all transcripts and enrich with catalog metadata."""
    
    # Load catalog for metadata
    catalog_map = {}
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
        for ep in catalog["episodes"]:
            # Create lookup keys from date
            catalog_map[ep["date"]] = ep
    
    transcripts = []
    for path in sorted(TRANSCRIPT_DIR.glob("*.json")):
        with open(path) as f:
            t = json.load(f)
        
        # Try to find catalog entry by date
        date = t.get("date", "unknown")
        catalog_entry = catalog_map.get(date, {})
        
        # Parse preacher from filename if not in transcript
        preacher = catalog_entry.get("preacher") or "Unknown"
        if preacher == "Unknown":
            # Try to extract from filename
            parts = path.stem.split("_")
            if len(parts) >= 3:
                preacher = f"{parts[1]} {parts[2]}"
        
        transcripts.append({
            "text": t["full_text"],
            "date": date,
            "title": catalog_entry.get("title", path.stem),
            "preacher": preacher,
            "word_count": t.get("word_count", len(t["full_text"].split())),
            "source_file": path.name,
        })
    
    return transcripts


def chunk_transcripts(transcripts: list[dict]) -> tuple[list[str], list[dict]]:
    """Split transcripts into chunks with metadata."""
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    all_chunks = []
    all_metadata = []
    
    for t in transcripts:
        chunks = splitter.split_text(t["text"])
        
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadata.append({
                "preacher": t["preacher"],
                "date": t["date"],
                "title": t["title"],
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source_file": t["source_file"],
            })
    
    return all_chunks, all_metadata


def main():
    # Load transcripts
    transcripts = load_transcripts()
    if not transcripts:
        print("No transcripts found in data/transcripts/")
        print("Run 03_transcribe.py first.")
        return
    
    print(f"Loaded {len(transcripts)} transcripts")
    total_words = sum(t["word_count"] for t in transcripts)
    print(f"Total words: {total_words:,}")
    print()
    
    # Chunk
    print(f"Chunking (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks, metadata = chunk_transcripts(transcripts)
    print(f"Created {len(chunks)} chunks")
    print()
    
    # Load embedding model
    print(f"Loading embedding model '{EMBEDDING_MODEL}'...")
    print("(First run downloads the model — one-time thing, ~90 MB)")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded!")
    print()
    
    # Generate embeddings
    print(f"Generating embeddings for {len(chunks)} chunks...")
    print("(This may take a few minutes)")
    embeddings = model.encode(chunks, show_progress_bar=True, batch_size=64)
    print(f"Embeddings shape: {embeddings.shape}")
    print()
    
    # Store in ChromaDB
    print("Storing in ChromaDB...")
    
    # Remove old database if it exists
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # Delete existing collection if present (fresh build)
    try:
        client.delete_collection("sermons")
    except Exception:
        pass
    
    collection = client.create_collection(
        name="sermons",
        metadata={"description": "Saint John's Cathedral sermon chunks"},
    )
    
    # Add in batches (ChromaDB has a batch size limit)
    batch_size = 500
    for i in range(0, len(chunks), batch_size):
        batch_end = min(i + batch_size, len(chunks))
        collection.add(
            ids=[f"chunk_{j}" for j in range(i, batch_end)],
            documents=chunks[i:batch_end],
            embeddings=embeddings[i:batch_end].tolist(),
            metadatas=metadata[i:batch_end],
        )
    
    print(f"Indexed {collection.count()} chunks in ChromaDB")
    print(f"Database location: {CHROMA_DIR}")
    print()
    
    # Quick test search
    print("Quick test — searching for 'grace and forgiveness'...")
    test_query = model.encode(["grace and forgiveness"]).tolist()
    results = collection.query(
        query_embeddings=test_query,
        n_results=3,
    )
    print("Top 3 results:")
    for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"  {i+1}. [{meta['date']}] {meta['preacher']} — {meta['title']}")
        print(f"     \"{doc[:100]}...\"")
    print()
    
    print("Index built successfully!")
    print(f"Next step: python 05_chat.py")


if __name__ == "__main__":
    main()
