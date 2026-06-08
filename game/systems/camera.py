# game/systems/camera.py
# Scrolling camera that tracks the tractor across the 2×-sized world.
#
# Usage pattern (main.py):
#   world = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
#   camera = Camera()
#
#   # each frame:
#   level.draw_ground(world)
#   entities.draw(world)
#   camera.update(tractor.rect)
#   screen.blit(world, (0, 0), camera.viewport)
#   hud.draw(screen, ...)        # HUD stays in screen space

from __future__ import annotations

import pygame

from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT


class Camera:
    """
    Centres the viewport on a target rect, clamped to world bounds.
    No smoothing — snaps immediately. Feels right for a young player
    who needs precise feedback on where they are.
    """

    def __init__(self) -> None:
        self._x: float = 0.0
        self._y: float = 0.0

    def update(self, target: pygame.Rect) -> None:
        """Re-centre on target each frame."""
        self._x = target.centerx - SCREEN_WIDTH  // 2
        self._y = target.centery - SCREEN_HEIGHT // 2
        # Clamp so the viewport never shows outside the world
        self._x = max(0.0, min(self._x, WORLD_WIDTH  - SCREEN_WIDTH))
        self._y = max(0.0, min(self._y, WORLD_HEIGHT - SCREEN_HEIGHT))

    @property
    def viewport(self) -> pygame.Rect:
        """The world-space rectangle that maps to the screen this frame."""
        return pygame.Rect(int(self._x), int(self._y), SCREEN_WIDTH, SCREEN_HEIGHT)

    @property
    def offset(self) -> tuple[int, int]:
        """Subtract from a world coord to get the screen coord."""
        return (int(self._x), int(self._y))
