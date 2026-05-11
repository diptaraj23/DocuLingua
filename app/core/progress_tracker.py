"""Streamlit-independent progress tracking for guide generation."""

from __future__ import annotations

import time
from dataclasses import dataclass


ALLOWED_STATUSES = {"pending", "running", "completed", "failed", "fallback"}
STATUS_ICONS = {
    "pending": "⏳",
    "running": "🔄",
    "completed": "✅",
    "failed": "❌",
    "fallback": "⚠️",
}


@dataclass
class PipelineStep:
    """State and timing information for one pipeline step."""

    name: str
    status: str = "pending"
    started_at: float | None = None
    finished_at: float | None = None
    duration_seconds: float | None = None
    provider: str | None = None
    model: str | None = None
    error_message: str | None = None


class ProgressTracker:
    """Track pipeline step status, timing, provider, and model metadata."""

    def __init__(self, step_names: list[str]) -> None:
        self.steps = {name: PipelineStep(name=name) for name in step_names}

    def start_step(self, step_name: str) -> None:
        """Mark a step as running and record its start time."""

        step = self._get_step(step_name)
        step.status = "running"
        step.started_at = time.perf_counter()
        step.finished_at = None
        step.duration_seconds = None
        step.error_message = None

    def complete_step(
        self,
        step_name: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        """Mark a step as completed and record duration/provider metadata."""

        self._finish_step(step_name, "completed", provider=provider, model=model)

    def fail_step(self, step_name: str, error_message: str) -> None:
        """Mark a step as failed and record the error message."""

        self._finish_step(step_name, "failed", error_message=error_message)

    def mark_fallback(self, step_name: str, error_message: str | None = None) -> None:
        """Mark a step as completed through fallback content."""

        self._finish_step(
            step_name,
            "fallback",
            provider="Mock fallback",
            model="Local sample content",
            error_message=error_message,
        )

    def get_progress_fraction(self) -> float:
        """Return the fraction of steps that have reached a terminal status."""

        total = self.get_total_count()
        return self.get_completed_count() / total if total else 0.0

    def get_display_rows(self) -> list[dict]:
        """Return table-friendly rows with icon, status, timing, and provider data."""

        rows: list[dict] = []
        for step in self.steps.values():
            rows.append(
                {
                    "icon": STATUS_ICONS.get(step.status, ""),
                    "step": step.name,
                    "status": step.status,
                    "duration_seconds": (
                        round(step.duration_seconds, 2)
                        if step.duration_seconds is not None
                        else None
                    ),
                    "provider": step.provider or "",
                    "model": step.model or "",
                    "error": step.error_message or "",
                }
            )
        return rows

    def get_completed_count(self) -> int:
        """Return count of steps in terminal statuses."""

        return sum(
            1
            for step in self.steps.values()
            if step.status in {"completed", "failed", "fallback"}
        )

    def get_total_count(self) -> int:
        """Return total tracked step count."""

        return len(self.steps)

    def _finish_step(
        self,
        step_name: str,
        status: str,
        provider: str | None = None,
        model: str | None = None,
        error_message: str | None = None,
    ) -> None:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Unsupported progress status: {status}")
        step = self._get_step(step_name)
        step.status = status
        step.finished_at = time.perf_counter()
        if step.started_at is None:
            step.started_at = step.finished_at
        step.duration_seconds = step.finished_at - step.started_at
        if provider is not None:
            step.provider = provider
        if model is not None:
            step.model = model
        step.error_message = error_message

    def _get_step(self, step_name: str) -> PipelineStep:
        try:
            return self.steps[step_name]
        except KeyError as error:
            raise ValueError(f"Unknown pipeline step: {step_name}") from error
