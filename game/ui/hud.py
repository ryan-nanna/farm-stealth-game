# game/ui/hud.py
from __future__ import annotations

import pygame

from game.settings import SCREEN_WIDTH
from game.systems.objectives import ObjectiveManager, ObjectiveType


_OBJ_LABELS: dict[ObjectiveType, str] = {
    ObjectiveType.PIGS:      "Feed the pigs",
    ObjectiveType.COWS:      "Help with cows",
    ObjectiveType.SCARECROW: "Find scarecrow",
}


class HUD:
    """
    Draws:
    - Objective checklist (top-right corner)
    - Active timing bar (bottom-centre, delegated to ObjectiveManager)
    - "Return to Gramps!" prompt (top-centre) once all objectives complete
    - Intel active indicator (below objective list)
    """

    def __init__(self) -> None:
        self._font      = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_sm   = pygame.font.SysFont("Arial", 18)
        self._font_big  = pygame.font.SysFont("Arial", 32, bold=True)

    def draw(self, surface: pygame.Surface, obj_manager: ObjectiveManager) -> None:
        self._draw_checklist(surface, obj_manager)
        obj_manager.draw(surface)   # timing bar

        if obj_manager.all_complete:
            self._draw_return_prompt(surface)
        elif obj_manager.intel_active:
            self._draw_intel_indicator(surface)

    # ------------------------------------------------------------------

    def _draw_checklist(self, surface: pygame.Surface, obj_manager: ObjectiveManager) -> None:
        x = SCREEN_WIDTH - 230
        y = 12
        for obj_type in obj_manager.order:
            done  = obj_type in obj_manager.completed
            tick  = "[x]" if done else "[ ]"
            label = _OBJ_LABELS[obj_type]
            colour = (120, 220, 120) if done else (230, 230, 230)
            text = self._font_sm.render(f"{tick} {label}", True, colour)
            shadow = self._font_sm.render(f"{tick} {label}", True, (0, 0, 0))
            surface.blit(shadow, (x + 1, y + 1))
            surface.blit(text,   (x, y))
            y += 26

    def _draw_return_prompt(self, surface: pygame.Surface) -> None:
        msg    = "Return to Gramps!"
        shadow = self._font_big.render(msg, True, (0, 0, 0))
        text   = self._font_big.render(msg, True, (255, 230, 60))
        cx = SCREEN_WIDTH // 2
        surface.blit(shadow, shadow.get_rect(center=(cx + 2, 32)))
        surface.blit(text,   text.get_rect(center=(cx, 30)))

    def _draw_intel_indicator(self, surface: pygame.Surface) -> None:
        msg    = "Intel: dealer positions revealed!"
        shadow = self._font_sm.render(msg, True, (0, 0, 0))
        text   = self._font_sm.render(msg, True, (80, 200, 255))
        cx = SCREEN_WIDTH // 2
        surface.blit(shadow, shadow.get_rect(center=(cx + 1, 57)))
        surface.blit(text,   text.get_rect(center=(cx, 56)))
