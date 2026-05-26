# game/systems/state_machine.py
# Generic finite-state machine used by enemy NPCs.
# Tracks the current state and time spent in it; callers own all transition logic.

from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

S = TypeVar("S", bound=Enum)


class StateMachine(Generic[S]):
    """
    Minimal state container: holds the current state and a per-state timer.
    Call tick(dt) each frame, then read time_in_state to drive transitions.
    Calling transition() resets the timer so time_in_state always measures
    how long the machine has been in its *current* state.
    """

    def __init__(self, initial: S) -> None:
        self.state: S = initial
        self._timer: float = 0.0

    def transition(self, new_state: S) -> None:
        if new_state is not self.state:
            self.state = new_state
            self._timer = 0.0

    def tick(self, dt: float) -> None:
        self._timer += dt

    @property
    def time_in_state(self) -> float:
        return self._timer
