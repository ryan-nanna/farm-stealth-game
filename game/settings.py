# settings.py
# Single source of truth for every magic number in the project.
# Import this module wherever you need a constant — never hardcode values elsewhere.

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
WINDOW_TITLE: str = "Farm Stealth"
TARGET_FPS: int = 60

# ---------------------------------------------------------------------------
# Colours  (R, G, B)
# Pulled from the toy-box art palette: warm greys, sky blue, saturated greens
# ---------------------------------------------------------------------------
COLOUR_SKY_BLUE:       tuple[int, int, int] = (135, 196, 235)
COLOUR_GRASS_GREEN:    tuple[int, int, int] = (94,  163,  65)
COLOUR_DARK_GREEN:     tuple[int, int, int] = (58,  110,  40)
COLOUR_WARM_GREY:      tuple[int, int, int] = (160, 155, 148)
COLOUR_LIGHT_GREY:     tuple[int, int, int] = (210, 207, 202)
COLOUR_DARK_GREY:      tuple[int, int, int] = ( 80,  78,  74)
COLOUR_BARN_RED:       tuple[int, int, int] = (185,  46,  46)
COLOUR_WHEAT:          tuple[int, int, int] = (220, 185,  90)
COLOUR_DIRT:           tuple[int, int, int] = (175, 140,  95)
COLOUR_WHITE:          tuple[int, int, int] = (255, 255, 255)
COLOUR_BLACK:          tuple[int, int, int] = (  0,   0,   0)

# Noise ring colours (used by HUD and tractor noise visualisation)
COLOUR_NOISE_HIDDEN:   tuple[int, int, int] = (  0,   0,   0)   # not shown
COLOUR_NOISE_STILL:    tuple[int, int, int] = ( 80, 200,  80)   # green pulse
COLOUR_NOISE_SLOW:     tuple[int, int, int] = (230, 180,  40)   # amber pulse
COLOUR_NOISE_FAST:     tuple[int, int, int] = (210,  55,  55)   # red pulse

# ---------------------------------------------------------------------------
# Tractor
# ---------------------------------------------------------------------------
TRACTOR_WIDTH:  int = 48
TRACTOR_HEIGHT: int = 40
TRACTOR_SPEED_NORMAL: float = 180.0   # pixels per second, normal drive
TRACTOR_SPEED_SILENT: float =  80.0   # pixels per second, B-button silence mode
TRACTOR_BODY_COLOUR:         tuple[int, int, int] = COLOUR_WARM_GREY
TRACTOR_HEADLIGHT_COLOUR:    tuple[int, int, int] = (255, 240, 140)
TRACTOR_WHEEL_COLOUR:        tuple[int, int, int] = ( 50,  48,  44)
TRACTOR_WHEEL_RADIUS:        int = 7
TRACTOR_COVER_RING_WIDTH:    int = 3   # pixel width of the cover-state outline ring

# Noise radii (pixels) — tractor emits noise proportional to movement state.
# Still + exposed: ring is drawn but dealers do NOT react (green = safe).
# Slow / fast movement: dealers within the radius hear the tractor.
NOISE_RADIUS_STILL: float =  50.0
NOISE_RADIUS_SLOW:  float =  95.0   # silent-mode movement (amber) — audible, but manageable
NOISE_RADIUS_FAST:  float = 210.0   # normal movement near a dealer = near-certain detection

# Objective completion noise burst — a real tense moment, not cosmetic
OBJ_BURST_RADIUS:   float = 280.0   # spike radius when an objective completes
OBJ_BURST_DURATION: float = 1.5     # seconds the spike lasts

# How long the HAPPY eye expression lasts after an objective completes
TRACTOR_EYE_HAPPY_DURATION: float = 0.8          # seconds

# Starting position — top-right area near barn
TRACTOR_SPAWN_X: int = SCREEN_WIDTH  - 120
TRACTOR_SPAWN_Y: int = 80

# ---------------------------------------------------------------------------
# Input — axis / button deadzone
# ---------------------------------------------------------------------------
AXIS_DEADZONE: float = 0.25   # ignore stick values below this threshold

# Pygame joystick hat / axis indices for a generic USB NES controller.
# These match the most common HID mapping; may need tweaking per device.
CONTROLLER_AXIS_X: int = 0    # left-right axis index
CONTROLLER_AXIS_Y: int = 1    # up-down axis index

# Button indices (0-based) for a generic USB NES controller
CONTROLLER_BUTTON_A:      int = 1   # rightmost face button (NES A)
CONTROLLER_BUTTON_B:      int = 0   # second face button   (NES B)
CONTROLLER_BUTTON_START:  int = 9   # Start
CONTROLLER_BUTTON_SELECT: int = 8   # Select

# ---------------------------------------------------------------------------
# Farm Map — zone positions as (x, y, width, height) tuples
# ---------------------------------------------------------------------------

# Safe zone / win condition (top-right)
MAP_BARN_RECT:         tuple[int, int, int, int] = (1060,  15, 205, 150)

# Objective zone 2 — cow pasture (top-left)
MAP_COW_PASTURE_RECT:  tuple[int, int, int, int] = (  15,  15, 250, 175)

# Full-cover hiding spots
MAP_APPLE_TREE_RECT:   tuple[int, int, int, int] = ( 555,  20, 100, 100)
MAP_OAK_TREE_RECT:     tuple[int, int, int, int] = (  30, 215, 110, 110)
MAP_CHICKEN_COOP_RECT: tuple[int, int, int, int] = (  35, 525, 165, 120)
MAP_OLD_SHED_RECT:     tuple[int, int, int, int] = ( 535, 515, 185, 140)
MAP_PIG_PEN_RECT:      tuple[int, int, int, int] = (1060, 480, 210, 195)  # objective 1

# Partial-cover / objective zones
MAP_SCARECROW_RECT:    tuple[int, int, int, int] = ( 600, 255,  55,  80)  # objective 3
MAP_WELL_RECT:         tuple[int, int, int, int] = ( 775, 530,  90,  65)

# Stone wall — three segments across mid-map at y=370.
# Passage gaps: x=265–435 (170 px wide) and x=885–1035 (150 px wide).
MAP_WALL_LEFT_RECT:    tuple[int, int, int, int] = (   0, 370, 265,  30)
MAP_WALL_CENTRE_RECT:  tuple[int, int, int, int] = ( 435, 370, 450,  30)
MAP_WALL_RIGHT_RECT:   tuple[int, int, int, int] = (1035, 370, 245,  30)

# Dirt paths through the wall gaps (drawn as ground-level trails)
MAP_PATH_LEFT_RECT:    tuple[int, int, int, int] = ( 305, 190,  80, 180)  # pasture→wall
MAP_PATH_RIGHT_RECT:   tuple[int, int, int, int] = ( 895, 165,  85, 315)  # barn→pig pen

# Dealer entry road (bottom of screen)
MAP_ENTRY_Y:           int = 680
MAP_ENTRY_HEIGHT:      int = 40

# ---------------------------------------------------------------------------
# Farm Map — feature colours
# ---------------------------------------------------------------------------
COLOUR_STONE:          tuple[int, int, int] = (148, 143, 136)   # stone wall body
COLOUR_TREE_TRUNK:     tuple[int, int, int] = (120,  85,  50)   # tree trunk / wood
COLOUR_TREE_CANOPY:    tuple[int, int, int] = ( 58, 130,  40)   # tree foliage
COLOUR_PASTURE:        tuple[int, int, int] = (112, 188,  78)   # bright cow-pasture grass
COLOUR_PIG_PEN:        tuple[int, int, int] = (195, 165, 130)   # muddy pen ground
COLOUR_FENCE:          tuple[int, int, int] = (185, 155, 100)   # tan wood fence
COLOUR_SHED:           tuple[int, int, int] = (145, 120,  85)   # weathered shed wood
COLOUR_COOP:           tuple[int, int, int] = (205, 185, 145)   # light chicken-coop wood
COLOUR_WELL:           tuple[int, int, int] = (110, 100,  90)   # dark stone well
COLOUR_WOOD_DARK:      tuple[int, int, int] = ( 95,  65,  35)   # dark wood (doors)

# Debug: cover-zone outline colours (used when DEBUG_DRAW_HITBOXES is True)
COLOUR_COVER_FULL:     tuple[int, int, int] = (  0, 200,   0)   # green — full cover
COLOUR_COVER_PARTIAL:  tuple[int, int, int] = (200, 200,   0)   # yellow — partial cover

# ---------------------------------------------------------------------------
# Hubert (Dealer 1 — tall, lanky, beard)
# ---------------------------------------------------------------------------
HUBERT_WIDTH:          int   = 16     # narrower than a regular person — he's lanky
HUBERT_HEIGHT:         int   = 46     # taller than a regular person
HUBERT_HEAD_RADIUS:    int   = 10
HUBERT_HEAD_OFFSET:    int   =  8     # px above body top-edge to head centre
HUBERT_SPEED_LURK:     float = 70.0   # px/s — slow methodical drift
HUBERT_SPEED_CHASE:    float = 150.0  # px/s — roughly 2× lurk speed
# Sprite display size — larger than the hitbox rect so the photo reads clearly on screen
HUBERT_SPRITE_W: int = 90
HUBERT_SPRITE_H: int = 110

HUBERT_BODY_COLOUR:       tuple[int, int, int] = ( 90, 120, 165)  # denim vest — mid blue (shape fallback)
HUBERT_HEAD_COLOUR:       tuple[int, int, int] = (200, 160, 120)  # warm skin tone
HUBERT_HAIR_COLOUR:       tuple[int, int, int] = ( 75,  42,  22)  # dark reddish-brown long hair
HUBERT_HAT_BRIM_COLOUR:   tuple[int, int, int] = (175, 158, 112)  # dirty tan bucket hat brim
HUBERT_HAT_CROWN_COLOUR:  tuple[int, int, int] = (148, 132,  88)  # slightly darker hat crown

# Vision cone — Hubert has a wide cone (methodical, covers a lot of ground)
VISION_CONE_RANGE:      float = 220.0  # px
VISION_CONE_HALF_ANGLE: float = 50.0   # degrees — half of total FOV (100° wide)
VISION_CONE_COLOUR:     tuple[int, int, int] = (255, 240, 100)  # warm yellow (LURK)
VISION_CONE_ALPHA:      int   = 65     # 0-255

WAYPOINT_REACH_DIST:    float = 12.0   # px — close enough to "arrive" at a waypoint

# Detection
PARTIAL_COVER_RANGE_MULT: float = 0.4   # vision range × this in partial cover (60% reduction)
DEALER_CATCH_DIST:        float = 40.0  # px — dealer catches tractor when this close during CHASE

# Hubert AI state timers
HUBERT_CURIOUS_TIME:  float = 3.0   # s in CURIOUS moving toward noise source before giving up
DEALER_ALERT_TIME:    float = 1.5   # s of continuous sight before CHASE
DEALER_CHASE_TIME:    float = 3.0   # s of active CHASE before SEARCHING
DEALER_SEARCH_TIME:   float = 3.5   # s of SEARCHING before returning to LURK

# Round escalation — applied per completed round (capped at ESCALATION_MAX_ROUNDS)
# Gentle slope: a confident 5-year-old wins round 1 comfortably; rounds 3–5 get challenging.
ESCALATION_SPEED_PER_ROUND:  float = 10.0   # px/s added to lurk and chase speeds
ESCALATION_VISION_PER_ROUND: float = 18.0   # px added to vision cone range
ESCALATION_MAX_ROUNDS:       int   = 5       # escalation stops growing after this round

# Cone colours per alert level (LURK uses VISION_CONE_COLOUR)
HUBERT_CONE_CURIOUS:    tuple[int, int, int] = (255, 160,  40)  # orange — heard something
DEALER_CONE_ALERT:      tuple[int, int, int] = (255,  50,  50)  # red — spotted tractor

# ---------------------------------------------------------------------------
# Hieronymus (Dealer 2 — shorter, faster, mismatched socks, noise-obsessed)
# Joins in Round 2. Narrow vision cone but reacts to any noise within sniff distance.
# ---------------------------------------------------------------------------
HIERONYMUS_WIDTH:          int   = 18
HIERONYMUS_HEIGHT:         int   = 36     # shorter than Hubert
HIERONYMUS_HEAD_RADIUS:    int   =  9
HIERONYMUS_HEAD_OFFSET:    int   =  8
HIERONYMUS_SPEED_LURK:     float = 105.0  # faster, more erratic drift
HIERONYMUS_SPEED_CHASE:    float = 195.0  # much faster chase — very scary
HIERONYMUS_BODY_COLOUR:    tuple[int, int, int] = ( 70,  50,  90)  # dark purple-grey coat
HIERONYMUS_HEAD_COLOUR:    tuple[int, int, int] = (200, 160, 120)  # warm skin tone
HIERONYMUS_SOCK_GREEN:     tuple[int, int, int] = ( 55, 180,  75)  # green sock (left)
HIERONYMUS_SOCK_RED:       tuple[int, int, int] = (205,  50,  50)  # red sock (right)

# Hieronymus has a narrower cone but an acute sense of noise
HIERONYMUS_VISION_RANGE:      float = 170.0  # shorter range than Hubert
HIERONYMUS_VISION_HALF_ANGLE: float = 32.0   # narrow cone — he's looking where he's going
HIERONYMUS_SNIFF_DIST:        float = 200.0  # snaps to CURIOUS on amber/red within this
HIERONYMUS_CURIOUS_TIME:      float = 2.5    # s in CURIOUS before giving up

HIERONYMUS_SPRITE_W: int = 80
HIERONYMUS_SPRITE_H: int = 95

# Hieronymus lurk waypoints — right-side focus with erratic corner-checking.
# He doubles back and checks tight spots, making him feel unpredictable.
HIERONYMUS_LURK_WAYPOINTS: list[tuple[int, int]] = [
    (1160, 650),   # entry road, bottom-right
    (1100, 490),   # right edge, mid-map
    (940, 440),    # right side, below wall
    (1060, 310),   # above wall, near barn
    (780, 200),    # mid-top, right of apple tree
    (640, 330),    # near scarecrow — he checks this spot
    (440, 450),    # below wall, centre-left
    (350, 560),    # bottom-left, coop area
    (650, 570),    # bottom-centre, near shed
    (1080, 555),   # pig pen area — doubles back
]

# ---------------------------------------------------------------------------
# Scrap Truck (Dealer 3 — hard mode, optional)
# Drives a fixed clockwise road loop around the farm perimeter.
# No vision cone or state machine — presence alone creates pressure.
# Enabled from round 3 onwards (or never, if game feels balanced without it).
# ---------------------------------------------------------------------------
SCRAP_TRUCK_SPEED:       float = 95.0   # px/s — slow enough to feel inevitable
SCRAP_TRUCK_WIDTH:       int   = 50
SCRAP_TRUCK_HEIGHT:      int   = 32
SCRAP_TRUCK_BODY_COLOUR: tuple[int, int, int] = ( 95,  75,  55)  # rusty brown
SCRAP_TRUCK_CAB_COLOUR:  tuple[int, int, int] = ( 70,  55,  40)  # darker cab
SCRAP_TRUCK_CATCH_DIST:  float = 48.0  # px — truck runs the tractor over if this close

# Perimeter loop — clockwise, hugging the screen edges.
# Offset inward by ~28px so the truck body is fully on-screen.
_M = 28   # margin from edge
SCRAP_TRUCK_WAYPOINTS: list[tuple[int, int]] = [
    (SCREEN_WIDTH - _M, _M),               # top-right
    (_M,                _M),               # top-left
    (_M,                SCREEN_HEIGHT - _M),# bottom-left
    (SCREEN_WIDTH - _M, SCREEN_HEIGHT - _M),# bottom-right
]
del _M

# ---------------------------------------------------------------------------
# Hubert lurk waypoints — spread across the whole farm so he meanders widely.
# Each time he reaches one he picks the next at random (never the same spot twice).
HUBERT_LURK_WAYPOINTS: list[tuple[int, int]] = [
    (120, 650),   # bottom-left, near entry road
    ( 90, 480),   # left edge, mid-map
    (200, 420),   # just below stone wall, left of gap
    (170, 290),   # above wall, near oak tree
    (490, 200),   # mid-top, apple-tree area
    (630, 320),   # mid-map, scarecrow area
    (900, 420),   # right side, below wall
    (1080, 590),  # bottom-right, near pig pen
    (640, 570),   # bottom-centre, near old shed
    (380, 530),   # bottom-left, near chicken coop
]

# ---------------------------------------------------------------------------
# Objectives and TimingBar
# ---------------------------------------------------------------------------
OBJ_PIGS_HOLD_TIME:       float = 2.5   # seconds to fill pig-pen bar (faster = more tense)
OBJ_COWS_OSCILLATE_SPEED: float = 1.0   # bar oscillation cycles per second (faster)
OBJ_COWS_SUCCESS_MIN:     float = 0.80  # tighter success window — requires precision
OBJ_SCARECROW_HOLD_TIME:  float = 2.0   # seconds to hold A for the scarecrow whisper
OBJ_INTEL_DURATION:       float = 10.0  # seconds the scarecrow intel overlay stays active

TIMING_BAR_W:   int = 260
TIMING_BAR_H:   int = 24
TIMING_BAR_X:   int = (SCREEN_WIDTH - 260) // 2
TIMING_BAR_Y:   int = SCREEN_HEIGHT - 80

COLOUR_BAR_BG:      tuple[int, int, int] = ( 30,  30,  30)
COLOUR_BAR_FILL:    tuple[int, int, int] = ( 80, 200,  80)  # pigs — green
COLOUR_BAR_PEAK:    tuple[int, int, int] = (255, 220,  50)  # cows peak zone — yellow
COLOUR_BAR_WHISPER: tuple[int, int, int] = ( 80, 160, 255)  # scarecrow — blue
COLOUR_BAR_BORDER:  tuple[int, int, int] = (200, 200, 200)

# ---------------------------------------------------------------------------
# Gramps (barn NPC — win-condition anchor)
# ---------------------------------------------------------------------------
GRAMPS_WIDTH:        int = 22
GRAMPS_HEIGHT:       int = 38
GRAMPS_HEAD_RADIUS:  int = 11
GRAMPS_HEAD_OFFSET:  int =  8    # px above body top-edge to head centre
GRAMPS_BODY_COLOUR:  tuple[int, int, int] = (110,  85,  60)  # dark overalls
GRAMPS_HEAD_COLOUR:  tuple[int, int, int] = (220, 175, 130)  # warm skin
GRAMPS_HAT_COLOUR:   tuple[int, int, int] = ( 80,  55,  30)  # straw hat brim

# Gramps stands just inside the barn entrance (south-centre of barn rect)
GRAMPS_SPAWN_X: int = 1162   # MAP_BARN_RECT x=1060, w=205 → centre=1162
GRAMPS_SPAWN_Y: int = 120    # MAP_BARN_RECT y=15, h=150 → 2/3 down = ~115

# ---------------------------------------------------------------------------
# Intel mini-map overlay (shown when scarecrow intel is active)
# ---------------------------------------------------------------------------
MINIMAP_W:             int   = 192
MINIMAP_H:             int   = 108    # 192 × (720/1280) — keeps 16:9 ratio
MINIMAP_X:             int   = SCREEN_WIDTH - MINIMAP_W - 10   # right-aligned
MINIMAP_Y:             int   = 108    # below objective checklist
MINIMAP_SCALE:         float = 192.0 / SCREEN_WIDTH             # ≈ 0.15
MINIMAP_BG_COLOUR:     tuple[int, int, int] = ( 15,  15,  20)
MINIMAP_BORDER_COLOUR: tuple[int, int, int] = ( 80, 200, 255)   # cyan
MINIMAP_DEALER_COLOUR: tuple[int, int, int] = (230,  60,  60)   # red
MINIMAP_TRACTOR_COLOUR:tuple[int, int, int] = (200, 195, 190)   # light grey

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG_DRAW_HITBOXES: bool = True   # draw tractor rect outline in debug mode
DEBUG_COLOUR: tuple[int, int, int] = (255, 0, 255)
