"""Console streaming for observable agent handoffs (R8).

The ConsoleStreamer prints richly formatted banners, handoff arrows, re-attempt
notices, and the final verdict to stdout so the four-agent relay is visible
during a live demo. Every line is mirrored into an in-memory transcript buffer
so the orchestrator can persist it as run_log.txt.
"""
from __future__ import annotations

from typing import List, Sequence

# Box-drawing widths for banners.
_WIDTH = 70


class ConsoleStreamer:
    """Streams agent output, handoffs, re-attempts, and errors to the console.

    All emitted lines are also appended to an internal transcript so the run
    can be replayed from run_log.txt.
    """

    def __init__(self, use_color: bool = True) -> None:
        """Create a streamer.

        Args:
            use_color: When True, wrap banners in ANSI color codes for a more
                striking live demo. Disable for plain transcripts/tests.
        """
        self.use_color = use_color
        self._transcript: List[str] = []

    # ----- public API (R8) -------------------------------------------------

    def emit_banner(self, run_id: str) -> None:
        """Print the top-of-run banner naming the run id."""
        self._line("")
        self._line("=" * _WIDTH)
        self._line(self._center("AUTOSPEC PIPELINE"))
        self._line(self._center("run " + run_id))
        self._line("=" * _WIDTH)

    def emit_output(self, agent: str, output: str) -> None:
        """Print the full output produced by an agent before any handoff (R8.1).

        Args:
            agent: The display name of the agent that just completed.
            output: The complete textual output the agent produced.
        """
        self._line("")
        self._line("┌" + "─" * (_WIDTH - 1))
        self._line("│ ▶ {0}  ·  completed".format(agent.upper()))
        self._line("└" + "─" * (_WIDTH - 1))
        for raw in output.splitlines() or [""]:
            self._line("   " + raw)

    def emit_handoff(self, from_agent: str, to_agent: str, note: str = "") -> None:
        """Print a handoff label naming both producing and receiving agent (R8.2).

        Args:
            from_agent: The agent that produced the output.
            to_agent: The agent that receives the output.
            note: Optional suffix (e.g. "gaps") shown in the label.
        """
        suffix = " ({0})".format(note) if note else ""
        label = "  HANDOFF: {0}  ──▶  {1}{2}".format(from_agent, to_agent, suffix)
        self._line("")
        self._line("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        self._line(label)
        self._line("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    def emit_reattempt(self, attempt: int, gaps: Sequence) -> None:
        """Print a re-attempt notice with the attempt number and each gap (R8.3).

        Args:
            attempt: The 1-based re-attempt number.
            gaps: The Gap objects that triggered the re-attempt; each gap's
                criterion id and discrepancy are listed.
        """
        self._line("")
        self._line("!! RE-ATTEMPT {0}/3 triggered. Gaps:".format(attempt))
        for gap in gaps:
            self._line("   - [{0}] {1}".format(gap.criterion_id, gap.discrepancy))

    def emit_verdict(self, verdict: str, coverage, gate_status) -> None:
        """Print the final verdict banner with coverage and gate status."""
        cov = "n/a" if coverage is None else "{0:.0f}%".format(coverage)
        gate = gate_status if gate_status else "n/a"
        self._line("")
        self._line("=" * _WIDTH)
        self._line(
            self._center(
                "VERDICT: {0}  ·  coverage {1}  ·  gate: {2}".format(
                    verdict, cov, gate
                )
            )
        )
        self._line("=" * _WIDTH)

    def emit_error(self, agent: str, message: str) -> None:
        """Print an error message identifying the agent that failed (R8.4).

        Args:
            agent: The agent/stage that failed.
            message: The failure description.
        """
        self._line("")
        self._line("XX ERROR in {0}: {1}".format(agent, message))

    # ----- transcript ------------------------------------------------------

    def transcript(self) -> str:
        """Return the full streamed transcript as a single string (for run_log.txt)."""
        return "\n".join(self._transcript) + "\n"

    # ----- internals -------------------------------------------------------

    def _center(self, text: str) -> str:
        return text.center(_WIDTH)

    def _line(self, text: str) -> None:
        # Always store the plain text in the transcript; print (optionally
        # colorized) to the live console.
        self._transcript.append(text)
        print(text, flush=True)
