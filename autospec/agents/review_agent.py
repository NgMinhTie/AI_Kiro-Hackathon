"""Review Agent — checks spec-to-code alignment."""
from __future__ import annotations

import time
from autospec.models import AgentError, AlignmentVerdict, Gap, GeneratedCode, SpecDocument, TestReport
from autospec.fallback_data import DEMO_VERDICT


class ReviewAgent:
    """Audits generated code and test results against the spec."""

    name = "Review Agent"

    def __init__(self, force_fail_first: bool = False) -> None:
        self._force_fail_first = force_fail_first
        self._call_count = 0

    def run(self, spec: SpecDocument, code: GeneratedCode, report: TestReport) -> AlignmentVerdict:
        """Produce an alignment verdict."""
        if not spec:
            raise AgentError(self.name, "Spec is missing.")
        if not code:
            raise AgentError(self.name, "Generated code is missing.")
        if not report:
            raise AgentError(self.name, "Test report is missing.")

        time.sleep(1.0)
        self._call_count += 1

        # Demo mode: fail on first attempt to show the self-correcting loop
        if self._force_fail_first and self._call_count == 1:
            return AlignmentVerdict(
                verdict="NOT ALIGNED",
                gaps=(
                    Gap(criterion_id="5.1", discrepancy="Edge case for non-integer people not handled"),
                    Gap(criterion_id="6.1", discrepancy="Negative tip percentage not rejected"),
                ),
            )

        return DEMO_VERDICT
