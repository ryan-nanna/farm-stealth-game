# create-issues.ps1
# Run from your farm-stealth-game folder after gh auth login
# .\create-issues.ps1

$repo = "ryan-nanna/farm-stealth-game"

$issues = @(
    @{
        title = "Update CLAUDE.md for Phase 2 scope"
        label = "documentation"
        body  = "## What`nUpdate CLAUDE.md to reflect all Phase 2 decisions before any new code is written.`n`n## Changes needed`n- Add Hubert and Hieronymus character specs (names, visual identity, behaviour)`n- Add scrap truck concept (Dealer 3, hard mode only)`n- Update enemy AI section: replace fixed patrol with lurk/hunt state machine`n- Update noise system spec: silent mode must be genuinely necessary`n- Add sprite integration plan (PNG files replacing drawn shapes)`n- Add Phase 2 session plan (sessions 9-16)`n- Lock difficulty target: confident 5-year-old playing solo`n- Round escalation: Round 1 Hubert only, Round 2 Hieronymus joins, Round 3+ both faster`n`n## Why first`nClaude Code reads CLAUDE.md at the start of every session. If it is not updated, Phase 2 sessions will build against the wrong spec."
    },
    @{
        title = "Replace generic dealer with Hubert - beard, tall, lurk behaviour"
        label = "enemy"
        body  = "## Character`nHubert is the taller, more methodical of the two scrap dealers. Identifiable by his beard.`n`n## Visual identity`n- Tall and lanky`n- Dark overcoat, flat cap`n- Beard (key identifier)`n- Top-down sprite when art pass is ready`n`n## Behaviour`n- Replaces the existing single dealer from MVP`n- Lurk pattern: slow drift with semi-random waypoints rather than fixed patrol`n- Wide vision cone, long range`n- Slow movement speed but covers a lot of ground over time`n- States: LURK, CURIOUS, SEARCHING, ALERT, CHASE, LEAVING`n`n## Acceptance criteria`n- [ ] Hubert class replaces existing dealer`n- [ ] Lurk waypoints feel organic, not mechanical`n- [ ] Vision cone width and range tuned for Round 1 solo play`n- [ ] Shape placeholder updated to reflect tall/lanky proportions until sprite ready"
    },
    @{
        title = "Add Hieronymus - mismatched socks, noise-sensitive, erratic"
        label = "enemy"
        body  = "## Character`nHieronymus is the shorter, more excitable dealer. Identifiable by one green sock and one red sock.`n`n## Visual identity`n- Shorter, rounder build than Hubert`n- Dark coat`n- One green sock, one red sock (visible in sprite)`n- Top-down sprite when art pass is ready`n`n## Behaviour`n- Joins in Round 2 (Hubert is solo in Round 1)`n- Erratic movement: checks corners, doubles back unexpectedly`n- Narrower vision cone than Hubert, shorter range`n- Highly noise-sensitive: snaps to CURIOUS on any amber+ noise nearby`n- Fast movement speed, unpredictable`n`n## Acceptance criteria`n- [ ] Hieronymus spawns from Round 2 onward`n- [ ] Distinct behaviour clearly different from Hubert in play`n- [ ] Noise sensitivity tuned so silent mode is necessary near him`n- [ ] Shape placeholder reflects shorter/rounder proportions until sprite ready"
    },
    @{
        title = "Replace fixed patrol with lurk/hunt state machine for all dealers"
        label = "enemy"
        body  = "## Why`nFixed patrol waypoints make dealers completely predictable. Hubert and Hieronymus are trespassers, not guards. They should feel like they are snooping suspiciously.`n`n## New states`n- LURK: slow drift around farm, semi-random waypoints`n- CURIOUS: heard/saw something, moves toward general area (not locked on)`n- SEARCHING: actively checks hiding spots at last known position`n- ALERT: vision cone locked on tractor for 1.5s`n- CHASE: 2-second escape window, dealer rushes tractor`n- LEAVING: round won, dealer exits farm bottom edge`n`n## Key design rules`n- LURK waypoints vary each round so no round feels the same`n- CURIOUS does not reveal tractor position to player`n- SEARCHING checks nearby hiding spots before returning to LURK`n- ALERT transitions to CHASE only after full 1.5s in cone`n`n## Acceptance criteria`n- [ ] All dealers use new state machine`n- [ ] LURK feels organic and unpredictable`n- [ ] SEARCHING makes hiding spots feel risky`n- [ ] State transitions visible in debug mode"
    },
    @{
        title = "Tune noise system - silent mode must be genuinely necessary"
        label = "gameplay"
        body  = "## Problem`nIn the MVP the noise system exists but dealers do not react meaningfully enough. Silent mode (B button / Left Shift) rarely changes the outcome.`n`n## Proposed changes`n- Dealers within noise radius immediately snap to CURIOUS state`n- Full-speed movement past a dealer within ~200px = near-certain ALERT`n- Silent mode cuts noise radius dramatically`n- Objective completion triggers a noise burst`n- Noise ring colours clearly communicate danger level`n`n## Tuning targets`n- Still, not hidden: 60px green pulse, no response`n- Moving slowly: 150px amber pulse, Hieronymus turns toward`n- Moving fast: 280px red pulse, both dealers investigate`n- Silent mode: 40px green dash, safe unless dealer very close`n- Objective complete: 200px orange spike, nearest dealer goes CURIOUS`n`n## Acceptance criteria`n- [ ] Silent mode demonstrably changes survival odds near dealers`n- [ ] A 5-year-old can understand noise rings without explanation`n- [ ] Objective completion feels tense due to noise burst`n- [ ] All noise radius values stored in settings.py"
    },
    @{
        title = "Little grey tractor PNG sprite - expressive headlight eyes"
        label = "art"
        body  = "## Why`nThe current tractor is a grey rectangle. The show's tractor is iconic and the expressive headlight eyes are the emotional heart of the character.`n`n## Visual requirements`n- Ferguson TE20 silhouette: rounded bonnet, exhaust pipe, large rear/small front wheels`n- Large expressive headlight eyes with pupils and glints (non-negotiable)`n- Warm grey palette with subtle depth`n- Top-down overhead camera angle`n- Transparent PNG background`n- Recommended size: 96x80px base`n`n## Image generation prompt`nTop-down overhead view of a small vintage grey Ferguson TE20 tractor, warm illustrated children's style, soft lighting, large expressive round headlight eyes with dark pupils and white glints showing personality, visible cab roof, large rear wheels with tread detail, small front wheels, exhaust pipe on bonnet, transparent PNG background, game sprite, clean edges, no cast shadows, flat overhead perspective`n`n## Integration`n- Save as assets/sprites/tractor.png`n- Claude Code replaces tractor.py shape drawing with pygame.image.load()`n`n## Acceptance criteria`n- [ ] Sprite loads without error`n- [ ] Eyes are clearly expressive and recognisable`n- [ ] Tractor readable at game scale within 96x80px rect`n- [ ] Transparent background renders correctly over grass/dirt"
    },
    @{
        title = "Hubert and Hieronymus sprites - top-down, show-accurate identity markers"
        label = "art"
        body  = "## Hubert sprite`nIdentity: tall, lanky, beard.`n`nImage generation prompt:`nTop-down overhead view of a tall thin man with a beard, wearing a dark overcoat and flat cap, children's illustrated style, slightly sinister but bumbling expression, hands in pockets, transparent PNG background, game sprite, overhead perspective, no cast shadows`n`nSave as: assets/sprites/hubert.png`n`n## Hieronymus sprite`nIdentity: shorter, one green sock and one red sock.`n`nImage generation prompt:`nTop-down overhead view of a shorter excitable man in a dark coat, one green sock and one red sock clearly visible at bottom of frame, children's illustrated style, hurrying posture, wide stance, transparent PNG background, game sprite, overhead perspective, no cast shadows`n`nSave as: assets/sprites/hieronymus.png`n`n## Acceptance criteria`n- [ ] Both sprites load without error`n- [ ] Hubert clearly taller than Hieronymus at game scale`n- [ ] Hieronymus socks visible and colour-distinct`n- [ ] Both readable at game scale"
    },
    @{
        title = "Farm environment sprites - replace all placeholder rects"
        label = "art"
        body  = "## Elements to replace`n- barn.png: warm red, weathered wood, large doors`n- tree_oak.png: full canopy top-down, large cover zone`n- tree_apple.png: smaller, visible apples`n- wall_stone.png: rough texture, mid-map horizontal`n- pig_pen.png: muddy ground, wooden fence posts`n- chicken_coop.png: small wooden shed`n- scarecrow.png: metal scarecrow, distinctive silhouette`n- gramps.png: old farmer at barn doorway`n- well.png: stone well`n`n## Prompt template`nTop-down overhead view of [element], farm setting, warm illustrated children's style, soft natural lighting, transparent PNG background, game sprite, clean edges, overhead perspective, no cast shadows`n`n## Integration`n- All sprites load in level.py`n- Claude Code replaces pygame.draw.rect() calls with blit() calls`n`n## Acceptance criteria`n- [ ] All elements load without error`n- [ ] Farm reads as a warm friendly environment`n- [ ] Cover zones still logically align with sprite boundaries"
    },
    @{
        title = "Headlight eye expressions - animate per game state"
        label = "art"
        body  = "## Why`nThe show's tractor communicates entirely through headlight eyes. Even simple eye variations add enormous personality.`n`n## Proposed expressions`n- Normal driving: forward, alert (default sprite)`n- Hidden in cover: eyes dart side to side nervously`n- Dealer nearby: eyes go wide`n- Completing objective: eyes focused, determined`n- Objective complete: eyes scrunch happy`n- Caught: eyes wide in shock`n- Win screen: eyes crinkle into smile`n`n## Implementation`nMultiple sprite files (tractor_normal.png, tractor_wide.png, etc.) for Phase 2. Upgrade to spritesheet later.`n`n## Acceptance criteria`n- [ ] At minimum: normal, hidden, alert, caught, win expressions`n- [ ] Eye state updates match game state transitions`n- [ ] Transitions feel responsive"
    },
    @{
        title = "Objective animations - pigs, cows, scarecrow personality moments"
        label = "objectives"
        body  = "## Why`nObjectives currently complete silently with a HUD tick. Each should have a small visual moment that feels rewarding for a 5-year-old.`n`n## Pig pen - feed the pigs`n- Tractor nudges feed trough (slight forward/back motion)`n- Brief pig silhouette bobs up at fence`n- Orange noise burst ring visible (tense!)`n`n## Cow pasture - help with cows`n- Gate swings open animation`n- Cow silhouette moves through gate`n- Farmer waves briefly`n`n## Scarecrow - whisper intel`n- Tractor leans slightly toward scarecrow`n- Small speech bubble appears briefly`n- Mini-map overlay activates immediately after`n`n## Implementation notes`n- Animations 0.5-1.0 seconds max`n- All implemented as simple state + timer in ObjectiveManager`n- No external animation library needed`n`n## Acceptance criteria`n- [ ] Each objective has a distinct visual moment on completion`n- [ ] Animations do not block gameplay`n- [ ] Noise burst during pig/scarecrow objectives creates genuine tension"
    },
    @{
        title = "Mini achievement moments on objective complete"
        label = "objectives"
        body  = "## What`nSmall celebratory visual moments layered on top of objective animations.`n`n## Proposed moments`n- Star burst/sparkle around tractor on each objective complete`n- HUD objective icon bounces and ticks with satisfying motion`n- Gramps waves from barn doorway when all 3 objectives are done`n- Tractor eyes go happy scrunch for 1 second on each completion`n`n## Implementation`n- Simple expanding circle + fade (no particle system needed)`n- All timers managed in ObjectiveManager or lightweight AnimationQueue class`n`n## Acceptance criteria`n- [ ] Completing each objective feels visually rewarding`n- [ ] All-complete signal (Gramps wave) is clearly different from single-objective complete`n- [ ] Celebratory moments brief enough not to distract from ongoing danger"
    },
    @{
        title = "Objective risk tuning - match CLAUDE.md danger ratings"
        label = "gameplay"
        body  = "## Why`nMVP objectives feel similar in difficulty. Each should have a distinct risk profile.`n`n## Target risk profile`n`n### Pig pen - HIGH risk`n- Near dealer entry road`n- Timing bar moves faster than other objectives`n- Noise burst on completion is largest (200px orange spike)`n- No good cover nearby`n`n### Cow pasture - MEDIUM risk`n- Hubert's lurk path passes through this zone periodically`n- Gate mechanic requires precise A-button timing`n- Oak tree nearby provides escape cover`n`n### Scarecrow - LOW-MEDIUM risk`n- Stone wall provides covered approach from barn side`n- Whisper noise burst attracts Hieronymus`n- Intel reward makes the risk worthwhile`n`n## Acceptance criteria`n- [ ] Pig pen feels genuinely dangerous`n- [ ] Cow pasture requires watching Hubert's position`n- [ ] Scarecrow requires silent mode on approach and exit`n- [ ] All timing bar speeds stored in settings.py"
    },
    @{
        title = "Title screen - Farm Stealth, tractor peeking around barn"
        label = "polish"
        body  = "## What`nA simple illustrated title screen before gameplay starts.`n`n## Design`n- Background: farm scene (sky + grass, barn visible top right)`n- Title text: Farm Stealth in large friendly font`n- Little grey tractor peeking around barn corner (just eyes and bonnet visible)`n- Press Start / Space to begin prompt`n- Controller and keyboard both trigger start`n`n## Implementation`n- New screen state in game/ui/screens.py`n- No animation required for Phase 2 (tractor can be static)`n- Uses existing palette and font from settings.py`n`n## Acceptance criteria`n- [ ] Title screen appears on launch`n- [ ] Start button / Space begins the game`n- [ ] Escape from title screen quits`n- [ ] Tractor peek is charming with eyes visible"
    },
    @{
        title = "Round escalation tuning for 5-year-old solo play"
        label = "gameplay"
        body  = "## Target player`nConfident 5-year-old playing solo.`n`n## Proposed escalation`n- Round 1: Hubert only, slow, forgiving noise radius`n- Round 2: Hubert + Hieronymus, normal speed, standard sensitivity`n- Round 3: Both faster, longer vision`n- Round 4+: Both at max speed and full spec`n`n## Key tuning principles`n- Round 1 should be winnable by a 5-year-old on first attempt`n- Round 2 introduces real tension`n- Rounds 3+ are the genuine challenge`n- No round should feel impossible`n- All escalation values in settings.py`n`n## Acceptance criteria`n- [ ] Round 1 consistently winnable by target age group`n- [ ] Round 2 feels noticeably harder`n- [ ] Escalation values in settings.py (not hardcoded)`n- [ ] Playtested with actual 5-year-old before closing issue"
    },
    @{
        title = "Scrap truck - Dealer 3, perimeter driver, hard mode only"
        label = "enemy"
        body  = "## What`nAn optional third threat for players who find Round 3+ too easy after the enemy overhaul.`n`n## Character`nA battered scrap dealer truck slowly driving a loop around the farm perimeter.`n`n## Behaviour`n- Simple path follower: drives a fixed road around the outside edge of the map`n- No vision cone, no state machine`n- Presence blocks certain escape routes`n- Speed increases slightly each round`n`n## Trigger`nOnly spawns from Round 3 onward or in a future Hard difficulty mode.`n`n## Image generation prompt`nTop-down overhead view of a battered old scrap dealer truck loaded with junk metal, rusty and dented, children's illustrated style, warm earthy colours, transparent PNG background, game sprite, overhead perspective, no cast shadows`n`nSave as: assets/sprites/scrap_truck.png`n`n## Acceptance criteria`n- [ ] Truck follows perimeter path without pathfinding complexity`n- [ ] Presence creates route pressure in Round 3+`n- [ ] Does not spawn in Rounds 1-2`n- [ ] Low priority: only implement if game still feels easy after issues 10-13"
    },
    @{
        title = "Sound design pass - engine, objectives, caught, win"
        label = "sound"
        body  = "## Status`nDeliberately last. MusicSystem class is stubbed in MVP. Do not start until art and gameplay are fully locked and playtested.`n`n## Planned sounds`n- Tractor engine hum: speed-reactive pitch`n- Silent mode cut: satisfying engine-off sound`n- Objective complete: warm cheerful chime`n- All objectives done: grander chime + Gramps bell`n- Dealer alert: tense sting, not scary`n- Caught jingle: funny and bumbling, not scary`n- Win fanfare: short cheerful music burst`n- Ambient farm: optional quiet background (birds, wind)`n`n## Implementation`n- Plug into existing stubbed MusicSystem class`n- All sound files in assets/sounds/`n- pygame.mixer for playback`n`n## Acceptance criteria`n- [ ] All sounds play at correct game moments`n- [ ] No sound is scary or jarring for a 3-6 year old`n- [ ] Engine pitch reflects tractor speed`n- [ ] Sound can be muted"
    },
    @{
        title = "README overhaul - screenshots, install guide, portfolio context"
        label = "documentation"
        body  = "## Why`nCurrent README is a placeholder. As a portfolio project this repo needs a README that tells the story clearly to a hiring manager or collaborator.`n`n## Sections to include`n- Project description: top-down stealth game for a 5-year-old who loves tractors`n- Inspired by the Little Grey Fergie / Gratass show`n- Built as both a gift and a portfolio demonstration`n- Screenshot or GIF of gameplay`n- Tech stack: Python 3.12, Pygame 2.6+, USB NES controller support, Windows`n- Install and run instructions`n- Controls reference`n- Build session log showing incremental approach`n`n## Install instructions to include`n````ngit clone https://github.com/ryan-nanna/farm-stealth-game`ncd farm-stealth-game`npy -3.12 -m pip install -r requirements.txt`npy -3.12 main.py`n```n`n## Acceptance criteria`n- [ ] README tells project story in under 2 minutes of reading`n- [ ] Install instructions work on a clean Windows machine`n- [ ] At least one screenshot included`n- [ ] Portfolio-appropriate tone"
    }
)

Write-Host "Creating $($issues.Count) GitHub issues for farm-stealth-game..." -ForegroundColor Cyan
Write-Host ""

foreach ($issue in $issues) {
    Write-Host "Creating: $($issue.title)" -ForegroundColor Yellow
    $result = gh issue create --repo $repo --title $issue.title --label $issue.label --body $issue.body
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Created: $result" -ForegroundColor Green
    } else {
        Write-Host "  Failed - check gh auth and repo name" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Done! View your issues at: https://github.com/$repo/issues" -ForegroundColor Cyan
