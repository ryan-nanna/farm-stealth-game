# game/entities/tractor.py
# Tractor: the player-controlled entity.
# Movement, screen-boundary clamping, wall collision, drawn as coloured shapes.
# Hiding state, noise system, and sprite art are added in later sessions.

from __future__ import annotations

import math

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
    TRACTOR_BODY_COLOUR,
    TRACTOR_COVER_RING_WIDTH,
    TRACTOR_HEADLIGHT_COLOUR,
    TRACTOR_HEIGHT,
    TRACTOR_SPEED_NORMAL,
    TRACTOR_SPEED_SILENT,
    TRACTOR_SPAWN_X,
    TRACTOR_SPAWN_Y,
    TRACTOR_WHEEL_COLOUR,
    TRACTOR_WHEEL_RADIUS,
    TRACTOR_WIDTH,
)
from game.systems.collision import check_cover
from game.systems.input import Action, InputState


class Tractor:
    """
    Player-controlled tractor entity.

    Keeps its own pygame.Rect for position and collision.
    Drawing is done in code as shapes until real sprites are ready.
    """

    def __init__(self) -> None:
        # Rect is the canonical position/size — always kept in sync with _x/_y
        self.rect: pygame.Rect = pygame.Rect(
            TRACTOR_SPAWN_X,
            TRACTOR_SPAWN_Y,
            TRACTOR_WIDTH,
            TRACTOR_HEIGHT,
        )
        # Sub-pixel position so floating-point movement doesn't accumulate rounding error
        self._x: float = float(TRACTOR_SPAWN_X)
        self._y: float = float(TRACTOR_SPAWN_Y)

        # True while B / Left Shift is held — cuts speed and (later) noise
        self.silent_mode: bool = False

        # Cover state — updated each frame after movement
        self.is_hidden: bool = False         # inside full-cover zone (invisible to dealers)
        self.in_partial_cover: bool = False  # inside partial-cover zone (60% vision reduction)

        # Noise state — updated each frame; read by dealers via dealer.update()
        self.noise_radius: float = 0.0
        self.noise_colour: tuple[int, int, int] | None = None

        # Facing direction in degrees: 0 = right, 90 = down (used for headlight drawing)
        self._facing_angle: float = 0.0
        self._pulse: float = 0.0   # drives the animated noise ring

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
        """
        Move the tractor, resolve wall collisions per-axis, then update cover state.
        dt is delta-time in seconds.
        """
        self.silent_mode = input_state.is_held(Action.B)

        speed = TRACTOR_SPEED_SILENT if self.silent_mode else TRACTOR_SPEED_NORMAL

        dx, dy    = input_state.move_vector
        is_moving = dx != 0.0 or dy != 0.0

        # Normalise diagonal movement so you don't go faster on diagonals
        magnitude = math.hypot(dx, dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
            self._facing_angle = math.degrees(math.atan2(dy, dx))

        # --- X axis: move, clamp, then resolve wall collisions ---
        self._x = max(0.0, min(self._x + dx * speed * dt, SCREEN_WIDTH - TRACTOR_WIDTH))
        self.rect.x = int(self._x)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right
                self._x = float(self.rect.x)

        # --- Y axis: move, clamp, then resolve wall collisions ---
        self._y = max(0.0, min(self._y + dy * speed * dt, SCREEN_HEIGHT - TRACTOR_HEIGHT))
        self.rect.y = int(self._y)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom
                self._y = float(self.rect.y)

        # --- Cover detection (after final position is settled) ---
        self.is_hidden, self.in_partial_cover = check_cover(
            self.rect, full_cover_rects, partial_cover_rects
        )

        # --- Noise level ---
        self._pulse += dt * 4.0  # ~0.64 Hz pulse cycle
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
            # Still and exposed — green ring, dealers do not react
            self.noise_radius = NOISE_RADIUS_STILL
            self.noise_colour = COLOUR_NOISE_STILL

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """Render the tractor as coloured shapes (no sprite art yet)."""
        # --- Noise ring (drawn first, behind the tractor body) ---
        if self.noise_colour is not None and self.noise_radius > 0:
            pulse_r = max(1, int(self.noise_radius + math.sin(self._pulse) * 8))
            pygame.draw.circle(surface, self.noise_colour, self.rect.center, pulse_r, 2)

        # --- Body ---
        pygame.draw.rect(surface, TRACTOR_BODY_COLOUR, self.rect, border_radius=8)

        # --- Cab (slightly darker rectangle, top two-thirds of body) ---
        cab_rect = pygame.Rect(
            self.rect.x + 4,
            self.rect.y + 4,
            TRACTOR_WIDTH - 8,
            TRACTOR_HEIGHT - 14,
        )
        cab_colour = (
            TRACTOR_BODY_COLOUR[0] - 20,
            TRACTOR_BODY_COLOUR[1] - 20,
            TRACTOR_BODY_COLOUR[2] - 20,
        )
        pygame.draw.rect(surface, cab_colour, cab_rect, border_radius=5)

        # --- Headlights (on right edge; facing direction used from Session 4 onward) ---
        hl_x        = self.rect.right - 6
        hl_y_top    = self.rect.y + 6
        hl_y_bottom = self.rect.y + TRACTOR_HEIGHT - 10
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_top),    4)
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_bottom), 4)

        # --- Wheels ---
        for wx, wy in [
            (self.rect.left  + 8, self.rect.top    + 5),
            (self.rect.right - 8, self.rect.top    + 5),
            (self.rect.left  + 8, self.rect.bottom - 5),
            (self.rect.right - 8, self.rect.bottom - 5),
        ]:
            pygame.draw.circle(surface, TRACTOR_WHEEL_COLOUR, (wx, wy), TRACTOR_WHEEL_RADIUS)

        # --- Cover-state ring ---
        # Drawn outside the body so it's visible when peeking out from under a canopy.
        if self.is_hidden:
            pygame.draw.rect(surface, COLOUR_COVER_FULL, self.rect, TRACTOR_COVER_RING_WIDTH, border_radius=8)
        elif self.in_partial_cover:
            pygame.draw.rect(surface, COLOUR_COVER_PARTIAL, self.rect, TRACTOR_COVER_RING_WIDTH, border_radius=8)

        # --- Debug hitbox ---
        if DEBUG_DRAW_HITBOXES:
            pygame.draw.rect(surface, DEBUG_COLOUR, self.rect, 1)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
