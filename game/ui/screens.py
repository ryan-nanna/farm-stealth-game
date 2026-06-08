# game/ui/screens.py
# Full-screen overlays: title, caught, win.

from __future__ import annotations

import math

import pygame

from game.settings import (
    COLOUR_BARN_RED,
    COLOUR_GRASS_GREEN,
    COLOUR_WARM_GREY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TRACTOR_HEADLIGHT_COLOUR,
)


class TitleScreen:
    """
    First screen the player sees. Tractor peeks around the barn corner.
    Press Space / A to start.
    """

    def __init__(self) -> None:
        self._font_title = pygame.font.SysFont("Arial", 90, bold=True)
        self._font_sub   = pygame.font.SysFont("Arial", 28)
        self._font_hint  = pygame.font.SysFont("Arial", 24)
        self._t: float   = 0.0   # drives the tractor peek animation

        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((15, 40, 15, 220))

    def update(self, dt: float) -> None:
        self._t += dt

    def draw(self, surface: pygame.Surface) -> None:
        # Dark green overlay over the game world
        surface.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH // 2

        # Title
        title  = self._font_title.render("Farm Stealth", True, (255, 230, 60))
        shadow = self._font_title.render("Farm Stealth", True, (0, 0, 0))
        surface.blit(shadow, shadow.get_rect(center=(cx + 3, 183)))
        surface.blit(title,  title.get_rect(center=(cx, 180)))

        # Subtitle
        sub = self._font_sub.render("Help the little grey tractor complete his chores!", True, (200, 230, 200))
        surface.blit(sub, sub.get_rect(center=(cx, 270)))

        # Tractor peeking around the right edge of a barn shape
        self._draw_peeking_tractor(surface)

        # Hint — gentle pulse
        alpha = int(180 + 70 * math.sin(self._t * 2.5))
        hint_surf = pygame.Surface((500, 40), pygame.SRCALPHA)
        hint_text = self._font_hint.render("Press  Space / A  to begin", True, (255, 255, 255))
        hint_text.set_alpha(alpha)
        surface.blit(hint_text, hint_text.get_rect(center=(cx, SCREEN_HEIGHT - 80)))

    def _draw_peeking_tractor(self, surface: pygame.Surface) -> None:
        """A small barn shape on the right, with the tractor peeking around its left edge."""
        # How far the tractor has peeked out — bounces gently
        peek = int(28 + 12 * math.sin(self._t * 1.8))

        # Barn block
        barn_x = SCREEN_WIDTH - 220
        barn_y = SCREEN_HEIGHT // 2 - 80
        barn_w = 220
        barn_h = 200
        pygame.draw.rect(surface, COLOUR_BARN_RED, (barn_x, barn_y, barn_w, barn_h), border_radius=6)
        # Roof ridge stripe
        pygame.draw.rect(surface, (255, 255, 255),
                         (barn_x + 10, barn_y + barn_h // 2 - 6, barn_w - 20, 12))
        # Barn doors
        door_w, door_h = 44, 55
        door_x = barn_x + barn_w // 2 - door_w // 2
        door_y = barn_y + barn_h - door_h
        pygame.draw.rect(surface, (60, 30, 20), (door_x, door_y, door_w, door_h))
        pygame.draw.line(surface, (40, 20, 10),
                         (door_x + door_w // 2, door_y),
                         (door_x + door_w // 2, door_y + door_h), 2)

        # Tractor body peeking from behind the barn's left edge
        tx = barn_x - peek
        ty = barn_y + barn_h // 2 - 20
        tw, th = 48, 40
        # Only draw the visible part (clip to screen and past barn edge)
        tractor_rect = pygame.Rect(tx, ty, tw, th)
        pygame.draw.rect(surface, COLOUR_WARM_GREY, tractor_rect, border_radius=6)
        # Headlight eyes
        hl_x = tractor_rect.right - 6
        for hl_y in (tractor_rect.y + 8, tractor_rect.bottom - 12):
            pygame.draw.circle(surface, TRACTOR_HEADLIGHT_COLOUR, (hl_x, hl_y), 4)
            pygame.draw.circle(surface, (40, 30, 10), (hl_x, hl_y), 2)


class CaughtScreen:
    """Friendly overlay shown when a dealer catches the tractor. Not scary."""

    def __init__(self) -> None:
        self._font_big   = pygame.font.SysFont("Arial", 80, bold=True)
        self._font_mid   = pygame.font.SysFont("Arial", 36)
        self._font_small = pygame.font.SysFont("Arial", 26)

        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((30, 0, 0, 180))

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        oh_no = self._font_big.render("OH NO!",                        True, (255, 220, 60))
        sub   = self._font_mid.render("They spotted the tractor!",     True, (255, 255, 255))
        hint  = self._font_small.render("Press Space / A to try again",True, (200, 200, 200))

        surface.blit(oh_no, oh_no.get_rect(center=(cx, cy - 70)))
        surface.blit(sub,   sub.get_rect(center=(cx, cy + 20)))
        surface.blit(hint,  hint.get_rect(center=(cx, cy + 70)))


class WinScreen:
    """Celebratory overlay shown when the tractor returns to Gramps."""

    def __init__(self) -> None:
        self._font_big   = pygame.font.SysFont("Arial", 80, bold=True)
        self._font_mid   = pygame.font.SysFont("Arial", 36)
        self._font_small = pygame.font.SysFont("Arial", 26)

        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((0, 40, 0, 180))

    def draw(self, surface: pygame.Surface, round_num: int) -> None:
        surface.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        hooray = self._font_big.render("HOORAY!",                          True, (255, 230, 60))
        sub    = self._font_mid.render("Gramps is so happy!",              True, (255, 255, 255))
        rounds = self._font_mid.render(f"Round {round_num} complete!",     True, (180, 255, 180))
        hint   = self._font_small.render("Press Space / A for next round", True, (200, 200, 200))

        surface.blit(hooray, hooray.get_rect(center=(cx, cy - 80)))
        surface.blit(sub,    sub.get_rect(center=(cx, cy + 10)))
        surface.blit(rounds, rounds.get_rect(center=(cx, cy + 55)))
        surface.blit(hint,   hint.get_rect(center=(cx, cy + 105)))
