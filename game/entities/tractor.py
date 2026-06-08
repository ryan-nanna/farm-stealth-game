# game/entities/tractor.py
# Tractor: the player-controlled entity.
# Movement, wall collision, cover/noise state, drawn as coloured shapes.
# Headlight eyes animate per game state to convey personality.

from __future__ import annotations

import math
from enum import Enum, auto

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


class EyeState(Enum):
    NORMAL    = auto()   # forward, alert, engaged
    NERVOUS   = auto()   # hidden — pupils dart side to side
    WIDE      = auto()   # dealer nearby in CURIOUS/ALERT — pupils wide
    FOCUSED   = auto()   # completing an objective — pupils converge
    HAPPY     = auto()   # objective just completed — eyes scrunch up briefly
    SHOCKED   = auto()   # caught — pupils blow out wide, jitter


class Tractor:
    """
    Player-controlled tractor entity.
    Keeps its own pygame.Rect for position and collision.
    Headlight eyes express the game state so the tractor reads as alive.
    """

    def __init__(self) -> None:
        self.rect: pygame.Rect = pygame.Rect(
            TRACTOR_SPAWN_X, TRACTOR_SPAWN_Y, TRACTOR_WIDTH, TRACTOR_HEIGHT,
        )
        self._x: float = float(TRACTOR_SPAWN_X)
        self._y: float = float(TRACTOR_SPAWN_Y)

        self.silent_mode: bool = False

        self.is_hidden: bool        = False
        self.in_partial_cover: bool = False

        self.noise_radius: float                          = 0.0
        self.noise_colour: tuple[int, int, int] | None   = None

        self._facing_angle: float = 0.0
        self._pulse:        float = 0.0

        # Eye state — set each frame by main.py via set_eye_state()
        self.eye_state: EyeState = EyeState.NORMAL
        self._eye_timer: float   = 0.0   # drives animations within a state

    # ------------------------------------------------------------------
    # Public eye state setter — called by main.py each frame
    # ------------------------------------------------------------------

    def set_eye_state(self, state: EyeState) -> None:
        if state != self.eye_state:
            self.eye_state  = state
            self._eye_timer = 0.0

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
        self.silent_mode = input_state.is_held(Action.B)
        self._eye_timer += dt

        speed = TRACTOR_SPEED_SILENT if self.silent_mode else TRACTOR_SPEED_NORMAL

        dx, dy    = input_state.move_vector
        is_moving = dx != 0.0 or dy != 0.0

        magnitude = math.hypot(dx, dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
            self._facing_angle = math.degrees(math.atan2(dy, dx))

        self._x = max(0.0, min(self._x + dx * speed * dt, SCREEN_WIDTH  - TRACTOR_WIDTH))
        self.rect.x = int(self._x)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                elif dx < 0: self.rect.left = wall.right
                self._x = float(self.rect.x)

        self._y = max(0.0, min(self._y + dy * speed * dt, SCREEN_HEIGHT - TRACTOR_HEIGHT))
        self.rect.y = int(self._y)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dy > 0: self.rect.bottom = wall.top
                elif dy < 0: self.rect.top = wall.bottom
                self._y = float(self.rect.y)

        self.is_hidden, self.in_partial_cover = check_cover(
            self.rect, full_cover_rects, partial_cover_rects
        )

        self._pulse += dt * 4.0
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
            self.noise_radius = NOISE_RADIUS_STILL
            self.noise_colour = COLOUR_NOISE_STILL

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if self.noise_colour is not None and self.noise_radius > 0:
            pulse_r = max(1, int(self.noise_radius + math.sin(self._pulse) * 8))
            pygame.draw.circle(surface, self.noise_colour, self.rect.center, pulse_r, 2)

        pygame.draw.rect(surface, TRACTOR_BODY_COLOUR, self.rect, border_radius=8)

        cab_rect = pygame.Rect(
            self.rect.x + 4, self.rect.y + 4,
            TRACTOR_WIDTH - 8, TRACTOR_HEIGHT - 14,
        )
        cab_colour = tuple(max(0, c - 20) for c in TRACTOR_BODY_COLOUR)
        pygame.draw.rect(surface, cab_colour, cab_rect, border_radius=5)

        self._draw_headlights(surface)

        for wx, wy in [
            (self.rect.left  + 8, self.rect.top    + 5),
            (self.rect.right - 8, self.rect.top    + 5),
            (self.rect.left  + 8, self.rect.bottom - 5),
            (self.rect.right - 8, self.rect.bottom - 5),
        ]:
            pygame.draw.circle(surface, TRACTOR_WHEEL_COLOUR, (wx, wy), TRACTOR_WHEEL_RADIUS)

        if self.is_hidden:
            pygame.draw.rect(surface, COLOUR_COVER_FULL, self.rect, TRACTOR_COVER_RING_WIDTH, border_radius=8)
        elif self.in_partial_cover:
            pygame.draw.rect(surface, COLOUR_COVER_PARTIAL, self.rect, TRACTOR_COVER_RING_WIDTH, border_radius=8)

        if DEBUG_DRAW_HITBOXES:
            pygame.draw.rect(surface, DEBUG_COLOUR, self.rect, 1)

    def _draw_headlights(self, surface: pygame.Surface) -> None:
        """Draw the two expressive headlight eyes based on current eye state."""
        hl_x        = self.rect.right - 6
        hl_y_top    = self.rect.y + 6
        hl_y_bottom = self.rect.y + TRACTOR_HEIGHT - 10
        hl_radius   = 4

        # Outer glow
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_top),    hl_radius)
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_bottom), hl_radius)

        # Pupils — position and size depend on eye state
        t = self._eye_timer

        if self.eye_state == EyeState.NORMAL:
            # Small centred pupils, slight forward lean
            pupil_r = 2
            for hl_y in (hl_y_top, hl_y_bottom):
                pygame.draw.circle(surface, (40, 30, 10), (hl_x, hl_y), pupil_r)

        elif self.eye_state == EyeState.NERVOUS:
            # Pupils dart left/right on a fast cycle — hidden but tense
            dart = int(math.sin(t * 6.0) * 2)
            pupil_r = 2
            for hl_y in (hl_y_top, hl_y_bottom):
                pygame.draw.circle(surface, (40, 30, 10), (hl_x + dart, hl_y), pupil_r)

        elif self.eye_state == EyeState.WIDE:
            # Pupils shrink to tiny dots — fear/alertness
            pygame.draw.circle(surface, (20, 15, 5), (hl_x, hl_y_top),    1)
            pygame.draw.circle(surface, (20, 15, 5), (hl_x, hl_y_bottom), 1)

        elif self.eye_state == EyeState.FOCUSED:
            # Pupils shift slightly inward — determined concentration
            pupil_r = 2
            pygame.draw.circle(surface, (40, 30, 10), (hl_x - 1, hl_y_top),    pupil_r)
            pygame.draw.circle(surface, (40, 30, 10), (hl_x - 1, hl_y_bottom), pupil_r)

        elif self.eye_state == EyeState.HAPPY:
            # Eyes scrunch: draw a small arc across the bottom of each headlight
            for hl_y in (hl_y_top, hl_y_bottom):
                # Crescent — draw a slightly-offset dark circle to create the squint
                pygame.draw.circle(surface, TRACTOR_BODY_COLOUR,
                                   (hl_x, hl_y - 2), hl_radius - 1)

        elif self.eye_state == EyeState.SHOCKED:
            # Pupils jitter randomly — chaotic panic
            jx = random.randint(-2, 2)
            jy = random.randint(-2, 2)
            pygame.draw.circle(surface, (20, 15, 5), (hl_x + jx, hl_y_top    + jy), 1)
            pygame.draw.circle(surface, (20, 15, 5), (hl_x + jx, hl_y_bottom + jy), 1)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
