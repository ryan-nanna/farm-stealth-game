# game/entities/tractor.py
# Tractor: the player-controlled entity.
# Drawn entirely in code as a Ferguson TE20 in left-quarter front view.
# Both headlights face the player — pupils animate per EyeState each frame.

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
    WORLD_HEIGHT,
    WORLD_WIDTH,
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
# Sprite geometry  (Ferguson TE20 — left-quarter front view)
#
# Camera sits low and slightly left of the tractor's front-right corner.
# We see: the full front face (both headlights face-on), the left side wall
# of the bonnet, the big left rear wheel, and the steering wheel above.
# This angle makes the eye mechanic feel natural — both headlights look
# straight at the player like a pair of eyes.
# ---------------------------------------------------------------------------
_SW, _SH = 260, 185   # sprite canvas (world pixels; ~130×93 on screen at 0.5×)

# ── Left rear wheel (dominant feature, left side) ───────────────────────
_RCX, _RCY, _RR = 64, 126, 52    # centre-x, centre-y, outer radius

# ── Right rear wheel (partially visible behind body, smaller in perspective) ─
_R2CX, _R2CY, _R2R = 196, 132, 40

# ── Front wheels ────────────────────────────────────────────────────────
_FLX, _FLY, _FLR = 106, 157, 20  # front-left  (small)
_FRX, _FRY, _FRR = 174, 159, 22  # front-right (slightly bigger, slightly further)

# ── Front face of the bonnet (what faces the viewer) ────────────────────
_FF_L, _FF_R = 144, 222          # left / right x of front face
_FF_T, _FF_B = 76,  162          # top  / bottom y of front face

# ── Bonnet body (behind front face, going left toward rear wheel) ────────
_BON_BACK = 90                   # x where bonnet rear meets fender

# ── Steering wheel (above bonnet, very prominent on open-cab tractor) ───
_SW_CX, _SW_CY, _SW_R = 148, 54, 22

# ── Exhaust pipe (rises from near-top of bonnet, left of front face) ────
_EXH_X   = 136
_EXH_TOP = 10

# ── Headlights — SIDE BY SIDE on the front face, no overlap ────────────
# Both the same radius so pupils look symmetric (like two eyes).
# Variable names kept for draw() / _draw_pupils() compatibility.
_HL_R1 = 14   # left  headlight radius  (was "upper")
_HL_R2 = 14   # right headlight radius  (was "lower")

# Face is _FF_L(144) → _FF_R(222) = 78px wide.
# Each headlight diameter = 28px.  Two = 56px.  Remaining = 22px.
# Layout: 6px margin | 28px HL | 10px gap | 28px HL | 6px margin  (= 78px ✓)
_HL_UPPER = (_FF_L + 6  + _HL_R1,  _FF_T + 28)   # left  headlight  → (164, 104)
_HL_LOWER = (_FF_L + 44 + _HL_R2,  _FF_T + 28)   # right headlight  → (202, 104)

# Headlight positions for the horizontally-flipped left-facing sprite.
# Flip formula: new_x = _SW - 1 - old_x  (canvas width 260)
_HL_UPPER_FLIP = (_SW - 1 - _HL_LOWER[0], _HL_LOWER[1])  # 57,  104
_HL_LOWER_FLIP = (_SW - 1 - _HL_UPPER[0], _HL_UPPER[1])  # 95,  104

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
    Draw the TE20 in left-quarter front view on a cached SRCALPHA surface.
    Camera is low and slightly left of the tractor's front-right corner.
    Both headlights face the viewer — pupils animate on top each frame.
    """
    surf = pygame.Surface((_SW, _SH), pygame.SRCALPHA)

    # ---------------------------------------------------------------
    # 1.  RIGHT REAR WHEEL  (drawn first — sits behind the body)
    # ---------------------------------------------------------------
    pygame.draw.circle(surf, _C_TYRE, (_R2CX, _R2CY), _R2R)
    pygame.draw.circle(surf, (56, 53, 48), (_R2CX, _R2CY), _R2R, 4)
    r2_rim = _R2R - 8
    pygame.draw.circle(surf, _C_RIM, (_R2CX, _R2CY), r2_rim)
    for i in range(6):
        a = math.radians(i * 60 + 10)
        x1 = int(_R2CX + 9 * math.cos(a));        y1 = int(_R2CY + 9 * math.sin(a))
        x2 = int(_R2CX + (r2_rim - 2) * math.cos(a)); y2 = int(_R2CY + (r2_rim - 2) * math.sin(a))
        pygame.draw.line(surf, _C_SPOKE, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(surf, _C_HUB, (_R2CX, _R2CY), 10)
    pygame.draw.circle(surf, _C_DARK, (_R2CX, _R2CY), 10, 1)

    # ---------------------------------------------------------------
    # 2.  MAIN CHASSIS / BODY BLOCK
    #     Viewed from the left-quarter: we see the left side wall and
    #     the front corner.  Body spans from rear-wheel area to front face.
    # ---------------------------------------------------------------
    body_top = _FF_T
    body_bot = _FF_B

    # Left side wall (in shadow — facing left/away from viewer slightly)
    left_wall = [
        (_BON_BACK,  body_top),
        (_FF_L,      body_top),
        (_FF_L,      body_bot),
        (_BON_BACK,  body_bot),
    ]
    pygame.draw.polygon(surf, _C_TRANS, left_wall)
    # Shadow line along bottom of left wall
    pygame.draw.line(surf, _C_DARK,
                     (_BON_BACK, body_bot), (_FF_L, body_bot), 2)

    # Transmission / gearbox hump visible on the top-left of the body
    tx_rect = pygame.Rect(_BON_BACK + 8, body_top + 2, 38, 18)
    pygame.draw.rect(surf, _C_BODY, tx_rect, border_radius=5)
    pygame.draw.rect(surf, _C_DARK, tx_rect, 1, border_radius=5)

    # Rear axle housing — rounded protrusion on the lower-left body
    axle_r = pygame.Rect(_BON_BACK + 4, body_bot - 30, 30, 26)
    pygame.draw.rect(surf, _C_DARK, axle_r, border_radius=6)
    pygame.draw.rect(surf, _C_TRANS, axle_r.inflate(-6, -6), border_radius=4)

    # ---------------------------------------------------------------
    # 3.  LEFT REAR FENDER  (mudguard — arc over left rear wheel)
    # ---------------------------------------------------------------
    fender_out = _RR + 13
    fpts = _arc_polygon(_RCX, _RCY, fender_out, _RR + 1, -15, 205, 32)
    if len(fpts) >= 3:
        pygame.draw.polygon(surf, _C_FENDER, fpts)
    # Top-edge highlight
    hpts = _arc_polygon(_RCX, _RCY, fender_out - 1, fender_out - 3, 12, 185, 20)
    if len(hpts) >= 3:
        pygame.draw.polygon(surf, (178, 175, 168), hpts)
    # Flat tab bridging fender to body
    pygame.draw.rect(surf, _C_FENDER,
                     pygame.Rect(_RCX + 10, _RCY - _RR - 12, 34, 16), border_radius=3)

    # ---------------------------------------------------------------
    # 4.  LEFT REAR TYRE  (dominant left-side element)
    # ---------------------------------------------------------------
    pygame.draw.circle(surf, _C_TYRE, (_RCX, _RCY), _RR)
    pygame.draw.circle(surf, (56, 53, 48), (_RCX, _RCY), _RR, 5)
    pygame.draw.circle(surf, (50, 48, 44), (_RCX, _RCY), _RR - 5, 2)
    # Tread lugs on the visible arc
    for deg in range(-110, 70, 18):
        a = math.radians(deg)
        x1 = int(_RCX + (_RR - 4) * math.cos(a))
        y1 = int(_RCY + (_RR - 4) * math.sin(a))
        x2 = int(_RCX + (_RR + 3) * math.cos(a))
        y2 = int(_RCY + (_RR + 3) * math.sin(a))
        pygame.draw.line(surf, (60, 57, 52), (x1, y1), (x2, y2), 4)
    # Rim + spokes + hub
    rim_r = _RR - 8
    pygame.draw.circle(surf, _C_RIM, (_RCX, _RCY), rim_r)
    for i in range(6):
        a = math.radians(i * 60 + 20)
        x1 = int(_RCX + 12 * math.cos(a));       y1 = int(_RCY + 12 * math.sin(a))
        x2 = int(_RCX + (rim_r - 2) * math.cos(a)); y2 = int(_RCY + (rim_r - 2) * math.sin(a))
        pygame.draw.line(surf, _C_SPOKE, (x1, y1), (x2, y2), 2)
    pygame.draw.circle(surf, _C_HUB, (_RCX, _RCY), 12)
    pygame.draw.circle(surf, _C_DARK, (_RCX, _RCY), 12, 1)

    # ---------------------------------------------------------------
    # 5.  BONNET / HOOD
    #     In left-quarter view we see:
    #       • Top surface — thin parallelogram, catches light from above
    #       • Left side wall — in shadow
    # ---------------------------------------------------------------
    # Top surface (slight angle shows depth)
    bon_top_pts = [
        (_BON_BACK + 6,  _FF_T),
        (_FF_L,          _FF_T),
        (_FF_L,          _FF_T + 8),
        (_BON_BACK + 6,  _FF_T + 8),
    ]
    pygame.draw.polygon(surf, _C_BONNET, bon_top_pts)
    # Top highlight stripe
    pygame.draw.line(surf, (205, 202, 196),
                     (_BON_BACK + 8, _FF_T + 1), (_FF_L - 2, _FF_T + 1), 1)

    # Left side wall (in shadow)
    bon_side_pts = [
        (_BON_BACK + 6,  _FF_T + 8),
        (_FF_L,          _FF_T + 8),
        (_FF_L,          _FF_B - 10),
        (_BON_BACK + 6,  _FF_B - 10),
    ]
    pygame.draw.polygon(surf, _C_DARK, bon_side_pts)
    # Bottom shadow line
    pygame.draw.line(surf, _C_DARK,
                     (_BON_BACK + 6, _FF_B - 10), (_FF_L, _FF_B - 10), 2)

    # ---------------------------------------------------------------
    # 6.  FRONT FACE  (the "face" of the tractor — slightly trapezoidal
    #     because we're looking at it from a few degrees to the left)
    # ---------------------------------------------------------------
    face_pts = [
        (_FF_L,     _FF_T),
        (_FF_R,     _FF_T + 4),
        (_FF_R,     _FF_B),
        (_FF_L,     _FF_B),
    ]
    pygame.draw.polygon(surf, _C_BODY, face_pts)

    # Radiator grille (lower half of front face — horizontal slats)
    grill_top = _FF_T + 55         # sits below the headlights
    grill_bot = _FF_B - 6
    grill_w   = _FF_R - _FF_L - 12
    for gy in range(grill_top, grill_bot, 7):
        pygame.draw.line(surf, _C_DARK,
                         (_FF_L + 6, gy), (_FF_R - 6, gy + 1), 4)
    # Grille surround
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(_FF_L + 4, grill_top - 2, grill_w + 2, grill_bot - grill_top + 4),
                     2, border_radius=3)

    # Ferguson badge — small red bar between headlights and grille
    badge_cx = (_FF_L + _FF_R) // 2
    badge_y  = _FF_T + 50
    pygame.draw.rect(surf, (172, 30, 30),
                     pygame.Rect(badge_cx - 22, badge_y, 44, 7), border_radius=2)
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(badge_cx - 22, badge_y, 44, 7), 1, border_radius=2)

    # Front face outline
    pygame.draw.polygon(surf, _C_DARK, face_pts, 2)

    # ---------------------------------------------------------------
    # 7.  HEADLIGHT BEZELS  (chrome rings — pupils drawn each frame)
    # ---------------------------------------------------------------
    for pos, r in ((_HL_UPPER, _HL_R1), (_HL_LOWER, _HL_R2)):
        pygame.draw.circle(surf, (148, 145, 140), pos, r + 3)   # chrome outer bezel
        pygame.draw.circle(surf, (100, 97, 92),   pos, r + 3, 1) # bezel edge
        pygame.draw.circle(surf, _C_HL_FILL,       pos, r)        # white lens

    # ---------------------------------------------------------------
    # 8.  EXHAUST PIPE  (rises above front face, slightly left of centre)
    # ---------------------------------------------------------------
    pipe_h = _FF_T - _EXH_TOP + 6
    pygame.draw.rect(surf, _C_EXHAUST,
                     pygame.Rect(_EXH_X, _EXH_TOP, 6, pipe_h), border_radius=2)
    # Flared cap
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(_EXH_X - 4, _EXH_TOP - 4, 14, 6), border_radius=3)
    # Clamp ring at base
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(_EXH_X - 2, _FF_T + 2, 10, 4), border_radius=2)

    # ---------------------------------------------------------------
    # 9.  STEERING COLUMN + WHEEL
    # ---------------------------------------------------------------
    col_bx = _SW_CX + 8
    col_by = _FF_T + 6
    pygame.draw.line(surf, _C_DARK, (col_bx, col_by), (_SW_CX, _SW_CY + _SW_R), 3)
    # Rim
    pygame.draw.circle(surf, _C_STEER_RIM, (_SW_CX, _SW_CY), _SW_R, 5)
    # 3 spokes (front-quarter view — angles shifted slightly)
    for spoke_angle in (50, 170, 290):
        a = math.radians(spoke_angle)
        sx = int(_SW_CX + _SW_R * math.cos(a))
        sy = int(_SW_CY + _SW_R * math.sin(a))
        pygame.draw.line(surf, _C_DARK, (_SW_CX, _SW_CY), (sx, sy), 2)
    pygame.draw.circle(surf, _C_DARK, (_SW_CX, _SW_CY), 5)

    # ---------------------------------------------------------------
    # 10. SEAT  (visible between steering wheel and fender)
    # ---------------------------------------------------------------
    seat_cx = _SW_CX - 18
    seat_cy = _FF_T - 4
    pygame.draw.ellipse(surf, _C_SEAT,
                        pygame.Rect(seat_cx - 14, seat_cy - 5, 28, 12))
    # Spring post
    pygame.draw.line(surf, _C_DARK,
                     (seat_cx, seat_cy + 5), (seat_cx + 5, _FF_T + 2), 3)

    # ---------------------------------------------------------------
    # 11. FRONT WHEELS  (left and right, at bottom-centre)
    # ---------------------------------------------------------------
    for cx, cy, fr in ((_FLX, _FLY, _FLR), (_FRX, _FRY, _FRR)):
        pygame.draw.circle(surf, _C_TYRE, (cx, cy), fr)
        pygame.draw.circle(surf, (56, 53, 48), (cx, cy), fr, 3)
        pygame.draw.circle(surf, _C_RIM,  (cx, cy), fr - 4)
        pygame.draw.circle(surf, _C_HUB,  (cx, cy), 6)
        pygame.draw.circle(surf, _C_DARK, (cx, cy), 6, 1)

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

    _sprite_cache_right: pygame.Surface | None = None
    _sprite_cache_left:  pygame.Surface | None = None

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

        # Facing direction — drives which sprite + headlight coords to use
        self._facing_right: bool = True

        if Tractor._sprite_cache_right is None:
            Tractor._sprite_cache_right = _build_sprite()
            Tractor._sprite_cache_left  = pygame.transform.flip(
                Tractor._sprite_cache_right, True, False
            )
        self._sprite_right: pygame.Surface = Tractor._sprite_cache_right
        self._sprite_left:  pygame.Surface = Tractor._sprite_cache_left  # type: ignore[assignment]

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

        # Update facing direction from horizontal input; vertical-only keeps last facing
        if dx > 0:
            self._facing_right = True
        elif dx < 0:
            self._facing_right = False

        magnitude = math.hypot(dx, dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude

        self._x = max(0.0, min(self._x + dx * speed * dt, WORLD_WIDTH  - TRACTOR_WIDTH))
        self.rect.x = int(self._x)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dx > 0:   self.rect.right = wall.left
                elif dx < 0: self.rect.left  = wall.right
                self._x = float(self.rect.x)

        self._y = max(0.0, min(self._y + dy * speed * dt, WORLD_HEIGHT - TRACTOR_HEIGHT))
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

        # Choose sprite and matching headlight canvas-coords based on facing direction
        if self._facing_right:
            sprite  = self._sprite_right
            hl_u_c  = _HL_UPPER
            hl_l_c  = _HL_LOWER
        else:
            sprite  = self._sprite_left
            hl_u_c  = _HL_UPPER_FLIP
            hl_l_c  = _HL_LOWER_FLIP

        sprite_rect = sprite.get_rect(center=self.rect.center)
        surface.blit(sprite, sprite_rect)

        hl_u = (sprite_rect.x + hl_u_c[0], sprite_rect.y + hl_u_c[1])
        hl_l = (sprite_rect.x + hl_l_c[0], sprite_rect.y + hl_l_c[1])
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
