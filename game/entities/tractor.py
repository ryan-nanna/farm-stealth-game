# game/entities/tractor.py
# Tractor: the player-controlled entity.
# Session 1 scope: movement + screen-boundary clamping, drawn as coloured shapes.
# Hiding state, noise system, and sprite art are added in later sessions.

from __future__ import annotations

import math

import pygame

from game.settings import (
    DEBUG_COLOUR,
    DEBUG_DRAW_HITBOXES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TRACTOR_BODY_COLOUR,
    TRACTOR_HEADLIGHT_COLOUR,
    TRACTOR_HEIGHT,
    TRACTOR_SPEED_NORMAL,
    TRACTOR_SPEED_SILENT,
    TRACTOR_SPAWN_X,
    TRACTOR_SPAWN_Y,
    TRACTOR_WIDTH,
)
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

        # Facing direction in degrees: 0 = right, 90 = down (used for headlight drawing)
        self._facing_angle: float = 0.0

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, input_state: InputState, dt: float) -> None:
        """
        Move the tractor based on this frame's abstract input.
        dt is the delta-time in seconds from the game clock.
        """
        self.silent_mode = input_state.is_held(Action.B)

        speed = TRACTOR_SPEED_SILENT if self.silent_mode else TRACTOR_SPEED_NORMAL

        dx, dy = input_state.move_vector

        # Normalise diagonal movement so you don't go faster on diagonals
        magnitude = math.hypot(dx, dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
            # Track facing direction for the headlight visual
            self._facing_angle = math.degrees(math.atan2(dy, dx))

        self._x += dx * speed * dt
        self._y += dy * speed * dt

        # Clamp to screen bounds
        self._x = max(0.0, min(self._x, SCREEN_WIDTH  - TRACTOR_WIDTH))
        self._y = max(0.0, min(self._y, SCREEN_HEIGHT - TRACTOR_HEIGHT))

        # Sync rect to float position
        self.rect.x = int(self._x)
        self.rect.y = int(self._y)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        """
        Render the tractor as coloured shapes (no sprite art yet).
        Body: rounded warm-grey rectangle.
        Headlights: two small yellow circles on the forward-facing edge.
        """
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

        # --- Headlights (always drawn on right edge — Session 3 will use facing angle) ---
        hl_y_top    = self.rect.y + 6
        hl_y_bottom = self.rect.y + TRACTOR_HEIGHT - 10
        hl_x        = self.rect.right - 6
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_top),    4)
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_bottom), 4)

        # --- Wheels (four dark circles at corners) ---
        wheel_colour = (50, 48, 44)
        wheel_radius = 7
        for wx, wy in [
            (self.rect.left  + 8,  self.rect.top    + 5),
            (self.rect.right - 8,  self.rect.top    + 5),
            (self.rect.left  + 8,  self.rect.bottom - 5),
            (self.rect.right - 8,  self.rect.bottom - 5),
        ]:
            pygame.draw.circle(surface, wheel_colour, (wx, wy), wheel_radius)

        # --- Debug hitbox ---
        if DEBUG_DRAW_HITBOXES:
            pygame.draw.rect(surface, DEBUG_COLOUR, self.rect, 1)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
