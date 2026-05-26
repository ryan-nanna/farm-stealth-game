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
NOISE_RADIUS_SLOW:  float =  80.0   # silent-mode movement (amber)
NOISE_RADIUS_FAST:  float = 160.0   # normal movement (red)

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
# Dealer (enemy NPC)
# ---------------------------------------------------------------------------
DEALER1_WIDTH:          int   = 18
DEALER1_HEIGHT:         int   = 40
DEALER1_HEAD_RADIUS:    int   = 10
DEALER1_HEAD_OFFSET:    int   =  8    # px above body top-edge to head centre
DEALER1_SPEED_PATROL:   float = 70.0  # px/s — slow deliberate patrol
DEALER1_BODY_COLOUR:    tuple[int, int, int] = ( 55,  55,  88)  # dark blue-grey
DEALER1_HEAD_COLOUR:    tuple[int, int, int] = (200, 160, 120)  # warm skin tone

# Vision cone
VISION_CONE_RANGE:      float = 220.0  # px
VISION_CONE_HALF_ANGLE: float = 50.0   # degrees — half of total FOV (100° wide)
VISION_CONE_COLOUR:     tuple[int, int, int] = (255, 240, 100)  # warm yellow
VISION_CONE_ALPHA:      int   = 65     # 0-255

WAYPOINT_REACH_DIST:    float = 12.0   # px — close enough to "arrive" at waypoint

# Detection
PARTIAL_COVER_RANGE_MULT: float = 0.4   # vision range × this in partial cover (60% reduction)
DEALER_CATCH_DIST:        float = 40.0  # px — dealer catches tractor when this close during CHASE

# Dealer AI speeds and state timers
DEALER1_SPEED_CHASE:    float = 150.0   # px/s — roughly 2× patrol speed
DEALER_SUSPICIOUS_TIME: float = 2.0     # s in SUSPICIOUS before giving up
DEALER_ALERT_TIME:      float = 1.5     # s of continuous sight before CHASE
DEALER_CHASE_TIME:      float = 3.0     # s of active CHASE before SEARCHING
DEALER_SEARCH_TIME:     float = 3.5     # s of SEARCHING before resuming PATROL

# Dealer cone colours per alert level (PATROL uses the existing VISION_CONE_COLOUR)
DEALER_CONE_SUSPICIOUS: tuple[int, int, int] = (255, 160,  40)  # orange
DEALER_CONE_ALERT:      tuple[int, int, int] = (255,  50,  50)  # red

# Dealer 1 patrol circuit — left side of map, below stone wall
DEALER1_PATROL_WAYPOINTS: list[tuple[int, int]] = [
    (120, 680),  # entry road, bottom-left
    ( 80, 500),  # up the left edge
    ( 80, 440),  # just below wall
    (380, 440),  # along wall toward left gap
    (380, 600),  # back down right side of patrol area
]

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG_DRAW_HITBOXES: bool = True   # draw tractor rect outline in debug mode
DEBUG_COLOUR: tuple[int, int, int] = (255, 0, 255)
