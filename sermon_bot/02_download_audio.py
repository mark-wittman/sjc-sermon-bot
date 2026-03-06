"""
PHASE 2: DOWNLOAD SERMON AUDIO
================================
Downloads MP3 files for all identified sermons from the podcast.

WHAT IT DOES:
1. Reads the catalog from Phase 1 (data/catalog.json)
2. Filters to only the preachers you care about
3. Downloads each sermon's audio file to data/audio/
4. Skips files that have already been downloaded (safe to re-run)

SPACE NEEDED: ~10-20 GB for all sermons. Each sermon is ~5-15 MB.
You can delete audio files after transcription to reclaim space.

RUN: python 02_download_audio.py
"""

import json
import requests
from pathlib import Path
from tqdm import tqdm
from config import CATALOG_PATH, AUDIO_DIR, INCLUDE_ALL_PREACHERS


def sanitize_filename(name: str) -> str:
    """Remove characters that aren't safe in filenames."""
    return "".join(c if c.isalnum() or c in " -_" else "" for c in name).strip()


def download_file(url: str, dest: Path) -> bool:
    """Download a file with a progress bar. Returns True on success."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) SJCSermonBot/1.0"}
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        
        total_size = int(response.headers.get("content-length", 0))
        
        with open(dest, "wb") as f:
            with tqdm(total=total_size, unit="B", unit_scale=True, 
                      desc=dest.name[:40], leave=False) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        if dest.exists():
            dest.unlink()  # Remove partial download
        return False


def main():
    # Load catalog
    if not CATALOG_PATH.exists():
        print("Error: catalog.json not found. Run 01_parse_rss.py first.")
        return
    
    with open(CATALOG_PATH) as f:
        catalog = json.load(f)
    
    episodes = catalog["episodes"]
    
    # Filter to relevant preachers
    if not INCLUDE_ALL_PREACHERS:
        episodes = [e for e in episodes if e["preacher"] is not None]
    
    print(f"Episodes to download: {len(episodes)}")
    print(f"Destination: {AUDIO_DIR}")
    print()
    
    # Check what we already have
    existing = set(f.stem for f in AUDIO_DIR.glob("*.mp3"))
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for ep in episodes:
        if not ep["audio_url"]:
            print(f"  No audio URL for: {ep['title']}")
            failed += 1
            continue
        
        # Create a filename: "2024-01-15_Richard_Lawson_Title_Here.mp3"
        preacher_slug = sanitize_filename(ep["preacher"] or "Unknown")
        title_slug = sanitize_filename(ep["title"])[:60]
        filename = f"{ep['date']}_{preacher_slug}_{title_slug}"
        
        if filename in existing:
            skipped += 1
            continue
        
        dest = AUDIO_DIR / f"{filename}.mp3"
        
        print(f"[{downloaded + skipped + failed + 1}/{len(episodes)}] {ep['title'][:50]}...")
        if download_file(ep["audio_url"], dest):
            downloaded += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Done! Downloaded: {downloaded}, Skipped (already had): {skipped}, Failed: {failed}")
    print(f"Audio files: {AUDIO_DIR}")
    
    # Calculate total size
    total_mb = sum(f.stat().st_size for f in AUDIO_DIR.glob("*.mp3")) / (1024 * 1024)
    print(f"Total audio size: {total_mb:.0f} MB")
    print(f"\nNext step: python 03_transcribe.py")


if __name__ == "__main__":
    main()
