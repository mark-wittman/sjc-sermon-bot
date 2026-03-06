"""
PHASE 3: TRANSCRIBE SERMONS WITH WHISPERKIT
=============================================
Converts audio files to text transcripts using WhisperKit (Apple Silicon optimized).

WHAT IT DOES:
1. Calls whisperkit-cli for each audio file in data/audio/
2. Parses the JSON report output
3. Saves transcripts as JSON files in data/transcripts/
4. Skips files already transcribed (safe to re-run)

PREREQUISITE:
    brew install whisperkit-cli

RUN: python 03_transcribe.py
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from config import AUDIO_DIR, TRANSCRIPT_DIR, CATALOG_PATH, WHISPERKIT_MODEL


def check_whisperkit_installed():
    """Verify whisperkit-cli is available on PATH."""
    if shutil.which("whisperkit-cli") is None:
        print("ERROR: whisperkit-cli is not installed.")
        print("Install it with:  brew install whisperkit-cli")
        raise SystemExit(1)


def transcribe_audio(audio_path: Path) -> dict:
    """
    Transcribe a single audio file using whisperkit-cli.

    Returns a dict with the full text and timestamped segments.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            "whisperkit-cli", "transcribe",
            "--audio-path", str(audio_path),
            "--model", WHISPERKIT_MODEL,
            "--language", "en",
            "--report",
            "--report-path", tmpdir,
        ]

        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Find the JSON report file whisperkit-cli wrote
        report_files = list(Path(tmpdir).glob("*.json"))
        if not report_files:
            raise RuntimeError(f"No JSON report found in {tmpdir}")

        with open(report_files[0]) as f:
            report = json.load(f)

        # Extract segments from the report
        raw_segments = report.get("segments", report.get("allSegments", []))
        segments = []
        for seg in raw_segments:
            segments.append({
                "start": seg.get("start", 0),
                "end": seg.get("end", 0),
                "text": seg.get("text", ""),
            })

        full_text = " ".join(seg["text"].strip() for seg in segments)

        return {
            "text": full_text,
            "segments": segments,
        }


def main():
    check_whisperkit_installed()

    # Check for audio files
    audio_files = sorted(AUDIO_DIR.glob("*.mp3"))
    if not audio_files:
        print("No audio files found in data/audio/")
        print("Run 02_download_audio.py first.")
        return

    # Check what's already transcribed
    existing = set(f.stem for f in TRANSCRIPT_DIR.glob("*.json"))
    to_process = [f for f in audio_files if f.stem not in existing]

    print(f"Audio files found: {len(audio_files)}")
    print(f"Already transcribed: {len(existing)}")
    print(f"To process: {len(to_process)}")
    print()

    if not to_process:
        print("All files already transcribed! Nothing to do.")
        return

    print(f"Using WhisperKit model: {WHISPERKIT_MODEL}")
    print()

    # Load catalog for metadata enrichment
    catalog_lookup = {}
    if CATALOG_PATH.exists():
        with open(CATALOG_PATH) as f:
            catalog = json.load(f)
        for ep in catalog["episodes"]:
            # Match by date and preacher in filename
            key_parts = [ep["date"], ep.get("preacher", "")]
            catalog_lookup[ep["date"] + "_" + (ep.get("preacher") or "")] = ep

    # Process each file
    for i, audio_path in enumerate(to_process, 1):
        print(f"[{i}/{len(to_process)}] Transcribing: {audio_path.name[:60]}...")
        start_time = datetime.now()

        try:
            result = transcribe_audio(audio_path)

            # Parse metadata from filename: "2024-01-15_Richard_Lawson_Title.mp3"
            parts = audio_path.stem.split("_", 3)
            date = parts[0] if len(parts) > 0 else "unknown"

            # Build transcript record
            transcript = {
                "source_file": audio_path.name,
                "date": date,
                "transcribed_at": datetime.now().isoformat(),
                "whisperkit_model": WHISPERKIT_MODEL,
                "full_text": result["text"],
                "segments": result["segments"],
                "word_count": len(result["text"].split()),
            }

            # Save
            output_path = TRANSCRIPT_DIR / f"{audio_path.stem}.json"
            with open(output_path, "w") as f:
                json.dump(transcript, f, indent=2)

            elapsed = (datetime.now() - start_time).total_seconds()
            words = transcript["word_count"]
            print(f"  Done! {words} words, {elapsed:.0f}s")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    # Final summary
    total = len(list(TRANSCRIPT_DIR.glob("*.json")))
    print()
    print(f"Transcription complete! {total} transcripts in {TRANSCRIPT_DIR}")
    print(f"Next step: python 04_build_index.py")


if __name__ == "__main__":
    main()
