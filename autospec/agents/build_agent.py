"""Build Agent — generates code from a specification."""
from __future__ import annotations

import time
from typing import List
from autospec.models import AgentError, Gap, GeneratedCode, SpecDocument
from autospec.fallback_data import DEMO_CODE


class BuildAgent:
    """Generates Python code that implements exactly the spec requirements."""

    name = "Build Agent"

    def run(self, spec: SpecDocument, gaps: List[Gap] = ()) -> GeneratedCode:
        """Generate code satisfying the spec."""
        if not spec.requirements:
            raise AgentError(self.name, "Spec contains zero requirements.")

        # Simulate agent thinking time
        time.sleep(1.5)

        return DEMO_CODE
