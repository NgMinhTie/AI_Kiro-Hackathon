"""Typed error model for AutoSpec agents."""
from __future__ import annotations


class AgentError(Exception):
    """Raised by an agent when it cannot complete its stage.

    Attributes:
        stage: The name of the agent/stage that failed (e.g. "Spec Agent").
        message: A human-readable description of the failure.
    """

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage}] {message}")
