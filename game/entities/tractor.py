# game/entities/tractor.py
# Tractor: the player-controlled entity.
# Rendered as a photo sprite with animated eye expressions drawn in code
# over the blank headlight holes. Hitbox rect stays small for collision/detection.

from __future__ import annotations

import math
import random
from enum import Enum, auto
from pathlib import Path

import numpy as np
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
    TRACTOR_HL_LOWER,
    TRACTOR_HL_RADIUS,
    TRACTOR_HL_UPPER,
    TRACTOR_SPEED_NORMAL,
    TRACTOR_SPEED_SILENT,
    TRACTOR_SPAWN_X,
    TRACTOR_SPAWN_Y,
    TRACTOR_SPRITE_H,
    TRACTOR_SPRITE_W,
    TRACTOR_WHEEL_COLOUR,
    TRACTOR_WHEEL_RADIUS,
    TRACTOR_WIDTH,
)
from game.systems.collision import check_cover
from game.systems.input import Action, InputState

_SPRITE_PATH = Path("assets/sprites/tractor.png")


def _load_sprite_remove_white(
    path: Path,
    display_size: tuple[int, int],
    threshold: int = 230,
) -> pygame.Surface:
    """
    Load a PNG with a white background and return a scaled RGBA surface with
    all near-white pixels made fully transparent.  Works correctly on
    anti-aliased JPEG-style edges where exact colorkey would leave fringing.
    Also removes the blank white headlight holes so pupils can be drawn on top.
    """
    raw  = pygame.image.load(str(path)).convert_alpha()
    rgb  = pygame.surfarray.pixels3d(raw)          # shape (w, h, 3), uint8
    alpha = pygame.surfarray.pixels_alpha(raw)     # shape (w, h), uint8

    # Mask: pixel is "white" when all three channels exceed the threshold
    white_mask = (
        (rgb[:, :, 0] > threshold) &
        (rgb[:, :, 1] > threshold) &
        (rgb[:, :, 2] > threshold)
    )
    alpha[white_mask] = 0   # make white pixels fully transparent

    del rgb, alpha   # release surfarray locks before transforming

    scaled = pygame.transform.smoothscale(raw, display_size)
    return scaled


# Threshold for removing the white background via alpha mask.
# Pixels where R, G, and B are ALL above this value become fully transparent.
# Set high enough to catch anti-aliased edges (~235+) while keeping grey tractor body.
# Also removes the blank white headlight holes — those are filled with drawn pupils.
_WHITE_THRESHOLD = 230

# Dark pupil colour
_PUPIL_COLOUR = (30, 20, 5)


class EyeState(Enum):
    NORMAL    = auto()   # forward-facing, engaged
    NERVOUS   = auto()   # hidden — pupils dart side to side
    WIDE      = auto()   # dealer nearby in alert/curious — pupils wide/tiny
    FOCUSED   = auto()   # completing an objective — pupils shifted inward
    HAPPY     = auto()   # objective just completed — eyes scrunch up
    SHOCKED   = auto()   # caught — pupils jitter in panic


class Tractor:
    """
    Player-controlled tractor. Hitbox rect drives collision and detection.
    Rendered as a photo sprite; animated headlight pupils drawn on top of
    the blank white headlight holes using the known pixel offsets.
    """

    def __init__(self) -> None:
        self.rect: pygame.Rect = pygame.Rect(
            TRACTOR_SPAWN_X, TRACTOR_SPAWN_Y, TRACTOR_WIDTH, TRACTOR_HEIGHT,
        )
        self._x: float = float(TRACTOR_SPAWN_X)
        self._y: float = float(TRACTOR_SPAWN_Y)

        self.silent_mode: bool      = False
        self.is_hidden: bool        = False
        self.in_partial_cover: bool = False
        self.noise_radius: float    = 0.0
        self.noise_colour: tuple[int, int, int] | None = None

        self._facing_angle: float = 0.0
        self._pulse: float        = 0.0

        self.eye_state: EyeState = EyeState.NORMAL
        self._eye_timer: float   = 0.0

        # Load sprite with proper alpha removal; fall back to shapes if file missing
        self._sprite: pygame.Surface | None = None
        if _SPRITE_PATH.exists():
            self._sprite = _load_sprite_remove_white(
                _SPRITE_PATH, (TRACTOR_SPRITE_W, TRACTOR_SPRITE_H), _WHITE_THRESHOLD
            )

    # ------------------------------------------------------------------
    # Eye state — called by main.py each frame
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

        speed     = TRACTOR_SPEED_SILENT if self.silent_mode else TRACTOR_SPEED_NORMAL
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
                if dx > 0:  self.rect.right = wall.left
                elif dx < 0: self.rect.left  = wall.right
                self._x = float(self.rect.x)

        self._y = max(0.0, min(self._y + dy * speed * dt, SCREEN_HEIGHT - TRACTOR_HEIGHT))
        self.rect.y = int(self._y)
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dy > 0:  self.rect.bottom = wall.top
                elif dy < 0: self.rect.top   = wall.bottom
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
        # Noise ring (behind sprite)
        if self.noise_colour is not None and self.noise_radius > 0:
            pulse_r = max(1, int(self.noise_radius + math.sin(self._pulse) * 8))
            pygame.draw.circle(surface, self.noise_colour, self.rect.center, pulse_r, 2)

        if self._sprite is not None:
            self._draw_sprite(surface)
        else:
            self._draw_shapes(surface)

        # Cover-state ring (drawn on top so it's visible under tree canopies)
        if self.is_hidden:
            pygame.draw.rect(surface, COLOUR_COVER_FULL,    self.rect, TRACTOR_COVER_RING_WIDTH, border_radius=8)
        elif self.in_partial_cover:
            pygame.draw.rect(surface, COLOUR_COVER_PARTIAL, self.rect, TRACTOR_COVER_RING_WIDTH, border_radius=8)

        if DEBUG_DRAW_HITBOXES:
            pygame.draw.rect(surface, DEBUG_COLOUR, self.rect, 1)

    def _draw_sprite(self, surface: pygame.Surface) -> None:
        assert self._sprite is not None

        # Centre the display sprite on the hitbox centre
        sprite_rect = self._sprite.get_rect(center=self.rect.center)
        surface.blit(self._sprite, sprite_rect)

        # Absolute screen positions of the two headlight holes
        hl_upper = (sprite_rect.x + TRACTOR_HL_UPPER[0], sprite_rect.y + TRACTOR_HL_UPPER[1])
        hl_lower = (sprite_rect.x + TRACTOR_HL_LOWER[0], sprite_rect.y + TRACTOR_HL_LOWER[1])
        r = TRACTOR_HL_RADIUS

        # Fill the transparent holes with a warm yellow glow
        for pos in (hl_upper, hl_lower):
            pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, pos, r)

        # Draw animated pupils on top
        self._draw_pupils(surface, hl_upper, hl_lower, r)

    def _draw_pupils(
        self,
        surface: pygame.Surface,
        hl_upper: tuple[int, int],
        hl_lower: tuple[int, int],
        r: int,
    ) -> None:
        """Animate pupils inside both headlight circles based on eye state."""
        t = self._eye_timer

        if self.eye_state == EyeState.NORMAL:
            for pos in (hl_upper, hl_lower):
                pygame.draw.circle(surface, _PUPIL_COLOUR, pos, max(1, r - 2))

        elif self.eye_state == EyeState.NERVOUS:
            # Pupils dart left/right on a quick sinusoidal cycle
            dart = int(math.sin(t * 7.0) * (r - 1))
            for pos in (hl_upper, hl_lower):
                pygame.draw.circle(surface, _PUPIL_COLOUR, (pos[0] + dart, pos[1]), max(1, r - 2))

        elif self.eye_state == EyeState.WIDE:
            # Pupils shrink to tiny pinpoints — fear
            for pos in (hl_upper, hl_lower):
                pygame.draw.circle(surface, _PUPIL_COLOUR, pos, max(1, r - 4))

        elif self.eye_state == EyeState.FOCUSED:
            # Pupils shift slightly toward the centre of the headlight pair
            for pos in (hl_upper, hl_lower):
                pygame.draw.circle(surface, _PUPIL_COLOUR, (pos[0] - 1, pos[1]), max(1, r - 2))

        elif self.eye_state == EyeState.HAPPY:
            # Scrunch: draw a crescent by overlaying a slightly-offset body-colour circle
            for pos in (hl_upper, hl_lower):
                pygame.draw.circle(surface, _PUPIL_COLOUR, pos, max(1, r - 2))
                # Crescent mask — cover the top half of the pupil
                pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR,
                                   (pos[0], pos[1] - (r - 2)), max(1, r - 2))

        elif self.eye_state == EyeState.SHOCKED:
            # Jittery panic — pupils jump around randomly
            for pos in (hl_upper, hl_lower):
                jx = random.randint(-(r - 2), r - 2)
                jy = random.randint(-(r - 2), r - 2)
                pygame.draw.circle(surface, _PUPIL_COLOUR,
                                   (pos[0] + jx, pos[1] + jy), max(1, r - 3))

    def _draw_shapes(self, surface: pygame.Surface) -> None:
        """Fallback: geometric shapes when sprite file is absent."""
        pygame.draw.rect(surface, TRACTOR_BODY_COLOUR, self.rect, border_radius=8)

        cab_rect = pygame.Rect(self.rect.x + 4, self.rect.y + 4,
                               TRACTOR_WIDTH - 8, TRACTOR_HEIGHT - 14)
        cab_colour = tuple(max(0, c - 20) for c in TRACTOR_BODY_COLOUR)
        pygame.draw.rect(surface, cab_colour, cab_rect, border_radius=5)

        hl_x        = self.rect.right - 6
        hl_y_top    = self.rect.y + 6
        hl_y_bottom = self.rect.y + TRACTOR_HEIGHT - 10
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_top),    4)
        pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y_bottom), 4)

        self._draw_pupils(
            surface,
            (hl_x, hl_y_top),
            (hl_x, hl_y_bottom),
            4,
        )

        for wx, wy in [
            (self.rect.left  + 8, self.rect.top    + 5),
            (self.rect.right - 8, self.rect.top    + 5),
            (self.rect.left  + 8, self.rect.bottom - 5),
            (self.rect.right - 8, self.rect.bottom - 5),
        ]:
            pygame.draw.circle(surface, TRACTOR_WHEEL_COLOUR, (wx, wy), TRACTOR_WHEEL_RADIUS)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def center(self) -> tuple[int, int]:
        return self.rect.center
