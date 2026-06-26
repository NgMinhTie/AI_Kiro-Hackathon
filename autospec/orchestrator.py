"""The orchestrator: sequences the agents, streams handoffs, runs the
bounded self-correcting retry loop, applies the quality gate, and persists
all artifacts."""

from __future__ import annotations

import dataclasses
import json
import os
import time
from typing import Callable, List, Optional

from .agents import BuildAgent, ReviewAgent, SpecAgent, TestAgent
from .models import (
    AgentError,
    AlignmentVerdict,
    Brief,
    Gap,
    RunConfig,
    SpecDocument,
    TestReport,
)

Emit = Callable[[str, dict], None]


def _spec_to_markdown(spec: SpecDocument) -> str:
    lines = ["# Generated Specification", ""]
    for req in spec.requirements:
        lines.append("## Requirement %d: %s" % (req.number, req.title))
        for crit in req.criteria:
            lines.append("- **AC %s** — %s" % (crit.id, crit.text()))
        lines.append("")
    lines.append("## Edge Cases")
    for edge in spec.edge_cases:
        lines.append("- %s" % edge)
    return "\n".join(lines)


def apply_quality_gate(report: TestReport, threshold: Optional[float]) -> TestReport:
    """Compare coverage against the threshold and record the gate status."""
    if threshold is None:
        return dataclasses.replace(
            report, quality_gate_status="error", coverage_note="no threshold configured"
        )
    if report.coverage_percentage is None:
        return dataclasses.replace(
            report, quality_gate_status="not met", coverage_note="coverage unavailable"
        )
    status = "met" if report.coverage_percentage >= threshold else "not met"
    return dataclasses.replace(report, quality_gate_status=status)


class Orchestrator:
    """Coordinates the whole pipeline from a single (brief, config) input."""

    def __init__(
        self,
        artifact_dir: str,
        emit: Optional[Emit] = None,
        retry_limit: int = 3,
        step_delay: float = 0.0,
        demo_retry: bool = False,
    ) -> None:
        self.artifact_dir = artifact_dir
        self.emit = emit or (lambda etype, data: None)
        self.retry_limit = retry_limit
        self.step_delay = step_delay
        self.demo_retry = demo_retry
        os.makedirs(artifact_dir, exist_ok=True)

    # -- persistence -------------------------------------------------------
    def _persist(self, name: str, content: str) -> None:
        path = os.path.join(self.artifact_dir, name)
        try:
            with open(path, "w") as fh:
                fh.write(content)
            self.emit("artifact_saved", {"name": name, "path": path})
        except OSError as exc:  # keep going even if one write fails
            self.emit("error", {"agent": "ArtifactStore", "message": str(exc)})

    def _pause(self) -> None:
        if self.step_delay:
            time.sleep(self.step_delay)

    # -- main run ----------------------------------------------------------
    def run(self, brief: Optional[Brief], config: Optional[RunConfig]) -> dict:
        self.emit("run_start", {"artifact_dir": self.artifact_dir})

        # Pre-flight: presence + config validation (no stage runs if invalid).
        if brief is None:
            return self._fail("missing Brief")
        if config is None:
            return self._fail("missing Run_Config")
        config_errors = config.validate()
        if config_errors:
            return self._fail("invalid Run_Config: " + "; ".join(config_errors))

        try:
            spec_agent = SpecAgent()
            build_agent = BuildAgent()
            test_agent = TestAgent(self.artifact_dir)
            review_agent = ReviewAgent(force_fail_first=self.demo_retry)

            # Stage 1: Spec (runs once).
            self.emit("stage_start", {"agent": spec_agent.name})
            self._pause()
            spec = spec_agent.run(brief)
            spec_md = _spec_to_markdown(spec)
            self.emit(
                "stage_output",
                {
                    "agent": spec_agent.name,
                    "title": "%d requirements, %d acceptance criteria"
                    % (len(spec.requirements), len(spec.all_criteria())),
                    "content": spec_md,
                },
            )
            self._persist("spec_document.md", spec_md)
            self.emit("handoff", {"from": spec_agent.name, "to": build_agent.name})

            gaps: List[Gap] = []
            attempt = 0
            verdict: Optional[AlignmentVerdict] = None
            report: Optional[TestReport] = None
            code = None
            suite = None

            while True:
                # Stage 2: Build.
                self.emit("stage_start", {"agent": build_agent.name})
                self._pause()
                code = build_agent.run(spec, gaps)
                self.emit(
                    "stage_output",
                    {
                        "agent": build_agent.name,
                        "title": "generated solution.py (%d lines)"
                        % (code.source.count("\n") + 1),
                        "content": code.source,
                        "kind": "python",
                    },
                )
                self._persist("generated_code.py", code.source)
                self.emit("handoff", {"from": build_agent.name, "to": test_agent.name})

                # Stage 3: Test.
                self.emit("stage_start", {"agent": test_agent.name})
                self._pause()
                suite, report = test_agent.run(spec, code)
                report = apply_quality_gate(report, config.quality_threshold)
                self.emit(
                    "stage_output",
                    {
                        "agent": test_agent.name,
                        "title": "%d passed, %d failed · coverage %.1f%% (gate: %s)"
                        % (
                            report.passed,
                            report.failed,
                            report.coverage_percentage or 0.0,
                            report.quality_gate_status,
                        ),
                        "content": suite.source,
                        "kind": "python",
                        "results": [
                            {
                                "criterion_id": r.criterion_id,
                                "name": r.name,
                                "status": r.status,
                                "detail": r.detail,
                            }
                            for r in report.results
                        ],
                    },
                )
                self._persist("test_suite.py", suite.source)
                self._persist("test_report.json", _report_json(report))
                self.emit("handoff", {"from": test_agent.name, "to": review_agent.name})

                # Stage 4: Review.
                self.emit("stage_start", {"agent": review_agent.name})
                self._pause()
                verdict = review_agent.run(spec, code, report)
                self.emit(
                    "verdict",
                    {
                        "verdict": verdict.verdict,
                        "coverage": report.coverage_percentage,
                        "gate": report.quality_gate_status,
                        "passed": report.passed,
                        "failed": report.failed,
                        "attempt": attempt,
                        "gaps": [
                            {"id": g.criterion_id, "discrepancy": g.discrepancy}
                            for g in verdict.gaps
                        ],
                    },
                )
                self._persist("alignment_verdict.json", _verdict_json(verdict, report))

                if verdict.aligned or attempt >= self.retry_limit:
                    break

                attempt += 1
                gaps = list(verdict.gaps)
                self.emit(
                    "reattempt",
                    {
                        "attempt": attempt,
                        "limit": self.retry_limit,
                        "gaps": [
                            {"id": g.criterion_id, "discrepancy": g.discrepancy}
                            for g in gaps
                        ],
                    },
                )
                self.emit("handoff", {"from": review_agent.name, "to": build_agent.name})

            status = "completed"
            self.emit(
                "done",
                {
                    "status": status,
                    "verdict": verdict.verdict if verdict else None,
                    "reattempts": attempt,
                    "coverage": report.coverage_percentage if report else None,
                },
            )
            return {"status": status, "verdict": verdict, "reattempts": attempt}

        except AgentError as exc:
            return self._fail(str(exc), agent=exc.stage)

    def _fail(self, message: str, agent: str = "Orchestrator") -> dict:
        self.emit("error", {"agent": agent, "message": message})
        self.emit("done", {"status": "failed", "error": message})
        return {"status": "failed", "error": message}


def _report_json(report: TestReport) -> str:
    return json.dumps(
        {
            "passed": report.passed,
            "failed": report.failed,
            "coverage_percentage": report.coverage_percentage,
            "quality_gate_status": report.quality_gate_status,
            "coverage_note": report.coverage_note,
            "results": [
                {
                    "criterion_id": r.criterion_id,
                    "name": r.name,
                    "status": r.status,
                    "detail": r.detail,
                }
                for r in report.results
            ],
        },
        indent=2,
    )


def _verdict_json(verdict: AlignmentVerdict, report: TestReport) -> str:
    return json.dumps(
        {
            "verdict": verdict.verdict,
            "coverage_percentage": report.coverage_percentage,
            "quality_gate_status": report.quality_gate_status,
            "gaps": [
                {"criterion_id": g.criterion_id, "discrepancy": g.discrepancy}
                for g in verdict.gaps
            ],
        },
        indent=2,
    )
