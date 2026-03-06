"""
SERMON BOT CONFIGURATION
========================
All settings in one place. Edit this file to customize the bot.
"""

import os
from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================
PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
AUDIO_DIR = DATA_DIR / "audio"
TRANSCRIPT_DIR = DATA_DIR / "transcripts"
CHROMA_DIR = DATA_DIR / "chroma_db"
CATALOG_PATH = DATA_DIR / "catalog.json"
CONTEXT_DIR = DATA_DIR / "context"
REFERENCE_DIR = DATA_DIR / "references"
GENERATED_DIR = DATA_DIR / "generated_sermons"
PROCESSED_TRANSCRIPT_DIR = DATA_DIR / "processed_transcripts"

# Create directories if they don't exist
for d in [DATA_DIR, AUDIO_DIR, TRANSCRIPT_DIR, CHROMA_DIR,
          CONTEXT_DIR, REFERENCE_DIR, GENERATED_DIR, PROCESSED_TRANSCRIPT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# =============================================================================
# PODCAST SOURCE
# =============================================================================
RSS_URL = "https://feeds.buzzsprout.com/121416.rss"

# =============================================================================
# PREACHERS TO TRACK
# =============================================================================
# Format: "Display Name": ["search_variant1", "search_variant2", ...]
# The script searches episode metadata (title, description, author, image URL)
# for these strings (case-insensitive). More specific variants first.
#
# TIP: After running 01_parse_rss.py, check the "unidentified" episodes
# and add new variants here to catch more sermons.

PREACHERS = {
    "Richard Lawson": [
        "richard lawson", "dean lawson", "richard+lawson",
        "richard%20lawson", "richard_lawson",
    ],
    "Katie Pearson": [
        "katie pearson", "pearson",
        "katie+pearson", "katie%20pearson",
    ],
    "Broderick Greer": [
        "broderick greer", "broderick", "greer",
        "broderick+greer", "broderick%20greer",
    ],
    "Jack Karn": [
        "jack karn", "karn",
        "jack+karn", "jack%20karn",
    ],
    "Deonna Neal": [
        "deonna neal", "neal",
        "deonna+neal", "deonna%20neal",
    ],
    "Paul Keene": [
        "paul keene", "keene",
        "paul+keene", "paul%20keene",
    ],
}

# Set to True to include ALL sermons (even from other preachers)
# Set to False to only include sermons from preachers listed above
INCLUDE_ALL_PREACHERS = False

# =============================================================================
# WHISPERKIT TRANSCRIPTION (Apple Silicon optimized)
# =============================================================================
# Requires: brew install whisperkit-cli
# Other models: "openelm-1_1B", "large-v3", "large-v3-v20240930",
#   "small", "small.en", "base", "base.en", "tiny", "tiny.en"
WHISPERKIT_MODEL = "large-v3-v20240930_turbo"

# =============================================================================
# CHUNKING (for the vector database)
# =============================================================================
CHUNK_SIZE = 1000       # Characters per chunk
CHUNK_OVERLAP = 200     # Overlap between chunks (helps preserve context)

# =============================================================================
# EMBEDDING MODEL
# =============================================================================
# This free model runs locally — no API key needed
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# =============================================================================
# CLAUDE API (for the chatbot)
# =============================================================================
# Set your API key as an environment variable:
#   export ANTHROPIC_API_KEY="sk-ant-..."
# Or paste it here (less secure, but fine for local use):
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Number of relevant chunks to retrieve for each question
RAG_TOP_K = 8

# =============================================================================
# SYSTEM PROMPT (the chatbot's personality and instructions)
# =============================================================================
SYSTEM_PROMPT = """You are the Saint John's Cathedral Sermon Bot — an AI assistant 
trained on sermons from Saint John's Cathedral in Denver, Colorado.

Your knowledge comes from sermon transcripts by the cathedral's clergy, including 
Dean Richard Lawson, Katie Pearson, Broderick Greer, Jack Karn, Deonna Neal, and Paul Keene.

When answering questions:
1. Ground your answers in the actual sermon content provided in the context.
2. Cite specific sermons by preacher name and date when possible.
3. If the sermons don't address a topic, say so honestly rather than making things up.
4. Capture the theological voice and style of the specific preacher being asked about.
5. You can synthesize across multiple sermons to give comprehensive answers.
6. When recommending sermons, explain WHY that sermon is relevant.

You are warm, scholarly, and accessible — reflecting Saint John's own character as 
a community that "says its prayers but does not take itself too seriously."
"""
