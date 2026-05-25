# Farm Stealth Game
## Project Brief for Claude Code

---

## What This Is

A top-down 2D stealth/adventure game built in Python + Pygame, targeting children aged 3–6.
The player controls a small grey tractor whose secret must never be discovered — he is alive
and can move on his own. Each round, the tractor must complete 3 farm objectives while hiding
from two bumbling scrap dealers, then return to Gramps at the barn to win.

This project is being built for two reasons:
1. As a gift for a 5-year-old boy who loves tractors and farm adventures
2. As a portfolio project on GitHub demonstrating real software engineering skills

Repo: https://github.com/ryan-nanna/farm-stealth-game

---

## Tech Stack

- **Language:** Python 3.12
- **Run Python with:** py -3.12 (not python — machine has multiple Python versions)
- **Library:** Pygame 2.6+
- **Platform:** Windows (primary dev + play environment)
- **Resolution:** 1280 × 720 fixed (no scrolling, no camera)
- **Controller:** Generic USB NES-style controller (any HID joystick)
- **Art style:** Illustrated SVG-inspired smooth style (NOT pixel art) — warm greys, bright sky
  blue, saturated greens pulled from the toy box art reference
- **Sound:** Placeholder / silent for MVP. Audio system is architected but assets are stubbed.

---

## Project Structure

```
farm-stealth-game/
├── README.md
├── requirements.txt
├── CLAUDE.md                  ← this file
├── main.py                    ← entry point, game loop
│
├── game/
│   ├── __init__.py
│   ├── settings.py            ← all constants (colours, speeds, sizes)
│   ├── game.py                ← Game class, state machine, round management
│   ├── level.py               ← farm map, tile layout, hiding spots, objective zones
│   │
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── tractor.py         ← player: movement, hiding state, noise level
│   │   ├── dealer.py          ← enemy: patrol path, vision cone, state machine
│   │   ├── gramps.py          ← NPC: safe zone anchor, bell trigger, win condition
│   │   ├── scarecrow.py       ← NPC: fixed position, intel whisper mechanic
│   │   └── farmer.py          ← NPC: cow objective zone (top-left)
│   │
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── input.py           ← InputManager: keyboard + USB NES controller unified
│   │   ├── detection.py       ← vision cone logic, noise radius logic
│   │   ├── collision.py       ← hiding spot overlap, wall collision
│   │   ├── objectives.py      ← ObjectiveManager, TimingBar mechanic
│   │   └── state_machine.py   ← reusable StateMachine class used by enemies
│   │
│   └── ui/
│       ├── __init__.py
│       ├── hud.py             ← objective tracker, noise ring display
│       └── screens.py         ← title, win, caught, pause screens
│
└── assets/
    ├── sprites/               ← empty for MVP (drawn in code as shapes)
    └── tiles/                 ← empty for MVP (drawn in code as shapes)
```

---

## Controls

### USB NES Controller (primary)
| Button   | Action                                      |
|----------|---------------------------------------------|
| D-Pad    | Move tractor (4 directions)                 |
| A        | Interact / hold to complete objective        |
| B        | Brake + silence engine (stealth move)        |
| Start    | Pause game                                  |
| Select   | Toggle scarecrow intel mini-map overlay      |

### Keyboard (developer fallback — always works simultaneously)
| Key          | Action          |
|--------------|-----------------|
| Arrow keys   | Move            |
| Space        | A (interact)    |
| Left Shift   | B (silence)     |
| Enter        | Start (pause)   |
| Tab          | Select          |
| Escape       | Quit            |

---

## Game Loop — One Round

```
ROUND START
  → Tractor spawns at barn (top-right)
  → 3 objectives assigned in random order
  → 3-second peaceful grace period

DEALERS ARRIVE (bottom of map)
  → Dealer 1 enters bottom-left, patrols left side
  → Dealer 2 enters bottom-right, patrols right side
  → Music would escalate here (stubbed for MVP)

PLAYER PHASE
  → Tractor completes objectives in any order
  → Each objective: drive to zone, hold A, pass timing bar
  → Hiding: drive into cover zone → tractor visually "tucks in"
  → Noise: moving = noise ring, B button = silence engine

OBJECTIVE COMPLETE (all 3 done)
  → HUD signals "Return to Gramps!"
  → Tractor must reach barn rect

WIN
  → Celebratory screen
  → Next round (dealers faster, longer vision)

CAUGHT
  → Dealer vision cone covers tractor for 1.5s
  → 2-second escape window
  → Funny caught screen (not scary)
```

---

## The 3 Objectives (per round, randomised order)

### 1. Help feed the pigs 🐷
- **Location:** Pig pen — bottom-right corner
- **Mechanic:** Drive to pen entrance. Hold A while timing bar fills.
- **Risk:** HIGH — near dealer entry road

### 2. Help with the cows 🐄
- **Location:** Cow pasture — top-left (near oak tree)
- **Mechanic:** Drive to gate. Press A at peak of timing bar.
- **Risk:** MEDIUM — near Dealer 1 patrol, oak tree nearby for cover

### 3. Find the scarecrow 🤖
- **Location:** Mid-map, fixed, near stone wall
- **Mechanic:** Drive to scarecrow. Hold A for 2 seconds (whisper).
- **Reward:** 10-second mini-map overlay showing dealer positions
- **Risk:** LOW-MEDIUM — wall provides partial cover

---

## Farm Map Layout

```
TOP-RIGHT:  Red Barn / Gramps ← WIN CONDITION / SAFE ZONE
TOP-LEFT:   Farmer + Cow Pasture ← Objective zone
TOP-CENTRE: Apple Tree ← Full cover hiding spot

MID-LEFT:   Oak Tree ← Full cover hiding spot
MID-CENTRE: Scarecrow (fixed) ← Objective zone + Partial cover
MID-MAP:    Stone Wall (full width) ← Partial cover corridor

BOT-LEFT:   Chicken Coop ← Full cover
BOT-CENTRE: Old Shed ← Full cover  |  Well/Trough ← Partial
BOT-RIGHT:  Pig Pen ← Objective zone + Full cover

BOTTOM EDGE: Farm entrance — dealers enter here each round
```

### Cover Quality
- **FULL cover:** Trees, haystacks, chicken coop, old shed, pig pen
  → Tractor invisible to vision cone, noise still active
- **PARTIAL cover:** Stone wall, well/trough
  → Vision cone range reduced 60%, tractor still detectable up close

---

## Characters

| Character    | Role         | Notes                                              |
|--------------|--------------|----------------------------------------------------|
| Tractor      | Player       | Small grey tractor. Enormous expressive headlights.|
| Scarecrow    | Friend NPC   | Metal scarecrow. Fixed position. Intel source.     |
| Farmhand     | Objective NPC| Pig pen. Warm and cheerful. Objective 1.           |
| Farmer       | Objective NPC| Cow pasture. Objective 2.                          |
| Gramps       | Safe zone    | Red barn. Win condition. Rings bell.               |
| Dealer 1     | Villain      | Tall, lanky. Wide vision cone. Slow patrol.        |
| Dealer 2     | Villain      | Short, round. Fast, erratic. Checks corners.       |

---

## Enemy AI States

```
PATROL      → follows waypoint path at base speed
SUSPICIOUS  → heard a noise, turns toward source, slows
ALERT       → spotted tractor, vision cone locked on for 1.5s
CHASE       → 2-second escape window, rushing toward tractor
SEARCHING   → lost tractor, checks last known position
LEAVING     → round won, walking back to entrance
```

---

## Noise System

Tractor engine generates noise proportional to speed.
Visualised as a pulsing circle around the tractor:

| State              | Ring colour | Dealer response               |
|--------------------|-------------|-------------------------------|
| Hidden + still     | None        | Ignored                       |
| Still, not hidden  | Green pulse | No response                   |
| Moving slowly      | Amber pulse | Dealers in range turn toward  |
| Moving fast        | Red pulse   | Dealers investigate immediately|
| Pig pen (objective)| Orange spike| Brief noise burst on completion|

B button (or Left Shift): cuts engine to zero noise instantly.

---

## MVP Scope (No Sound)

Build sessions in this order:

- **Session 1:** Tractor moves on screen. Arrow keys + controller input. Commit.
- **Session 2:** Farm map renders. Hiding spots as coloured rects. Stone wall collision.
- **Session 3:** Cover system. Tractor sprite changes when inside cover zone.
- **Session 4:** One dealer. Patrol path. Vision cone drawn on screen.
- **Session 5:** Detection logic. Noise radius. State machine. Caught screen.
- **Session 6:** All 3 objectives. TimingBar mechanic. ObjectiveManager.
- **Session 7:** Gramps + win condition. Round escalation. Full game loop.
- **Session 8:** Scarecrow intel mechanic. HUD polish. README + GitHub cleanup.

Sound integration is a separate phase after MVP gameplay is solid.

---

## Code Style Preferences

- Classes for all game entities (not functions)
- Type hints on all method signatures
- Single responsibility — each file does one thing
- settings.py for ALL magic numbers (no hardcoded values in entity files)
- Input system returns abstract actions (UP, DOWN, A_PRESS) not raw keys
- Comments explain WHY not what
- Run with: py -3.12 main.py

---

## What NOT to Build Yet

- Sound (stubbed only — MusicSystem class exists but does nothing)
- Actual sprite art (shapes only for MVP)
- Save system
- Multiple levels / maps
- Menu system beyond a basic title screen

