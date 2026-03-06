"""
PHASE 5: THE SERMON CHATBOT
=============================
Ask questions about sermons and get answers grounded in actual content.

HOW IT WORKS:
1. You type a question
2. Your question gets converted to a vector (same as the sermon chunks)
3. ChromaDB finds the most similar sermon chunks
4. Those chunks are sent to Claude along with your question
5. Claude answers based on the sermon content, citing specific sermons

PREREQUISITES:
- Phases 1-4 completed
- ANTHROPIC_API_KEY set (export ANTHROPIC_API_KEY="sk-ant-...")

RUN: python 05_chat.py
"""

import anthropic
import chromadb
from sentence_transformers import SentenceTransformer
from config import (
    CHROMA_DIR, EMBEDDING_MODEL, ANTHROPIC_API_KEY,
    CLAUDE_MODEL, RAG_TOP_K, SYSTEM_PROMPT
)


def format_context(results: dict) -> str:
    """Format retrieved sermon chunks into context for Claude."""
    
    context_parts = []
    for i, (doc, meta) in enumerate(zip(
        results["documents"][0], results["metadatas"][0]
    )):
        context_parts.append(
            f"--- Sermon Excerpt {i+1} ---\n"
            f"Preacher: {meta['preacher']}\n"
            f"Date: {meta['date']}\n"
            f"Title: {meta['title']}\n"
            f"Content:\n{doc}\n"
        )
    
    return "\n".join(context_parts)


def main():
    # Check API key
    if not ANTHROPIC_API_KEY:
        print("ERROR: No Anthropic API key found!")
        print("Set it with: export ANTHROPIC_API_KEY='sk-ant-...'")
        print("Or add it to config.py")
        return
    
    # Load models and database
    print("Loading sermon database...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    try:
        collection = client.get_collection("sermons")
    except ValueError:
        print("ERROR: No sermon index found. Run 04_build_index.py first.")
        return
    
    print(f"Loaded {collection.count()} sermon chunks")
    
    print("Loading embedding model...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    
    print("Connecting to Claude...")
    claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    print()
    print("=" * 60)
    print("  SAINT JOHN'S CATHEDRAL SERMON BOT")
    print("  Ask anything about sermons from Richard, Katie, Jack,")
    print("  Deonna, or Paul. Type 'quit' to exit.")
    print("=" * 60)
    print()
    
    # Conversation history for multi-turn chat
    messages = []
    
    while True:
        # Get user input
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        
        # Search for relevant sermon chunks
        query_embedding = embedder.encode([question]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=RAG_TOP_K,
        )
        
        context = format_context(results)
        
        # Build the message with context
        user_message = (
            f"Here are relevant sermon excerpts from Saint John's Cathedral:\n\n"
            f"{context}\n\n"
            f"Based on these sermon excerpts, please answer this question:\n"
            f"{question}"
        )
        
        messages.append({"role": "user", "content": user_message})
        
        # Send to Claude
        try:
            response = claude.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=messages,
            )
            
            answer = response.content[0].text
            messages.append({"role": "assistant", "content": answer})
            
            # Print the answer
            print(f"\nSermon Bot: {answer}\n")
            
            # Show which sermons were referenced
            seen = set()
            sources = []
            for meta in results["metadatas"][0]:
                key = f"{meta['date']}_{meta['preacher']}"
                if key not in seen:
                    seen.add(key)
                    sources.append(f"  [{meta['date']}] {meta['preacher']} — {meta['title']}")
            
            print(f"  Sources searched ({len(sources)} sermons):")
            for s in sources[:5]:
                print(s)
            print()
            
        except Exception as e:
            print(f"\nError calling Claude: {e}\n")
            messages.pop()  # Remove the failed message
    
    print("\nThanks for chatting! May the peace of the Lord be always with you.")


if __name__ == "__main__":
    main()
