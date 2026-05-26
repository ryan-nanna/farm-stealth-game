# game/entities/dealer.py
# Dealer: the enemy villain NPC.
# Runs a 5-state machine: PATROL → SUSPICIOUS → ALERT → CHASE → SEARCHING.
# LEAVING is stubbed for Session 7 (round-won exit animation).

from __future__ import annotations

import math
from enum import Enum, auto

import pygame

from game.settings import (
    DEALER1_BODY_COLOUR,
    DEALER1_HEAD_COLOUR,
    DEALER1_HEAD_OFFSET,
    DEALER1_HEAD_RADIUS,
    DEALER1_HEIGHT,
    DEALER1_SPEED_CHASE,
    DEALER1_SPEED_PATROL,
    DEALER1_WIDTH,
    DEALER_ALERT_TIME,
    DEALER_CATCH_DIST,
    DEALER_CHASE_TIME,
    DEALER_CONE_ALERT,
    DEALER_CONE_SUSPICIOUS,
    DEALER_SEARCH_TIME,
    DEALER_SUSPICIOUS_TIME,
    PARTIAL_COVER_RANGE_MULT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VISION_CONE_ALPHA,
    VISION_CONE_COLOUR,
    VISION_CONE_HALF_ANGLE,
    VISION_CONE_RANGE,
    WAYPOINT_REACH_DIST,
    MAP_ENTRY_Y,
)
from game.systems.detection import dealer_hears_noise, tractor_in_cone
from game.systems.state_machine import StateMachine


class DealerState(Enum):
    PATROL     = auto()
    SUSPICIOUS = auto()
    ALERT      = auto()
    CHASE      = auto()
    SEARCHING  = auto()
    LEAVING    = auto()   # stubbed — used in Session 7


class Dealer:
    """
    Enemy NPC. Patrols a waypoint circuit and reacts to tractor sightings and
    noise via a 5-state machine. Sets caught_tractor=True when it gets close
    enough to the tractor during CHASE.
    """

    def __init__(
        self,
        waypoints:    list[tuple[int, int]],
        patrol_speed: float = DEALER1_SPEED_PATROL,
        chase_speed:  float = DEALER1_SPEED_CHASE,
        vision_range: float = VISION_CONE_RANGE,
    ) -> None:
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
        self._facing_angle: float = 0.0

        self._patrol_speed: float = patrol_speed
        self._chase_speed:  float = chase_speed
        self._vision_range: float = vision_range

        self._sm: StateMachine[DealerState] = StateMachine(DealerState.PATROL)

        # Positions remembered across state transitions
        self._suspicious_target: tuple[int, int] = start
        self._last_seen:         tuple[int, int] = start

        # Set to True for exactly one frame when the dealer catches the tractor
        self.caught_tractor: bool = False

        self._vision_surf: pygame.Surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        dt: float,
        tractor_rect: pygame.Rect,
        tractor_noise_radius: float,
        full_cover_rects: list[pygame.Rect],
        partial_cover_rects: list[pygame.Rect],
    ) -> None:
        self.caught_tractor = False
        self._sm.tick(dt)

        tractor_center = tractor_rect.center
        dealer_center  = self.rect.center

        can_see = tractor_in_cone(
            dealer_center,
            self._facing_angle,
            self._vision_range,
            VISION_CONE_HALF_ANGLE,
            tractor_rect,
            full_cover_rects,
            partial_cover_rects,
            PARTIAL_COVER_RANGE_MULT,
        )
        # Green (still) noise is cosmetic — dealers only react to amber/red.
        # tractor_noise_radius is 0 when hidden+still, NOISE_RADIUS_STILL when
        # just standing exposed, and NOISE_RADIUS_SLOW/FAST when moving.
        # We treat any radius > NOISE_RADIUS_STILL as "audible" to the dealer.
        from game.settings import NOISE_RADIUS_STILL
        can_hear = dealer_hears_noise(
            dealer_center, tractor_center,
            tractor_noise_radius if tractor_noise_radius > NOISE_RADIUS_STILL else 0.0,
        )

        state = self._sm.state

        if state == DealerState.PATROL:
            self._patrol_move(dt)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(DealerState.ALERT)
            elif can_hear:
                self._suspicious_target = tractor_center
                self._sm.transition(DealerState.SUSPICIOUS)

        elif state == DealerState.SUSPICIOUS:
            self._face_toward(self._suspicious_target)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(DealerState.ALERT)
            elif self._sm.time_in_state >= DEALER_SUSPICIOUS_TIME:
                self._sm.transition(DealerState.PATROL)

        elif state == DealerState.ALERT:
            if can_see:
                self._last_seen = tractor_center
                self._face_toward(tractor_center)
                if self._sm.time_in_state >= DEALER_ALERT_TIME:
                    self._sm.transition(DealerState.CHASE)
            else:
                self._sm.transition(DealerState.SEARCHING)

        elif state == DealerState.CHASE:
            if can_see:
                self._last_seen = tractor_center
            self._move_toward(dt, self._last_seen, self._chase_speed)
            dist = math.hypot(
                tractor_center[0] - dealer_center[0],
                tractor_center[1] - dealer_center[1],
            )
            if dist <= DEALER_CATCH_DIST:
                self.caught_tractor = True
            elif self._sm.time_in_state >= DEALER_CHASE_TIME:
                self._sm.transition(DealerState.SEARCHING)

        elif state == DealerState.SEARCHING:
            self._move_toward(dt, self._last_seen, self._patrol_speed)
            dist = math.hypot(
                self._last_seen[0] - dealer_center[0],
                self._last_seen[1] - dealer_center[1],
            )
            if dist <= WAYPOINT_REACH_DIST or self._sm.time_in_state >= DEALER_SEARCH_TIME:
                self._sm.transition(DealerState.PATROL)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(DealerState.ALERT)

        elif state == DealerState.LEAVING:
            # Walk off the bottom of the map toward the dealer entry road
            exit_target = (self.rect.centerx, MAP_ENTRY_Y + 60)
            self._move_toward(dt, exit_target, self._patrol_speed)

    # ------------------------------------------------------------------
    # Movement helpers
    # ------------------------------------------------------------------

    def _patrol_move(self, dt: float) -> None:
        target   = self.waypoints[self._waypoint_index]
        cx, cy   = float(self.rect.centerx), float(self.rect.centery)
        dx, dy   = target[0] - cx, target[1] - cy
        dist     = math.hypot(dx, dy)
        if dist <= WAYPOINT_REACH_DIST:
            self._waypoint_index = (self._waypoint_index + 1) % len(self.waypoints)
        else:
            self._facing_angle = math.degrees(math.atan2(dy, dx))
            self._x += (dx / dist) * self._patrol_speed * dt
            self._y += (dy / dist) * self._patrol_speed * dt
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)

    def _move_toward(self, dt: float, target: tuple[int, int], speed: float) -> None:
        cx, cy = float(self.rect.centerx), float(self.rect.centery)
        dx, dy = target[0] - cx, target[1] - cy
        dist   = math.hypot(dx, dy)
        if dist > WAYPOINT_REACH_DIST:
            self._facing_angle = math.degrees(math.atan2(dy, dx))
            self._x += (dx / dist) * speed * dt
            self._y += (dy / dist) * speed * dt
            self.rect.x = int(self._x)
            self.rect.y = int(self._y)

    def _face_toward(self, target: tuple[int, int]) -> None:
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        if math.hypot(dx, dy) > 1:
            self._facing_angle = math.degrees(math.atan2(dy, dx))

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_vision_cone(surface)
        self._draw_body(surface)

    def _draw_vision_cone(self, surface: pygame.Surface) -> None:
        state = self._sm.state
        if state == DealerState.SUSPICIOUS:
            colour = DEALER_CONE_SUSPICIOUS
        elif state in (DealerState.ALERT, DealerState.CHASE, DealerState.SEARCHING):
            colour = DEALER_CONE_ALERT
        else:
            colour = VISION_CONE_COLOUR

        self._vision_surf.fill((0, 0, 0, 0))
        origin    = self.rect.center
        angle_rad = math.radians(self._facing_angle)
        half_rad  = math.radians(VISION_CONE_HALF_ANGLE)

        arc_steps = 14
        points    = [origin]
        for i in range(arc_steps + 1):
            t = -half_rad + (2 * half_rad * i / arc_steps)
            a = angle_rad + t
            points.append((
                origin[0] + math.cos(a) * self._vision_range,
                origin[1] + math.sin(a) * self._vision_range,
            ))

        pygame.draw.polygon(self._vision_surf, (*colour, VISION_CONE_ALPHA), points)
        surface.blit(self._vision_surf, (0, 0))

    def _draw_body(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, DEALER1_BODY_COLOUR, self.rect, border_radius=4)

        head_center = (self.rect.centerx, self.rect.y - DEALER1_HEAD_OFFSET)
        pygame.draw.circle(surface, DEALER1_HEAD_COLOUR, head_center, DEALER1_HEAD_RADIUS)

        eye_rad = math.radians(self._facing_angle)
        for side in (-0.4, 0.4):
            ex = int(head_center[0] + math.cos(eye_rad + side) * 5)
            ey = int(head_center[1] + math.sin(eye_rad + side) * 5)
            pygame.draw.circle(surface, (30, 30, 30), (ex, ey), 2)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    def leave(self) -> None:
        """Trigger the LEAVING walk-off animation (called when round is won)."""
        if self._sm.state != DealerState.LEAVING:
            self._sm.transition(DealerState.LEAVING)

    @property
    def is_offscreen(self) -> bool:
        return self.rect.top > SCREEN_HEIGHT

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center

    @property
    def state(self) -> DealerState:
        return self._sm.state
