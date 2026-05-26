# game/systems/input.py
# InputManager: translates raw Pygame events (keyboard + USB NES joystick)
# into abstract game actions.
#
# WHY abstract actions instead of raw keys?
# The rest of the game never needs to know whether the player pressed an arrow
# key or tilted a d-pad — it just asks "is UP held?" or "was A_PRESS fired?".
# This makes adding/remapping controls trivial in one place.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

import pygame

from game.settings import (
    AXIS_DEADZONE,
    CONTROLLER_AXIS_X,
    CONTROLLER_AXIS_Y,
    CONTROLLER_BUTTON_A,
    CONTROLLER_BUTTON_B,
    CONTROLLER_BUTTON_SELECT,
    CONTROLLER_BUTTON_START,
)


# ---------------------------------------------------------------------------
# Action catalogue
# ---------------------------------------------------------------------------

class Action(Enum):
    """Every abstract input the game cares about."""
    UP     = auto()
    DOWN   = auto()
    LEFT   = auto()
    RIGHT  = auto()
    A      = auto()   # Interact / hold to complete objective
    B      = auto()   # Brake + silence engine
    START  = auto()   # Pause
    SELECT = auto()   # Scarecrow intel overlay
    QUIT   = auto()   # Escape key — exit game


# ---------------------------------------------------------------------------
# Frame snapshot
# ---------------------------------------------------------------------------

@dataclass
class InputState:
    """
    Immutable snapshot of input for a single frame.
    held   — actions currently pressed/held down
    just_pressed  — actions that became active THIS frame
    just_released — actions that were released THIS frame
    """
    held:          frozenset[Action] = field(default_factory=frozenset)
    just_pressed:  frozenset[Action] = field(default_factory=frozenset)
    just_released: frozenset[Action] = field(default_factory=frozenset)

    def is_held(self, action: Action) -> bool:
        return action in self.held

    def pressed(self, action: Action) -> bool:
        """True only on the first frame the action was activated."""
        return action in self.just_pressed

    def released(self, action: Action) -> bool:
        return action in self.just_released

    @property
    def move_vector(self) -> tuple[float, float]:
        """
        Returns a (dx, dy) direction tuple in the range [-1, 1] per axis.
        Diagonal movement is allowed; normalisation happens in the tractor entity.
        """
        dx = (1.0 if Action.RIGHT in self.held else 0.0) - (1.0 if Action.LEFT in self.held else 0.0)
        dy = (1.0 if Action.DOWN  in self.held else 0.0) - (1.0 if Action.UP   in self.held else 0.0)
        return (dx, dy)


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class InputManager:
    """
    Polls keyboard and the first detected USB joystick each frame.
    Call update() once per frame, then read via .state.
    """

    # Keyboard → Action mapping
    _KEY_MAP: dict[int, Action] = {
        pygame.K_UP:        Action.UP,
        pygame.K_DOWN:      Action.DOWN,
        pygame.K_LEFT:      Action.LEFT,
        pygame.K_RIGHT:     Action.RIGHT,
        pygame.K_SPACE:     Action.A,
        pygame.K_LSHIFT:    Action.B,
        pygame.K_RSHIFT:    Action.B,
        pygame.K_RETURN:    Action.START,
        pygame.K_TAB:       Action.SELECT,
        pygame.K_ESCAPE:    Action.QUIT,
    }

    def __init__(self) -> None:
        self._joystick: pygame.joystick.JoystickType | None = None
        self._prev_held: set[Action] = set()
        self.state: InputState = InputState()

        self._init_joystick()

    # ------------------------------------------------------------------
    # Joystick lifecycle
    # ------------------------------------------------------------------

    def _init_joystick(self) -> None:
        """Attempt to grab the first available joystick."""
        pygame.joystick.init()
        count = pygame.joystick.get_count()
        if count > 0:
            self._joystick = pygame.joystick.Joystick(0)
            self._joystick.init()
            print(f"[Input] Controller connected: {self._joystick.get_name()}")
        else:
            print("[Input] No controller found — keyboard only.")

    def refresh_joystick(self) -> None:
        """
        Call this when a JOYDEVICEADDED or JOYDEVICEREMOVED event fires
        so the manager picks up hot-plugged controllers.
        """
        if self._joystick:
            self._joystick.quit()
            self._joystick = None
        self._init_joystick()

    # ------------------------------------------------------------------
    # Per-frame update
    # ------------------------------------------------------------------

    def update(self, events: list[pygame.event.EventType]) -> None:
        """
        Build this frame's InputState from raw pygame events + key/axis state.
        Must be called once per frame AFTER pygame.event.get().
        """
        # Check for hot-plug events
        for event in events:
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self.refresh_joystick()

        current_held: set[Action] = set()

        # --- Keyboard held state ---
        keys = pygame.key.get_pressed()
        for key, action in self._KEY_MAP.items():
            if keys[key]:
                current_held.add(action)

        # --- Joystick state ---
        if self._joystick:
            current_held |= self._read_joystick()

        # Derive just_pressed / just_released by diffing against previous frame
        just_pressed  = current_held - self._prev_held
        just_released = self._prev_held - current_held

        self.state = InputState(
            held          = frozenset(current_held),
            just_pressed  = frozenset(just_pressed),
            just_released = frozenset(just_released),
        )

        self._prev_held = current_held

    # ------------------------------------------------------------------
    # Joystick → actions
    # ------------------------------------------------------------------

    def _read_joystick(self) -> set[Action]:
        """
        Translate joystick axes, hat switch, and buttons into Actions.
        Handles both hat-based d-pads and axis-based d-pads (device-dependent).
        """
        actions: set[Action] = set()
        joy = self._joystick

        # Hat switch (most NES-style USB pads expose the d-pad as hat 0)
        if joy.get_numhats() > 0:
            hat_x, hat_y = joy.get_hat(0)
            if hat_x == -1: actions.add(Action.LEFT)
            if hat_x ==  1: actions.add(Action.RIGHT)
            # Pygame hat y: +1 is UP (opposite of screen y)
            if hat_y ==  1: actions.add(Action.UP)
            if hat_y == -1: actions.add(Action.DOWN)

        # Axis fallback (some controllers expose d-pad as axes 0/1)
        if joy.get_numaxes() > max(CONTROLLER_AXIS_X, CONTROLLER_AXIS_Y):
            ax = joy.get_axis(CONTROLLER_AXIS_X)
            ay = joy.get_axis(CONTROLLER_AXIS_Y)
            if ax < -AXIS_DEADZONE: actions.add(Action.LEFT)
            if ax >  AXIS_DEADZONE: actions.add(Action.RIGHT)
            if ay < -AXIS_DEADZONE: actions.add(Action.UP)
            if ay >  AXIS_DEADZONE: actions.add(Action.DOWN)

        # Buttons
        btn_map: dict[int, Action] = {
            CONTROLLER_BUTTON_A:      Action.A,
            CONTROLLER_BUTTON_B:      Action.B,
            CONTROLLER_BUTTON_START:  Action.START,
            CONTROLLER_BUTTON_SELECT: Action.SELECT,
        }
        for btn_idx, action in btn_map.items():
            if btn_idx < joy.get_numbuttons() and joy.get_button(btn_idx):
                actions.add(action)

        return actions

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        joy_name = self._joystick.get_name() if self._joystick else "none"
        return f"<InputManager controller='{joy_name}'>"
