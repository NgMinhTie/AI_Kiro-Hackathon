"""Immutable data models shared across the AutoSpec pipeline.

These mirror the data models in the design document. We keep them tiny and
dependency-free so the whole pipeline runs on the Python standard library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


class AgentError(Exception):
    """Raised by an agent when it cannot complete its stage."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(f"[{stage}] {message}")
        self.stage = stage
        self.message = message


@dataclass(frozen=True)
class Brief:
    """A plain-English product brief (the single pipeline input)."""

    text: str


@dataclass(frozen=True)
class RunConfig:
    """Run configuration: target language and coverage quality threshold."""

    tech_stack_preference: str
    quality_threshold: float

    def validate(self) -> List[str]:
        """Return a list of human-readable field errors. Empty list means valid."""
        errors: List[str] = []
        if self.tech_stack_preference not in ("Python", "Node"):
            errors.append(
                "Tech_Stack_Preference '%s' must be exactly 'Python' or 'Node'"
                % (self.tech_stack_preference,)
            )
        try:
            threshold = float(self.quality_threshold)
            if threshold < 0 or threshold > 100:
                errors.append(
                    "Quality_Threshold %s must be between 0 and 100 inclusive"
                    % (self.quality_threshold,)
                )
        except (TypeError, ValueError):
            errors.append(
                "Quality_Threshold '%s' must be a number" % (self.quality_threshold,)
            )
        return errors


@dataclass(frozen=True)
class AcceptanceCriterion:
    """A single Given/When/Then acceptance criterion."""

    id: str
    given: str
    when: str
    then: str

    def text(self) -> str:
        return "GIVEN %s WHEN %s THEN %s" % (self.given, self.when, self.then)


@dataclass(frozen=True)
class Requirement:
    """A numbered requirement with one or more acceptance criteria."""

    number: int
    title: str
    criteria: Tuple[AcceptanceCriterion, ...]


@dataclass(frozen=True)
class SpecDocument:
    """Structured specification produced by the Spec Agent."""

    requirements: Tuple[Requirement, ...]
    edge_cases: Tuple[str, ...]

    def all_criteria(self) -> Tuple[AcceptanceCriterion, ...]:
        out: List[AcceptanceCriterion] = []
        for req in self.requirements:
            out.extend(req.criteria)
        return tuple(out)


@dataclass(frozen=True)
class GeneratedCode:
    """A single generated Python module."""

    module_name: str
    source: str


@dataclass(frozen=True)
class TestSuite:
    """A single generated test file plus the criterion ids it covers."""

    source: str
    criterion_ids: Tuple[str, ...]


@dataclass(frozen=True)
class TestResult:
    """The outcome of one generated test, mapped to its acceptance criterion."""

    criterion_id: str
    name: str
    status: str  # "passed" | "failed"
    detail: str = ""


@dataclass(frozen=True)
class TestReport:
    """Pass/fail counts plus measured coverage for one run."""

    results: Tuple[TestResult, ...]
    passed: int
    failed: int
    coverage_percentage: Optional[float]
    quality_gate_status: Optional[str] = None
    coverage_note: Optional[str] = None


@dataclass(frozen=True)
class Gap:
    """One unmet acceptance criterion reported by the Review Agent."""

    criterion_id: str
    discrepancy: str


@dataclass(frozen=True)
class AlignmentVerdict:
    """The Review Agent's verdict: ALIGNED or NOT ALIGNED with gaps."""

    verdict: str
    gaps: Tuple[Gap, ...] = ()

    @property
    def aligned(self) -> bool:
        return self.verdict == "ALIGNED"
