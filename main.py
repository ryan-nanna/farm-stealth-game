# main.py
# Entry point. Run with:  py -3.12 main.py

from __future__ import annotations

import math
import sys
from enum import Enum, auto

import pygame

from game.settings import (
    ESCALATION_MAX_ROUNDS,
    ESCALATION_SPEED_PER_ROUND,
    ESCALATION_VISION_PER_ROUND,
    HIERONYMUS_SPEED_CHASE,
    HIERONYMUS_SPEED_LURK,
    HIERONYMUS_VISION_RANGE,
    HUBERT_SPEED_CHASE,
    HUBERT_SPEED_LURK,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TARGET_FPS,
    VISION_CONE_RANGE,
    WINDOW_TITLE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from game.systems.camera import Camera
from game.entities.dealer import Hubert
from game.entities.hieronymus import Hieronymus
from game.entities.scrap_truck import ScrapTruck
from game.entities.gramps import Gramps
from game.entities.tractor import EyeState, Tractor
from game.level import Level
from game.systems.input import Action, InputManager
from game.systems.objectives import ObjectiveManager
from game.ui.hud import HUD
from game.ui.screens import CaughtScreen, TitleScreen, WinScreen


class GameState(Enum):
    TITLE   = auto()
    PLAYING = auto()
    CAUGHT  = auto()
    WIN     = auto()


def _make_hubert(round_num: int) -> Hubert:
    r = min(round_num - 1, ESCALATION_MAX_ROUNDS - 1)
    return Hubert(
        lurk_speed   = HUBERT_SPEED_LURK  + r * ESCALATION_SPEED_PER_ROUND,
        chase_speed  = HUBERT_SPEED_CHASE + r * ESCALATION_SPEED_PER_ROUND,
        vision_range = VISION_CONE_RANGE  + r * ESCALATION_VISION_PER_ROUND,
    )


def _make_hieronymus(round_num: int) -> Hieronymus:
    # Hieronymus joins in round 2; escalation still applies
    r = min(round_num - 1, ESCALATION_MAX_ROUNDS - 1)
    return Hieronymus(
        lurk_speed   = HIERONYMUS_SPEED_LURK  + r * ESCALATION_SPEED_PER_ROUND,
        chase_speed  = HIERONYMUS_SPEED_CHASE + r * ESCALATION_SPEED_PER_ROUND,
        vision_range = HIERONYMUS_VISION_RANGE + r * ESCALATION_VISION_PER_ROUND,
    )


def _desired_eye_state(
    tractor: Tractor,
    hubert: Hubert,
    hieronymus: Hieronymus | None,
    obj_manager: ObjectiveManager,
    game_state: GameState,
) -> EyeState:
    """Derive the correct eye state from current game context."""
    from game.entities.dealer import HubertState
    from game.entities.hieronymus import HieronymusState

    if game_state == GameState.CAUGHT:
        return EyeState.SHOCKED

    if obj_manager.just_completed is not None:
        return EyeState.HAPPY

    if obj_manager.active is not None:
        return EyeState.FOCUSED

    # Any dealer in ALERT or CHASE nearby?
    alert_states = {HubertState.ALERT, HubertState.CHASE}
    hubert_threatening = hubert.state in alert_states
    hiero_threatening  = (
        hieronymus is not None
        and hieronymus.state in {HieronymusState.ALERT, HieronymusState.CHASE}
    )
    # Also trigger WIDE when a dealer is in CURIOUS and close
    curious_states = {HubertState.CURIOUS, HubertState.SEARCHING}
    hubert_curious = hubert.state in curious_states
    hiero_curious  = (
        hieronymus is not None
        and hieronymus.state in {HieronymusState.CURIOUS, HieronymusState.SEARCHING}
    )
    hubert_close = math.hypot(
        hubert.center[0] - tractor.rect.centerx,
        hubert.center[1] - tractor.rect.centery,
    ) < 520
    hiero_close = (
        hieronymus is not None and math.hypot(
            hieronymus.center[0] - tractor.rect.centerx,
            hieronymus.center[1] - tractor.rect.centery,
        ) < 440
    )

    if hubert_threatening or hiero_threatening:
        return EyeState.WIDE
    if (hubert_curious and hubert_close) or (hiero_curious and hiero_close):
        return EyeState.WIDE
    if tractor.is_hidden:
        return EyeState.NERVOUS

    return EyeState.NORMAL


def main() -> None:
    pygame.init()

    screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # World surface — all game entities draw here; camera blits a viewport to screen
    world: pygame.Surface = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
    camera = Camera()

    clock         = pygame.time.Clock()
    input_manager = InputManager()
    level         = Level()
    gramps        = Gramps()
    caught_screen = CaughtScreen()
    win_screen    = WinScreen()
    title_screen  = TitleScreen()
    hud           = HUD()

    round_num: int = 1

    def _new_round() -> tuple[Hubert, Hieronymus | None, ScrapTruck | None, Tractor, ObjectiveManager]:
        hubert      = _make_hubert(round_num)
        hieronymus  = _make_hieronymus(round_num) if round_num >= 2 else None
        truck       = ScrapTruck(round_num)   # present every round, patrol pattern rotates
        tractor     = Tractor()
        obj_manager = ObjectiveManager(
            level.pig_pen_rect,
            level.cow_pasture_rect,
            level.scarecrow_rect,
        )
        return hubert, hieronymus, truck, tractor, obj_manager

    hubert, hieronymus, truck, tractor, obj_manager = _new_round()
    game_state = GameState.TITLE

    font = pygame.font.SysFont("Arial", 18)

    running: bool = True
    while running:
        dt: float = clock.tick(TARGET_FPS) / 1000.0

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        input_manager.update(events)
        inp = input_manager.state

        if inp.pressed(Action.QUIT):
            running = False

        # -------------------------------------------------------------------
        # Logic
        # -------------------------------------------------------------------

        if game_state == GameState.TITLE:
            title_screen.update(dt)
            if inp.pressed(Action.A) or inp.pressed(Action.START):
                game_state = GameState.PLAYING

        elif game_state == GameState.PLAYING:
            # Effective noise = tractor noise OR objective burst, whichever is louder
            effective_noise = max(tractor.noise_radius, obj_manager.burst_noise_radius)

            hubert.update(
                dt, tractor.rect, effective_noise,
                level.full_cover_rects, level.partial_cover_rects,
            )
            if hieronymus is not None:
                hieronymus.update(
                    dt, tractor.rect, effective_noise,
                    level.full_cover_rects, level.partial_cover_rects,
                )

            tractor.update(inp, dt, level.wall_rects, level.full_cover_rects, level.partial_cover_rects)
            obj_manager.update(tractor.rect, inp.is_held(Action.A), inp.pressed(Action.A), dt)

            if truck is not None:
                truck.update(dt, tractor.rect)

            # Eye state
            tractor.set_eye_state(
                _desired_eye_state(tractor, hubert, hieronymus, obj_manager, game_state)
            )

            caught = (
                hubert.caught_tractor
                or (hieronymus is not None and hieronymus.caught_tractor)
                or (truck is not None and truck.caught_tractor)
            )
            if caught:
                tractor.set_eye_state(EyeState.SHOCKED)
                game_state = GameState.CAUGHT
            elif obj_manager.all_complete and tractor.rect.colliderect(level.barn_rect):
                hubert.leave()
                if hieronymus is not None:
                    hieronymus.leave()
                if truck is not None:
                    truck.leave()
                game_state = GameState.WIN

        elif game_state == GameState.CAUGHT:
            tractor.set_eye_state(EyeState.SHOCKED)
            if inp.pressed(Action.A) or inp.pressed(Action.START):
                hubert, hieronymus, truck, tractor, obj_manager = _new_round()
                game_state = GameState.PLAYING

        elif game_state == GameState.WIN:
            hubert.update(
                dt, tractor.rect, tractor.noise_radius,
                level.full_cover_rects, level.partial_cover_rects,
            )
            if hieronymus is not None:
                hieronymus.update(
                    dt, tractor.rect, tractor.noise_radius,
                    level.full_cover_rects, level.partial_cover_rects,
                )
            if inp.pressed(Action.A) or inp.pressed(Action.START):
                round_num += 1
                hubert, hieronymus, truck, tractor, obj_manager = _new_round()
                game_state = GameState.PLAYING

        # -------------------------------------------------------------------
        # Draw — everything goes to `world`; camera blits viewport to screen
        # -------------------------------------------------------------------

        if game_state == GameState.TITLE:
            level.draw_ground(world)
            gramps.draw(world)
            level.draw_canopies(world)
            camera.update(tractor.rect)
            screen.blit(world, (0, 0), camera.viewport)
            title_screen.draw(screen)
        else:
            level.draw_ground(world)
            gramps.draw(world)
            hubert.draw(world)
            if hieronymus is not None:
                hieronymus.draw(world)
            if truck is not None:
                truck.draw(world)
            tractor.draw(world)
            level.draw_canopies(world)

            # Update camera to follow tractor (only in active play states)
            if game_state in (GameState.PLAYING, GameState.WIN):
                camera.update(tractor.rect)

            # Blit the camera viewport to the actual screen
            screen.blit(world, (0, 0), camera.viewport)

            dealer_positions = [hubert.rect.center]
            if hieronymus is not None:
                dealer_positions.append(hieronymus.rect.center)

            # HUD is drawn in screen space (not world space) — always on top
            if game_state in (GameState.PLAYING, GameState.WIN):
                hud.draw(
                    screen, obj_manager, tractor.noise_colour,
                    tractor.rect.center, dealer_positions,
                )

            if game_state == GameState.WIN:
                win_screen.draw(screen, round_num)
            elif game_state == GameState.CAUGHT:
                caught_screen.draw(screen)

            _draw_debug_hud(screen, font, input_manager, tractor, hubert, hieronymus, obj_manager, round_num, clock, truck)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


def _draw_debug_hud(
    screen:        pygame.Surface,
    font:          pygame.font.Font,
    input_manager: InputManager,
    tractor:       Tractor,
    hubert:        Hubert,
    hieronymus:    Hieronymus | None,
    obj_manager:   ObjectiveManager,
    round_num:     int,
    clock:         pygame.time.Clock,
    truck:         ScrapTruck | None = None,
) -> None:
    cover_label = "HIDDEN" if tractor.is_hidden else "partial" if tractor.in_partial_cover else "exposed"
    completed   = len(obj_manager.completed)
    hiero_state = hieronymus.state.name if hieronymus is not None else "—"
    truck_state = "active" if truck is not None else "—"

    lines = [
        f"FPS: {clock.get_fps():.0f}  Round: {round_num}",
        f"Pos: {tractor.rect.x}, {tractor.rect.y}",
        f"Cover: {cover_label}  Noise r: {int(tractor.noise_radius)}",
        f"Silent: {'ON' if tractor.silent_mode else 'off'}  Eyes: {tractor.eye_state.name}",
        f"Hubert: {hubert.state.name}",
        f"Hieronymus: {hiero_state}   Truck: {truck_state}",
        f"Objectives: {completed}/3  Intel: {'ON' if obj_manager.intel_active else 'off'}",
        f"Burst noise: {int(obj_manager.burst_noise_radius)}",
        f"Controller: {input_manager._joystick.get_name() if input_manager._joystick else 'keyboard only'}",
        "",
        "Arrows / D-pad: move   Shift / B: silent",
        "Space / A: interact    Esc: quit",
    ]
    for i, line in enumerate(lines):
        text_surf   = font.render(line, True, (255, 255, 255))
        shadow_surf = font.render(line, True, (0, 0, 0))
        screen.blit(shadow_surf, (11, 11 + i * 22))
        screen.blit(text_surf,   (10, 10 + i * 22))


if __name__ == "__main__":
    main()
