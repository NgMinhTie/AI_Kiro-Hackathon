"""Artifact persistence for AutoSpec (R9).

ArtifactStore writes each artifact to a per-run directory, creating the
directory if needed. A failed write never aborts the run: the content is kept
in memory and an error-flagged PersistResult is returned so the orchestrator
can continue persisting the remaining artifacts.
"""
from __future__ import annotations

import os
from typing import Dict

from .models import PersistResult


class ArtifactStore:
    """Persists run artifacts to a directory on disk."""

    def __init__(self, artifact_dir: str) -> None:
        """Create a store rooted at the given Artifact_Directory.

        Args:
            artifact_dir: The directory all artifacts for this run are written to.
        """
        self.artifact_dir = artifact_dir
        # Retained content for any artifact whose write failed (R9.7).
        self.retained: Dict[str, str] = {}

    def persist(self, name: str, content: str) -> PersistResult:
        """Write a single artifact to the Artifact_Directory.

        Creates the directory if it does not exist (R9.6) and writes a
        non-empty file (R9.1-R9.5). On any failure the content is retained in
        memory and an error-flagged PersistResult is returned without raising
        (R9.7).

        Args:
            name: The artifact file name (e.g. "spec_document.json").
            content: The textual content to write; must be non-empty.

        Returns:
            A PersistResult describing success or failure.
        """
        try:
            if content is None or content == "":
                raise ValueError("refusing to persist empty content")
            os.makedirs(self.artifact_dir, exist_ok=True)
            path = os.path.join(self.artifact_dir, name)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            return PersistResult(name=name, path=path, ok=True, error=None)
        except Exception as exc:  # noqa: BLE001 - persistence must never crash the run
            self.retained[name] = content
            return PersistResult(
                name=name,
                path=None,
                ok=False,
                error="failed to persist '{0}': {1}".format(name, exc),
            )
