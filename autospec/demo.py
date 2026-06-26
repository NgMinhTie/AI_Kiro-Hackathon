"""Built-in demo brief and default configuration for the tip-calculator sample run."""
from __future__ import annotations

from autospec.models import Brief, RunConfig

DEMO_BRIEF = Brief(
    text=(
        "Build a tip calculator that takes a bill total, a tip percentage, and a number of "
        "people, and returns the tip amount, the total with tip, and the amount each person "
        "owes. Round money to 2 decimal places. The grand total is split evenly between people. "
        "0% tip is allowed (tip = 0). Number of people must be at least 1; reject 0 or negative."
    )
)

DEFAULT_RUN_CONFIG = RunConfig(
    tech_stack_preference="Python",
    quality_threshold=90
)
