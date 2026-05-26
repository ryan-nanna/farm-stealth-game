# game/ui/screens.py
# Full-screen overlays: caught, win, pause. (Win and pause are stubbed for later sessions.)

from __future__ import annotations

import pygame

from game.settings import SCREEN_HEIGHT, SCREEN_WIDTH


class CaughtScreen:
    """
    Friendly overlay shown when the dealer catches the tractor.
    Not scary — warm colours, big text, clear restart prompt.
    """

    def __init__(self) -> None:
        self._font_big   = pygame.font.SysFont("Arial", 80, bold=True)
        self._font_mid   = pygame.font.SysFont("Arial", 36)
        self._font_small = pygame.font.SysFont("Arial", 26)

        # Dark warm overlay so the game world is still visible underneath
        self._overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self._overlay.fill((30, 0, 0, 180))

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._overlay, (0, 0))

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        oh_no  = self._font_big.render("OH NO!",                         True, (255, 220, 60))
        sub    = self._font_mid.render("They spotted the tractor!",       True, (255, 255, 255))
        hint   = self._font_small.render("Press Space / A to try again",  True, (200, 200, 200))

        surface.blit(oh_no, oh_no.get_rect(center=(cx, cy - 70)))
        surface.blit(sub,   sub.get_rect(center=(cx, cy + 20)))
        surface.blit(hint,  hint.get_rect(center=(cx, cy + 70)))


class WinScreen:
    """
    Celebratory overlay shown when the tractor returns to Gramps.
    Warm and cheerful — never scary.
    """

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

        hooray = self._font_big.render("HOORAY!",                            True, (255, 230, 60))
        sub    = self._font_mid.render("Gramps is so happy!",                True, (255, 255, 255))
        rounds = self._font_mid.render(f"Round {round_num} complete!",       True, (180, 255, 180))
        hint   = self._font_small.render("Press Space / A for next round",   True, (200, 200, 200))

        surface.blit(hooray, hooray.get_rect(center=(cx, cy - 80)))
        surface.blit(sub,    sub.get_rect(center=(cx, cy + 10)))
        surface.blit(rounds, rounds.get_rect(center=(cx, cy + 55)))
        surface.blit(hint,   hint.get_rect(center=(cx, cy + 105)))
