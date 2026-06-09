# game/entities/scrap_truck.py
# Scrap Truck: Hubert and Hieronymus's vehicle — present every round.
# Drives a fixed patrol loop near Hubert's spawn zone. Pattern rotates
# each round so the player can't memorise it.
# No vision cone, no state machine — pure momentum and inevitability.
# Contact with the tractor = game over.

from __future__ import annotations

import math

import pygame

from game.settings import (
    SCRAP_TRUCK_BODY_COLOUR,
    SCRAP_TRUCK_BUMP_YELLOW,
    SCRAP_TRUCK_CAB_COLOUR,
    SCRAP_TRUCK_CATCH_DIST,
    SCRAP_TRUCK_HEIGHT,
    SCRAP_TRUCK_PATROL_PATTERNS,
    SCRAP_TRUCK_ROOF_COLOUR,
    SCRAP_TRUCK_SPEED,
    SCRAP_TRUCK_WIDTH,
    WAYPOINT_REACH_DIST,
    WORLD_HEIGHT,
)

# ---------------------------------------------------------------------------
# Sprite geometry  (military surplus truck, side profile facing right)
# Canvas is drawn larger than the hitbox for visual weight.
# ---------------------------------------------------------------------------
_TW, _TH = 240, 120    # canvas size (world pixels)
_GROUND   = 108        # y where wheels rest

# Colours
_C_BODY   = SCRAP_TRUCK_BODY_COLOUR          # (195, 95, 110) pink/rust
_C_CAB    = SCRAP_TRUCK_CAB_COLOUR           # (175, 82,  98) cab panels
_C_ROOF   = SCRAP_TRUCK_ROOF_COLOUR          # ( 60, 72,  46) dark olive
_C_BUMP_Y = SCRAP_TRUCK_BUMP_YELLOW          # (255, 215, 45) hazard yellow
_C_BUMP_K = ( 38,  34,  30)                  # hazard black
_C_TYRE   = ( 44,  42,  38)                  # near-black rubber
_C_RIM    = (110, 108, 102)                  # wheel rim
_C_GLASS  = ( 48,  62,  80)                  # windshield tint
_C_DARK   = ( 38,  34,  28)                  # outlines / shadows
_C_RUST   = (155,  70,  60)                  # rust streaks


def _build_sprite() -> pygame.Surface:
    """
    Draw a battered military-surplus flatbed truck facing right.
    Cab on the left, flatbed on the right, big dual rear wheels.
    Hazard-stripe bumper, dark olive cab roof, scrap pile on the bed.
    """
    surf = pygame.Surface((_TW, _TH), pygame.SRCALPHA)

    # ── 1. REAR DUAL TYRES (right side, large, drawn first — behind body) ──
    for rcx in (168, 186):
        rcy, rr = 86, 22
        pygame.draw.circle(surf, _C_TYRE, (rcx, rcy), rr)
        pygame.draw.circle(surf, (60, 57, 52), (rcx, rcy), rr, 4)
        pygame.draw.circle(surf, _C_RIM,  (rcx, rcy), rr - 7)
        for i in range(6):
            a = math.radians(i * 60 + 5)
            x1 = int(rcx + 8 * math.cos(a)); y1 = int(rcy + 8 * math.sin(a))
            x2 = int(rcx + (rr - 9) * math.cos(a)); y2 = int(rcy + (rr - 9) * math.sin(a))
            pygame.draw.line(surf, (90, 88, 84), (x1, y1), (x2, y2), 1)
        pygame.draw.circle(surf, (130, 128, 122), (rcx, rcy), 7)

    # ── 2. FLATBED / CARGO BED ────────────────────────────────────────────
    bed = pygame.Rect(86, 50, 130, 40)
    pygame.draw.rect(surf, _C_BODY, bed, border_radius=2)
    # Bed floor boards (horizontal lines)
    for by in range(bed.y + 6, bed.bottom - 4, 8):
        pygame.draw.line(surf, (168, 75, 88), (bed.x + 4, by), (bed.right - 4, by), 1)
    # Bed side rails (low walls around the bed)
    pygame.draw.rect(surf, _C_DARK, pygame.Rect(bed.x, bed.y, bed.width, 5))        # top rail
    pygame.draw.rect(surf, _C_DARK, pygame.Rect(bed.x, bed.bottom - 5, bed.width, 5))  # bottom rail
    pygame.draw.rect(surf, _C_DARK, pygame.Rect(bed.right - 5, bed.y, 5, bed.height))  # rear gate
    # Rust streaks on bed
    for rx, ry in ((94, 58), (118, 64), (145, 55), (190, 62)):
        pygame.draw.line(surf, _C_RUST, (rx, ry), (rx + 2, ry + 10), 2)

    # ── 3. SCRAP PILE on the flatbed ─────────────────────────────────────
    # A jumble of bent metal, pipes, old parts — suggested with rough polygons
    scrap_items = [
        # (x, y, w, h, colour)
        (95,  40, 28, 14, (105, 95, 82)),   # big flat panel
        (118, 36, 16, 18, ( 88, 82, 72)),   # upright chunk
        (142, 42, 22, 10, (120, 105, 88)),  # sheet
        (162, 34, 12, 20, ( 78, 75, 65)),   # tall piece
        (178, 38, 24, 14, (100, 90, 78)),   # another panel
    ]
    for sx, sy, sw, sh, sc in scrap_items:
        pygame.draw.rect(surf, sc, pygame.Rect(sx, sy, sw, sh), border_radius=2)
        pygame.draw.rect(surf, _C_DARK, pygame.Rect(sx, sy, sw, sh), 1, border_radius=2)
    # A rusty pipe sticking out the back
    pygame.draw.rect(surf, (140, 110, 80),
                     pygame.Rect(bed.right - 2, 60, 14, 6), border_radius=2)
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(bed.right - 2, 60, 14, 6), 1, border_radius=2)

    # ── 4. CAB ────────────────────────────────────────────────────────────
    cab = pygame.Rect(18, 44, 72, 46)
    pygame.draw.rect(surf, _C_CAB, cab, border_radius=4)
    # Panel line down the middle of the cab door
    pygame.draw.line(surf, (155, 68, 82), (54, 50), (54, cab.bottom - 4), 1)
    # Cab outline
    pygame.draw.rect(surf, _C_DARK, cab, 2, border_radius=4)

    # Cab ROOF (dark olive — just like the reference)
    roof = pygame.Rect(22, 28, 66, 20)
    pygame.draw.rect(surf, _C_ROOF, roof, border_radius=4)
    # Roof highlight strip
    pygame.draw.line(surf, (78, 92, 62), (26, 31), (82, 31), 1)
    pygame.draw.rect(surf, _C_DARK, roof, 2, border_radius=4)

    # Windshield (front of cab, split into two panes)
    ws = pygame.Rect(18, 33, 12, 26)
    pygame.draw.rect(surf, _C_GLASS, ws)
    pygame.draw.line(surf, _C_DARK, (ws.centerx, ws.y), (ws.centerx, ws.bottom), 1)
    pygame.draw.rect(surf, _C_DARK, ws, 1)

    # Side window
    sw_r = pygame.Rect(28, 48, 32, 20)
    pygame.draw.rect(surf, _C_GLASS, sw_r, border_radius=2)
    pygame.draw.rect(surf, _C_DARK,  sw_r, 1, border_radius=2)

    # Cab/bed join strip
    pygame.draw.rect(surf, _C_DARK, pygame.Rect(86, 44, 6, 46))

    # ── 5. FRONT GRILLE ───────────────────────────────────────────────────
    grille = pygame.Rect(6, 50, 14, 38)
    pygame.draw.rect(surf, _C_DARK, grille, border_radius=3)
    # Horizontal grille slots
    for gy in range(grille.y + 4, grille.bottom - 3, 6):
        pygame.draw.line(surf, (65, 60, 55),
                         (grille.x + 2, gy), (grille.right - 2, gy), 3)
    pygame.draw.rect(surf, (55, 50, 44), grille, 1, border_radius=3)

    # Headlights (two small round lights on the grille)
    for lx, ly in ((10, 57), (10, 74)):
        pygame.draw.circle(surf, (240, 235, 200), (lx, ly), 5)   # lens
        pygame.draw.circle(surf, _C_DARK, (lx, ly), 5, 1)

    # ── 6. FRONT BUMPER with hazard stripes ───────────────────────────────
    bump = pygame.Rect(4, 83, 16, 14)
    # Draw alternating yellow / black diagonal stripes
    stripe_w = 5
    for i in range(-2, 6):
        x1 = bump.x + i * stripe_w
        col = _C_BUMP_Y if i % 2 == 0 else _C_BUMP_K
        pts = [
            (x1,             bump.y),
            (x1 + stripe_w,  bump.y),
            (x1 + stripe_w + bump.height // 2, bump.bottom),
            (x1 + bump.height // 2,             bump.bottom),
        ]
        # Clip to bumper rect via a clipping approach (draw rect over the surface)
        pygame.draw.polygon(surf, col, pts)
    # Bumper outline to clean up the stripes
    pygame.draw.rect(surf, _C_DARK, bump, 2)

    # ── 7. EXHAUST STACK (rises from cab roof, left side) ─────────────────
    pygame.draw.rect(surf, (55, 52, 46),
                     pygame.Rect(24, 6, 7, 26), border_radius=2)
    # Cap
    pygame.draw.rect(surf, _C_DARK,
                     pygame.Rect(20, 4, 15, 5), border_radius=2)

    # ── 8. FRONT WHEEL (single, left side) ────────────────────────────────
    fcx, fcy, fr = 40, 88, 18
    pygame.draw.circle(surf, _C_TYRE, (fcx, fcy), fr)
    pygame.draw.circle(surf, (60, 57, 52), (fcx, fcy), fr, 4)
    pygame.draw.circle(surf, _C_RIM,  (fcx, fcy), fr - 6)
    for i in range(5):
        a = math.radians(i * 72 + 10)
        x1 = int(fcx + 6 * math.cos(a)); y1 = int(fcy + 6 * math.sin(a))
        x2 = int(fcx + (fr - 7) * math.cos(a)); y2 = int(fcy + (fr - 7) * math.sin(a))
        pygame.draw.line(surf, (92, 90, 86), (x1, y1), (x2, y2), 1)
    pygame.draw.circle(surf, (130, 128, 122), (fcx, fcy), 6)

    # ── 9. GROUND SHADOW ──────────────────────────────────────────────────
    shadow_surf = pygame.Surface((200, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 55), shadow_surf.get_rect())
    surf.blit(shadow_surf, (20, _GROUND + 4))

    return surf


class ScrapTruck:
    """
    Present every round. Patrols a fixed loop near Hubert's spawn zone.
    Pattern rotates each round so the player can't memorise it.
    No AI — just momentum. Catches the tractor on contact.
    """

    _sprite_cache_right: pygame.Surface | None = None
    _sprite_cache_left:  pygame.Surface | None = None

    def __init__(self, round_num: int = 1, speed: float = SCRAP_TRUCK_SPEED) -> None:
        # Pick patrol pattern for this round (cycles through available patterns)
        pattern_idx = (round_num - 1) % len(SCRAP_TRUCK_PATROL_PATTERNS)
        self._waypoints: list[tuple[int, int]] = SCRAP_TRUCK_PATROL_PATTERNS[pattern_idx]
        self._waypoint_index: int = 0

        start = self._waypoints[0]
        self.rect: pygame.Rect = pygame.Rect(
            start[0] - SCRAP_TRUCK_WIDTH  // 2,
            start[1] - SCRAP_TRUCK_HEIGHT // 2,
            SCRAP_TRUCK_WIDTH,
            SCRAP_TRUCK_HEIGHT,
        )
        self._x: float = float(self.rect.x)
        self._y: float = float(self.rect.y)

        self._speed:        float = speed
        self._facing_right: bool  = True
        self._active:       bool  = True

        self.caught_tractor: bool = False

        # Build sprite pair once; reuse across instances
        if ScrapTruck._sprite_cache_right is None:
            ScrapTruck._sprite_cache_right = _build_sprite()
            ScrapTruck._sprite_cache_left  = pygame.transform.flip(
                ScrapTruck._sprite_cache_right, True, False
            )
        self._sprite_right: pygame.Surface = ScrapTruck._sprite_cache_right
        self._sprite_left:  pygame.Surface = ScrapTruck._sprite_cache_left  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float, tractor_rect: pygame.Rect) -> None:
        self.caught_tractor = False
        if not self._active:
            return

        target = self._waypoints[self._waypoint_index]
        cx, cy = float(self.rect.centerx), float(self.rect.centery)
        dx, dy = target[0] - cx, target[1] - cy
        dist   = math.hypot(dx, dy)

        if dist <= WAYPOINT_REACH_DIST:
            self._waypoint_index = (self._waypoint_index + 1) % len(self._waypoints)
        else:
            if dx > 0:
                self._facing_right = True
            elif dx < 0:
                self._facing_right = False
            self._x += (dx / dist) * self._speed * dt
            self._y += (dy / dist) * self._speed * dt
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)

        dist_to_tractor = math.hypot(
            tractor_rect.centerx - self.rect.centerx,
            tractor_rect.centery - self.rect.centery,
        )
        if dist_to_tractor <= SCRAP_TRUCK_CATCH_DIST:
            self.caught_tractor = True

    def leave(self) -> None:
        self._active = False

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        sprite = self._sprite_right if self._facing_right else self._sprite_left
        r = sprite.get_rect(center=self.rect.center)
        surface.blit(sprite, r)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_offscreen(self) -> bool:
        return self.rect.top > WORLD_HEIGHT

    @property
    def caught_tractor(self) -> bool:
        return self._caught_tractor

    @caught_tractor.setter
    def caught_tractor(self, value: bool) -> None:
        self._caught_tractor = value

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
