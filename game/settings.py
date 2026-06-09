# settings.py
# Single source of truth for every magic number in the project.
# Import this module wherever you need a constant — never hardcode values elsewhere.

# ---------------------------------------------------------------------------
# Display — viewport stays 1280×720; the game world is 2×
# ---------------------------------------------------------------------------
SCREEN_WIDTH:  int = 1280   # actual window / viewport size
SCREEN_HEIGHT: int = 720
WORLD_WIDTH:   int = 2560   # scrollable game-world size
WORLD_HEIGHT:  int = 1440
WINDOW_TITLE:  str = "Farm Stealth"
TARGET_FPS:    int = 60

# ---------------------------------------------------------------------------
# Colours  (R, G, B)
# Pulled from the toy-box art palette: warm greys, sky blue, saturated greens
# ---------------------------------------------------------------------------
COLOUR_SKY_BLUE:       tuple[int, int, int] = (135, 196, 235)
COLOUR_GRASS_GREEN:    tuple[int, int, int] = (108, 178,  45)   # warm yellow-green grass
COLOUR_DARK_GREEN:     tuple[int, int, int] = ( 68, 130,  30)   # shadow/border green
COLOUR_WARM_GREY:      tuple[int, int, int] = (160, 155, 148)
COLOUR_LIGHT_GREY:     tuple[int, int, int] = (210, 207, 202)
COLOUR_DARK_GREY:      tuple[int, int, int] = ( 68,  62,  56)
COLOUR_BARN_RED:       tuple[int, int, int] = (212,  46,  46)   # vivid barn red
COLOUR_WHEAT:          tuple[int, int, int] = (218, 182,  78)
COLOUR_DIRT:           tuple[int, int, int] = (208, 172, 102)   # warm golden-sandy dirt
COLOUR_WHITE:          tuple[int, int, int] = (255, 255, 255)
COLOUR_BLACK:          tuple[int, int, int] = (  0,   0,   0)

# Farm structure colours — art-pass palette
COLOUR_ROOF_DARK:      tuple[int, int, int] = ( 88,  68,  48)   # dark wood/slate roof
COLOUR_ROOF_SILVER:    tuple[int, int, int] = (198, 203, 215)   # metal standing-seam roof
COLOUR_BARN_FENCE:     tuple[int, int, int] = ( 32,  28,  25)   # near-black board fence
COLOUR_FENCE_POST:     tuple[int, int, int] = (122,  82,  40)   # dark wood fence post
COLOUR_TREE_HIGHLIGHT: tuple[int, int, int] = ( 88, 178,  55)   # bright sunlit canopy
COLOUR_TREE_SHADOW:    tuple[int, int, int] = ( 35, 102,  22)   # canopy underside shadow
COLOUR_STONE_MORTAR:   tuple[int, int, int] = (102,  97,  90)   # mortar between stones

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
TRACTOR_SPEED_NORMAL: float = 360.0   # px/s — doubled for 2× world
TRACTOR_SPEED_SILENT: float = 160.0
TRACTOR_BODY_COLOUR:         tuple[int, int, int] = COLOUR_WARM_GREY
TRACTOR_HEADLIGHT_COLOUR:    tuple[int, int, int] = (255, 240, 140)
TRACTOR_WHEEL_COLOUR:        tuple[int, int, int] = ( 50,  48,  44)
TRACTOR_WHEEL_RADIUS:        int = 7
TRACTOR_COVER_RING_WIDTH:    int = 3

# Noise radii — doubled for 2× world
NOISE_RADIUS_STILL: float = 100.0
NOISE_RADIUS_SLOW:  float = 190.0
NOISE_RADIUS_FAST:  float = 420.0

# Objective completion noise burst
OBJ_BURST_RADIUS:   float = 560.0
OBJ_BURST_DURATION: float = 1.5

TRACTOR_EYE_HAPPY_DURATION: float = 0.8   # seconds

# Starting position — just outside the barn fence gate (south side)
TRACTOR_SPAWN_X: int = 2280
TRACTOR_SPAWN_Y: int = 620

# ---------------------------------------------------------------------------
# Input — axis / button deadzone
# ---------------------------------------------------------------------------
AXIS_DEADZONE: float = 0.25

CONTROLLER_AXIS_X: int = 0
CONTROLLER_AXIS_Y: int = 1

CONTROLLER_BUTTON_A:      int = 1
CONTROLLER_BUTTON_B:      int = 0
CONTROLLER_BUTTON_START:  int = 9
CONTROLLER_BUTTON_SELECT: int = 8

# ---------------------------------------------------------------------------
# Farm Map — zone positions as (x, y, width, height) tuples
# All coordinates are in world space (2560×1440).
# ---------------------------------------------------------------------------

# Safe zone / win condition — outer fence yard (top-right)
# Touching this rect when all objectives complete = WIN
MAP_BARN_RECT:         tuple[int, int, int, int] = (1960,  10, 600, 560)
# Solid barn building — impassable wall collision
MAP_BARN_BODY_RECT:    tuple[int, int, int, int] = (2060,  10, 460, 420)

# Objective zone 2 — cow pasture (top-left)
MAP_COW_PASTURE_RECT:  tuple[int, int, int, int] = (  30,  30, 500, 350)

# Full-cover hiding spots
MAP_APPLE_TREE_RECT:   tuple[int, int, int, int] = (1110,  40, 200, 200)
MAP_OAK_TREE_RECT:     tuple[int, int, int, int] = (  60, 430, 220, 220)
MAP_CHICKEN_COOP_RECT: tuple[int, int, int, int] = (  70,1050, 330, 240)
MAP_OLD_SHED_RECT:     tuple[int, int, int, int] = (1070,1030, 370, 280)
MAP_PIG_PEN_RECT:      tuple[int, int, int, int] = (2120, 960, 420, 390)  # objective 1

# Partial-cover / objective zones
MAP_SCARECROW_RECT:    tuple[int, int, int, int] = (1200, 510, 110, 160)  # objective 3
MAP_WELL_RECT:         tuple[int, int, int, int] = (1550,1060, 180, 130)

# New full-cover hiding spots (balances the tougher Hubert)
MAP_HAY_BALE_1_RECT:   tuple[int, int, int, int] = (1640, 450, 120,  90)  # mid-right, crossing cover
MAP_HAY_BALE_2_RECT:   tuple[int, int, int, int] = ( 660,1170, 130,  95)  # bottom-centre
MAP_SILO_RECT:         tuple[int, int, int, int] = (1840,  30, 100, 130)  # near barn (left of fence)

# Decorative / additional cover elements
MAP_SHEEP_PEN_RECT:    tuple[int, int, int, int] = ( 380, 430, 280, 220)  # mid-left, partial cover
MAP_POND_RECT:         tuple[int, int, int, int] = (1380, 820, 200, 130)  # below wall, partial cover
MAP_ORCHARD_TREE_1:    tuple[int, int, int, int] = ( 780,  40, 140, 140)  # top-centre orchard
MAP_ORCHARD_TREE_2:    tuple[int, int, int, int] = ( 960,  40, 140, 140)
MAP_EXTRA_OAK_RECT:    tuple[int, int, int, int] = (1820,1150, 180, 180)  # bottom-right cover

# Colour additions
COLOUR_POND:           tuple[int, int, int] = ( 88, 162, 218)   # water blue
COLOUR_SHEEP:          tuple[int, int, int] = (238, 235, 228)   # off-white wool

# Stone wall — three segments across mid-map at y=740.
# Passage gaps: x=530–870 (340 px) and x=1770–2070 (300 px).
MAP_WALL_LEFT_RECT:    tuple[int, int, int, int] = (   0, 740, 530,  60)
MAP_WALL_CENTRE_RECT:  tuple[int, int, int, int] = ( 870, 740, 900,  60)
MAP_WALL_RIGHT_RECT:   tuple[int, int, int, int] = (2070, 740, 490,  60)

# Dirt paths through the wall gaps
MAP_PATH_LEFT_RECT:    tuple[int, int, int, int] = ( 580, 380, 220, 370)
MAP_PATH_RIGHT_RECT:   tuple[int, int, int, int] = (1750, 330, 230, 680)

# Dealer entry road (bottom of world)
MAP_ENTRY_Y:           int = 1360
MAP_ENTRY_HEIGHT:      int = 60

# ---------------------------------------------------------------------------
# Farm Map — feature colours
# ---------------------------------------------------------------------------
COLOUR_STONE:          tuple[int, int, int] = (158, 152, 142)
COLOUR_TREE_TRUNK:     tuple[int, int, int] = (118,  82,  46)
COLOUR_TREE_CANOPY:    tuple[int, int, int] = ( 52, 135,  38)
COLOUR_PASTURE:        tuple[int, int, int] = (118, 198,  75)
COLOUR_PIG_PEN:        tuple[int, int, int] = (188, 158, 118)
COLOUR_FENCE:          tuple[int, int, int] = (172, 128,  68)
COLOUR_SHED:           tuple[int, int, int] = (148, 122,  88)
COLOUR_COOP:           tuple[int, int, int] = (200, 175, 130)
COLOUR_WELL:           tuple[int, int, int] = (115, 105,  92)
COLOUR_WOOD_DARK:      tuple[int, int, int] = ( 92,  62,  32)

COLOUR_COVER_FULL:     tuple[int, int, int] = (  0, 200,   0)
COLOUR_COVER_PARTIAL:  tuple[int, int, int] = (200, 200,   0)

# ---------------------------------------------------------------------------
# Hubert (Dealer 1)
# ---------------------------------------------------------------------------
HUBERT_WIDTH:          int   = 16
HUBERT_HEIGHT:         int   = 46
HUBERT_HEAD_RADIUS:    int   = 10
HUBERT_HEAD_OFFSET:    int   =  8
HUBERT_SPEED_LURK:     float = 210.0   # ~50% harder than launch
HUBERT_SPEED_CHASE:    float = 420.0
HUBERT_SPRITE_W:       int   = 90
HUBERT_SPRITE_H:       int   = 110

HUBERT_BODY_COLOUR:       tuple[int, int, int] = ( 90, 120, 165)
HUBERT_HEAD_COLOUR:       tuple[int, int, int] = (200, 160, 120)
HUBERT_HAIR_COLOUR:       tuple[int, int, int] = ( 75,  42,  22)
HUBERT_HAT_BRIM_COLOUR:   tuple[int, int, int] = (175, 158, 112)
HUBERT_HAT_CROWN_COLOUR:  tuple[int, int, int] = (148, 132,  88)

VISION_CONE_RANGE:      float = 620.0   # ~50% harder
VISION_CONE_HALF_ANGLE: float = 60.0   # wider cone
VISION_CONE_COLOUR:     tuple[int, int, int] = (255, 240, 100)
VISION_CONE_ALPHA:      int   = 65

WAYPOINT_REACH_DIST:    float = 24.0    # doubled
PARTIAL_COVER_RANGE_MULT: float = 0.4
DEALER_CATCH_DIST:        float = 80.0  # doubled

HUBERT_CURIOUS_TIME:  float = 3.0
DEALER_ALERT_TIME:    float = 1.5
DEALER_CHASE_TIME:    float = 3.0
DEALER_SEARCH_TIME:   float = 3.5

ESCALATION_SPEED_PER_ROUND:  float = 20.0   # doubled
ESCALATION_VISION_PER_ROUND: float = 36.0   # doubled
ESCALATION_MAX_ROUNDS:       int   = 5

HUBERT_CONE_CURIOUS:    tuple[int, int, int] = (255, 160,  40)
DEALER_CONE_ALERT:      tuple[int, int, int] = (255,  50,  50)

# Hubert lurk waypoints (world coords, 2× scale)
HUBERT_LURK_WAYPOINTS: list[tuple[int, int]] = [
    ( 240, 1300),
    ( 180,  960),
    ( 400,  840),
    ( 340,  580),
    ( 980,  400),
    (1260,  640),
    (1800,  840),
    (2160, 1180),
    (1280, 1140),
    ( 760, 1060),
]

# ---------------------------------------------------------------------------
# Hieronymus (Dealer 2)
# ---------------------------------------------------------------------------
HIERONYMUS_WIDTH:          int   = 18
HIERONYMUS_HEIGHT:         int   = 36
HIERONYMUS_HEAD_RADIUS:    int   =  9
HIERONYMUS_HEAD_OFFSET:    int   =  8
HIERONYMUS_SPEED_LURK:     float = 210.0   # doubled
HIERONYMUS_SPEED_CHASE:    float = 390.0
HIERONYMUS_BODY_COLOUR:    tuple[int, int, int] = ( 70,  50,  90)
HIERONYMUS_HEAD_COLOUR:    tuple[int, int, int] = (200, 160, 120)
HIERONYMUS_SOCK_GREEN:     tuple[int, int, int] = ( 55, 180,  75)
HIERONYMUS_SOCK_RED:       tuple[int, int, int] = (205,  50,  50)

HIERONYMUS_VISION_RANGE:      float = 340.0   # doubled
HIERONYMUS_VISION_HALF_ANGLE: float = 32.0
HIERONYMUS_SNIFF_DIST:        float = 400.0   # doubled
HIERONYMUS_CURIOUS_TIME:      float = 2.5

HIERONYMUS_SPRITE_W: int = 110
HIERONYMUS_SPRITE_H: int = 130

# Hieronymus lurk waypoints (world coords, 2× scale, right-side focus)
HIERONYMUS_LURK_WAYPOINTS: list[tuple[int, int]] = [
    (2320, 1300),
    (2200,  980),
    (1880,  880),
    (2120,  620),
    (1560,  400),
    (1280,  660),
    ( 880,  900),
    ( 700, 1120),
    (1300, 1140),
    (2160, 1110),
]

# ---------------------------------------------------------------------------
# Scrap Truck (Dealer 3 — hard mode)
# ---------------------------------------------------------------------------
SCRAP_TRUCK_SPEED:       float = 200.0
SCRAP_TRUCK_WIDTH:       int   = 90     # hitbox (sprite is drawn larger)
SCRAP_TRUCK_HEIGHT:      int   = 55
SCRAP_TRUCK_CATCH_DIST:  float = 120.0  # large — truck is big

# Art colours (pink/rust military surplus, inspired by reference image)
SCRAP_TRUCK_BODY_COLOUR: tuple[int, int, int] = (195,  95, 110)   # distressed pink
SCRAP_TRUCK_CAB_COLOUR:  tuple[int, int, int] = (175,  82,  98)   # cab (slightly darker)
SCRAP_TRUCK_ROOF_COLOUR: tuple[int, int, int] = ( 60,  72,  46)   # dark olive roof
SCRAP_TRUCK_BUMP_YELLOW: tuple[int, int, int] = (255, 215,  45)   # hazard stripe yellow

# Patrol patterns — one per round (cycles when exhausted).
# All patterns start near Hubert's spawn zone (bottom-left area).
# Deliberately stay below the stone wall — truck is too big for the gaps.
SCRAP_TRUCK_PATROL_PATTERNS: list[list[tuple[int, int]]] = [
    # Round 1 — tight loop, bottom-left quarter
    [(350, 1200), (720, 1310), (640, 1060), (280, 1020)],
    # Round 2 — wider bottom sweep, more of the lower map
    [(350, 1200), (1080, 1310), (940, 1020), (560, 960), (240, 1040)],
    # Round 3 — crosses mid-map through left wall gap
    [(350, 1200), (500, 1310), (480, 880), (800, 780), (820, 1060), (500, 1280)],
    # Round 4 — large lower-map loop creating real pressure
    [(350, 1200), (1400, 1320), (1500, 980), (960, 820), (480, 900), (280, 1100)],
]

# Legacy single-waypoint list (kept for any old references)
SCRAP_TRUCK_WAYPOINTS: list[tuple[int, int]] = SCRAP_TRUCK_PATROL_PATTERNS[0]

# ---------------------------------------------------------------------------
# Objectives and TimingBar
# ---------------------------------------------------------------------------
OBJ_PIGS_HOLD_TIME:       float = 2.5
OBJ_COWS_OSCILLATE_SPEED: float = 1.0
OBJ_COWS_SUCCESS_MIN:     float = 0.80
OBJ_SCARECROW_HOLD_TIME:  float = 2.0
OBJ_INTEL_DURATION:       float = 10.0

TIMING_BAR_W:   int = 260
TIMING_BAR_H:   int = 24
TIMING_BAR_X:   int = (SCREEN_WIDTH - 260) // 2
TIMING_BAR_Y:   int = SCREEN_HEIGHT - 80

COLOUR_BAR_BG:      tuple[int, int, int] = ( 30,  30,  30)
COLOUR_BAR_FILL:    tuple[int, int, int] = ( 80, 200,  80)
COLOUR_BAR_PEAK:    tuple[int, int, int] = (255, 220,  50)
COLOUR_BAR_WHISPER: tuple[int, int, int] = ( 80, 160, 255)
COLOUR_BAR_BORDER:  tuple[int, int, int] = (200, 200, 200)

# ---------------------------------------------------------------------------
# Gramps (barn NPC — win-condition anchor)
# ---------------------------------------------------------------------------
GRAMPS_WIDTH:        int = 22
GRAMPS_HEIGHT:       int = 38
GRAMPS_HEAD_RADIUS:  int = 11
GRAMPS_HEAD_OFFSET:  int =  8
GRAMPS_BODY_COLOUR:  tuple[int, int, int] = (110,  85,  60)
GRAMPS_HEAD_COLOUR:  tuple[int, int, int] = (220, 175, 130)
GRAMPS_HAT_COLOUR:   tuple[int, int, int] = ( 80,  55,  30)

# Gramps stands in the yard in front of the barn doors
GRAMPS_SPAWN_X: int = 2290
GRAMPS_SPAWN_Y: int = 490

# ---------------------------------------------------------------------------
# Intel mini-map overlay
# ---------------------------------------------------------------------------
MINIMAP_W:              int   = 192
MINIMAP_H:              int   = 108
MINIMAP_X:              int   = SCREEN_WIDTH - MINIMAP_W - 10
MINIMAP_Y:              int   = 108
MINIMAP_SCALE:          float = 192.0 / WORLD_WIDTH   # maps world→minimap x coords
MINIMAP_BG_COLOUR:      tuple[int, int, int] = ( 15,  15,  20)
MINIMAP_BORDER_COLOUR:  tuple[int, int, int] = ( 80, 200, 255)
MINIMAP_DEALER_COLOUR:  tuple[int, int, int] = (230,  60,  60)
MINIMAP_TRACTOR_COLOUR: tuple[int, int, int] = (200, 195, 190)

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG_DRAW_HITBOXES: bool = False
DEBUG_COLOUR: tuple[int, int, int] = (255, 0, 255)
