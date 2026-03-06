from __future__ import annotations
"""
PHASE 7: INTELLECTUAL DNA MAPPING
====================================
Extract every writer, scholar, theologian, philosopher, and book
referenced in each preacher's sermons. Then map their intellectual
influences and find similar thinkers.

WHAT IT DOES:
1. EXTRACTION: Sends each transcript to Claude and asks it to identify
   every reference to a thinker, writer, book, or intellectual tradition.
   This catches both explicit citations ("As Bonhoeffer wrote...") and
   implicit references ("the theologian who spoke of cheap grace...").

2. AGGREGATION: Builds a reference profile for each preacher showing
   who they cite most, what traditions they draw from, and how their
   references evolve over time.

3. INFLUENCE MAPPING: For each preacher's reference set, Claude identifies
   similar thinkers they DON'T cite — expanding the intellectual map to
   find "adjacent voices" who share the same theological DNA.

4. VOICE PROFILE: Synthesizes everything into a "preacher voice profile"
   that captures their intellectual style, preferred sources, theological
   commitments, and rhetorical patterns. This is the foundation for
   generating synthetic sermons that sound authentically like each preacher.

OUTPUT:
- data/references/[preacher]_references.json — All citations per sermon
- data/references/[preacher]_influence_map.json — Aggregated influence profile
- data/references/voice_profiles.json — Synthesis for sermon generation

RUN: python 07_intellectual_dna.py
"""

import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import anthropic
from config import (
    TRANSCRIPT_DIR, DATA_DIR, CATALOG_PATH,
    ANTHROPIC_API_KEY, CLAUDE_MODEL, PREACHERS
)

REFERENCE_DIR = DATA_DIR / "references"
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

# ─── EXTRACTION PROMPT ────────────────────────────────────────────────────────
EXTRACT_PROMPT = """Analyze this sermon transcript and extract ALL intellectual references.

Preacher: {preacher}
Date: {date}
Title: "{title}"

TRANSCRIPT:
{text}

Please identify every reference to:

1. **NAMED THINKERS** — Anyone cited by name: theologians, philosophers, writers, 
   poets, scholars, saints, church fathers, historical figures used as intellectual 
   authorities (not just mentioned in passing as narrative characters).

2. **BOOKS & WORKS** — Specific books, articles, poems, hymns, or other works cited 
   or alluded to (beyond scripture).

3. **SCRIPTURE** — All biblical passages referenced, quoted, or alluded to. 
   Use standard citation format (e.g., "John 3:16", "Romans 8:28-39").

4. **INTELLECTUAL TRADITIONS** — Schools of thought invoked: existentialism, 
   liberation theology, mysticism, process theology, Augustinian thought, etc.

5. **IMPLICIT REFERENCES** — Ideas or phrases that clearly come from a specific 
   thinker even if not named. For example, "cheap grace" = Bonhoeffer, 
   "cloud of unknowing" = medieval mystical tradition, "the ground of being" = Tillich.

For each reference, provide:
- name: The person, work, or tradition
- type: "thinker" | "book" | "scripture" | "tradition" | "implicit"
- context: A brief quote or description of how it's used in the sermon (1 sentence)
- significance: "central" (builds the sermon's argument), "supporting" (used as evidence), 
  or "passing" (brief mention)

Also note the sermon's:
- primary_theme: The main topic or argument (1 sentence)
- rhetorical_style: How the preacher makes their case (e.g., "narrative storytelling", 
  "scholarly argument", "pastoral reflection", "prophetic challenge")

Respond in JSON format:
{{
  "references": [
    {{"name": "...", "type": "...", "context": "...", "significance": "..."}},
    ...
  ],
  "primary_theme": "...",
  "rhetorical_style": "..."
}}"""

# ─── INFLUENCE MAP PROMPT ─────────────────────────────────────────────────────
INFLUENCE_MAP_PROMPT = """I have a complete catalog of intellectual references from a preacher's sermons over several years. Based on this reference profile, I need you to:

PREACHER: {preacher}
ROLE: {role}

REFERENCE SUMMARY:
Most cited thinkers (with frequency):
{top_thinkers}

Most cited books/works:
{top_books}

Intellectual traditions drawn from:
{traditions}

Scripture emphasis (most referenced books of the Bible):
{scripture_emphasis}

Rhetorical styles used:
{styles}

Themes over time:
{themes}

Please provide:

## 1. INTELLECTUAL PROFILE
A 2-3 paragraph portrait of this preacher's intellectual world. What kind of 
theologian are they? Where do they sit on the spectrum from academic to pastoral, 
from progressive to traditional, from systematic to narrative?

## 2. THEOLOGICAL COMMITMENTS
What theological convictions emerge from their reference patterns? What do they 
care about most deeply? What's their implicit theology even when they don't name it?

## 3. ADJACENT VOICES (The Extended Influence Set)
Based on WHO they cite, identify 10-15 thinkers they DON'T cite but whose work 
is closely aligned. These are the "you'd also like..." recommendations for their 
intellectual world. For each:
- Name and brief description
- Why they're adjacent to this preacher's thinking
- One specific work that would resonate

## 4. VOICE SIGNATURE
Describe the distinctive elements of this preacher's voice that a language model 
would need to capture to generate authentic-sounding content:
- Vocabulary patterns (formal/casual, technical/accessible)
- Sentence structure preferences
- How they use humor, if at all
- How they handle difficult topics
- Their relationship with doubt and certainty
- How they move between scripture, tradition, reason, and experience

## 5. GENERATIVE PROMPT SEED
Write a system prompt (200-300 words) that could be used to make a language model 
generate sermons in this preacher's authentic voice and intellectual style.

Respond in JSON format with keys: intellectual_profile, theological_commitments, 
adjacent_voices (array), voice_signature, generative_prompt_seed."""

PREACHER_ROLES = {
    "Richard Lawson": "Dean of Saint John's Cathedral, Denver. Sewanee-trained. Published scholar on mysticism and religious architecture.",
    "Katie Pearson": "Clergy at Saint John's Cathedral, Denver.",
    "Broderick Greer": "Clergy at Saint John's Cathedral, Denver.",
    "Jack Karn": "Canon at Saint John's Cathedral, Denver.",
    "Deonna Neal": "Clergy at Saint John's Cathedral, Denver.",
    "Paul Keene": "Clergy at Saint John's Cathedral, Denver.",
}


def load_transcripts_for_preacher(preacher: str) -> list[dict]:
    """Load all transcripts for a specific preacher."""
    transcripts = []
    for path in sorted(TRANSCRIPT_DIR.glob("*.json")):
        # Check if this transcript belongs to this preacher
        if preacher.replace(" ", "_") in path.stem:
            with open(path) as f:
                t = json.load(f)
            transcripts.append({
                "text": t["full_text"],
                "date": t.get("date", "unknown"),
                "title": path.stem,
                "source_file": path.name,
            })
    return transcripts


def extract_references(client, preacher: str, sermon: dict) -> dict | None:
    """Extract intellectual references from a single sermon."""
    # Truncate very long transcripts to stay within token limits
    text = sermon["text"][:12000]

    prompt = EXTRACT_PROMPT.format(
        preacher=preacher,
        date=sermon["date"],
        title=sermon["title"],
        text=text,
    )

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        # Parse JSON from response
        response_text = response.content[0].text
        # Handle case where Claude wraps JSON in markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  Warning: Could not parse response as JSON: {e}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def aggregate_references(all_refs: list[dict], preacher: str) -> dict:
    """Aggregate references across all sermons for a preacher."""
    thinkers = Counter()
    books = Counter()
    traditions = Counter()
    scripture_books = Counter()
    styles = Counter()
    themes = []

    for sermon_refs in all_refs:
        if not sermon_refs:
            continue

        for ref in sermon_refs.get("references", []):
            ref_type = ref.get("type", "")
            name = ref.get("name", "")
            significance = ref.get("significance", "passing")

            # Weight central references more heavily
            weight = {"central": 3, "supporting": 2, "passing": 1}.get(significance, 1)

            if ref_type == "thinker":
                thinkers[name] += weight
            elif ref_type == "book":
                books[name] += weight
            elif ref_type == "tradition":
                traditions[name] += weight
            elif ref_type == "scripture":
                # Extract the book name from citations like "John 3:16"
                book_name = name.split()[0] if name else ""
                scripture_books[book_name] += weight
            elif ref_type == "implicit":
                thinkers[name] += weight  # Implicit refs are still thinker-adjacent

        if sermon_refs.get("rhetorical_style"):
            styles[sermon_refs["rhetorical_style"]] += 1
        if sermon_refs.get("primary_theme"):
            themes.append(sermon_refs["primary_theme"])

    return {
        "preacher": preacher,
        "total_sermons_analyzed": len(all_refs),
        "top_thinkers": thinkers.most_common(30),
        "top_books": books.most_common(20),
        "traditions": traditions.most_common(15),
        "scripture_emphasis": scripture_books.most_common(20),
        "rhetorical_styles": styles.most_common(10),
        "themes": themes,
    }


def build_influence_map(client, preacher: str, aggregated: dict) -> dict | None:
    """Build the full influence map and voice profile for a preacher."""
    prompt = INFLUENCE_MAP_PROMPT.format(
        preacher=preacher,
        role=PREACHER_ROLES.get(preacher, "Clergy at Saint John's Cathedral, Denver."),
        top_thinkers="\n".join(f"  - {name}: {count}" for name, count in aggregated["top_thinkers"][:20]),
        top_books="\n".join(f"  - {name}: {count}" for name, count in aggregated["top_books"][:15]),
        traditions="\n".join(f"  - {name}: {count}" for name, count in aggregated["traditions"][:10]),
        scripture_emphasis="\n".join(f"  - {name}: {count}" for name, count in aggregated["scripture_emphasis"][:15]),
        styles="\n".join(f"  - {style}: {count}" for style, count in aggregated["rhetorical_styles"]),
        themes="\n".join(f"  - {theme}" for theme in aggregated["themes"][:30]),
    )

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        return json.loads(response_text)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"  Warning: Could not parse influence map as JSON: {e}")
        # Save the raw text instead
        return {"raw_response": response.content[0].text}
    except Exception as e:
        print(f"  Error building influence map: {e}")
        return None


def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in environment or config.py")
        return

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Load catalog for metadata
    if not CATALOG_PATH.exists():
        print("No catalog found. Run 01_parse_rss.py first.")
        return

    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    print("=" * 60)
    print("INTELLECTUAL DNA MAPPING")
    print("=" * 60)
    print()

    voice_profiles = {}

    for preacher in PREACHERS:
        print(f"\n{'─' * 60}")
        print(f"Processing: {preacher}")
        print(f"{'─' * 60}")

        # Check if we already have a reference file for this preacher
        ref_file = REFERENCE_DIR / f"{preacher.replace(' ', '_')}_references.json"
        influence_file = REFERENCE_DIR / f"{preacher.replace(' ', '_')}_influence_map.json"

        # Get this preacher's sermons from catalog
        preacher_sermons = [
            ep for ep in catalog["episodes"]
            if ep.get("preacher") == preacher
        ]
        print(f"  Found {len(preacher_sermons)} sermons in catalog")

        if not preacher_sermons:
            print(f"  Skipping — no sermons found")
            continue

        # STEP 1: Extract references from each sermon
        if ref_file.exists():
            print(f"  Loading existing references from {ref_file.name}")
            with open(ref_file) as f:
                all_refs = json.load(f)
        else:
            print(f"  Extracting references from {len(preacher_sermons)} sermons...")
            all_refs = []

            # Load transcripts
            transcript_files = sorted(TRANSCRIPT_DIR.glob("*.json"))
            transcript_map = {}
            for tf in transcript_files:
                with open(tf) as f:
                    t = json.load(f)
                transcript_map[tf.stem] = t

            for i, sermon in enumerate(preacher_sermons, 1):
                # Find matching transcript
                date_prefix = sermon["date"]
                matching_transcripts = [
                    t for key, t in transcript_map.items()
                    if date_prefix in key and preacher in key
                ]

                if not matching_transcripts:
                    print(f"  [{i}/{len(preacher_sermons)}] No transcript for {sermon['date']} — skipping")
                    all_refs.append(None)
                    continue

                transcript = matching_transcripts[0]
                sermon_data = {
                    "text": transcript["full_text"],
                    "date": sermon["date"],
                    "title": sermon["title"],
                }

                print(f"  [{i}/{len(preacher_sermons)}] {sermon['date']} — {sermon['title'][:40]}")
                refs = extract_references(client, preacher, sermon_data)
                all_refs.append(refs)

                if refs:
                    n_refs = len(refs.get("references", []))
                    print(f"    Found {n_refs} references")

                time.sleep(1.5)  # Rate limiting

            # Save
            with open(ref_file, "w") as f:
                json.dump(all_refs, f, indent=2)
            print(f"  Saved references to {ref_file.name}")

        # STEP 2: Aggregate
        valid_refs = [r for r in all_refs if r is not None]
        print(f"  Aggregating from {len(valid_refs)} analyzed sermons...")
        aggregated = aggregate_references(valid_refs, preacher)

        # Print summary
        print(f"\n  TOP THINKERS CITED:")
        for name, count in aggregated["top_thinkers"][:10]:
            print(f"    {name}: {count}")

        print(f"\n  INTELLECTUAL TRADITIONS:")
        for name, count in aggregated["traditions"][:5]:
            print(f"    {name}: {count}")

        print(f"\n  SCRIPTURE EMPHASIS:")
        for name, count in aggregated["scripture_emphasis"][:5]:
            print(f"    {name}: {count}")

        # STEP 3: Build influence map
        if influence_file.exists():
            print(f"\n  Loading existing influence map from {influence_file.name}")
            with open(influence_file) as f:
                influence_map = json.load(f)
        else:
            print(f"\n  Building influence map and voice profile...")
            influence_map = build_influence_map(client, preacher, aggregated)

            if influence_map:
                with open(influence_file, "w") as f:
                    json.dump(influence_map, f, indent=2)
                print(f"  Saved influence map to {influence_file.name}")

        # Add to voice profiles
        if influence_map:
            voice_profiles[preacher] = {
                "aggregated_references": {
                    "top_thinkers": aggregated["top_thinkers"][:20],
                    "top_books": aggregated["top_books"][:15],
                    "traditions": aggregated["traditions"][:10],
                },
                "influence_map": influence_map,
            }

    # Save combined voice profiles
    profiles_path = REFERENCE_DIR / "voice_profiles.json"
    with open(profiles_path, "w") as f:
        json.dump(voice_profiles, f, indent=2)

    print()
    print("=" * 60)
    print("INTELLECTUAL DNA MAPPING COMPLETE")
    print("=" * 60)
    print(f"Reference files: {REFERENCE_DIR}")
    print(f"Voice profiles: {profiles_path}")
    print(f"\nNext step: python 08_generate_sermon.py")


if __name__ == "__main__":
    main()
