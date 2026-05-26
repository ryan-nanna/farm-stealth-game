# game/ui/hud.py
from __future__ import annotations

import pygame

from game.settings import (
    COLOUR_BARN_RED,
    COLOUR_NOISE_FAST,
    COLOUR_NOISE_SLOW,
    COLOUR_NOISE_STILL,
    COLOUR_STONE,
    MAP_BARN_RECT,
    MAP_WALL_CENTRE_RECT,
    MAP_WALL_LEFT_RECT,
    MAP_WALL_RIGHT_RECT,
    MINIMAP_BG_COLOUR,
    MINIMAP_BORDER_COLOUR,
    MINIMAP_DEALER_COLOUR,
    MINIMAP_H,
    MINIMAP_SCALE,
    MINIMAP_TRACTOR_COLOUR,
    MINIMAP_W,
    MINIMAP_X,
    MINIMAP_Y,
    SCREEN_WIDTH,
)
from game.systems.objectives import ObjectiveManager, ObjectiveType


_OBJ_LABELS: dict[ObjectiveType, str] = {
    ObjectiveType.PIGS:      "Feed the pigs",
    ObjectiveType.COWS:      "Help with cows",
    ObjectiveType.SCARECROW: "Find scarecrow",
}

_NOISE_LABELS: dict[tuple[int, int, int] | None, str] = {
    None:              "Hidden",
    COLOUR_NOISE_STILL: "Still",
    COLOUR_NOISE_SLOW:  "Slow",
    COLOUR_NOISE_FAST:  "Fast",
}

_PANEL_X  = SCREEN_WIDTH - 235
_PANEL_Y  = 8
_PANEL_W  = 225
_CHECKLIST_ROWS = 3
_ROW_H    = 26


class HUD:
    """
    Draws:
    - Objective checklist with dark panel background (top-right)
    - Noise level colour dot below the checklist
    - Timing bar (bottom-centre, delegated to ObjectiveManager)
    - "Return to Gramps!" prompt (top-centre) once all objectives complete
    - Intel mini-map (top-right, below checklist) while intel is active
    """

    def __init__(self) -> None:
        self._font_sm  = pygame.font.SysFont("Arial", 18)
        self._font_big = pygame.font.SysFont("Arial", 32, bold=True)
        self._minimap_surf = pygame.Surface((MINIMAP_W, MINIMAP_H))

    def draw(
        self,
        surface:      pygame.Surface,
        obj_manager:  ObjectiveManager,
        noise_colour: tuple[int, int, int] | None,
        tractor_pos:  tuple[int, int],
        dealer_pos:   tuple[int, int],
    ) -> None:
        self._draw_checklist(surface, obj_manager, noise_colour)
        obj_manager.draw(surface)

        if obj_manager.all_complete:
            self._draw_return_prompt(surface)

        if obj_manager.intel_active:
            self._draw_intel_minimap(surface, tractor_pos, dealer_pos)

    # ------------------------------------------------------------------

    def _draw_checklist(
        self,
        surface:      pygame.Surface,
        obj_manager:  ObjectiveManager,
        noise_colour: tuple[int, int, int] | None,
    ) -> None:
        panel_h = _CHECKLIST_ROWS * _ROW_H + _ROW_H + 12   # items + noise row + padding
        panel = pygame.Surface((_PANEL_W, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 130))
        surface.blit(panel, (_PANEL_X - 4, _PANEL_Y - 4))

        x = _PANEL_X
        y = _PANEL_Y + 4

        for obj_type in obj_manager.order:
            done   = obj_type in obj_manager.completed
            tick   = "[x]" if done else "[ ]"
            label  = _OBJ_LABELS[obj_type]
            colour = (120, 220, 120) if done else (230, 230, 230)
            text   = self._font_sm.render(f"{tick} {label}", True, colour)
            shadow = self._font_sm.render(f"{tick} {label}", True, (0, 0, 0))
            surface.blit(shadow, (x + 1, y + 1))
            surface.blit(text,   (x, y))
            y += _ROW_H

        # Noise dot + label
        dot_colour = noise_colour if noise_colour is not None else (60, 60, 60)
        pygame.draw.circle(surface, dot_colour, (x + 8, y + 9), 7)
        pygame.draw.circle(surface, (0, 0, 0), (x + 8, y + 9), 7, 1)
        noise_label = _NOISE_LABELS.get(noise_colour, "?")
        n_text   = self._font_sm.render(f"Noise: {noise_label}", True, (200, 200, 200))
        n_shadow = self._font_sm.render(f"Noise: {noise_label}", True, (0, 0, 0))
        surface.blit(n_shadow, (x + 20, y + 1))
        surface.blit(n_text,   (x + 19, y))

    def _draw_return_prompt(self, surface: pygame.Surface) -> None:
        msg    = "Return to Gramps!"
        shadow = self._font_big.render(msg, True, (0, 0, 0))
        text   = self._font_big.render(msg, True, (255, 230, 60))
        cx = SCREEN_WIDTH // 2
        surface.blit(shadow, shadow.get_rect(center=(cx + 2, 32)))
        surface.blit(text,   text.get_rect(center=(cx, 30)))

    def _draw_intel_minimap(
        self,
        surface:     pygame.Surface,
        tractor_pos: tuple[int, int],
        dealer_pos:  tuple[int, int],
    ) -> None:
        s  = MINIMAP_SCALE
        mm = self._minimap_surf
        mm.fill(MINIMAP_BG_COLOUR)

        # Stone wall segments
        for wall_data in (MAP_WALL_LEFT_RECT, MAP_WALL_CENTRE_RECT, MAP_WALL_RIGHT_RECT):
            wx, wy, ww, wh = wall_data
            pygame.draw.rect(mm, COLOUR_STONE,
                pygame.Rect(int(wx * s), int(wy * s), max(1, int(ww * s)), max(2, int(wh * s))))

        # Barn
        bx, by, bw, bh = MAP_BARN_RECT
        pygame.draw.rect(mm, COLOUR_BARN_RED,
            pygame.Rect(int(bx * s), int(by * s), max(2, int(bw * s)), max(2, int(bh * s))))

        # Tractor (grey dot)
        pygame.draw.circle(mm, MINIMAP_TRACTOR_COLOUR,
            (int(tractor_pos[0] * s), int(tractor_pos[1] * s)), 4)

        # Dealer (red dot — the intel payoff)
        pygame.draw.circle(mm, MINIMAP_DEALER_COLOUR,
            (int(dealer_pos[0] * s), int(dealer_pos[1] * s)), 5)

        surface.blit(mm, (MINIMAP_X, MINIMAP_Y))
        pygame.draw.rect(surface, MINIMAP_BORDER_COLOUR,
            pygame.Rect(MINIMAP_X - 1, MINIMAP_Y - 1, MINIMAP_W + 2, MINIMAP_H + 2), 2)

        label  = self._font_sm.render("INTEL", True, MINIMAP_BORDER_COLOUR)
        lshadow = self._font_sm.render("INTEL", True, (0, 0, 0))
        surface.blit(lshadow, (MINIMAP_X + 2, MINIMAP_Y - 21))
        surface.blit(label,   (MINIMAP_X + 1, MINIMAP_Y - 22))
