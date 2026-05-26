# game/systems/objectives.py
from __future__ import annotations

import math
import random
from enum import Enum, auto

import pygame

from game.settings import (
    COLOUR_BAR_BG,
    COLOUR_BAR_BORDER,
    COLOUR_BAR_FILL,
    COLOUR_BAR_PEAK,
    COLOUR_BAR_WHISPER,
    OBJ_COWS_OSCILLATE_SPEED,
    OBJ_COWS_SUCCESS_MIN,
    OBJ_INTEL_DURATION,
    OBJ_PIGS_HOLD_TIME,
    OBJ_SCARECROW_HOLD_TIME,
    TIMING_BAR_H,
    TIMING_BAR_W,
    TIMING_BAR_X,
    TIMING_BAR_Y,
)


class ObjectiveType(Enum):
    PIGS      = auto()   # hold A until bar fills (3 s)
    COWS      = auto()   # press A when oscillating bar hits peak zone
    SCARECROW = auto()   # hold A for 2 s whisper


class TimingBar:
    """Draws and updates the bar at the bottom of the screen for the active objective."""

    def __init__(self) -> None:
        self._progress: float = 0.0   # 0.0 – 1.0
        self._phase:    float = 0.0   # oscillation phase (COWS only)
        self._obj_type: ObjectiveType | None = None

    def start(self, obj_type: ObjectiveType) -> None:
        self._obj_type = obj_type
        self._progress = 0.0
        self._phase    = 0.0

    def reset(self) -> None:
        self._obj_type = None
        self._progress = 0.0
        self._phase    = 0.0

    @property
    def progress(self) -> float:
        return self._progress

    def update(self, dt: float, a_held: bool, a_pressed: bool) -> bool:
        """
        Advance bar state. Returns True the moment the objective succeeds.
        a_held   — A button currently down
        a_pressed — A button newly pressed this frame
        """
        if self._obj_type is None:
            return False

        if self._obj_type == ObjectiveType.PIGS:
            if a_held:
                self._progress = min(1.0, self._progress + dt / OBJ_PIGS_HOLD_TIME)
            else:
                # drains at 2× fill speed when released
                self._progress = max(0.0, self._progress - 2 * dt / OBJ_PIGS_HOLD_TIME)
            return self._progress >= 1.0

        if self._obj_type == ObjectiveType.COWS:
            self._phase += dt * OBJ_COWS_OSCILLATE_SPEED * 2 * math.pi
            self._progress = (math.sin(self._phase) + 1.0) / 2.0   # 0 – 1
            if a_pressed:
                return self._progress >= OBJ_COWS_SUCCESS_MIN
            return False

        if self._obj_type == ObjectiveType.SCARECROW:
            if a_held:
                self._progress = min(1.0, self._progress + dt / OBJ_SCARECROW_HOLD_TIME)
            else:
                self._progress = max(0.0, self._progress - 2 * dt / OBJ_SCARECROW_HOLD_TIME)
            return self._progress >= 1.0

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if self._obj_type is None:
            return

        # Outer border
        border_rect = pygame.Rect(TIMING_BAR_X - 2, TIMING_BAR_Y - 2, TIMING_BAR_W + 4, TIMING_BAR_H + 4)
        pygame.draw.rect(surface, COLOUR_BAR_BORDER, border_rect, border_radius=4)

        # Background
        bg_rect = pygame.Rect(TIMING_BAR_X, TIMING_BAR_Y, TIMING_BAR_W, TIMING_BAR_H)
        pygame.draw.rect(surface, COLOUR_BAR_BG, bg_rect, border_radius=3)

        fill_colour = (
            COLOUR_BAR_WHISPER if self._obj_type == ObjectiveType.SCARECROW else COLOUR_BAR_FILL
        )

        if self._obj_type == ObjectiveType.COWS:
            # Draw peak success zone marker first
            peak_start = int(TIMING_BAR_W * OBJ_COWS_SUCCESS_MIN)
            peak_rect  = pygame.Rect(TIMING_BAR_X + peak_start, TIMING_BAR_Y, TIMING_BAR_W - peak_start, TIMING_BAR_H)
            pygame.draw.rect(surface, COLOUR_BAR_PEAK, peak_rect, border_radius=3)

        fill_w = int(TIMING_BAR_W * self._progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(TIMING_BAR_X, TIMING_BAR_Y, fill_w, TIMING_BAR_H)
            pygame.draw.rect(surface, fill_colour, fill_rect, border_radius=3)


class ObjectiveManager:
    """
    Manages the three per-round objectives. Randomises order, tracks
    which are complete, handles intel timer for the scarecrow objective.
    """

    def __init__(
        self,
        pig_pen_rect:      pygame.Rect,
        cow_pasture_rect:  pygame.Rect,
        scarecrow_rect:    pygame.Rect,
    ) -> None:
        self._zones: dict[ObjectiveType, pygame.Rect] = {
            ObjectiveType.PIGS:      pig_pen_rect,
            ObjectiveType.COWS:      cow_pasture_rect,
            ObjectiveType.SCARECROW: scarecrow_rect,
        }
        self._order:     list[ObjectiveType] = random.sample(list(ObjectiveType), 3)
        self._completed: set[ObjectiveType]  = set()
        self._active:    ObjectiveType | None = None
        self._bar:       TimingBar            = TimingBar()
        self._intel_timer: float = 0.0

    # ------------------------------------------------------------------
    # Public read-only state
    # ------------------------------------------------------------------

    @property
    def all_complete(self) -> bool:
        return len(self._completed) == 3

    @property
    def intel_active(self) -> bool:
        return self._intel_timer > 0.0

    @property
    def completed(self) -> set[ObjectiveType]:
        return self._completed

    @property
    def order(self) -> list[ObjectiveType]:
        return self._order

    @property
    def active(self) -> ObjectiveType | None:
        return self._active

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        tractor_rect: pygame.Rect,
        a_held:       bool,
        a_pressed:    bool,
        dt:           float,
    ) -> None:
        if self._intel_timer > 0.0:
            self._intel_timer = max(0.0, self._intel_timer - dt)

        if self.all_complete:
            return

        # Determine which (incomplete) zone the tractor is in
        zone_now: ObjectiveType | None = None
        for obj_type, zone_rect in self._zones.items():
            if obj_type not in self._completed and tractor_rect.colliderect(zone_rect):
                zone_now = obj_type
                break

        if zone_now != self._active:
            self._bar.reset()
            self._active = zone_now
            if zone_now is not None:
                self._bar.start(zone_now)

        if self._active is not None:
            done = self._bar.update(dt, a_held, a_pressed)
            if done:
                self._completed.add(self._active)
                if self._active == ObjectiveType.SCARECROW:
                    self._intel_timer = OBJ_INTEL_DURATION
                self._bar.reset()
                self._active = None

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        self._bar.draw(surface)
