# Trucazo — A Truco Roguelike

A terminal-based roguelike deckbuilder inspired by Argentine Truco and Balatro. Play rounds of Truco against AI opponents, collect talismans (augments), defeat bosses, and build your truquera deck across escalating blinds.

## 🚀 Quick Start

No external dependencies are required! Just clone and play:

```bash
git clone https://github.com/yourusername/trucazo.git
cd trucazo
python3 -m trucazo
```

## 📖 Game Documentation

### 🎯 The Core Loop

Travel through 8 towns (Antes). In each town, you must survive 3 tables (Blinds):

1. **Entry Table (Small Blind)**
2. **Back Table (Big Blind)**
3. **Patrón's Table (Boss Blind)** - Features special modifiers that change the rules!

Defeat tables by reaching the Score Target before you run out of hands.

### 🃏 Truco Mechanics (Real Argentine Rules)

* **The Deck:** 40-card Spanish Baraja (Swords ⚔, Clubs 🪵, Cups 🏆, Gold 🪙).
* **Card Hierarchy:** 1⚔ > 1🪵 > 7⚔ > 7🪙 > 3 > 2 > 1🏆 1🪙 > 12 > 11 > 10 > 7🏆 7🪵 > 6 > 5 > 4.
* **Envido:** A pre-round bet based on your two best cards of the same suit. (Values: 1-7 = face value; 10, 11, 12 = 0). Score = 20 + sum of cards. Max score is 33.
* **Flor:** If you are dealt 3 cards of the same suit, you have a Flor! This overrides Envido for massive points.
* **Truco:** During the hand, call Truco to multiply the round's score (x2). The AI can fold, accept, or raise (Retruco x3, Vale Cuatro x4).
* **Cascade (Racha):** Win consecutive hands to build a score multiplier (up to x2.5!).

### 🛒 Roguelike Elements (The Shop)

Between tables, visit the Shop (El Kiosco) to spend your winnings and upgrade your run:

* **Talismanes (Augments):** Passive buffs (max 3 slots). Examples: Mate Amargo (extra income), Poncho (Envido shield).
* **Ediciones:** Visual and mechanical upgrades applied permanently to cards (e.g., Dorada gives money when played, Holográfica multiplies score x1.5).
* **Poderes:** Magical effects triggered when a card is played (e.g., Fuego gives +20 flat points, Hielo lowers the opponent's card rank).
* **Truqueras:** Cards that permanently level up the base score of your Truco, Envido, or Flor hands.

### 🔥 Meta-Progression (El Fogón)

Even when you lose, you earn Prestige. Spend Prestige at The Campfire (El Fogón) to unlock permanent upgrades across all future runs, such as starting money, extra hands, or shop discounts. Complete Challenges to unlock new items, bosses, and the Endless Mode!

## ⚙️ Project Structure

```text
trucazo/
├── __main__.py      # Entry point
├── game.py          # Main game engine, run loop, shops, menus
├── cards.py         # Spanish baraja deck, card classes, Truco ranking
├── hands.py         # Battle resolution, AI logic, scoring
├── data.py          # Talismans, bosses, shop items, truquera cards
├── display.py       # Terminal rendering, colors, layout
├── collection.py    # Persistent item collection tracking
├── meta.py          # Meta-progression (prestige, challenges, unlocks)
└── difficulty.py    # Difficulty configurations
```