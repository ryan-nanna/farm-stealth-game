# Farm Stealth

A top-down 2D stealth/adventure game built in Python + Pygame.

Guide a small grey tractor (Fergie) through a farm to complete three secret chores while hiding from two bumbling scrap dealers. Return to Gramps at the barn to win the round!

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
| 🤖 Find Clunky the scarecrow | Mid-map, near stone wall | Drive up, **hold A** for 2 seconds to whisper — earns 10 s of intel |

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

## The Cast

### Fergie (You)
A small grey Ferguson TE20 tractor with enormous expressive headlights. His secret: he's alive and can move on his own. His headlights change expression based on what's happening — focused during objectives, nervous when hiding, shocked when caught. The tractor faces the direction you're driving.

### Hubert
Long dark hair, bucket hat, denim vest. Slow and methodical — wanders the whole farm on a wide semi-random circuit. Wide vision cone. Heard noise draws him toward the general area before he locks on.

### Hieronymus
One green sock, one red sock. Fast and erratic — darts between corners, doubles back unexpectedly. Narrow vision cone, but very noise-sensitive: he'll react to any movement sound within 200 px even if you're outside his normal detection range. **Silent mode matters most near Hieronymus.**

### The Scrap Truck
A battered pink military-surplus flatbed truck that patrols a fixed route near the farm entrance. Present every round. No vision cone — just size and momentum. Pattern changes each round so you can't memorise it.

### Clunky
A cheerful metal scarecrow in a black top hat and jacket, with a tin-bucket head and a painted-on smiley face. Approach and whisper for 2 seconds to unlock the intel mini-map showing where the dealers are.

### Gramps
Waits in the barn yard. Ring the bell when all three missions are done to win the round.

---

## Mechanics

### Cover

| Zone | Effect |
|---|---|
| Trees, hay bales, chicken coop, old shed, pig pen, silo | **Full cover** — invisible to vision cones. Noise still active. |
| Stone wall, well/trough, sheep pen, pond | **Partial cover** — vision range cut 60%. Detectable up close. |

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

## The Farm

The world is 2560×1440 — twice the viewport size — with a camera that follows Fergie. Locations are discovered as you explore, which keeps the game surprising even on repeat plays.

```
TOP-RIGHT   Red barn + Gramps — win condition / safe zone
TOP-LEFT    Farmer + cow pasture — objective zone
TOP-CENTRE  Orchard (2 trees) + apple tree — full cover

MID-LEFT    Oak tree + sheep paddock — cover
MID-CENTRE  Clunky the scarecrow — objective + intel
MID-MAP     Stone wall (3 segments, 2 gaps) — partial cover corridor
            Pond — partial cover

BOT-LEFT    Chicken coop — full cover
BOT-CENTRE  Old shed + well/trough + hay bales — cover
BOT-RIGHT   Pig pen — objective + full cover

BOTTOM      Farm entrance — dealers and scrap truck enter here
NEAR BARN   Silo — full cover (close to start)
```

---

## Project Structure

```
farm-stealth-game/
├── main.py                        # Game loop, state machine, round management
├── game/
│   ├── settings.py                # All constants — single source of truth
│   ├── level.py                   # Static farm map, cover zones, procedural art
│   ├── entities/
│   │   ├── tractor.py             # Fergie: movement, cover, noise, eye expressions
│   │   ├── dealer.py              # Hubert: lurk/hunt AI, photo sprite, vision cone
│   │   ├── hieronymus.py          # Hieronymus: noise-sensitive second dealer
│   │   ├── scrap_truck.py         # Scrap truck: patrol driver, round-based routes
│   │   └── gramps.py              # Win-condition NPC at the barn
│   ├── systems/
│   │   ├── camera.py              # Scrolling camera — follows tractor, clamps to world
│   │   ├── input.py               # Unified keyboard + USB controller input
│   │   ├── detection.py           # Vision cone + noise detection (pure functions)
│   │   ├── collision.py           # Cover overlap detection
│   │   ├── objectives.py          # ObjectiveManager, TimingBar, ParticleSystem
│   │   └── state_machine.py       # Generic StateMachine[S] used by all AI
│   └── ui/
│       ├── hud.py                 # Checklist, noise dot, intel mini-map
│       └── screens.py             # Title, win, and caught overlays
└── assets/
    └── sprites/                   # PNG sprites (photo references for dealers)
        ├── hubert.png
        └── hieronymus.png
```

---

## Tech Stack

- **Python 3.12** · **Pygame 2.6**
- **Scrolling camera** — 2560×1440 world with 1280×720 viewport; all entities draw to a world surface, camera blits the viewport to screen
- **Procedural art** — tractor, truck, scarecrow, barn, animals, and all farm elements drawn entirely in code using Pygame primitives
- Generic `StateMachine[S]` keeps all enemy AI states clean and testable
- Unified input system: keyboard and USB NES controller work simultaneously
- All gameplay constants in `settings.py` — no magic numbers anywhere else

---

## Build History

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
| 9 | Hieronymus, noise overhaul, eye expressions, title screen, particles, scrap truck |
| 10 | Art pass — scrolling camera, 2× world, farm scenery, animals, barn redesign |
| 11 | Tractor 3/4 view, directional sprites, Clunky scarecrow, scrap truck art + patrol routes |

---

## Roadmap

- [ ] Sound design — engine hum, Gramps bell, caught sting
- [ ] Wall/cover hitbox tuning (tractor size vs stone wall)
- [ ] Title screen art
- [ ] Hubert & Hieronymus visual polish
