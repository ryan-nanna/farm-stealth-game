# game/entities/gramps.py
# Gramps: the friendly NPC standing in the barn. Static — no state machine.
# Serves as the visual anchor for the win condition.

from __future__ import annotations

import pygame

from game.settings import (
    GRAMPS_BODY_COLOUR,
    GRAMPS_HAT_COLOUR,
    GRAMPS_HEAD_COLOUR,
    GRAMPS_HEAD_OFFSET,
    GRAMPS_HEAD_RADIUS,
    GRAMPS_HEIGHT,
    GRAMPS_SPAWN_X,
    GRAMPS_SPAWN_Y,
    GRAMPS_WIDTH,
)


class Gramps:
    """
    Stationary friendly NPC inside the barn. Drawn as a simple
    figure — overalls, warm skin, straw hat. No update logic needed.
    """

    def __init__(self) -> None:
        self.rect: pygame.Rect = pygame.Rect(
            GRAMPS_SPAWN_X - GRAMPS_WIDTH  // 2,
            GRAMPS_SPAWN_Y - GRAMPS_HEIGHT // 2,
            GRAMPS_WIDTH,
            GRAMPS_HEIGHT,
        )

    def draw(self, surface: pygame.Surface) -> None:
        # Body (overalls)
        pygame.draw.rect(surface, GRAMPS_BODY_COLOUR, self.rect, border_radius=4)

        # Head
        head_center = (self.rect.centerx, self.rect.y - GRAMPS_HEAD_OFFSET)
        pygame.draw.circle(surface, GRAMPS_HEAD_COLOUR, head_center, GRAMPS_HEAD_RADIUS)

        # Straw hat (flat brim + small crown)
        brim_rect = pygame.Rect(
            head_center[0] - GRAMPS_HEAD_RADIUS - 4,
            head_center[1] - GRAMPS_HEAD_RADIUS // 2,
            (GRAMPS_HEAD_RADIUS + 4) * 2,
            5,
        )
        pygame.draw.rect(surface, GRAMPS_HAT_COLOUR, brim_rect, border_radius=2)
        crown_rect = pygame.Rect(
            head_center[0] - GRAMPS_HEAD_RADIUS // 2,
            brim_rect.top - 8,
            GRAMPS_HEAD_RADIUS,
            10,
        )
        pygame.draw.rect(surface, GRAMPS_HAT_COLOUR, crown_rect, border_radius=2)

        # Simple smile dots (two eyes, curved mouth suggestion)
        pygame.draw.circle(surface, (50, 30, 10), (head_center[0] - 3, head_center[1] - 2), 2)
        pygame.draw.circle(surface, (50, 30, 10), (head_center[0] + 3, head_center[1] - 2), 2)
        pygame.draw.circle(surface, (200, 100, 80), (head_center[0], head_center[1] + 3), 2)
