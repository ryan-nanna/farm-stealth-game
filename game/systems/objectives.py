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
    OBJ_BURST_DURATION,
    OBJ_BURST_RADIUS,
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
    PIGS      = auto()
    COWS      = auto()
    SCARECROW = auto()


# ---------------------------------------------------------------------------
# Particle system — sparkle burst on objective complete
# ---------------------------------------------------------------------------

class _Particle:
    __slots__ = ("x", "y", "vx", "vy", "lifetime", "age", "colour", "radius")

    def __init__(
        self,
        x: float, y: float,
        vx: float, vy: float,
        lifetime: float,
        colour: tuple[int, int, int],
        radius: int,
    ) -> None:
        self.x = x; self.y = y
        self.vx = vx; self.vy = vy
        self.lifetime = lifetime
        self.age = 0.0
        self.colour = colour
        self.radius = radius


class ParticleSystem:
    """Lightweight sparkle/particle system for objective completion effects."""

    def __init__(self) -> None:
        self._particles: list[_Particle] = []

    def burst(
        self,
        cx: int, cy: int,
        count: int = 12,
        speed: float = 140.0,
        lifetime: float = 0.7,
        colours: list[tuple[int, int, int]] | None = None,
    ) -> None:
        if colours is None:
            colours = [(255, 220, 50), (255, 180, 30), (255, 255, 120), (255, 140, 0)]
        for i in range(count):
            angle = (2 * math.pi * i / count) + random.uniform(-0.3, 0.3)
            spd   = speed * random.uniform(0.6, 1.4)
            self._particles.append(_Particle(
                x        = float(cx),
                y        = float(cy),
                vx       = math.cos(angle) * spd,
                vy       = math.sin(angle) * spd,
                lifetime = lifetime * random.uniform(0.7, 1.3),
                colour   = random.choice(colours),
                radius   = random.randint(3, 6),
            ))

    def update(self, dt: float) -> None:
        for p in self._particles:
            p.x   += p.vx * dt
            p.y   += p.vy * dt
            p.vy  += 60.0 * dt   # gentle gravity
            p.age += dt
        self._particles = [p for p in self._particles if p.age < p.lifetime]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self._particles:
            alpha = max(0.0, 1.0 - p.age / p.lifetime)
            r = max(1, int(p.radius * alpha))
            colour = tuple(int(c * alpha) for c in p.colour)
            pygame.draw.circle(surface, colour, (int(p.x), int(p.y)), r)

    @property
    def active(self) -> bool:
        return len(self._particles) > 0


# ---------------------------------------------------------------------------
# TimingBar
# ---------------------------------------------------------------------------

class TimingBar:
    def __init__(self) -> None:
        self._progress: float = 0.0
        self._phase:    float = 0.0
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
        if self._obj_type is None:
            return False

        if self._obj_type == ObjectiveType.PIGS:
            if a_held:
                self._progress = min(1.0, self._progress + dt / OBJ_PIGS_HOLD_TIME)
            else:
                self._progress = max(0.0, self._progress - 2 * dt / OBJ_PIGS_HOLD_TIME)
            return self._progress >= 1.0

        if self._obj_type == ObjectiveType.COWS:
            self._phase += dt * OBJ_COWS_OSCILLATE_SPEED * 2 * math.pi
            self._progress = (math.sin(self._phase) + 1.0) / 2.0
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

        border_rect = pygame.Rect(TIMING_BAR_X - 2, TIMING_BAR_Y - 2, TIMING_BAR_W + 4, TIMING_BAR_H + 4)
        pygame.draw.rect(surface, COLOUR_BAR_BORDER, border_rect, border_radius=4)

        bg_rect = pygame.Rect(TIMING_BAR_X, TIMING_BAR_Y, TIMING_BAR_W, TIMING_BAR_H)
        pygame.draw.rect(surface, COLOUR_BAR_BG, bg_rect, border_radius=3)

        fill_colour = (
            COLOUR_BAR_WHISPER if self._obj_type == ObjectiveType.SCARECROW else COLOUR_BAR_FILL
        )

        if self._obj_type == ObjectiveType.COWS:
            peak_start = int(TIMING_BAR_W * OBJ_COWS_SUCCESS_MIN)
            peak_rect  = pygame.Rect(TIMING_BAR_X + peak_start, TIMING_BAR_Y, TIMING_BAR_W - peak_start, TIMING_BAR_H)
            pygame.draw.rect(surface, COLOUR_BAR_PEAK, peak_rect, border_radius=3)

        fill_w = int(TIMING_BAR_W * self._progress)
        if fill_w > 0:
            fill_rect = pygame.Rect(TIMING_BAR_X, TIMING_BAR_Y, fill_w, TIMING_BAR_H)
            pygame.draw.rect(surface, fill_colour, fill_rect, border_radius=3)


# ---------------------------------------------------------------------------
# ObjectiveManager
# ---------------------------------------------------------------------------

class ObjectiveManager:
    """
    Manages the three per-round objectives. Tracks completion noise bursts,
    sparkle particles, and per-objective completion timers for HUD animations.
    """

    def __init__(
        self,
        pig_pen_rect:     pygame.Rect,
        cow_pasture_rect: pygame.Rect,
        scarecrow_rect:   pygame.Rect,
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

        # Noise burst on objective completion
        self._burst_timer: float = 0.0

        # Per-objective completion flash timers (for HUD bounce)
        self._completion_timers: dict[ObjectiveType, float] = {}

        # Sparkle particles
        self.particles: ParticleSystem = ParticleSystem()

        # Set for exactly one frame on completion — used by main.py for eye state
        self.just_completed: ObjectiveType | None = None

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

    @property
    def burst_noise_radius(self) -> float:
        """Non-zero for OBJ_BURST_DURATION seconds after any objective completes."""
        return OBJ_BURST_RADIUS if self._burst_timer > 0.0 else 0.0

    def completion_flash(self, obj_type: ObjectiveType) -> float:
        """0→1 completion flash progress for HUD bounce animation (1.0 = just done)."""
        t = self._completion_timers.get(obj_type, 0.0)
        return max(0.0, t)

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
        self.just_completed = None

        if self._intel_timer > 0.0:
            self._intel_timer = max(0.0, self._intel_timer - dt)

        if self._burst_timer > 0.0:
            self._burst_timer = max(0.0, self._burst_timer - dt)

        # Tick completion flash timers down
        for k in list(self._completion_timers):
            self._completion_timers[k] = max(0.0, self._completion_timers[k] - dt)

        self.particles.update(dt)

        if self.all_complete:
            return

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
                completed_type = self._active
                self._completed.add(completed_type)
                self.just_completed = completed_type

                # Noise burst so dealers react to the commotion
                self._burst_timer = OBJ_BURST_DURATION

                # Flash timer for HUD bounce
                self._completion_timers[completed_type] = 0.6

                # Sparkle particles at tractor position
                cx, cy = tractor_rect.center
                self.particles.burst(cx, cy)

                if completed_type == ObjectiveType.SCARECROW:
                    self._intel_timer = OBJ_INTEL_DURATION

                self._bar.reset()
                self._active = None

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        self._bar.draw(surface)
        self.particles.draw(surface)
