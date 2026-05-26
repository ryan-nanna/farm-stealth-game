# Farm Stealth Game

A top-down 2D stealth/adventure game built in Python + Pygame.

Guide a small grey tractor through a farm to complete three secret missions while hiding from bumbling scrap dealers. Return to Gramps at the barn to win the round!

Designed as a gift for a 5-year-old who loves tractors, and built as a portfolio project demonstrating Python game development with clean architecture and incremental delivery.

---

## Quick Start

```bash
pip install pygame
py -3.12 main.py
```

Requires Python 3.12+ and Pygame 2.6+.

---

## Controls

### USB NES-Style Controller (primary)

| Input    | Action                                  |
|----------|-----------------------------------------|
| D-Pad    | Move tractor                            |
| A        | Interact / hold to complete objective   |
| B        | Silent mode — slower and quieter        |
| Start    | Pause                                   |

### Keyboard (always active alongside controller)

| Key         | Action          |
|-------------|-----------------|
| Arrow keys  | Move            |
| Space       | Interact (A)    |
| Left Shift  | Silent mode (B) |
| Escape      | Quit            |

---

## How to Play

Each round the tractor must complete three farm missions, then return to Gramps at the red barn:

| Mission            | Location                 | How                                                    |
|--------------------|--------------------------|--------------------------------------------------------|
| Feed the pigs      | Pig pen (bottom-right)   | Drive in, hold A until the bar fills                   |
| Help with the cows | Cow pasture (top-left)   | Drive in, press A when the bar hits the yellow zone    |
| Find the scarecrow | Mid-map near stone wall  | Drive up, hold A for 2 seconds — earns 10 s of intel   |

Two scrap dealers patrol the farm. If a dealer's vision cone covers the tractor long enough, it's game over. Stay in cover, use silent mode near dealers, and use the scarecrow intel to track their positions.

After each win the dealers get faster and their vision reaches further — how many rounds can you complete?

---

## Mechanics

### Cover System

| Zone                               | Effect                                    |
|------------------------------------|-------------------------------------------|
| Trees, chicken coop, shed, pig pen | Full cover — invisible to vision cones    |
| Stone wall, well                   | Partial cover — vision range reduced 60%  |

### Noise Rings

| Colour | State               | Dealer response                    |
|--------|---------------------|------------------------------------|
| Green  | Standing still      | No reaction                        |
| Amber  | Moving (silent B)   | Dealers in range turn toward you   |
| Red    | Moving normally     | Dealers investigate immediately    |

Hold B / Left Shift to cut the engine and move silently (amber ring, slower speed).

### Intel Overlay

Completing the scarecrow mission reveals a mini-map for 10 seconds showing dealer positions in real time.

---

## Project Structure

```
farm-stealth-game/
├── main.py                    # Entry point, game loop, state machine
├── game/
│   ├── settings.py            # All constants — single source of truth
│   ├── level.py               # Static farm map, cover zones, objective rects
│   ├── entities/
│   │   ├── tractor.py         # Player: movement, cover, noise system
│   │   ├── dealer.py          # Enemy: patrol AI, vision cone, state machine
│   │   └── gramps.py          # Win-condition NPC in the barn
│   ├── systems/
│   │   ├── input.py           # Unified keyboard + controller input
│   │   ├── detection.py       # Vision cone + noise detection (pure functions)
│   │   ├── collision.py       # Cover overlap detection
│   │   ├── objectives.py      # ObjectiveManager, TimingBar
│   │   └── state_machine.py   # Generic StateMachine[S] used by dealer AI
│   └── ui/
│       ├── hud.py             # Objective checklist, noise dot, intel mini-map
│       └── screens.py         # Win and caught overlays
└── assets/                    # Reserved for future sprite art and audio
```

---

## Tech Stack

- **Python 3.12**
- **Pygame 2.6**
- All visuals drawn as code shapes — no external art assets required for MVP
- Generic `StateMachine[S]` keeps enemy AI states clean and extensible
- Unified input system: keyboard and USB NES controller work simultaneously

---

## Roadmap

- [ ] Sprite art to replace placeholder shapes
- [ ] Audio — engine hum, scarecrow whisper, Gramps bell
- [ ] Second dealer with different patrol and behaviour
- [ ] Title screen and pause menu
