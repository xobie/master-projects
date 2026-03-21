# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### Python

- Use `python3.13` (not 3.14) for skill scripts — 3.14 has argparse compatibility issues
- venv for polymarket: `/Users/xobie/.openclaw/workspace/.venv313`
- Run polymarket: `/Users/xobie/.openclaw/workspace/.venv313/bin/python3 /opt/homebrew/lib/node_modules/openclaw/skills/polymarket-trade/scripts/polymarket.py`

---

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
