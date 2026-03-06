# SJC Sermon Bot

An AI-powered system trained on sermons from Saint John's Cathedral, Denver. It goes beyond simple search — it maps each preacher's intellectual DNA, contextualizes sermons in their historical moment, and can generate synthetic sermons in each preacher's authentic voice.

## What This Does

**Search & Chat** — Ask theological questions and get answers grounded in actual sermon content, with citations.

**Temporal Context** — Each sermon is enriched with what was happening that week: church news, Denver news, national/international events, and lectionary readings. The bot understands that a sermon about fear on March 15, 2020 is about COVID.

**Intellectual DNA Mapping** — Every writer, scholar, theologian, and philosopher referenced by each preacher is cataloged. This builds an influence profile showing each preacher's intellectual world, theological commitments, and voice signature.

**Synthetic Sermon Generation** — Using voice profiles, reference patterns, and RAG retrieval, the system can generate sermons in each preacher's authentic style for any given Sunday.

## The Pipeline (8 Phases)

```
01_parse_rss.py          Parse podcast feed, identify preachers
02_download_audio.py     Download sermon audio files
03_transcribe.py         Speech-to-text with Whisper
04_build_index.py        Chunk, embed, and index for search
05_chat.py               Interactive chatbot (RAG + Claude)
06_enrich_context.py     Add temporal context (news, events) per sermon
07_intellectual_dna.py   Extract references, build influence maps + voice profiles
08_generate_sermon.py    Generate synthetic sermons in each preacher's voice
```

## Project Structure

```
sermon_bot/
├── README.md
├── requirements.txt
├── config.py                  ← All settings: preachers, models, API keys
├── 01_parse_rss.py           ← Catalog 606+ episodes from Buzzsprout
├── 02_download_audio.py      ← Download MP3s for selected preachers
├── 03_transcribe.py          ← Whisper transcription (local, free)
├── 04_build_index.py         ← ChromaDB vector index
├── 05_chat.py                ← Sermon chatbot
├── 06_enrich_context.py      ← Temporal context enrichment
├── 07_intellectual_dna.py    ← Reference extraction + influence mapping
├── 08_generate_sermon.py     ← Synthetic sermon generator
└── data/
    ├── catalog.json          ← Episode metadata
    ├── audio/                ← MP3 files (can delete after transcription)
    ├── transcripts/          ← JSON transcripts with timestamps
    ├── chroma_db/            ← Vector search index
    ├── context/              ← Temporal context per sermon
    ├── references/           ← Intellectual DNA maps + voice profiles
    └── generated_sermons/    ← Synthetic sermon output
```

## Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key (for phases 5-8)
- ~10-20 GB disk space for audio (temporary)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Pipeline
```bash
# Phase 1: Catalog all episodes
python 01_parse_rss.py

# Phase 2: Download audio (takes a while — 400+ sermons)
python 02_download_audio.py

# Phase 3: Transcribe (longest step — can run overnight)
python 03_transcribe.py

# Phase 4: Build search index
python 04_build_index.py

# Phase 5: Chat with the bot
export ANTHROPIC_API_KEY="sk-ant-..."
python 05_chat.py

# Phase 6: Enrich with temporal context
python 06_enrich_context.py

# Phase 7: Map intellectual DNA (the fascinating part)
python 07_intellectual_dna.py

# Phase 8: Generate synthetic sermons
python 08_generate_sermon.py
```

Phases 1-5 give you a working chatbot. Phases 6-8 are the advanced layer.

## Preachers Tracked

- **Richard Lawson** — Dean. Sewanee-trained. Published on mysticism and religious architecture.
- **Katie Pearson**
- **Broderick Greer**
- **Jack Karn** — Canon
- **Deonna Neal**
- **Paul Keene**

Edit `config.py` to add or remove preachers.

## Time & Cost Estimates

| Phase | Time | Cost |
|-------|------|------|
| 01 Parse RSS | 10 seconds | Free |
| 02 Download audio | 1-2 hours | Free |
| 03 Transcribe | 10-15 hours (CPU) / 1-2 hours (GPU) | Free |
| 04 Build index | 5-10 minutes | Free |
| 05 Chat | Interactive | ~$0.01/question |
| 06 Temporal context | 1-2 hours (API calls) | ~$2-5 |
| 07 Intellectual DNA | 2-4 hours (API calls) | ~$5-15 |
| 08 Generate sermon | 1-2 min per sermon | ~$0.05/sermon |

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Podcast feed | feedparser | Standard RSS parsing |
| Audio download | requests + tqdm | Simple with progress bars |
| Transcription | openai-whisper | Free, local, accurate |
| Text chunking | langchain | Battle-tested splitting |
| Embeddings | sentence-transformers | Free, local |
| Vector DB | chromadb | Zero config, local |
| Chat + Generation | Anthropic Claude API | Best quality |

## For the Coding Novice

Scripts are numbered in order. Run them 01 through 08. Each script:
- Has comments explaining what it does and why
- Skips work that's already done (safe to re-run)
- Prints progress so you know what's happening

If something breaks, copy the error and paste it to Claude Code.
