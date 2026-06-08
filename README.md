# Farm Stealth

A top-down 2D stealth/adventure game built in Python + Pygame.

Guide a small grey tractor through a farm to complete three secret chores while hiding from two bumbling scrap dealers. Return to Gramps at the barn to win the round!

Made as a gift for a 5-year-old who loves tractors — and built as a portfolio project demonstrating incremental delivery, clean architecture, and Python game development.

---

## Quick Start

```bash
pip install pygame
py -3.12 main.py
```

**Requires:** Python 3.12+, Pygame 2.6+

---

## How to Play

Complete **three farm missions** in any order, then drive back to the red barn and find Gramps.

| Mission | Location | How |
|---|---|---|
| 🐷 Feed the pigs | Pig pen — bottom-right | Drive in, **hold A** until the bar fills |
| 🐄 Help with the cows | Cow pasture — top-left | Drive in, **press A** when bar hits the yellow zone |
| 🤖 Find the scarecrow | Mid-map, near stone wall | Drive up, **hold A** for 2 seconds to whisper — earns 10 s of intel |

Two scrap dealers are snooping around the farm. If a dealer's vision cone stays on you long enough, they'll chase you down. Stay in cover, use silent mode when passing close, and complete the scarecrow mission early to track their positions on the mini-map.

After each round the dealers get faster and see further — how many rounds can you survive?

---

## Controls

### USB NES-Style Controller (primary)

| Input | Action |
|---|---|
| D-Pad | Move |
| **A** | Interact / hold to complete objective |
| **B** | Silent mode — cuts engine noise, moves slower |
| Start | Pause |
| Select | Toggle scarecrow intel overlay |

### Keyboard (works simultaneously with controller)

| Key | Action |
|---|---|
| Arrow keys | Move |
| **Space** | Interact (A) |
| **Left Shift** | Silent mode (B) |
| **Tab** | Intel overlay (Select) |
| Escape | Quit |

---

## The Dealers

### Hubert
Long dark hair, bucket hat, denim vest. Slow and methodical — wanders the whole farm on a wide semi-random circuit. Wide vision cone. Heard noise draws him toward the general area before he locks on.

### Hieronymus
One green sock, one red sock. Fast and erratic — darts between corners, doubles back unexpectedly. Narrow vision cone, but very noise-sensitive: he'll react to any movement sound within 200 px even if you're outside his normal detection range. **Silent mode matters most near Hieronymus.**

### Scrap Truck *(round 3+)*
A battered truck that drives a slow clockwise loop around the farm perimeter. No vision cone — just inevitable presence blocking the outer edge.

---

## Mechanics

### Cover

| Zone | Effect |
|---|---|
| Trees, chicken coop, old shed, pig pen | **Full cover** — invisible to vision cones. Noise still active. |
| Stone wall, well/trough | **Partial cover** — vision range cut 60%. Detectable up close. |

### Noise

| Ring colour | State | Dealer response |
|---|---|---|
| None | Hidden + still | Ignored |
| 🟢 Green | Standing still, exposed | No reaction |
| 🟡 Amber | Moving in **silent mode** | Dealers in range snap to curious |
| 🔴 Red | Moving at normal speed | Dealers investigate immediately |
| 🟠 Orange burst | Objective just completed | Real tense moment — be ready to hide |

### Enemy AI States

```
LURK      → slow drift across farm, semi-random waypoints
CURIOUS   → heard noise, moving toward general area (not locked on)
SEARCHING → checking last known position
ALERT     → visual lock — cone held on tractor for 1.5 s
CHASE     → rushing toward tractor (2 s window to escape)
LEAVING   → round won, walking off the bottom edge
```

---

## Project Structure

```
farm-stealth-game/
├── main.py                        # Game loop, state machine, round management
├── game/
│   ├── settings.py                # All constants — single source of truth
│   ├── level.py                   # Static farm map, cover zones, objective rects
│   ├── entities/
│   │   ├── tractor.py             # Player: movement, cover, noise, eye expressions
│   │   ├── dealer.py              # Hubert: lurk/hunt AI, photo sprite, vision cone
│   │   ├── hieronymus.py          # Hieronymus: noise-sensitive second dealer
│   │   ├── scrap_truck.py         # Scrap truck: perimeter driver, hard mode
│   │   └── gramps.py              # Win-condition NPC at the barn
│   ├── systems/
│   │   ├── input.py               # Unified keyboard + USB controller input
│   │   ├── detection.py           # Vision cone + noise detection (pure functions)
│   │   ├── collision.py           # Cover overlap detection
│   │   ├── objectives.py          # ObjectiveManager, TimingBar, ParticleSystem
│   │   └── state_machine.py       # Generic StateMachine[S] used by all AI
│   └── ui/
│       ├── hud.py                 # Checklist, noise dot, intel mini-map
│       └── screens.py             # Title, win, and caught overlays
└── assets/
    └── sprites/                   # PNG sprites (transparent background, top-down)
```

---

## Tech Stack

- **Python 3.12** · **Pygame 2.6**
- Generic `StateMachine[S]` keeps all enemy AI states clean and testable
- Unified input system: keyboard and USB NES controller work simultaneously
- Sprite system: `pygame.image.load()` with graceful shape fallback if PNG not present
- All gameplay constants in `settings.py` — no magic numbers anywhere else

---

## Build Sessions

| Session | What shipped |
|---|---|
| 1 | Tractor moves — keyboard + controller input |
| 2 | Farm map renders — cover zones, stone wall collision |
| 3 | Cover system — tractor hides in cover zones |
| 4 | One dealer — patrol path, vision cone |
| 5 | Detection — noise radius, state machine, caught screen |
| 6 | All 3 objectives — TimingBar mechanic, ObjectiveManager |
| 7 | Gramps + win condition — round escalation, full game loop |
| 8 | Scarecrow intel — mini-map overlay, HUD polish |
| 9 | Phase 2 — Hieronymus, noise overhaul, eye expressions, title screen, sparkle particles, scrap truck |

---

## Roadmap

- [ ] Sprite art for Hieronymus, tractor, farm elements (issues #14–16)
- [ ] Sound design — engine hum, Gramps bell, caught sting (issue #24)
- [ ] Scrap truck sprite (issue #15)
