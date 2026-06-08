# game/entities/scrap_truck.py
# Scrap Truck: optional Dealer 3 — hard mode only (round 3+).
# Drives a fixed clockwise perimeter loop. No vision cone, no state machine.
# Presence alone creates pressure — it blocks escape routes and runs the tractor
# over if it gets within SCRAP_TRUCK_CATCH_DIST.

from __future__ import annotations

import math
from pathlib import Path

import pygame

from game.settings import (
    COLOUR_DARK_GREY,
    COLOUR_DIRT,
    DEALER_CATCH_DIST,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SCRAP_TRUCK_BODY_COLOUR,
    SCRAP_TRUCK_CAB_COLOUR,
    SCRAP_TRUCK_CATCH_DIST,
    SCRAP_TRUCK_HEIGHT,
    SCRAP_TRUCK_SPEED,
    SCRAP_TRUCK_WAYPOINTS,
    SCRAP_TRUCK_WIDTH,
    WAYPOINT_REACH_DIST,
)

_SPRITE_PATH = Path("assets/sprites/scrap_truck.png")

# Wheel colour recycled from dirt palette — looks suitably beaten-up
_WHEEL_COLOUR = (55, 45, 35)


class ScrapTruck:
    """
    Hard-mode perimeter threat. Drives clockwise around the farm edge.
    No AI — just momentum and inevitability. Catches the tractor on contact.
    """

    def __init__(self, speed: float = SCRAP_TRUCK_SPEED) -> None:
        start = SCRAP_TRUCK_WAYPOINTS[0]
        self.rect: pygame.Rect = pygame.Rect(
            start[0] - SCRAP_TRUCK_WIDTH  // 2,
            start[1] - SCRAP_TRUCK_HEIGHT // 2,
            SCRAP_TRUCK_WIDTH,
            SCRAP_TRUCK_HEIGHT,
        )
        self._x: float = float(self.rect.x)
        self._y: float = float(self.rect.y)

        self._speed:         float = speed
        self._waypoints:     list[tuple[int, int]] = SCRAP_TRUCK_WAYPOINTS
        self._waypoint_index: int  = 0
        self._facing_angle:  float = 0.0
        self._active:        bool  = True   # set to False when round ends

        self.caught_tractor: bool = False

        self._sprite: pygame.Surface | None = None
        if _SPRITE_PATH.exists():
            raw = pygame.image.load(str(_SPRITE_PATH)).convert_alpha()
            self._sprite = pygame.transform.smoothscale(raw, (SCRAP_TRUCK_WIDTH + 20, SCRAP_TRUCK_HEIGHT + 14))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        dt: float,
        tractor_rect: pygame.Rect,
    ) -> None:
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
            self._facing_angle = math.degrees(math.atan2(dy, dx))
            self._x += (dx / dist) * self._speed * dt
            self._y += (dy / dist) * self._speed * dt
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)

        # Catch check — truck runs the tractor over on contact
        dist_to_tractor = math.hypot(
            tractor_rect.centerx - self.rect.centerx,
            tractor_rect.centery - self.rect.centery,
        )
        if dist_to_tractor <= SCRAP_TRUCK_CATCH_DIST:
            self.caught_tractor = True

    def leave(self) -> None:
        """Stop the truck at end of round (it just idles)."""
        self._active = False

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if self._sprite is not None:
            self._draw_sprite(surface)
        else:
            self._draw_shapes(surface)

    def _draw_sprite(self, surface: pygame.Surface) -> None:
        assert self._sprite is not None
        r = self._sprite.get_rect(center=self.rect.center)
        surface.blit(self._sprite, r)

    def _draw_shapes(self, surface: pygame.Surface) -> None:
        """Battered truck shape — cab + flatbed + wheels."""
        # Flatbed (rear, larger)
        flatbed = pygame.Rect(self.rect.x, self.rect.y + 6, SCRAP_TRUCK_WIDTH - 14, SCRAP_TRUCK_HEIGHT - 10)
        pygame.draw.rect(surface, SCRAP_TRUCK_BODY_COLOUR, flatbed, border_radius=2)

        # Cab (front)
        cab_w = 18
        cab_x = self.rect.right - cab_w
        cab   = pygame.Rect(cab_x, self.rect.y, cab_w, SCRAP_TRUCK_HEIGHT)
        pygame.draw.rect(surface, SCRAP_TRUCK_CAB_COLOUR, cab, border_radius=3)

        # Windshield — tiny dark rectangle on cab front
        ws = pygame.Rect(cab_x + 2, self.rect.y + 4, cab_w - 4, 10)
        pygame.draw.rect(surface, COLOUR_DARK_GREY, ws)

        # Wheels — four dark circles
        wy_top    = self.rect.y + 4
        wy_bottom = self.rect.bottom - 4
        for wx in (self.rect.x + 8, self.rect.right - 18):
            pygame.draw.circle(surface, _WHEEL_COLOUR, (wx, wy_top),    6)
            pygame.draw.circle(surface, _WHEEL_COLOUR, (wx, wy_bottom), 6)

        # Scrap pile suggestion — a few rough coloured dots on the flatbed
        for ox, oy, col in ((6, 3, (120, 100, 70)), (14, 6, (90, 80, 60)), (22, 2, (110, 95, 65))):
            pygame.draw.circle(surface, col, (flatbed.x + ox, flatbed.centery + oy), 4)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
