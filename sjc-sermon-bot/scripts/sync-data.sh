#!/bin/bash
# Sync data from the Python pipeline output to the Next.js data directory
PIPELINE_DIR="../sermon_bot/data"
WEB_DATA_DIR="./data"

echo "Syncing pipeline data to web app..."

# Create data directory if needed
mkdir -p "$WEB_DATA_DIR"

# Copy catalog
if [ -f "$PIPELINE_DIR/catalog.json" ]; then
  cp "$PIPELINE_DIR/catalog.json" "$WEB_DATA_DIR/"
  echo "  Copied catalog.json"
fi

# Copy transcripts
if [ -d "$PIPELINE_DIR/transcripts" ]; then
  mkdir -p "$WEB_DATA_DIR/transcripts"
  cp "$PIPELINE_DIR/transcripts/"*.json "$WEB_DATA_DIR/transcripts/" 2>/dev/null
  echo "  Copied transcripts/"
fi

# Copy context
if [ -d "$PIPELINE_DIR/context" ]; then
  mkdir -p "$WEB_DATA_DIR/context"
  cp "$PIPELINE_DIR/context/"*.json "$WEB_DATA_DIR/context/" 2>/dev/null
  echo "  Copied context/"
fi

# Copy references (voice profiles, influence maps)
if [ -d "$PIPELINE_DIR/references" ]; then
  mkdir -p "$WEB_DATA_DIR/references"
  cp "$PIPELINE_DIR/references/"*.json "$WEB_DATA_DIR/references/" 2>/dev/null
  echo "  Copied references/"
fi

echo "Done! Data synced to $WEB_DATA_DIR"
