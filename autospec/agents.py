"""The four specialised agents. Deterministic (offline) implementations that
mirror the LLM-backed agents described in the design, so the demo always runs.
"""

from __future__ import annotations

import os
from typing import Dict, List, Sequence, Tuple

from .models import (
    AgentError,
    AlignmentVerdict,
    Brief,
    GeneratedCode,
    Gap,
    SpecDocument,
    TestReport,
    TestSuite,
)
from . import templates


class SpecAgent:
    """Turns a brief into a structured Spec_Document. Writes no code."""

    name = "Spec Agent"

    def run(self, brief: Brief) -> SpecDocument:
        if not brief.text or not brief.text.strip():
            raise AgentError("Spec", "the brief is empty or non-actionable")
        return templates.tip_calculator_spec()


class BuildAgent:
    """Generates a single Python module from the spec.

    First attempt (no gaps) omits input validation on purpose; when the Review
    Agent reports gaps, the rebuild addresses them (the self-correcting loop).
    """

    name = "Build Agent"

    def run(self, spec: SpecDocument, gaps: Sequence[Gap] = ()) -> GeneratedCode:
        if not spec.requirements:
            raise AgentError("Build", "the spec contains zero requirements")
        source = templates.FIXED_SOURCE if gaps else templates.BUGGY_SOURCE
        return GeneratedCode(module_name="solution", source=source)


class TestAgent:
    """Writes one pytest-style test per acceptance criterion, runs them, and
    reports pass/fail counts plus measured coverage."""

    name = "Test Agent"

    def __init__(self, run_dir: str) -> None:
        self.run_dir = run_dir

    def run(self, spec: SpecDocument, code: GeneratedCode) -> Tuple[TestSuite, TestReport]:
        if spec is None or not spec.requirements:
            raise AgentError("Test", "missing or invalid spec")
        if code is None or not code.source.strip():
            raise AgentError("Test", "missing or invalid generated code")
        from .runner import run_suite  # local import keeps module load fast

        criterion_map = {
            "test_criterion_%s" % cid: cid for cid in templates.CRITERION_IDS
        }
        suite = TestSuite(
            source=templates.TEST_SOURCE, criterion_ids=templates.CRITERION_IDS
        )
        report = run_suite(code.source, templates.TEST_SOURCE, self.run_dir, criterion_map)
        return suite, report


class ReviewAgent:
    """Checks every acceptance criterion and emits an alignment verdict."""

    name = "Review Agent"

    def run(
        self, spec: SpecDocument, code: GeneratedCode, report: TestReport
    ) -> AlignmentVerdict:
        missing = []
        if spec is None:
            missing.append("spec")
        if code is None:
            missing.append("code")
        if report is None:
            missing.append("report")
        if missing:
            raise AgentError("Review", "missing inputs: %s" % ", ".join(missing))

        status_by_criterion: Dict[str, List[str]] = {}
        for result in report.results:
            status_by_criterion.setdefault(result.criterion_id, []).append(result.status)

        gaps: List[Gap] = []
        for criterion in spec.all_criteria():
            statuses = status_by_criterion.get(criterion.id, [])
            met = bool(statuses) and all(s == "passed" for s in statuses)
            if not met:
                reason = (
                    "no test maps to this criterion"
                    if not statuses
                    else "test(s) failed for this criterion"
                )
                gaps.append(Gap(criterion_id=criterion.id, discrepancy=reason))

        if gaps:
            return AlignmentVerdict(verdict="NOT ALIGNED", gaps=tuple(gaps))
        return AlignmentVerdict(verdict="ALIGNED", gaps=())
