# main.py
# Entry point. Run with:  py -3.12 main.py

from __future__ import annotations

import sys

import pygame

from game.settings import (
    DEALER1_PATROL_WAYPOINTS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TARGET_FPS,
    WINDOW_TITLE,
)
from game.entities.dealer import Dealer
from game.entities.tractor import Tractor
from game.level import Level
from game.systems.input import Action, InputManager


def main() -> None:
    pygame.init()

    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    clock: pygame.time.Clock = pygame.time.Clock()
    input_manager = InputManager()
    level         = Level()
    dealer        = Dealer(waypoints=DEALER1_PATROL_WAYPOINTS)
    tractor       = Tractor()

    # Small debug font — shows controller status and speed mode in the corner
    font = pygame.font.SysFont("Arial", 18)

    running: bool = True
    while running:
        dt: float = clock.tick(TARGET_FPS) / 1000.0  # seconds since last frame

        # --- Event pump ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # --- Input ---
        input_manager.update(events)
        inp = input_manager.state

        if inp.pressed(Action.QUIT):
            running = False

        # --- Logic ---
        dealer.update(dt)
        tractor.update(inp, dt, level.wall_rects, level.full_cover_rects, level.partial_cover_rects)

        # --- Draw ---
        level.draw_ground(screen)
        dealer.draw(screen)   # cone drawn first (inside dealer.draw), then body
        tractor.draw(screen)
        level.draw_canopies(screen)

        # Debug overlay — controller + silent mode status
        _draw_debug_hud(screen, font, input_manager, tractor, clock)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def _draw_debug_hud(
    screen:        pygame.Surface,
    font:          pygame.font.Font,
    input_manager: InputManager,
    tractor:       Tractor,
    clock:         pygame.time.Clock,
) -> None:
    """
    Minimal on-screen info while there's no real HUD yet.
    Displayed in the top-left corner; will be removed once hud.py exists.
    """
    if tractor.is_hidden:
        cover_label = "HIDDEN"
    elif tractor.in_partial_cover:
        cover_label = "partial"
    else:
        cover_label = "exposed"

    lines = [
        f"FPS: {clock.get_fps():.0f}",
        f"Pos: {tractor.rect.x}, {tractor.rect.y}",
        f"Cover: {cover_label}",
        f"Silent: {'ON' if tractor.silent_mode else 'off'}",
        f"Controller: {input_manager._joystick.get_name() if input_manager._joystick else 'keyboard only'}",
        "",
        "Arrow keys / D-pad: move",
        "Shift / B: silent mode",
        "Esc: quit",
    ]
    for i, line in enumerate(lines):
        text_surf = font.render(line, True, (255, 255, 255))
        # Thin shadow for legibility over any background colour
        shadow_surf = font.render(line, True, (0, 0, 0))
        screen.blit(shadow_surf, (11, 11 + i * 22))
        screen.blit(text_surf,   (10, 10 + i * 22))


if __name__ == "__main__":
    main()
