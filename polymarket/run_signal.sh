#!/bin/bash
# Polymarket daily weather signal runner
cd /Users/xobie/.openclaw/workspace/polymarket
DATE=$(date +%Y-%m-%d)
OUTPUT="/Users/xobie/.openclaw/workspace/polymarket/signals/signal-${DATE}.md"
mkdir -p /Users/xobie/.openclaw/workspace/polymarket/signals
python3 weather_signal.py > "$OUTPUT" 2>&1
# Push to GitHub
cd /Users/xobie/.openclaw/workspace
git add polymarket/
git commit -m "Polymarket signal: ${DATE}" 2>/dev/null || true
git push 2>/dev/null || true
echo "Signal saved: $OUTPUT"
