"""
PHASE 6: TEMPORAL CONTEXT ENRICHMENT
======================================
For each sermon, gather what was happening in the world that week.
This helps the bot understand WHY a preacher said what they said.

WHAT IT DOES:
1. For each sermon date, queries multiple context layers:
   - Episcopal/Anglican church news
   - Denver & Colorado local news
   - National US news
   - International news
   - Lectionary readings for that Sunday
2. Uses Claude to summarize the key events into a concise context block
3. Saves enriched context alongside each transcript

WHY THIS MATTERS:
A sermon about "fear" preached March 15, 2020 is about COVID.
A sermon about "justice" preached June 7, 2020 is about George Floyd.
A sermon about "community" preached March 2020 is about isolation.
Without this context, the bot loses half the meaning.

APPROACH:
We use the Anthropic API with web search to find news for each date.
This is more reliable than trying to scrape old news archives directly.

COST NOTE:
This script makes Claude API calls for each sermon. With ~400 sermons,
expect ~$2-5 in API costs depending on response length.

RUN: python 06_enrich_context.py
"""

import json
import time
import anthropic
from pathlib import Path
from datetime import datetime, timedelta
from config import (
    TRANSCRIPT_DIR, DATA_DIR, CATALOG_PATH,
    ANTHROPIC_API_KEY, CLAUDE_MODEL
)

CONTEXT_DIR = DATA_DIR / "context"
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)

# Lectionary calendar helps identify the church season and readings
# We'll ask Claude to figure this out from the sermon title + date
CONTEXT_PROMPT = """I need you to build a temporal context snapshot for a sermon preached at Saint John's Episcopal Cathedral in Denver, Colorado.

Sermon date: {date}
Sermon title: "{title}"
Preacher: {preacher}

Please provide a concise context block covering what was happening around this date across these layers. Be specific with real events, not generic summaries. If you're not sure about something for this exact date, note the closest relevant events.

## 1. LITURGICAL CONTEXT
- What Sunday/feast day is this in the church calendar?
- What are the likely lectionary readings (Book of Common Prayer / Revised Common Lectionary)?
- What season of the church year (Advent, Lent, Ordinary Time, etc.)?

## 2. EPISCOPAL / ANGLICAN CHURCH NEWS
- Any significant denominational news around this time?
- Diocesan events in Colorado?
- General Convention actions, bishop elections, major church controversies?

## 3. DENVER & COLORADO NEWS
- Major local news events in the week before this sermon
- Weather events, politics, community issues
- Anything affecting the Capitol Hill neighborhood or downtown Denver

## 4. NATIONAL NEWS (US)
- Top 3-5 national news stories from the week before this sermon
- Political developments, social movements, major events

## 5. INTERNATIONAL NEWS
- Top 2-3 international stories from the week before this sermon
- Wars, disasters, diplomatic developments

## 6. CULTURAL MOMENT
- What was the general mood/zeitgeist at this time?
- Any major cultural events (sports, entertainment, etc.) that a Denver congregation would be aware of?

Keep each section to 2-4 sentences. Be factual and specific. Format as clean text, not markdown."""


def load_sermons_to_enrich() -> list[dict]:
    """Load catalog entries that need context enrichment."""
    if not CATALOG_PATH.exists():
        print("No catalog found. Run 01_parse_rss.py first.")
        return []

    with open(CATALOG_PATH) as f:
        catalog = json.load(f)

    # Filter to sermons with identified preachers
    sermons = [
        ep for ep in catalog["episodes"]
        if ep.get("preacher") is not None
    ]

    # Check which ones already have context
    existing = set(f.stem for f in CONTEXT_DIR.glob("*.json"))
    to_process = []
    for s in sermons:
        context_key = f"{s['date']}_{s['preacher'].replace(' ', '_')}"
        if context_key not in existing:
            to_process.append(s)

    return to_process


def enrich_sermon(client: anthropic.Anthropic, sermon: dict) -> dict:
    """Generate temporal context for a single sermon."""
    prompt = CONTEXT_PROMPT.format(
        date=sermon["date"],
        title=sermon["title"],
        preacher=sermon["preacher"],
    )

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    context_text = response.content[0].text

    return {
        "date": sermon["date"],
        "title": sermon["title"],
        "preacher": sermon["preacher"],
        "context": context_text,
        "generated_at": datetime.now().isoformat(),
        "model": CLAUDE_MODEL,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }


def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY in environment or config.py")
        return

    sermons = load_sermons_to_enrich()
    if not sermons:
        print("All sermons already have context (or no sermons found).")
        print(f"Context files: {CONTEXT_DIR}")
        return

    print(f"Sermons needing context: {len(sermons)}")
    print(f"Estimated API cost: ~${len(sermons) * 0.01:.2f}")
    print()

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    total_input = 0
    total_output = 0

    for i, sermon in enumerate(sermons, 1):
        print(f"[{i}/{len(sermons)}] {sermon['date']} — {sermon['preacher']} — {sermon['title'][:50]}")

        try:
            result = enrich_sermon(client, sermon)

            # Save
            context_key = f"{sermon['date']}_{sermon['preacher'].replace(' ', '_')}"
            output_path = CONTEXT_DIR / f"{context_key}.json"
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)

            total_input += result["input_tokens"]
            total_output += result["output_tokens"]

            # Rate limit: ~50 requests/minute for most tiers
            time.sleep(1.5)

        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(3)  # Back off on errors

    print()
    print("=" * 60)
    print(f"Context enrichment complete!")
    print(f"Files saved to: {CONTEXT_DIR}")
    print(f"Total tokens: {total_input:,} input + {total_output:,} output")
    print(f"Estimated cost: ~${(total_input * 0.003 + total_output * 0.015) / 1000:.2f}")


if __name__ == "__main__":
    main()
