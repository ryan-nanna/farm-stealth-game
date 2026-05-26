# game/entities/dealer.py
# Dealer: the enemy villain NPC.
# Session 4 scope: PATROL state only — follows waypoints, draws a vision cone.
# Detection logic (SUSPICIOUS / ALERT / CHASE / SEARCHING) added in Session 5.

from __future__ import annotations

import math

import pygame

from game.settings import (
    DEALER1_BODY_COLOUR,
    DEALER1_HEAD_COLOUR,
    DEALER1_HEAD_OFFSET,
    DEALER1_HEAD_RADIUS,
    DEALER1_HEIGHT,
    DEALER1_SPEED_PATROL,
    DEALER1_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VISION_CONE_ALPHA,
    VISION_CONE_COLOUR,
    VISION_CONE_HALF_ANGLE,
    VISION_CONE_RANGE,
    WAYPOINT_REACH_DIST,
)


class Dealer:
    """
    Enemy NPC that patrols a fixed waypoint circuit and casts a vision cone.

    waypoints — list of (x, y) screen positions forming a closed patrol loop.
    The dealer starts at waypoints[0] and advances through them in order,
    wrapping back to index 0 after the last point.
    """

    def __init__(self, waypoints: list[tuple[int, int]]) -> None:
        start = waypoints[0]
        self.rect: pygame.Rect = pygame.Rect(
            start[0] - DEALER1_WIDTH  // 2,
            start[1] - DEALER1_HEIGHT // 2,
            DEALER1_WIDTH,
            DEALER1_HEIGHT,
        )
        self._x: float = float(self.rect.x)
        self._y: float = float(self.rect.y)

        self.waypoints: list[tuple[int, int]] = waypoints
        self._waypoint_index: int = 0

        # Degrees; 0 = right, 90 = down — initialised toward first target
        self._facing_angle: float = 0.0

        # Reused each frame to composite the semi-transparent cone without
        # allocating a new surface on every draw call.
        self._vision_surf: pygame.Surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        target      = self.waypoints[self._waypoint_index]
        tx, ty      = float(target[0]), float(target[1])
        cx, cy      = float(self.rect.centerx), float(self.rect.centery)
        dx, dy      = tx - cx, ty - cy
        dist        = math.hypot(dx, dy)

        if dist <= WAYPOINT_REACH_DIST:
            self._waypoint_index = (self._waypoint_index + 1) % len(self.waypoints)
        else:
            self._facing_angle = math.degrees(math.atan2(dy, dx))
            self._x += (dx / dist) * DEALER1_SPEED_PATROL * dt
            self._y += (dy / dist) * DEALER1_SPEED_PATROL * dt
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_vision_cone(surface)
        self._draw_body(surface)

    def _draw_vision_cone(self, surface: pygame.Surface) -> None:
        self._vision_surf.fill((0, 0, 0, 0))

        origin    = self.rect.center
        angle_rad = math.radians(self._facing_angle)
        half_rad  = math.radians(VISION_CONE_HALF_ANGLE)

        # Fan of points from origin out to range along the cone arc
        arc_steps = 14
        points    = [origin]
        for i in range(arc_steps + 1):
            t  = -half_rad + (2 * half_rad * i / arc_steps)
            a  = angle_rad + t
            points.append((
                origin[0] + math.cos(a) * VISION_CONE_RANGE,
                origin[1] + math.sin(a) * VISION_CONE_RANGE,
            ))

        pygame.draw.polygon(self._vision_surf, (*VISION_CONE_COLOUR, VISION_CONE_ALPHA), points)
        surface.blit(self._vision_surf, (0, 0))

    def _draw_body(self, surface: pygame.Surface) -> None:
        # Body — tall narrow rectangle
        pygame.draw.rect(surface, DEALER1_BODY_COLOUR, self.rect, border_radius=4)

        # Head — circle above the body
        head_center = (self.rect.centerx, self.rect.y - DEALER1_HEAD_OFFSET)
        pygame.draw.circle(surface, DEALER1_HEAD_COLOUR, head_center, DEALER1_HEAD_RADIUS)

        # Eyes — two small dots offset in the facing direction
        eye_rad = math.radians(self._facing_angle)
        for side in (-0.4, 0.4):
            ex = int(head_center[0] + math.cos(eye_rad + side) * 5)
            ey = int(head_center[1] + math.sin(eye_rad + side) * 5)
            pygame.draw.circle(surface, (30, 30, 30), (ex, ey), 2)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
