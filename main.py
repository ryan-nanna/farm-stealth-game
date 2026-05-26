# main.py
# Entry point. Run with:  py -3.12 main.py

from __future__ import annotations

import sys
from enum import Enum, auto

import pygame

from game.settings import (
    DEALER1_PATROL_WAYPOINTS,
    DEALER1_SPEED_CHASE,
    DEALER1_SPEED_PATROL,
    ESCALATION_MAX_ROUNDS,
    ESCALATION_SPEED_PER_ROUND,
    ESCALATION_VISION_PER_ROUND,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TARGET_FPS,
    VISION_CONE_RANGE,
    WINDOW_TITLE,
)
from game.entities.dealer import Dealer
from game.entities.gramps import Gramps
from game.entities.tractor import Tractor
from game.level import Level
from game.systems.input import Action, InputManager
from game.systems.objectives import ObjectiveManager
from game.ui.hud import HUD
from game.ui.screens import CaughtScreen, WinScreen


class GameState(Enum):
    PLAYING = auto()
    CAUGHT  = auto()
    WIN     = auto()


def _make_dealer(round_num: int) -> Dealer:
    """Create a dealer with speeds and vision scaled to the current round."""
    r = min(round_num - 1, ESCALATION_MAX_ROUNDS - 1)
    return Dealer(
        waypoints    = DEALER1_PATROL_WAYPOINTS,
        patrol_speed = DEALER1_SPEED_PATROL + r * ESCALATION_SPEED_PER_ROUND,
        chase_speed  = DEALER1_SPEED_CHASE  + r * ESCALATION_SPEED_PER_ROUND,
        vision_range = VISION_CONE_RANGE    + r * ESCALATION_VISION_PER_ROUND,
    )


def main() -> None:
    pygame.init()

    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    clock: pygame.time.Clock = pygame.time.Clock()
    input_manager = InputManager()
    level         = Level()
    gramps        = Gramps()
    caught_screen = CaughtScreen()
    win_screen    = WinScreen()
    hud           = HUD()

    round_num: int = 1

    def _new_round() -> tuple[Dealer, Tractor, ObjectiveManager]:
        return (
            _make_dealer(round_num),
            Tractor(),
            ObjectiveManager(level.pig_pen_rect, level.cow_pasture_rect, level.scarecrow_rect),
        )

    dealer, tractor, obj_manager = _new_round()
    game_state = GameState.PLAYING

    font = pygame.font.SysFont("Arial", 18)

    running: bool = True
    while running:
        dt: float = clock.tick(TARGET_FPS) / 1000.0

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
        if game_state == GameState.PLAYING:
            dealer.update(
                dt, tractor.rect, tractor.noise_radius,
                level.full_cover_rects, level.partial_cover_rects,
            )
            tractor.update(inp, dt, level.wall_rects, level.full_cover_rects, level.partial_cover_rects)
            obj_manager.update(
                tractor.rect,
                inp.is_held(Action.A),
                inp.pressed(Action.A),
                dt,
            )

            if dealer.caught_tractor:
                game_state = GameState.CAUGHT
            elif obj_manager.all_complete and tractor.rect.colliderect(level.barn_rect):
                dealer.leave()
                game_state = GameState.WIN

        elif game_state == GameState.CAUGHT:
            if inp.pressed(Action.A) or inp.pressed(Action.START):
                dealer, tractor, obj_manager = _new_round()
                game_state = GameState.PLAYING

        elif game_state == GameState.WIN:
            # Keep dealer walking off while the win screen is shown
            dealer.update(
                dt, tractor.rect, tractor.noise_radius,
                level.full_cover_rects, level.partial_cover_rects,
            )
            if inp.pressed(Action.A) or inp.pressed(Action.START):
                round_num += 1
                dealer, tractor, obj_manager = _new_round()
                game_state = GameState.PLAYING

        # --- Draw ---
        level.draw_ground(screen)
        gramps.draw(screen)
        dealer.draw(screen)
        tractor.draw(screen)
        level.draw_canopies(screen)

        if game_state == GameState.PLAYING:
            hud.draw(screen, obj_manager, tractor.noise_colour, tractor.rect.center, dealer.rect.center)
        elif game_state == GameState.WIN:
            hud.draw(screen, obj_manager, tractor.noise_colour, tractor.rect.center, dealer.rect.center)
            win_screen.draw(screen, round_num)
        elif game_state == GameState.CAUGHT:
            caught_screen.draw(screen)

        _draw_debug_hud(screen, font, input_manager, tractor, dealer, obj_manager, round_num, clock)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def _draw_debug_hud(
    screen:        pygame.Surface,
    font:          pygame.font.Font,
    input_manager: InputManager,
    tractor:       Tractor,
    dealer:        Dealer,
    obj_manager:   ObjectiveManager,
    round_num:     int,
    clock:         pygame.time.Clock,
) -> None:
    cover_label = "HIDDEN" if tractor.is_hidden else "partial" if tractor.in_partial_cover else "exposed"
    completed   = len(obj_manager.completed)

    lines = [
        f"FPS: {clock.get_fps():.0f}  Round: {round_num}",
        f"Pos: {tractor.rect.x}, {tractor.rect.y}",
        f"Cover: {cover_label}  Noise r: {int(tractor.noise_radius)}",
        f"Silent: {'ON' if tractor.silent_mode else 'off'}",
        f"Dealer: {dealer.state.name}",
        f"Objectives: {completed}/3  Intel: {'ON' if obj_manager.intel_active else 'off'}",
        f"Controller: {input_manager._joystick.get_name() if input_manager._joystick else 'keyboard only'}",
        "",
        "Arrow keys / D-pad: move",
        "Shift / B: silent mode",
        "Space / A: interact",
        "Esc: quit",
    ]
    for i, line in enumerate(lines):
        text_surf   = font.render(line, True, (255, 255, 255))
        shadow_surf = font.render(line, True, (0, 0, 0))
        screen.blit(shadow_surf, (11, 11 + i * 22))
        screen.blit(text_surf,   (10, 10 + i * 22))


if __name__ == "__main__":
    main()
