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
# Debug
# ---------------------------------------------------------------------------
DEBUG_DRAW_HITBOXES: bool = True   # draw tractor rect outline in debug mode
DEBUG_COLOUR: tuple[int, int, int] = (255, 0, 255)
