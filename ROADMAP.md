# Farm Stealth Game — Phase 2 Roadmap & Backlog

**Status:** MVP complete (Sessions 1–8). Gameplay loop works end-to-end.  
**Next phase focus:** Art pass, enemy overhaul, gameplay depth, objective polish.

---

## What the MVP Delivered

- ✅ Tractor moves on screen — keyboard + USB NES controller
- ✅ Farm map renders with cover zones and stone wall collision
- ✅ Cover system — tractor hides when inside cover zones
- ✅ One dealer — patrol path, vision cone drawn on screen
- ✅ Detection logic — noise radius, state machine, caught screen
- ✅ All 3 objectives — TimingBar mechanic, ObjectiveManager
- ✅ Gramps + win condition — round escalation, full game loop
- ✅ Scarecrow intel mechanic — HUD polish

---

## Known MVP Gaps (from playtesting)

| Area | Issue |
|------|-------|
| Enemies | Only one dealer — not enough threat |
| Enemies | Patrol pattern too predictable — easy to avoid |
| Noise system | Silent mode rarely necessary — dealers not reactive enough |
| Art | Placeholder shapes only — nothing like the show visually |
| Objectives | Lack personality — no animations or mini-moments |
| Sound | Fully stubbed — silent throughout |

---

## Locked Design Decisions

| Question | Decision |
|----------|----------|
| Number of dealers | 2 default (Hubert + Hieronymus). 3rd optional — scrap truck, simpler behaviour. Max 3. |
| Dealer names | **Hubert** (beard) and **Hieronymus** (one green sock, one red sock) — from the show |
| Dealer 3 | Scrap dealer truck driving slowly around farm perimeter. No flush/wait complexity. |
| Character names in-game | Not shown for now (Gramps exception stays) |
| Game title | Farm Stealth — keep for now |
| Difficulty | Tuned for a confident 5-year-old playing solo |
| Sprite approach | Source inspiration images online → use as reference for image generation prompts |
| Dealer 4 | Not in scope |

---

## Phase 2 Feature Backlog

---

### THEME 1: Enemy Overhaul

#### Feature: Hubert — Dealer 1 (replace generic dealer)
**Identity:** Tall, lanky, has a beard.  
**Behaviour:** Wide sweeping lurk pattern. Slow but covers a lot of ground. Wide vision cone.  
**From the show:** Methodical, serious about finding the tractor.

#### Feature: Hieronymus — Dealer 2
**Identity:** Distinguishing feature — one green sock, one red sock. Shorter, more excitable.  
**Behaviour:** Erratic — checks corners, doubles back, moves faster. Narrow vision cone but very noise-sensitive.  
**From the show:** The more bumbling of the two, but unpredictable.

#### Feature: Scrap Truck (Dealer 3 — optional hard mode)
**Identity:** A battered scrap dealer truck slowly circling the farm perimeter.  
**Behaviour:** Drives a fixed road loop around the outside of the farm. Blocks certain exit paths. No vision cone — just presence creates pressure.  
**Complexity:** Low — no state machine needed, just a path follower.

#### Feature: Hunting Behaviour (replaces fixed patrol)
**Why:** Fixed waypoints make dealers predictable. Hubert and Hieronymus are trespassers — they should feel like they're snooping, not guarding.

Proposed states:
```
LURK       → slow drift around farm, semi-random waypoints
CURIOUS    → heard something, moves toward general area (not locked on)
SEARCHING  → actively checks hiding spots and corners
ALERT      → vision cone locked on tractor for 1.5s
CHASE      → 2-second escape window
LEAVING    → round won, exits farm bottom edge
```

#### Feature: Noise System Teeth
**Why:** Silent mode (B button) is currently underused. Dealers need to react to noise immediately and meaningfully.

Proposed changes:
- Dealers within noise radius snap to CURIOUS state immediately
- Moving at full speed past a dealer within ~200px = near-certain detection
- Silent mode becomes genuinely necessary for close passes and objective completions
- Objective completion noise burst is a real tense moment — player must be ready to hide

---

### THEME 2: Art Pass

#### Sprite approach
Source reference images from the show online → use as visual brief for AI image generation
(Midjourney, DALL-E, Adobe Firefly) → drop PNGs into `assets/sprites/` → Claude Code
replaces shape-drawing with `pygame.image.load()`.

All sprites need: **transparent PNG background, top-down overhead camera angle.**

#### Feature: Little Grey Tractor Sprite
**Key visual requirements:**
- Ferguson TE20 silhouette — rounded bonnet, exhaust pipe, large rear / small front wheels
- **Large expressive headlight eyes with pupils and glints** — this is the emotional core
- Warm grey, slight depth/shading (not flat)
- Top-down perspective

**Image generation prompt:**
```
Top-down overhead view of a small vintage grey Ferguson TE20 tractor,
warm illustrated children's style, soft lighting, large expressive round
headlight eyes with dark pupils and white glints showing personality,
visible cab roof, large rear wheels with tread detail, small front wheels,
exhaust pipe on bonnet, transparent PNG background, game sprite,
clean edges, no cast shadows, flat overhead perspective
```

#### Feature: Hubert Sprite (Dealer 1)
**Identity markers:** Tall, lanky, beard.

**Image generation prompt:**
```
Top-down overhead view of a tall thin man with a beard, wearing a dark
overcoat and flat cap, children's illustrated style, slightly sinister
but bumbling expression, hands in pockets, transparent PNG background,
game sprite, overhead perspective, no cast shadows
```

#### Feature: Hieronymus Sprite (Dealer 2)
**Identity markers:** One green sock, one red sock. Shorter, excitable.

**Image generation prompt:**
```
Top-down overhead view of a shorter excitable man in a dark coat,
one green sock and one red sock clearly visible, children's illustrated
style, hurrying posture, transparent PNG background, game sprite,
overhead perspective, no cast shadows
```

#### Feature: Scrap Truck Sprite (if Dealer 3 implemented)
**Image generation prompt:**
```
Top-down overhead view of a battered old scrap dealer truck loaded with
junk metal, rusty and dented, children's illustrated style, warm earthy
colours, transparent PNG background, game sprite, overhead perspective,
no cast shadows
```

#### Feature: Farm Environment Sprites
Replace coloured rectangles with illustrated farm elements.

| Element | Key visual notes |
|---------|-----------------|
| Red barn | Warm red, weathered wood, large doors — Gramps' home base |
| Oak tree | Full canopy top-down, large enough to hide tractor |
| Apple tree | Smaller, visible apples, top-down |
| Stone wall | Rough stone texture, mid-map horizontal run |
| Pig pen | Muddy ground, wooden fence posts |
| Chicken coop | Small wooden shed |
| Scarecrow | Metal scarecrow, fixed position — intel source |
| Gramps | Old farmer at barn doorway |
| Well / trough | Stone well, partial cover |

**Prompt template:**
```
Top-down overhead view of [element], farm setting, warm illustrated
children's style, soft natural lighting, transparent PNG background,
game sprite, clean edges, overhead perspective, no cast shadows
```

#### Feature: Headlight Eye Expressions
The show's tractor communicates entirely through headlight eyes. Animate these per state.

| Game state | Eye expression |
|-----------|---------------|
| Normal driving | Forward, alert, engaged |
| Hidden in cover | Eyes dart side to side nervously |
| Dealer nearby (CURIOUS) | Eyes go wide |
| Objective completing | Eyes focused, determined |
| Objective complete | Eyes scrunch happy |
| Caught | Eyes wide in shock |
| Win screen | Eyes crinkle into a big smile |

---

### THEME 3: Objective Polish

#### Feature: Objective Animations
Small personality moments when objectives complete — even simple shape animations work here.

| Objective | Animation |
|-----------|-----------|
| Feed the pigs | Tractor nudges trough, brief pig silhouette bounces |
| Help with cows | Gate swings open, cow silhouette moves through |
| Scarecrow whisper | Tractor leans in, small speech bubble appears briefly |

#### Feature: Mini Achievement Moments
- Star burst / sparkle around tractor on completion
- Objective icon ticks off HUD with bounce
- Gramps waves from barn doorway when all 3 done

#### Feature: Objective Risk Tuning
Make each objective feel appropriately tense:
- **Pig pen (HIGH risk):** Near dealer entry road. Noise burst on completion. Fast timing bar.
- **Cow pasture (MEDIUM):** Hubert's patrol passes nearby. Gate mechanic requires precision.
- **Scarecrow (LOW-MEDIUM):** Wall provides cover approach. Noise burst on whisper attracts Hieronymus.

---

### THEME 4: Game Feel & Polish

#### Feature: Title Screen
- "Farm Stealth" title
- Little grey tractor peeking around barn corner
- Press Start / Space to begin

#### Feature: Round Escalation Tuning
Calibrate escalation for a 5-year-old solo player:
- Round 1: Hubert only, slow, forgiving noise radius
- Round 2: Hieronymus joins, noise system tightens
- Round 3+: Both at increased speed, tighter vision

#### Feature: Sound Design (last)
After art and gameplay are fully locked.

| Sound | Notes |
|-------|-------|
| Tractor engine hum | Speed-reactive pitch |
| Silent mode | Engine cuts to near-silence |
| Objective complete | Warm chime |
| Dealer alert | Tense sting |
| Caught | Funny, not scary |
| Win | Cheerful fanfare |
| Gramps bell | Rings when all objectives done |

---

### THEME 5: GitHub & Portfolio

#### Feature: README Overhaul
- Project description + motivation (gift for a 5-year-old)
- Gameplay screenshot / GIF
- Install and run instructions
- Controls reference
- Build session log

#### Feature: Update CLAUDE.md for Phase 2
First task in Claude Code before any Phase 2 code is written.

---

## GitHub Issues to Create

| Issue # | Title | Theme | Priority |
|---------|-------|-------|----------|
| 9 | Update CLAUDE.md for Phase 2 scope | Portfolio | **Do first** |
| 10 | Replace dealer with Hubert — beard, lurk behaviour | Enemy | High |
| 11 | Add Hieronymus — mismatched socks, noise-sensitive | Enemy | High |
| 12 | Replace fixed patrol with lurk/hunt state machine | Enemy | High |
| 13 | Tune noise system — silent mode must matter | Enemy | High |
| 14 | Little grey tractor PNG sprite | Art | High |
| 15 | Hubert + Hieronymus sprites | Art | High |
| 16 | Farm environment sprites | Art | Medium |
| 17 | Headlight eye expressions per game state | Art | Medium |
| 18 | Objective animations — pigs, cows, scarecrow | Objectives | Medium |
| 19 | Mini achievement moments on objective complete | Objectives | Low |
| 20 | Objective risk tuning per difficulty | Objectives | Medium |
| 21 | Title screen | Polish | Medium |
| 22 | Round escalation tuning for 5-year-old | Polish | High |
| 23 | Scrap truck (Dealer 3) — perimeter driver, hard mode | Enemy | Low |
| 24 | Sound design pass | Sound | **Do last** |
| 25 | README overhaul for GitHub portfolio | Portfolio | Medium |

---

## Recommended Sequence

1. **Create GitHub issues #9–25** from the table above
2. **Start Issue #9** — update CLAUDE.md in Claude Code before anything else
3. **Issues #10–13** — enemy overhaul first, fixes biggest gameplay gap
4. **Generate sprites** in parallel while Claude Code works on enemies
5. **Issues #14–17** — art integration once sprites are ready
6. **Issues #18–22** — objective and polish pass
7. **Issue #23** — scrap truck only if game feels too easy after enemy overhaul
8. **Issue #24** — sound, very last

---

*Updated with player input: Hubert + Hieronymus character details, dealer count confirmed at 2 default / 3 max, scrap truck concept added, difficulty set for confident 5-year-old.*
