"""
STEP 3.5: PROCESS TRANSCRIPTS
==============================
Cleans WhisperKit tokens from transcripts and segments them into
~3-4 minute topical sections with AI-generated headers.

Input:  data/transcripts/*.json  (raw WhisperKit output)
Output: data/processed_transcripts/*.json  (clean, sectioned)

Usage:
    python 03_5_process_transcripts.py
"""

from __future__ import annotations

import json
import re
import os
from pathlib import Path
from typing import Optional

from anthropic import Anthropic
from config import TRANSCRIPT_DIR, PROCESSED_TRANSCRIPT_DIR, ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove WhisperKit special tokens and clean up whitespace."""
    text = re.sub(r'<\|startoftranscript\|>', '', text)
    text = re.sub(r'<\|endoftext\|>', '', text)
    text = re.sub(r'<\|en\|>', '', text)
    text = re.sub(r'<\|transcribe\|>', '', text)
    # Remove timestamp tokens like <|0.00|>, <|10.28|>
    text = re.sub(r'<\|\d+\.?\d*\|>', '', text)
    # Clean up extra whitespace
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ---------------------------------------------------------------------------
# Segmentation into ~3-4 minute blocks
# ---------------------------------------------------------------------------

SECTION_DURATION = 210  # ~3.5 minutes in seconds

def group_segments(segments: list, target_duration: float = SECTION_DURATION) -> list:
    """Group raw WhisperKit segments into larger blocks by time."""
    if not segments:
        return []

    blocks = []
    current_texts = []
    block_start = segments[0].get("start", 0.0)

    for seg in segments:
        current_texts.append(clean_text(seg.get("text", "")))
        block_end = seg.get("end", seg.get("start", 0.0))

        if block_end - block_start >= target_duration:
            combined = " ".join(t for t in current_texts if t)
            combined = re.sub(r'  +', ' ', combined).strip()
            if combined:
                blocks.append({
                    "start_time": round(block_start, 2),
                    "end_time": round(block_end, 2),
                    "text": combined,
                })
            current_texts = []
            block_start = block_end

    # Last block
    if current_texts:
        combined = " ".join(t for t in current_texts if t)
        combined = re.sub(r'  +', ' ', combined).strip()
        if combined:
            last_end = segments[-1].get("end", segments[-1].get("start", 0.0))
            blocks.append({
                "start_time": round(block_start, 2),
                "end_time": round(last_end, 2),
                "text": combined,
            })

    return blocks

# ---------------------------------------------------------------------------
# Generate section headers via Claude Haiku
# ---------------------------------------------------------------------------

def generate_header(text: str) -> str:
    """Ask Claude Haiku for a short (3-6 word) section header."""
    # Take first ~500 chars to keep cost low
    excerpt = text[:500]
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=30,
            messages=[{
                "role": "user",
                "content": (
                    "Give a short title (3-6 words) for this sermon section. "
                    "Return ONLY the title, no quotes or punctuation.\n\n"
                    f"{excerpt}"
                ),
            }],
        )
        header = response.content[0].text.strip().strip('"').strip("'")
        return header
    except Exception as e:
        print(f"  Warning: header generation failed ({e}), using fallback")
        return "Continued"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def process_transcript(path: Path) -> Optional[dict]:
    """Process a single transcript file."""
    with open(path) as f:
        data = json.load(f)

    raw_full = data.get("full_text", "")
    segments = data.get("segments", [])

    # Clean full text
    full_text = clean_text(raw_full)
    if not full_text:
        return None

    # Group segments into blocks
    blocks = group_segments(segments)

    # Generate headers for each block
    sections = []
    for i, block in enumerate(blocks):
        print(f"    Section {i+1}/{len(blocks)}...", end=" ", flush=True)
        header = generate_header(block["text"])
        print(header)
        sections.append({
            "header": header,
            "start_time": block["start_time"],
            "end_time": block["end_time"],
            "text": block["text"],
        })

    word_count = len(full_text.split())

    return {
        "source_file": data.get("source_file", path.name),
        "date": data.get("date", ""),
        "full_text": full_text,
        "sections": sections,
        "word_count": word_count,
    }


def main():
    transcript_files = sorted(TRANSCRIPT_DIR.glob("*.json"))
    print(f"Found {len(transcript_files)} transcripts to process\n")

    processed = 0
    skipped = 0

    for path in transcript_files:
        out_path = PROCESSED_TRANSCRIPT_DIR / path.name

        # Skip if already processed
        if out_path.exists():
            print(f"  Skipping (already processed): {path.name}")
            skipped += 1
            continue

        print(f"Processing: {path.name}")
        result = process_transcript(path)
        if result is None:
            print(f"  Skipped (empty transcript)")
            skipped += 1
            continue

        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Saved: {out_path.name} ({result['word_count']} words, {len(result['sections'])} sections)\n")
        processed += 1

    print(f"\nDone! Processed: {processed}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
