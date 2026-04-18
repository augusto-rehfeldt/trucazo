# Trucazo — A Truco Roguelike

Trucazo is a terminal roguelike deckbuilder inspired by Argentine Truco and Balatro. You play through escalating towns and tables, manage money, buy talismans/powers/editions, unlock permanent upgrades, and push for the highest run you can survive.

## Quick Start

This project uses only the Python standard library. No external dependencies are required.

From the repository root:

```bash
python3 __main__.py
```

If you prefer module execution, run it from the parent directory of the repo:

```bash
cd ..
python3 -m trucazo
```

## Current Game Loop

- 8 towns per standard run
- 3 tables per town:
  - Entry Table
  - Back Table
  - Patrón's Table (boss blind)
- Beat each table by reaching its score target before you run out of hands
- Visit the shop between tables to buy:
  - Talismans (passive augments)
  - Powers (attached to cards)
  - Editions (card modifiers)
  - Truquera cards (level up Truco / Envido / Flor / Racha)
- Earn Prestige at the end of a run and spend it at El Fogón for permanent upgrades
- Complete Challenges to unlock more content, including Endless Mode

## Controls

### Title screen

- `1` New Run
- `2` Collection
- `3` How to Play
- `4` El Fogón
- `5` Challenges
- `6` Settings
- `7` Quit
- `C` Continue, if an autosave exists

### During a hand

- `1` / `2` / `3` play a card
- `e` call Envido
- `f` call Flor
- `t` call Truco
- `i` show info / deck state
- `q` quit

## Settings

The game includes:

- Bilingual UI: Español / English
- Difficulty modes:
  - Easy
  - Normal
  - Hard
- Persistent meta-progression and collection tracking

## Repository Layout

```text
trucazo/
├── __main__.py      # Entry point for `python3 __main__.py`
├── __init__.py      # Package marker
├── cards.py         # Spanish deck, card models, Truco hierarchy, scoring helpers
├── hands.py         # AI opponent, battle resolution, hand scoring
├── data.py          # Talismans, bosses, shop pools, Truquera cards
├── display.py       # Terminal rendering, menus, layout, colors
├── game.py          # Main game loop, menus, shop, run flow
├── collection.py    # Persistent collection tracking
├── meta.py          # Prestige, El Fogón upgrades, challenges
├── lang.py          # English / Spanish strings and help text
├── difficulty.py    # Difficulty tiers and modifiers
└── LICENSE
```

## Save Data

The game writes a few files next to the code when you play:

- `autosave.pkl` — mid-run save file
- `.meta.json` — permanent meta-progression
- `.collection.json` — collection / discovery tracking

These generated files are ignored by git.

## Notes

- Runs are capped at 8 towns by default.
- If you unlock Endless Mode, the run can continue beyond town 8.
- The project is designed to be launched from the terminal, not via a GUI.
