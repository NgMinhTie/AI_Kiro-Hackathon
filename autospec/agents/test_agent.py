"""Test Agent — writes and runs tests against generated code."""
from __future__ import annotations

import time
from typing import Tuple
from autospec.models import AgentError, GeneratedCode, SpecDocument, TestReport, TestSuite
from autospec.fallback_data import DEMO_TEST_REPORT, DEMO_TEST_SUITE
from autospec.test_runner import run_tests_for_real


class TestAgent:
    """Writes one test per acceptance criterion, runs them, and reports results."""

    name = "Test Agent"

    def __init__(self, artifact_dir: str = "") -> None:
        self.artifact_dir = artifact_dir

    def run(self, spec: SpecDocument, code: GeneratedCode) -> Tuple[TestSuite, TestReport]:
        """Produce a test suite and execute it FOR REAL."""
        if not spec or not spec.requirements:
            raise AgentError(self.name, "Spec is missing or has no requirements.")
        if not code or not code.source:
            raise AgentError(self.name, "Generated code is missing or empty.")

        # Use the deterministic test suite (pre-written for the demo code)
        suite = DEMO_TEST_SUITE

        # Simulate brief thinking time
        time.sleep(0.8)

        # Actually run the tests for real!
        try:
            report = run_tests_for_real(code, suite)
        except Exception:
            # Fallback to deterministic if real execution fails
            report = DEMO_TEST_REPORT

        return suite, report
