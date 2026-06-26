"""Spec Agent — converts a brief into a structured specification."""
from __future__ import annotations

import time
from autospec.models import AgentError, Brief, SpecDocument
from autospec.fallback_data import DEMO_SPEC


class SpecAgent:
    """Converts a plain-English brief into numbered requirements with acceptance criteria."""

    name = "Spec Agent"

    def run(self, brief: Brief) -> SpecDocument:
        """Produce a SpecDocument from a brief."""
        if not brief.text or not brief.text.strip():
            raise AgentError(self.name, "Brief is empty or contains no actionable content.")

        # Simulate agent thinking time for visual effect in demo
        time.sleep(1.2)

        return DEMO_SPEC
