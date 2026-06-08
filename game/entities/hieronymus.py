# game/entities/hieronymus.py
# Hieronymus: the second scrap dealer villain.
# Shorter, faster, and excitable. One green sock, one red sock.
# Narrow vision cone but reacts to amber/red noise within HIERONYMUS_SNIFF_DIST,
# making silent mode genuinely necessary when passing near him.
# Joins the farm starting Round 2.

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
    HIERONYMUS_BODY_COLOUR,
    HIERONYMUS_HEAD_COLOUR,
    HIERONYMUS_HEAD_OFFSET,
    HIERONYMUS_HEAD_RADIUS,
    HIERONYMUS_HEIGHT,
    HIERONYMUS_LURK_WAYPOINTS,
    HIERONYMUS_SNIFF_DIST,
    HIERONYMUS_SOCK_GREEN,
    HIERONYMUS_SOCK_RED,
    HIERONYMUS_SPEED_CHASE,
    HIERONYMUS_SPEED_LURK,
    HIERONYMUS_SPRITE_H,
    HIERONYMUS_SPRITE_W,
    HIERONYMUS_VISION_HALF_ANGLE,
    HIERONYMUS_VISION_RANGE,
    HIERONYMUS_CURIOUS_TIME,
    HIERONYMUS_WIDTH,
    MAP_ENTRY_Y,
    NOISE_RADIUS_STILL,
    PARTIAL_COVER_RANGE_MULT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VISION_CONE_ALPHA,
    HUBERT_CONE_CURIOUS,
    WAYPOINT_REACH_DIST,
)
from game.systems.detection import dealer_hears_noise, tractor_in_cone
from game.systems.state_machine import StateMachine

_SPRITE_PATH = Path("assets/sprites/hieronymus.png")


class HieronymusState(Enum):
    LURK      = auto()
    CURIOUS   = auto()
    SEARCHING = auto()
    ALERT     = auto()
    CHASE     = auto()
    LEAVING   = auto()

# Cone colours: reuse Hubert's orange for CURIOUS/SEARCHING, shared red for ALERT/CHASE
_CONE_LURK    = (200, 100, 220)  # purple tint — distinct from Hubert's yellow
_CONE_CURIOUS = HUBERT_CONE_CURIOUS
_CONE_ALERT   = DEALER_CONE_ALERT
_CONE_ALPHA   = VISION_CONE_ALPHA


class Hieronymus:
    """
    Fast, erratic scrap dealer. Narrow vision cone, but he'll snap to CURIOUS
    on any amber/red noise within HIERONYMUS_SNIFF_DIST — so silent mode is
    essential whenever the player passes close to him.
    """

    def __init__(
        self,
        lurk_speed:   float = HIERONYMUS_SPEED_LURK,
        chase_speed:  float = HIERONYMUS_SPEED_CHASE,
        vision_range: float = HIERONYMUS_VISION_RANGE,
    ) -> None:
        start = HIERONYMUS_LURK_WAYPOINTS[0]
        self.rect: pygame.Rect = pygame.Rect(
            start[0] - HIERONYMUS_WIDTH  // 2,
            start[1] - HIERONYMUS_HEIGHT // 2,
            HIERONYMUS_WIDTH,
            HIERONYMUS_HEIGHT,
        )
        self._x: float = float(self.rect.x)
        self._y: float = float(self.rect.y)

        self._lurk_waypoints: list[tuple[int, int]] = HIERONYMUS_LURK_WAYPOINTS
        self._lurk_index:     int   = 0
        self._facing_angle:   float = 90.0  # starts facing upward (entering from bottom)

        self._lurk_speed:   float = lurk_speed
        self._chase_speed:  float = chase_speed
        self._vision_range: float = vision_range

        self._sm: StateMachine[HieronymusState] = StateMachine(HieronymusState.LURK)

        self._curious_target: tuple[int, int] = start
        self._last_seen:      tuple[int, int] = start

        self.caught_tractor: bool = False

        self._vision_surf: pygame.Surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )

        self._sprite: pygame.Surface | None = None
        if _SPRITE_PATH.exists():
            raw = pygame.image.load(str(_SPRITE_PATH)).convert_alpha()
            self._sprite = pygame.transform.smoothscale(raw, (HIERONYMUS_SPRITE_W, HIERONYMUS_SPRITE_H))

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
            HIERONYMUS_VISION_HALF_ANGLE,
            tractor_rect,
            full_cover_rects,
            partial_cover_rects,
            PARTIAL_COVER_RANGE_MULT,
        )

        # Standard hearing: within the tractor's noise radius (amber/red only)
        can_hear = dealer_hears_noise(
            dealer_center,
            tractor_center,
            tractor_noise_radius if tractor_noise_radius > NOISE_RADIUS_STILL else 0.0,
        )

        # Hieronymus's acute sensitivity: snaps to CURIOUS on ANY amber/red noise
        # within SNIFF_DIST, even if outside the normal noise radius
        if not can_hear and tractor_noise_radius > NOISE_RADIUS_STILL:
            dist = math.hypot(
                tractor_center[0] - dealer_center[0],
                tractor_center[1] - dealer_center[1],
            )
            if dist <= HIERONYMUS_SNIFF_DIST:
                can_hear = True

        state = self._sm.state

        if state == HieronymusState.LURK:
            self._lurk_move(dt)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(HieronymusState.ALERT)
            elif can_hear:
                self._curious_target = tractor_center
                self._sm.transition(HieronymusState.CURIOUS)

        elif state == HieronymusState.CURIOUS:
            self._move_toward(dt, self._curious_target, self._lurk_speed)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(HieronymusState.ALERT)
            else:
                dist = math.hypot(
                    self._curious_target[0] - dealer_center[0],
                    self._curious_target[1] - dealer_center[1],
                )
                if dist <= WAYPOINT_REACH_DIST or self._sm.time_in_state >= HIERONYMUS_CURIOUS_TIME:
                    self._last_seen = self._curious_target
                    self._sm.transition(HieronymusState.SEARCHING)

        elif state == HieronymusState.SEARCHING:
            self._move_toward(dt, self._last_seen, self._lurk_speed)
            if can_see:
                self._last_seen = tractor_center
                self._sm.transition(HieronymusState.ALERT)
            else:
                dist = math.hypot(
                    self._last_seen[0] - dealer_center[0],
                    self._last_seen[1] - dealer_center[1],
                )
                if dist <= WAYPOINT_REACH_DIST or self._sm.time_in_state >= DEALER_SEARCH_TIME:
                    self._sm.transition(HieronymusState.LURK)

        elif state == HieronymusState.ALERT:
            if can_see:
                self._last_seen = tractor_center
                self._face_toward(tractor_center)
                if self._sm.time_in_state >= DEALER_ALERT_TIME:
                    self._sm.transition(HieronymusState.CHASE)
            else:
                self._sm.transition(HieronymusState.SEARCHING)

        elif state == HieronymusState.CHASE:
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
                self._sm.transition(HieronymusState.SEARCHING)

        elif state == HieronymusState.LEAVING:
            exit_target = (self.rect.centerx, MAP_ENTRY_Y + 60)
            self._move_toward(dt, exit_target, self._lurk_speed)

    # ------------------------------------------------------------------
    # Movement helpers
    # ------------------------------------------------------------------

    def _lurk_move(self, dt: float) -> None:
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
        if state in (HieronymusState.CURIOUS, HieronymusState.SEARCHING):
            colour = _CONE_CURIOUS
        elif state in (HieronymusState.ALERT, HieronymusState.CHASE):
            colour = _CONE_ALERT
        else:
            colour = _CONE_LURK

        self._vision_surf.fill((0, 0, 0, 0))
        origin    = self.rect.center
        angle_rad = math.radians(self._facing_angle)
        half_rad  = math.radians(HIERONYMUS_VISION_HALF_ANGLE)

        arc_steps = 12
        points    = [origin]
        for i in range(arc_steps + 1):
            t = -half_rad + (2 * half_rad * i / arc_steps)
            a = angle_rad + t
            points.append((
                origin[0] + math.cos(a) * self._vision_range,
                origin[1] + math.sin(a) * self._vision_range,
            ))

        pygame.draw.polygon(self._vision_surf, (*colour, _CONE_ALPHA), points)
        surface.blit(self._vision_surf, (0, 0))

    def _draw_sprite(self, surface: pygame.Surface) -> None:
        assert self._sprite is not None
        r = self._sprite.get_rect(center=self.rect.center)
        surface.blit(self._sprite, r)

    def _draw_shapes(self, surface: pygame.Surface) -> None:
        """Fallback: shorter stocky body with mismatched sock detail."""
        pygame.draw.rect(surface, HIERONYMUS_BODY_COLOUR, self.rect, border_radius=3)

        # Mismatched socks — two small coloured dots at the bottom of the body
        sock_y = self.rect.bottom - 5
        pygame.draw.circle(surface, HIERONYMUS_SOCK_GREEN, (self.rect.centerx - 5, sock_y), 4)
        pygame.draw.circle(surface, HIERONYMUS_SOCK_RED,   (self.rect.centerx + 5, sock_y), 4)

        head_center = (self.rect.centerx, self.rect.y - HIERONYMUS_HEAD_OFFSET)
        pygame.draw.circle(surface, HIERONYMUS_HEAD_COLOUR, head_center, HIERONYMUS_HEAD_RADIUS)

        eye_rad = math.radians(self._facing_angle)
        for side in (-0.45, 0.45):
            ex = int(head_center[0] + math.cos(eye_rad + side) * 4)
            ey = int(head_center[1] + math.sin(eye_rad + side) * 4)
            pygame.draw.circle(surface, (30, 30, 30), (ex, ey), 2)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def leave(self) -> None:
        if self._sm.state != HieronymusState.LEAVING:
            self._sm.transition(HieronymusState.LEAVING)

    @property
    def is_offscreen(self) -> bool:
        return self.rect.top > SCREEN_HEIGHT

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center

    @property
    def state(self) -> HieronymusState:
        return self._sm.state
