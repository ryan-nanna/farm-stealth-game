# game/entities/dealer.py
# Hubert: the first scrap dealer villain.
# Runs a 6-state lurk/hunt machine: LURK → CURIOUS → SEARCHING → ALERT → CHASE → LEAVING.
# Rendered as a photo sprite (assets/sprites/hubert.png) that slides around the farm.
# Vision cone draws on top; hitbox rect drives all collision and detection logic.

from __future__ import annotations

import math
import random
from enum import Enum, auto
from pathlib import Path

import pygame

from game.settings import (
    DEALER_ALERT_TIME,
    DEALER_CATCH_DIST,
    DEALER_CHASE_TIME,
    DEALER_CONE_ALERT,
    DEALER_SEARCH_TIME,
    HUBERT_BODY_COLOUR,
    HUBERT_CONE_CURIOUS,
    HUBERT_CURIOUS_TIME,
    HUBERT_HAIR_COLOUR,
    HUBERT_HAT_BRIM_COLOUR,
    HUBERT_HAT_CROWN_COLOUR,
    HUBERT_HEAD_COLOUR,
    HUBERT_HEAD_OFFSET,
    HUBERT_HEAD_RADIUS,
    HUBERT_HEIGHT,
    HUBERT_LURK_WAYPOINTS,
    HUBERT_SPEED_CHASE,
    HUBERT_SPEED_LURK,
    HUBERT_SPRITE_H,
    HUBERT_SPRITE_W,
    HUBERT_WIDTH,
    MAP_ENTRY_Y,
    NOISE_RADIUS_STILL,
    PARTIAL_COVER_RANGE_MULT,
    VISION_CONE_ALPHA,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    VISION_CONE_COLOUR,
    VISION_CONE_HALF_ANGLE,
    VISION_CONE_RANGE,
    WAYPOINT_REACH_DIST,
)
from game.systems.detection import dealer_hears_noise, tractor_in_cone
from game.systems.state_machine import StateMachine

_SPRITE_PATH = Path("assets/sprites/hubert.png")


class HubertState(Enum):
    LURK      = auto()   # slow semi-random drift across the whole farm
    CURIOUS   = auto()   # heard noise, moving toward general area (not locked on tractor)
    SEARCHING = auto()   # actively checking last known position
    ALERT     = auto()   # visual lock — cone held on tractor for ALERT_TIME
    CHASE     = auto()   # rushing toward tractor
    LEAVING   = auto()   # round won, walking off the bottom edge


class Hubert:
    """
    Scrap dealer villain. Photo sprite slides around the farm; vision cone renders on top.
    AI runs the LURK/CURIOUS/SEARCHING/ALERT/CHASE/LEAVING state machine.
    The hitbox rect (self.rect) is small and stays separate from the display sprite
    so collision and detection work at game-unit scale.
    """

    def __init__(
        self,
        lurk_speed:   float = HUBERT_SPEED_LURK,
        chase_speed:  float = HUBERT_SPEED_CHASE,
        vision_range: float = VISION_CONE_RANGE,
    ) -> None:
        start = HUBERT_LURK_WAYPOINTS[0]
        self.rect: pygame.Rect = pygame.Rect(
            start[0] - HUBERT_WIDTH  // 2,
            start[1] - HUBERT_HEIGHT // 2,
            HUBERT_WIDTH,
            HUBERT_HEIGHT,
        )
        self._x: float = float(self.rect.x)
        self._y: float = float(self.rect.y)

        self._lurk_waypoints: list[tuple[int, int]] = HUBERT_LURK_WAYPOINTS
        self._lurk_index:     int   = 0
        self._facing_angle:   float = 0.0

        self._lurk_speed:   float = lurk_speed
        self._chase_speed:  float = chase_speed
        self._vision_range: float = vision_range

        self._sm: StateMachine[HubertState] = StateMachine(HubertState.LURK)

        self._curious_target: tuple[int, int] = start
        self._last_seen:      tuple[int, int] = start

        self.caught_tractor: bool = False

        # World-sized so the cone renders correctly anywhere on the scrollable map
        self._vision_surf: pygame.Surface = pygame.Surface(
            (WORLD_WIDTH, WORLD_HEIGHT), pygame.SRCALPHA
        )

        # Photo sprite — loaded once; None means fall back to shape drawing
        self._sprite: pygame.Surface | None = None
        if _SPRITE_PATH.exists():
            raw = pygame.image.load(str(_SPRITE_PATH)).convert_alpha()
            self._sprite = pygame.transform.smoothscale(raw, (HUBERT_SPRITE_W, HUBERT_SPRITE_H))

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
        # Green (still/exposed) noise is cosmetic — Hubert only reacts to amber/red.
        can_hear = dealer_hears_noise(
            dealer_center,
            tractor_center,
            tractor_noise_radius if tractor_noise_radius > NOISE_RADIUS_STILL else 0.0,
        )

        state = self._sm.state

        if state == HubertState.LURK:
            self._lurk_move(dt)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(HubertState.ALERT)
            elif can_hear:
                self._curious_target = tractor_center
                self._sm.transition(HubertState.CURIOUS)

        elif state == HubertState.CURIOUS:
            self._move_toward(dt, self._curious_target, self._lurk_speed)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(HubertState.ALERT)
            else:
                dist = math.hypot(
                    self._curious_target[0] - dealer_center[0],
                    self._curious_target[1] - dealer_center[1],
                )
                if dist <= WAYPOINT_REACH_DIST or self._sm.time_in_state >= HUBERT_CURIOUS_TIME:
                    self._last_seen = self._curious_target
                    self._sm.transition(HubertState.SEARCHING)

        elif state == HubertState.SEARCHING:
            self._move_toward(dt, self._last_seen, self._lurk_speed)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(HubertState.ALERT)
            else:
                dist = math.hypot(
                    self._last_seen[0] - dealer_center[0],
                    self._last_seen[1] - dealer_center[1],
                )
                if dist <= WAYPOINT_REACH_DIST or self._sm.time_in_state >= DEALER_SEARCH_TIME:
                    self._sm.transition(HubertState.LURK)

        elif state == HubertState.ALERT:
            if can_see:
                self._last_seen = tractor_center
                self._face_toward(tractor_center)
                if self._sm.time_in_state >= DEALER_ALERT_TIME:
                    self._sm.transition(HubertState.CHASE)
            else:
                self._sm.transition(HubertState.SEARCHING)

        elif state == HubertState.CHASE:
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
                self._sm.transition(HubertState.SEARCHING)

        elif state == HubertState.LEAVING:
            exit_target = (self.rect.centerx, MAP_ENTRY_Y + 60)
            self._move_toward(dt, exit_target, self._lurk_speed)

    # ------------------------------------------------------------------
    # Movement helpers
    # ------------------------------------------------------------------

    def _lurk_move(self, dt: float) -> None:
        """Drift toward current waypoint; on arrival pick a random new one."""
        target = self._lurk_waypoints[self._lurk_index]
        cx, cy = float(self.rect.centerx), float(self.rect.centery)
        dx, dy = target[0] - cx, target[1] - cy
        dist   = math.hypot(dx, dy)
        if dist <= WAYPOINT_REACH_DIST:
            choices = [i for i in range(len(self._lurk_waypoints)) if i != self._lurk_index]
            self._lurk_index = random.choice(choices)
        else:
            self._facing_angle = math.degrees(math.atan2(dy, dx))
            self._x += (dx / dist) * self._lurk_speed * dt
            self._y += (dy / dist) * self._lurk_speed * dt
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
        if self._sprite is not None:
            self._draw_sprite(surface)
        else:
            self._draw_shapes(surface)

    def _draw_vision_cone(self, surface: pygame.Surface) -> None:
        state = self._sm.state
        if state in (HubertState.CURIOUS, HubertState.SEARCHING):
            colour = HUBERT_CONE_CURIOUS
        elif state in (HubertState.ALERT, HubertState.CHASE):
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

    def _draw_sprite(self, surface: pygame.Surface) -> None:
        """Blit the photo sprite centred on the hitbox. No rotation — photo just translates."""
        assert self._sprite is not None
        r = self._sprite.get_rect(center=self.rect.center)
        surface.blit(self._sprite, r)

    def _draw_shapes(self, surface: pygame.Surface) -> None:
        """Fallback geometric drawing used when the sprite image is not present."""
        pygame.draw.rect(surface, HUBERT_BODY_COLOUR, self.rect, border_radius=3)

        head_center = (self.rect.centerx, self.rect.y - HUBERT_HEAD_OFFSET)
        pygame.draw.circle(surface, HUBERT_HAIR_COLOUR,     head_center, HUBERT_HEAD_RADIUS + 7)
        pygame.draw.circle(surface, HUBERT_HAT_BRIM_COLOUR, head_center, HUBERT_HEAD_RADIUS + 4)
        pygame.draw.circle(surface, HUBERT_HAT_CROWN_COLOUR,head_center, HUBERT_HEAD_RADIUS)
        pygame.draw.circle(surface, HUBERT_HEAD_COLOUR,     head_center, HUBERT_HEAD_RADIUS - 2)

        eye_rad = math.radians(self._facing_angle)
        for side in (-0.4, 0.4):
            ex = int(head_center[0] + math.cos(eye_rad + side) * 4)
            ey = int(head_center[1] + math.sin(eye_rad + side) * 4)
            pygame.draw.circle(surface, (30, 30, 30), (ex, ey), 2)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def leave(self) -> None:
        """Trigger the LEAVING walk-off (called when round is won)."""
        if self._sm.state != HubertState.LEAVING:
            self._sm.transition(HubertState.LEAVING)

    @property
    def is_offscreen(self) -> bool:
        return self.rect.top > SCREEN_HEIGHT

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center

    @property
    def state(self) -> HubertState:
        return self._sm.state
