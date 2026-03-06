from __future__ import annotations
"""
PHASE 1: PARSE THE RSS FEED
============================
Downloads the Saint John's Cathedral podcast feed and catalogs all episodes.

WHAT IT DOES:
1. Downloads the RSS feed (a structured list of all podcast episodes)
2. Extracts metadata: title, date, audio URL, duration, description
3. Identifies which preacher gave each sermon
4. Saves everything to data/catalog.json

RUN: python 01_parse_rss.py
"""

import feedparser
import json
from datetime import datetime
from collections import Counter
from config import RSS_URL, PREACHERS, CATALOG_PATH, INCLUDE_ALL_PREACHERS


def identify_preacher(entry: dict) -> str | None:
    """Figure out who preached by searching all available metadata."""
    title = entry.get("title", "")
    description = entry.get("summary", entry.get("subtitle", ""))
    author = entry.get("author", "")
    
    # Gather all link URLs (image URLs often contain preacher names)
    all_links = " ".join(link.get("href", "") for link in entry.get("links", []))
    
    # Combine everything for searching (lowercase)
    search_text = f"{title} {description} {author} {all_links}".lower()
    
    # Search for each preacher
    for preacher, variants in PREACHERS.items():
        for variant in variants:
            if variant.lower() in search_text:
                return preacher
    
    return None


def parse_feed():
    """Download and parse the RSS feed."""
    print(f"Downloading RSS feed from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    
    if feed.bozo and not feed.entries:
        print(f"Error parsing feed: {feed.bozo_exception}")
        return None
    
    print(f"Found {len(feed.entries)} episodes")
    print(f"Podcast: {feed.feed.get('title', 'Unknown')}")
    print()
    
    episodes = []
    preacher_counts = Counter()
    unidentified = []
    
    for entry in feed.entries:
        try:
            pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
        except (AttributeError, TypeError):
            pub_date = entry.get("published", "unknown")
        
        # Get audio URL
        audio_url = ""
        for link in entry.get("links", []):
            href = link.get("href", "")
            if link.get("type", "").startswith("audio/") or href.endswith(".mp3"):
                audio_url = href
                break
        if not audio_url:
            for enc in entry.get("enclosures", []):
                audio_url = enc.get("href", "")
                break
        
        preacher = identify_preacher(entry)
        
        episode = {
            "title": entry.get("title", "Untitled"),
            "date": pub_date,
            "preacher": preacher,
            "audio_url": audio_url,
            "description": entry.get("summary", "")[:500],
            "author_field": entry.get("author", ""),
            "duration": entry.get("itunes_duration", ""),
        }
        episodes.append(episode)
        
        if preacher:
            preacher_counts[preacher] += 1
        else:
            unidentified.append(f"[{pub_date}] {entry.get('title', 'Untitled')}")
    
    return episodes, preacher_counts, unidentified


def main():
    result = parse_feed()
    if result is None:
        return
    
    episodes, preacher_counts, unidentified = result
    episodes.sort(key=lambda x: x["date"], reverse=True)
    
    # Summary
    print("=" * 60)
    print("SERMON CATALOG SUMMARY")
    print("=" * 60)
    print(f"Total episodes: {len(episodes)}")
    print()
    print("Sermons by preacher:")
    for preacher, count in preacher_counts.most_common():
        pct = count / len(episodes) * 100
        print(f"  {preacher}: {count} ({pct:.0f}%)")
    print(f"  Unidentified: {len(unidentified)}")
    print()
    
    if INCLUDE_ALL_PREACHERS:
        print(f"Mode: ALL preachers -> {len(episodes)} sermons to process")
    else:
        print(f"Mode: Selected preachers only -> {sum(preacher_counts.values())} sermons")
    
    dates = [e["date"] for e in episodes if e["date"] != "unknown"]
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")
    print()
    
    # Unidentified episodes
    if unidentified:
        print(f"Unidentified episodes (first 15 of {len(unidentified)}):")
        print("  (Add names to config.py PREACHERS to catch more)")
        for item in unidentified[:15]:
            print(f"  {item}")
        if len(unidentified) > 15:
            print(f"  ... and {len(unidentified) - 15} more")
    print()
    
    # Samples
    for preacher in PREACHERS:
        eps = [e for e in episodes if e["preacher"] == preacher]
        if eps:
            print(f"{preacher} ({len(eps)} sermons) — recent:")
            for ep in eps[:3]:
                dur = f" ({ep['duration']})" if ep['duration'] else ""
                print(f"  [{ep['date']}] {ep['title']}{dur}")
            print()
    
    # Save
    catalog = {
        "generated": datetime.now().isoformat(),
        "rss_url": RSS_URL,
        "total_episodes": len(episodes),
        "preacher_counts": dict(preacher_counts),
        "unidentified_count": len(unidentified),
        "episodes": episodes,
    }
    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Catalog saved to {CATALOG_PATH}")
    print(f"Next step: python 02_download_audio.py")


if __name__ == "__main__":
    main()
