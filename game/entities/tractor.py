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
# Sprite geometry  — proportions tuned to a real Ferguson TE20 side profile.
# Key ratio: rear wheel diameter ≈ 85 % of bonnet length (makes it look like
# a tractor, not a car). Rear wheel dominates; bonnet is compact.
# ---------------------------------------------------------------------------
_SW, _SH = 168, 120   # sprite canvas size

# Rear wheel — large and dominant (diameter = 66 px in 120 px tall canvas)
_RCX, _RCY, _RR = 52, 82, 33   # centre-x, centre-y, tyre radius
# Ground level: _RCY + _RR = 115
_GROUND = _RCY + _RR            # 115

# Front wheel — noticeably smaller
_FCX, _FCY, _FR = 142, _GROUND - 14, 14   # cy = 101, ground = 115 ✓

# Bonnet (hood) — length 76 px, height 22 px; ratio to rear-wheel diam = 76/66 ≈ 1.15
_BON_TOP   = _RCY - _RR + 4    # 53 — slightly below wheel top
_BON_BOT   = _BON_TOP + 22     # 75
_BON_LEFT  = _RCX + 16         # 68
_BON_RIGHT = _BON_LEFT + 76    # 144

# Exhaust pipe — sits 40 % along the bonnet, rises high
_EXH_X   = _BON_LEFT + 30      # 98
_EXH_TOP = 14                  # top of pipe (tall, distinctive)

# Headlights — on the nose face, deliberately large for expression
_HL_R1 = 8    # upper headlight radius
_HL_R2 = 6    # lower headlight radius

def _hl_positions() -> tuple[tuple[int, int], tuple[int, int]]:
    nose_x   = _BON_RIGHT + 5
    nose_mid = (_BON_TOP + _BON_BOT) // 2
    return (nose_x + _HL_R1 - 2, nose_mid - 8), \
           (nose_x + _HL_R2 - 2, nose_mid + 7)

_HL_UPPER, _HL_LOWER = _hl_positions()

# ---------------------------------------------------------------------------
# Colour palette  (warm Ferguson grey + character accents)
# ---------------------------------------------------------------------------
_C_TYRE    = ( 40,  38,  34)   # near-black tyres
_C_RIM     = (138, 135, 130)   # wheel rims
_C_HUB     = (158, 155, 150)   # hub caps
_C_SPOKE   = (115, 112, 108)   # spokes
_C_BODY    = (172, 168, 160)   # main body warm grey
_C_BONNET  = (186, 182, 174)   # bonnet (slightly lighter)
_C_FENDER  = (162, 158, 152)   # mudguard/fender
_C_DARK    = ( 98,  95,  90)   # shadows, outlines
_C_EXHAUST = ( 68,  65,  60)   # exhaust pipe
_C_SEAT    = ( 84,  50,  26)   # leather seat
_C_HL_FILL = (255, 255, 255)   # headlight fill (white)
_C_PUPIL   = ( 28,  20,   8)   # dark pupil


def _arc_polygon(
    cx: int, cy: int,
    r_outer: float, r_inner: float,
    deg_start: int, deg_end: int,
    steps: int = 20,
) -> list[tuple[int, int]]:
    """
    Build a filled-arc polygon (a ring segment).
    Angles in degrees: 0=right, 90=UP on screen (using cy - r*sin convention).
    """
    pts: list[tuple[int, int]] = []
    for d in range(deg_start, deg_end + 1, max(1, (deg_end - deg_start) // steps)):
        a = math.radians(d)
        pts.append((int(cx + r_outer * math.cos(a)), int(cy - r_outer * math.sin(a))))
    for d in range(deg_end, deg_start - 1, -max(1, (deg_end - deg_start) // steps)):
        a = math.radians(d)
        pts.append((int(cx + r_inner * math.cos(a)), int(cy - r_inner * math.sin(a))))
    return pts


def _build_sprite() -> pygame.Surface:
    """
    Draw a Ferguson TE20 side profile and return a cached SRCALPHA surface.
    Drawing order: back to front.
    Headlight circles are left WHITE — pupils are drawn on top each frame.
    """
    surf = pygame.Surface((_SW, _SH), pygame.SRCALPHA)

    # ------------------------------------------------------------------
    # 1. REAR TYRE
    # ------------------------------------------------------------------
    pygame.draw.circle(surf, _C_TYRE, (_RCX, _RCY), _RR)
    # Subtle tyre sidewall ring
    pygame.draw.circle(surf, (54, 51, 47), (_RCX, _RCY), _RR, 4)

    # ------------------------------------------------------------------
    # 2. REAR MUDGUARD / FENDER
    # Thick arc over the upper portion of the rear wheel, then a flat tab
    # connecting forward to the bonnet area.
    # ------------------------------------------------------------------
    fender_out = _RR + 11
    fender_pts = _arc_polygon(_RCX, _RCY, fender_out, _RR + 1, -8, 198, 32)
    if len(fender_pts) >= 3:
        pygame.draw.polygon(surf, _C_FENDER, fender_pts)
    # Light highlight on top edge of fender — makes it read against the body
    hl_pts = _arc_polygon(_RCX, _RCY, fender_out, fender_out - 2, 15, 175, 20)
    if len(hl_pts) >= 3:
        pygame.draw.polygon(surf, (178, 175, 168), hl_pts)
    # Flat fender tab connecting toward bonnet
    pygame.draw.rect(surf, _C_FENDER,
                     pygame.Rect(_RCX + 4, _RCY - _RR - 10, 30, 14),
                     border_radius=3)

    # ------------------------------------------------------------------
    # 3. REAR WHEEL RIM + SPOKES + HUB
    # ------------------------------------------------------------------
    pygame.draw.circle(surf, _C_RIM, (_RCX, _RCY), _RR - 7)
    for i in range(6):
        a = math.radians(i * 60 + 15)
        x1 = int(_RCX + 10 * math.cos(a));  y1 = int(_RCY + 10 * math.sin(a))
        x2 = int(_RCX + (_RR - 9) * math.cos(a)); y2 = int(_RCY + (_RR - 9) * math.sin(a))
        pygame.draw.line(surf, _C_SPOKE, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(surf, _C_HUB, (_RCX, _RCY), 10)
    pygame.draw.circle(surf, _C_DARK, (_RCX, _RCY), 10, 1)

    # ------------------------------------------------------------------
    # 4. CHASSIS / BODY PLATFORM  (between the wheels)
    # ------------------------------------------------------------------
    body_top  = _RCY - _RR + 22
    body_bot  = _GROUND
    body_left = _RCX - 6
    body_right = _FCX + _FR + 2
    pygame.draw.rect(surf, _C_BODY,
                     pygame.Rect(body_left, body_top, body_right - body_left, body_bot - body_top),
                     border_radius=5)

    # ------------------------------------------------------------------
    # 5. BONNET / HOOD  (long horizontal hood, the tractor's "face")
    # ------------------------------------------------------------------
    # Slightly tapered — a touch lower at the front to match TE20 profile
    bonnet_poly = [
        (_BON_LEFT,      _BON_TOP),
        (_BON_RIGHT + 5, _BON_TOP + 5),   # front-top (slopes slightly down)
        (_BON_RIGHT + 5, _BON_BOT),        # front-bottom
        (_BON_LEFT,      _BON_BOT),        # back-bottom
    ]
    pygame.draw.polygon(surf, _C_BONNET, bonnet_poly)
    # Top highlight line
    pygame.draw.line(surf, (198, 195, 188),
                     (_BON_LEFT + 2, _BON_TOP + 1),
                     (_BON_RIGHT + 3, _BON_TOP + 6), 1)
    # Bottom shadow line
    pygame.draw.line(surf, _C_DARK,
                     (_BON_LEFT, _BON_BOT),
                     (_BON_RIGHT + 5, _BON_BOT), 1)

    # ------------------------------------------------------------------
    # 6. EXHAUST PIPE
    # ------------------------------------------------------------------
    pipe_h = _BON_TOP - _EXH_TOP + 6
    pygame.draw.rect(surf, _C_EXHAUST,
                     pygame.Rect(_EXH_X, _EXH_TOP, 5, pipe_h), border_radius=1)
    # Flared cap
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(_EXH_X - 3, _EXH_TOP - 3, 11, 5), border_radius=3)

    # ------------------------------------------------------------------
    # 7. SEAT
    # ------------------------------------------------------------------
    seat_cx = _RCX + 14
    seat_cy = body_top - 6
    pygame.draw.ellipse(surf, _C_SEAT,
                        pygame.Rect(seat_cx - 12, seat_cy - 5, 24, 11))
    # Seat post
    pygame.draw.line(surf, _C_DARK,
                     (seat_cx + 2, seat_cy + 5), (seat_cx + 4, body_top), 2)

    # ------------------------------------------------------------------
    # 8. FRONT TYRE + RIM + HUB
    # ------------------------------------------------------------------
    pygame.draw.circle(surf, _C_TYRE, (_FCX, _FCY), _FR)
    pygame.draw.circle(surf, (54, 51, 47), (_FCX, _FCY), _FR, 2)
    pygame.draw.circle(surf, _C_RIM, (_FCX, _FCY), _FR - 3)
    pygame.draw.circle(surf, _C_HUB, (_FCX, _FCY), 5)
    pygame.draw.circle(surf, _C_DARK, (_FCX, _FCY), 5, 1)

    # ------------------------------------------------------------------
    # 9. RADIATOR / NOSE (front face of bonnet)
    # ------------------------------------------------------------------
    nose_x   = _BON_RIGHT + 4
    nose_top = _BON_TOP + 5
    nose_bot = _BON_BOT - 1
    nose_h   = nose_bot - nose_top
    # Grill face
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(nose_x, nose_top, 9, nose_h), border_radius=3)
    # Horizontal grill lines
    for gy in range(nose_top + 3, nose_bot - 2, 4):
        pygame.draw.line(surf, (78, 75, 70), (nose_x + 1, gy), (nose_x + 7, gy), 1)

    # ------------------------------------------------------------------
    # 10. HEADLIGHTS  (white circles — pupils drawn on top each frame)
    # ------------------------------------------------------------------
    pygame.draw.circle(surf, _C_HL_FILL, _HL_UPPER, _HL_R1)
    pygame.draw.circle(surf, _C_HL_FILL, _HL_LOWER, _HL_R2)
    # Thin outline so they read against the dark nose
    pygame.draw.circle(surf, _C_DARK, _HL_UPPER, _HL_R1, 1)
    pygame.draw.circle(surf, _C_DARK, _HL_LOWER, _HL_R2, 1)

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
    Player-controlled tractor. Procedurally drawn as a TE20 side profile.
    Static geometry is pre-baked into a cached surface at init; only the
    animated headlight pupils are redrawn each frame.
    """

    # Cache the static sprite at class level so multiple Tractor instances
    # (e.g. across rounds) don't re-draw it every time.
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

        # Build (or reuse) the cached static sprite surface
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

        # Keep HAPPY visible for its full duration
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
        # Noise ring (behind tractor)
        if self.noise_colour is not None and self.noise_radius > 0:
            pulse_r = max(1, int(self.noise_radius + math.sin(self._pulse) * 8))
            pygame.draw.circle(surface, self.noise_colour, self.rect.center, pulse_r, 2)

        # Static tractor sprite — centred on hitbox
        sprite_rect = self._sprite.get_rect(center=self.rect.center)
        surface.blit(self._sprite, sprite_rect)

        # Animated pupils on top of headlights
        hl_u = (sprite_rect.x + _HL_UPPER[0], sprite_rect.y + _HL_UPPER[1])
        hl_l = (sprite_rect.x + _HL_LOWER[0], sprite_rect.y + _HL_LOWER[1])
        self._draw_pupils(surface, hl_u, hl_l)

        # Cover ring
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
            pr = pr if pr >= 0 else max(1, r - 2)
            pygame.draw.circle(surface, _C_PUPIL, (pos[0] + ox, pos[1] + oy), pr)

        def glint(pos: tuple[int, int]) -> None:
            """Tiny white highlight on pupil — makes eyes feel alive."""
            pygame.draw.circle(surface, _C_HL_FILL, (pos[0] - 2, pos[1] - 2), 1)

        if self.eye_state == EyeState.NORMAL:
            # Pupil fills ~half the headlight so white ring is clearly visible
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, pr=max(1, r - 4))
                glint(pos)

        elif self.eye_state == EyeState.NERVOUS:
            # Pupils dart side to side — hide-and-peek
            dart = int(math.sin(t * 7.0) * (r1 - 3))
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, ox=dart, pr=max(1, r - 4))
                glint((pos[0] + dart, pos[1]))

        elif self.eye_state == EyeState.WIDE:
            # Tiny pinpoint pupils — wide-eyed fear
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, pr=2)
                glint(pos)

        elif self.eye_state == EyeState.FOCUSED:
            # Pupils shift inward — determined concentration
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pupil(pos, r, ox=-2, pr=max(1, r - 4))
                glint((pos[0] - 2, pos[1]))

        elif self.eye_state == EyeState.HAPPY:
            # Crescent scrunch — draw pupil then mask top half with white
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                pr = max(2, r - 3)
                pygame.draw.circle(surface, _C_PUPIL, pos, pr)
                pygame.draw.circle(surface, _C_HL_FILL, (pos[0], pos[1] - pr + 1), pr)

        elif self.eye_state == EyeState.SHOCKED:
            # Jitter in panic
            for pos, r in ((hl_u, r1), (hl_l, r2)):
                jx = random.randint(-(r - 3), r - 3)
                jy = random.randint(-(r - 3), r - 3)
                pupil(pos, r, ox=jx, oy=jy, pr=max(1, r - 4))
                glint((pos[0] + jx, pos[1] + jy))

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
