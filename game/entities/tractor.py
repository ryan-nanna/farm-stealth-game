# game/entities/tractor.py
# Tractor: the player-controlled entity.
# Drawn entirely in code as a recognisable Ferguson TE20 side profile.
# Large expressive headlights are the emotional core — pupils animate per game state.

from __future__ import annotations

import math
import random
from enum import Enum, auto

import pygame

from game.settings import (
    COLOUR_COVER_FULL,
    COLOUR_COVER_PARTIAL,
    COLOUR_NOISE_FAST,
    COLOUR_NOISE_SLOW,
    COLOUR_NOISE_STILL,
    DEBUG_COLOUR,
    DEBUG_DRAW_HITBOXES,
    NOISE_RADIUS_FAST,
    NOISE_RADIUS_SLOW,
    NOISE_RADIUS_STILL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TRACTOR_COVER_RING_WIDTH,
    TRACTOR_EYE_HAPPY_DURATION,
    TRACTOR_HEIGHT,
    TRACTOR_SPEED_NORMAL,
    TRACTOR_SPEED_SILENT,
    TRACTOR_SPAWN_X,
    TRACTOR_SPAWN_Y,
    TRACTOR_WIDTH,
)
from game.systems.collision import check_cover
from game.systems.input import Action, InputState

# ---------------------------------------------------------------------------
# Sprite geometry  (Ferguson TE20 side profile, facing right)
#
# Key proportions from real TE20:
#   rear wheel diameter / overall height  ≈ 55 %
#   rear wheel diameter / bonnet length   ≈ 80 %
#   front wheel diameter / rear           ≈ 40 %
#   steering wheel radius                 ≈ half of bonnet height — very prominent
# ---------------------------------------------------------------------------
_SW, _SH = 264, 165   # sprite canvas — wide/tall enough for full wheel + headlights

# Ground line (both wheels rest here)
_GROUND = 152

# Rear wheel — large and fully visible, no clipping
_RCX, _RCY, _RR = 60, 108, 44   # centre, tyre radius  (bottom = 152 ✓, top = 64)

# Front wheel — noticeably smaller (real ratio ~0.40)
_FCX = 195
_FR  = 18
_FCY = _GROUND - _FR            # 134

# Bonnet / hood  (length ≈ 112 px, height ≈ 26 px)
_BON_LEFT  = _RCX + 26          # 86  — starts where fender meets body
_BON_RIGHT = _FCX + _FR - 4     # 209
_BON_TOP   = _RCY - _RR + 14   # 78  — sits comfortably below wheel top
_BON_BOT   = _BON_TOP + 26     # 104

# Exhaust pipe — rises tall from mid-bonnet
_EXH_X   = _BON_LEFT + 38      # 124
_EXH_TOP = 18                  # very top of canvas

# Steering wheel (the defining visual of an old tractor)
_SW_CX = _BON_LEFT + 10        # 96  — set back on the bonnet
_SW_CY = _BON_TOP - 22         # 56  — well above bonnet top
_SW_R  = 24                    # large! visible from far away

# Headlights — DOUBLED from previous version, on the nose face
_HL_R1 = 16   # upper / primary headlight
_HL_R2 = 12   # lower / secondary headlight

def _hl_positions() -> tuple[tuple[int, int], tuple[int, int]]:
    nose_x  = _BON_RIGHT + 6
    mid_y   = (_BON_TOP + _BON_BOT) // 2
    upper   = (nose_x + _HL_R1 - 3, mid_y - 12)
    lower   = (nose_x + _HL_R2 - 2, mid_y + 11)
    return upper, lower

_HL_UPPER, _HL_LOWER = _hl_positions()

# ---------------------------------------------------------------------------
# Colour palette  (warm Ferguson grey)
# ---------------------------------------------------------------------------
_C_TYRE      = ( 42,  40,  36)   # near-black tyres
_C_RIM       = (138, 135, 130)   # wheel rims
_C_HUB       = (160, 157, 152)   # hub caps
_C_SPOKE     = (112, 109, 105)   # spokes
_C_BODY      = (170, 166, 158)   # main chassis warm grey
_C_TRANS     = (155, 151, 144)   # transmission housing (slightly darker)
_C_BONNET    = (188, 184, 176)   # bonnet (lighter — catches light on top)
_C_FENDER    = (158, 155, 148)   # mudguard/fender
_C_DARK      = ( 92,  89,  84)   # shadows, outlines, dark metal
_C_EXHAUST   = ( 65,  62,  57)   # exhaust pipe (dark metal)
_C_SEAT      = ( 82,  48,  22)   # worn leather seat
_C_STEER_RIM = (125, 122, 117)   # steering wheel rim (dark bakelite)
_C_HL_FILL   = (255, 255, 255)   # headlight fill — white holes for pupils
_C_PUPIL     = ( 28,  20,   8)   # dark pupil colour


def _arc_polygon(
    cx: int, cy: int,
    r_outer: float, r_inner: float,
    deg_start: int, deg_end: int,
    steps: int = 24,
) -> list[tuple[int, int]]:
    """
    Filled arc polygon.  Angles: 0=right, 90=UP on screen (cy − r·sin).
    """
    pts: list[tuple[int, int]] = []
    span = deg_end - deg_start
    step = max(1, span // steps)
    for d in range(deg_start, deg_end + 1, step):
        a = math.radians(d)
        pts.append((int(cx + r_outer * math.cos(a)), int(cy - r_outer * math.sin(a))))
    for d in range(deg_end, deg_start - 1, -step):
        a = math.radians(d)
        pts.append((int(cx + r_inner * math.cos(a)), int(cy - r_inner * math.sin(a))))
    return pts


def _build_sprite() -> pygame.Surface:
    """
    Draw the TE20 side profile onto a cached SRCALPHA surface.
    Rear wheel is fully visible top-to-bottom.
    Steering wheel is prominent above the bonnet.
    Headlights are large — pupils drawn on top each frame.
    """
    surf = pygame.Surface((_SW, _SH), pygame.SRCALPHA)

    # ---------------------------------------------------------------
    # 1.  REAR TYRE  (large, fully visible)
    # ---------------------------------------------------------------
    pygame.draw.circle(surf, _C_TYRE, (_RCX, _RCY), _RR)
    # Tyre sidewall bead ring
    pygame.draw.circle(surf, (56, 53, 48), (_RCX, _RCY), _RR, 5)
    # Inner shoulder line
    pygame.draw.circle(surf, (50, 48, 44), (_RCX, _RCY), _RR - 5, 2)

    # ---------------------------------------------------------------
    # 2.  REAR MUDGUARD / FENDER
    #     Wide arc over the upper wheel, connecting to the body.
    #     Drawn before the rim so it sits behind the wheel face.
    # ---------------------------------------------------------------
    fender_out = _RR + 12
    fpts = _arc_polygon(_RCX, _RCY, fender_out, _RR + 1, -10, 200, 32)
    if len(fpts) >= 3:
        pygame.draw.polygon(surf, _C_FENDER, fpts)
    # Top-edge highlight
    hpts = _arc_polygon(_RCX, _RCY, fender_out - 1, fender_out - 3, 10, 175, 20)
    if len(hpts) >= 3:
        pygame.draw.polygon(surf, (175, 172, 165), hpts)
    # Flat tab forward — bridges fender to bonnet
    pygame.draw.rect(surf, _C_FENDER,
                     pygame.Rect(_RCX + 6, _RCY - _RR - 11, 32, 16), border_radius=4)

    # ---------------------------------------------------------------
    # 3.  REAR WHEEL RIM + 6 SPOKES + HUB
    # ---------------------------------------------------------------
    rim_r = _RR - 8
    pygame.draw.circle(surf, _C_RIM, (_RCX, _RCY), rim_r)
    for i in range(6):
        a = math.radians(i * 60 + 15)
        x1 = int(_RCX + 11 * math.cos(a));      y1 = int(_RCY + 11 * math.sin(a))
        x2 = int(_RCX + (rim_r - 2) * math.cos(a)); y2 = int(_RCY + (rim_r - 2) * math.sin(a))
        pygame.draw.line(surf, _C_SPOKE, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(surf, _C_HUB,  (_RCX, _RCY), 11)
    pygame.draw.circle(surf, _C_DARK, (_RCX, _RCY), 11, 1)

    # ---------------------------------------------------------------
    # 4.  CHASSIS / BODY  (not a flat rectangle — has shape)
    #     Shows:  side rail, rear axle housing, transmission hump
    # ---------------------------------------------------------------
    body_top   = _RCY - _RR + 28   # 80 — sits below the fender
    body_bot   = _GROUND            # 152
    body_left  = _RCX - 10
    body_right = _FCX + _FR + 2

    # Main body polygon — tapers at front to show axle geometry
    chassis_pts = [
        (body_left,          body_top + 4),
        (_BON_LEFT - 4,      body_top),          # rises to meet bonnet
        (body_right,         body_top + 8),      # front corner
        (body_right,         body_bot - 10),     # front-bottom
        (body_right - 22,    body_bot - 6),      # front axle step
        (body_left + 22,     body_bot - 6),      # rear axle step
        (body_left,          body_bot - 12),     # rear lower
    ]
    pygame.draw.polygon(surf, _C_BODY, chassis_pts)

    # Transmission / gearbox hump — distinctive rounded box in mid-body
    tx  = _RCX + 28
    ty  = body_top + 2
    tw, th = 42, body_bot - body_top - 20
    pygame.draw.rect(surf, _C_TRANS,
                     pygame.Rect(tx, ty, tw, th), border_radius=6)
    # Side detail line on trans housing
    pygame.draw.line(surf, _C_DARK,
                     (tx + 4, ty + 4), (tx + 4, ty + th - 4), 1)

    # Footboard step (operator's footrest, visible on the side)
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(body_left + 14, body_bot - 8, 28, 5), border_radius=2)

    # ---------------------------------------------------------------
    # 5.  BONNET / HOOD
    #     Rounded top, tapers slightly toward nose, raised at engine end
    # ---------------------------------------------------------------
    # Main bonnet polygon — slightly higher at the rear (engine hump)
    bonnet_pts = [
        (_BON_LEFT,         _BON_TOP + 4),       # rear-base (meets body)
        (_BON_LEFT + 4,     _BON_TOP),            # rear-top shoulder
        (_BON_RIGHT - 6,    _BON_TOP + 3),        # front-top (slopes down)
        (_BON_RIGHT + 2,    _BON_TOP + 10),       # nose shoulder
        (_BON_RIGHT + 2,    _BON_BOT),            # nose-bottom
        (_BON_LEFT,         _BON_BOT),            # rear-bottom
    ]
    pygame.draw.polygon(surf, _C_BONNET, bonnet_pts)
    # Top highlight
    pygame.draw.line(surf, (200, 197, 190),
                     (_BON_LEFT + 5, _BON_TOP + 1),
                     (_BON_RIGHT - 5, _BON_TOP + 4), 1)
    # Underside shadow line
    pygame.draw.line(surf, _C_DARK,
                     (_BON_LEFT, _BON_BOT),
                     (_BON_RIGHT + 2, _BON_BOT), 1)
    # Engine cover panel line (horizontal seam near rear of bonnet)
    pygame.draw.line(surf, _C_DARK,
                     (_BON_LEFT + 4, _BON_TOP + 12),
                     (_BON_LEFT + 36, _BON_TOP + 14), 1)

    # ---------------------------------------------------------------
    # 6.  EXHAUST PIPE  (tall, with flared cap)
    # ---------------------------------------------------------------
    pipe_h = _BON_TOP - _EXH_TOP + 8
    pygame.draw.rect(surf, _C_EXHAUST,
                     pygame.Rect(_EXH_X, _EXH_TOP, 6, pipe_h), border_radius=2)
    # Flared cap
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(_EXH_X - 4, _EXH_TOP - 4, 14, 6), border_radius=3)
    # Pipe clamp ring on bonnet
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(_EXH_X - 2, _BON_TOP + 4, 10, 4), border_radius=2)

    # ---------------------------------------------------------------
    # 7.  STEERING COLUMN + STEERING WHEEL
    #     The most recognisable feature of a vintage open-cab tractor.
    # ---------------------------------------------------------------
    # Column — angled toward driver
    col_base_x = _SW_CX + 6
    col_base_y = _BON_TOP + 4
    pygame.draw.line(surf, _C_DARK,
                     (col_base_x, col_base_y),
                     (_SW_CX, _SW_CY + _SW_R), 3)

    # Steering wheel rim (thick ring — bakelite/metal)
    pygame.draw.circle(surf, _C_STEER_RIM, (_SW_CX, _SW_CY), _SW_R, 4)
    # 3 spokes visible from the side
    for spoke_angle in (60, 180, 300):
        a = math.radians(spoke_angle)
        sx = int(_SW_CX + _SW_R * math.cos(a))
        sy = int(_SW_CY + _SW_R * math.sin(a))
        pygame.draw.line(surf, _C_DARK, (_SW_CX, _SW_CY), (sx, sy), 2)
    # Hub
    pygame.draw.circle(surf, _C_DARK, (_SW_CX, _SW_CY), 5)

    # ---------------------------------------------------------------
    # 8.  SEAT
    # ---------------------------------------------------------------
    seat_cx = _SW_CX - 12
    seat_cy = _BON_TOP - 6
    # Seat pan
    pygame.draw.ellipse(surf, _C_SEAT,
                        pygame.Rect(seat_cx - 14, seat_cy - 6, 28, 14))
    # Seat spring post
    pygame.draw.line(surf, _C_DARK,
                     (seat_cx, seat_cy + 6), (seat_cx + 4, _BON_TOP + 2), 3)

    # ---------------------------------------------------------------
    # 9.  FRONT TYRE + RIM + HUB
    # ---------------------------------------------------------------
    pygame.draw.circle(surf, _C_TYRE, (_FCX, _FCY), _FR)
    pygame.draw.circle(surf, (56, 53, 48), (_FCX, _FCY), _FR, 3)
    pygame.draw.circle(surf, _C_RIM, (_FCX, _FCY), _FR - 4)
    pygame.draw.circle(surf, _C_HUB, (_FCX, _FCY), 6)
    pygame.draw.circle(surf, _C_DARK, (_FCX, _FCY), 6, 1)

    # ---------------------------------------------------------------
    # 10. RADIATOR / NOSE FACE
    # ---------------------------------------------------------------
    nose_x   = _BON_RIGHT + 2
    nose_top = _BON_TOP + 9
    nose_bot = _BON_BOT
    nose_h   = nose_bot - nose_top
    # Nose face — slightly curved front
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(nose_x, nose_top, 12, nose_h), border_radius=4)
    # Horizontal grill slots
    for gy in range(nose_top + 4, nose_bot - 4, 5):
        pygame.draw.line(surf, (72, 69, 64),
                         (nose_x + 2, gy), (nose_x + 9, gy), 2)
    # Grill surround outline
    pygame.draw.rect(surf, (78, 75, 70),
                     pygame.Rect(nose_x, nose_top, 12, nose_h), 1, border_radius=4)

    # ---------------------------------------------------------------
    # 11. HEADLIGHTS  (large white circles — pupils drawn each frame)
    # ---------------------------------------------------------------
    for pos, r in ((_HL_UPPER, _HL_R1), (_HL_LOWER, _HL_R2)):
        # Outer ring (chrome bezel)
        pygame.draw.circle(surf, (145, 142, 138), pos, r + 2)
        # White lens
        pygame.draw.circle(surf, _C_HL_FILL, pos, r)

    return surf


# ---------------------------------------------------------------------------
# Eye state enum
# ---------------------------------------------------------------------------

class EyeState(Enum):
    NORMAL    = auto()   # forward-facing, engaged
    NERVOUS   = auto()   # hidden — pupils dart side to side
    WIDE      = auto()   # dealer alert/close — pupils shrink to pinpoints
    FOCUSED   = auto()   # completing objective — pupils shift inward
    HAPPY     = auto()   # objective complete — eyes scrunch into crescents
    SHOCKED   = auto()   # caught — pupils jitter in panic


# ---------------------------------------------------------------------------
# Tractor entity
# ---------------------------------------------------------------------------

class Tractor:
    """
    Player-controlled tractor. Procedurally drawn TE20 side profile.
    Static geometry is pre-baked into a cached surface; only the animated
    headlight pupils are redrawn each frame.
    """

    _sprite_cache: pygame.Surface | None = None

    def __init__(self) -> None:
        self.rect: pygame.Rect = pygame.Rect(
            TRACTOR_SPAWN_X, TRACTOR_SPAWN_Y, TRACTOR_WIDTH, TRACTOR_HEIGHT,
        )
        self._x: float = float(TRACTOR_SPAWN_X)
        self._y: float = float(TRACTOR_SPAWN_Y)

        self.silent_mode: bool      = False
        self.is_hidden: bool        = False
        self.in_partial_cover: bool = False
        self.noise_radius: float    = 0.0
        self.noise_colour: tuple[int, int, int] | None = None

        self._pulse: float = 0.0

        self.eye_state: EyeState = EyeState.NORMAL
        self._eye_timer: float   = 0.0
        self._happy_timer: float = 0.0

        if Tractor._sprite_cache is None:
            Tractor._sprite_cache = _build_sprite()
        self._sprite: pygame.Surface = Tractor._sprite_cache

    # ------------------------------------------------------------------
    # Eye state — set by main.py each frame
    # ------------------------------------------------------------------

    def set_eye_state(self, state: EyeState) -> None:
        if state == EyeState.HAPPY:
            self._happy_timer = TRACTOR_EYE_HAPPY_DURATION
        if state != self.eye_state:
            self.eye_state  = state
            self._eye_timer = 0.0

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        input_state: InputState,
        dt: float,
        wall_rects: list[pygame.Rect],
        full_cover_rects: list[pygame.Rect],
        partial_cover_rects: list[pygame.Rect],
    ) -> None:
        self.silent_mode = input_state.is_held(Action.B)
        self._eye_timer += dt
        self._pulse      += dt * 4.0

        if self._happy_timer > 0.0:
            self._happy_timer -= dt
            self.eye_state = EyeState.HAPPY

        speed     = TRACTOR_SPEED_SILENT if self.silent_mode else TRACTOR_SPEED_NORMAL
        dx, dy    = input_state.move_vector
        is_moving = dx != 0.0 or dy != 0.0

        magnitude = math.hypot(dx, dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude

        self._x = max(0.0, min(self._x + dx * speed * dt, SCREEN_WIDTH  - TRACTOR_WIDTH))
        self.rect.x = int(self._x)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dx > 0:   self.rect.right = wall.left
                elif dx < 0: self.rect.left  = wall.right
                self._x = float(self.rect.x)

        self._y = max(0.0, min(self._y + dy * speed * dt, SCREEN_HEIGHT - TRACTOR_HEIGHT))
        self.rect.y = int(self._y)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dy > 0:   self.rect.bottom = wall.top
                elif dy < 0: self.rect.top    = wall.bottom
                self._y = float(self.rect.y)

        self.is_hidden, self.in_partial_cover = check_cover(
            self.rect, full_cover_rects, partial_cover_rects
        )

        if self.is_hidden and not is_moving:
            self.noise_radius = 0.0
            self.noise_colour = None
        elif is_moving:
            if self.silent_mode:
                self.noise_radius = NOISE_RADIUS_SLOW
                self.noise_colour = COLOUR_NOISE_SLOW
            else:
                self.noise_radius = NOISE_RADIUS_FAST
                self.noise_colour = COLOUR_NOISE_FAST
        else:
            self.noise_radius = NOISE_RADIUS_STILL
            self.noise_colour = COLOUR_NOISE_STILL

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if self.noise_colour is not None and self.noise_radius > 0:
            pulse_r = max(1, int(self.noise_radius + math.sin(self._pulse) * 8))
            pygame.draw.circle(surface, self.noise_colour, self.rect.center, pulse_r, 2)

        sprite_rect = self._sprite.get_rect(center=self.rect.center)
        surface.blit(self._sprite, sprite_rect)

        hl_u = (sprite_rect.x + _HL_UPPER[0], sprite_rect.y + _HL_UPPER[1])
        hl_l = (sprite_rect.x + _HL_LOWER[0], sprite_rect.y + _HL_LOWER[1])
        self._draw_pupils(surface, hl_u, hl_l)

        if self.is_hidden:
            pygame.draw.rect(surface, COLOUR_COVER_FULL, self.rect,
                             TRACTOR_COVER_RING_WIDTH, border_radius=4)
        elif self.in_partial_cover:
            pygame.draw.rect(surface, COLOUR_COVER_PARTIAL, self.rect,
                             TRACTOR_COVER_RING_WIDTH, border_radius=4)

        if DEBUG_DRAW_HITBOXES:
            pygame.draw.rect(surface, DEBUG_COLOUR, self.rect, 1)

    def _draw_pupils(
        self,
        surface: pygame.Surface,
        hl_u: tuple[int, int],
        hl_l: tuple[int, int],
    ) -> None:
        t  = self._eye_timer
        r1 = _HL_R1
        r2 = _HL_R2

        def pupil(pos: tuple[int, int], r: int, ox: int = 0, oy: int = 0,
                  pr: int = -1) -> None:
            pr = pr if pr >= 0 else max(2, r - 6)
            pygame.draw.circle(surface, _C_PUPIL, (pos[0] + ox, pos[1] + oy), pr)

        def glint(pos: tuple[int, int], ox: int = 0, oy: int = 0) -> None:
            pygame.draw.circle(surface, _C_HL_FILL,
                               (pos[0] + ox - 3, pos[1] + oy - 3), 2)

        if self.eye_state == EyeState.NORMAL:
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r)
                glint(pos)

        elif self.eye_state == EyeState.NERVOUS:
            dart = int(math.sin(t * 7.0) * (r1 - 5))
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, ox=dart)
                glint(pos, ox=dart)

        elif self.eye_state == EyeState.WIDE:
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, pr=3)
                glint(pos)

        elif self.eye_state == EyeState.FOCUSED:
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, ox=-3)
                glint(pos, ox=-3)

        elif self.eye_state == EyeState.HAPPY:
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pr = max(3, r - 5)
                pygame.draw.circle(surface, _C_PUPIL, pos, pr)
                # Crescent: mask top half with white
                pygame.draw.circle(surface, _C_HL_FILL,
                                   (pos[0], pos[1] - pr + 2), pr)

        elif self.eye_state == EyeState.SHOCKED:
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                jx = random.randint(-(r - 6), r - 6)
                jy = random.randint(-(r - 6), r - 6)
                pupil(pos, r, ox=jx, oy=jy, pr=max(2, r - 8))
                glint(pos, ox=jx, oy=jy)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
