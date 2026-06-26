"""CLI entry point: `python -m autospec` runs the built-in demo end to end."""

from __future__ import annotations

import os
import time

from .demo import DEFAULT_RUN_CONFIG, DEMO_BRIEF
from .orchestrator import Orchestrator


def _print_emit(etype: str, data: dict) -> None:
    if etype == "stage_start":
        print("\n[%s] working..." % data["agent"])
    elif etype == "stage_output":
        print("  -> %s" % data.get("title", ""))
    elif etype == "handoff":
        print("  ---- HANDOFF: %s -> %s ----" % (data["from"], data["to"]))
    elif etype == "reattempt":
        gaps = ", ".join("[%s] %s" % (g["id"], g["discrepancy"]) for g in data["gaps"])
        print("\n!! RE-ATTEMPT %d/%d. Gaps: %s" % (data["attempt"], data["limit"], gaps))
    elif etype == "verdict":
        print(
            "\n==== VERDICT: %s · coverage %s%% (gate: %s) ===="
            % (data["verdict"], data["coverage"], data["gate"])
        )
    elif etype == "error":
        print("  !! ERROR [%s]: %s" % (data["agent"], data["message"]))
    elif etype == "done":
        print("\nPipeline %s after %s re-attempt(s)." % (data["status"], data.get("reattempts", 0)))


def main() -> None:
    run_id = time.strftime("%Y%m%d-%H%M%S")
    artifact_dir = os.path.join("artifacts", run_id)
    Orchestrator(artifact_dir=artifact_dir, emit=_print_emit, step_delay=0.0).run(
        DEMO_BRIEF, DEFAULT_RUN_CONFIG
    )
    print("\nArtifacts written to %s/" % artifact_dir)


if __name__ == "__main__":
    main()
