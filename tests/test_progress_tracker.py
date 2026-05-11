from app.core.progress_tracker import ProgressTracker


def test_tracker_initializes_steps_as_pending() -> None:
    tracker = ProgressTracker(["A", "B"])

    rows = tracker.get_display_rows()

    assert [row["status"] for row in rows] == ["pending", "pending"]
    assert tracker.get_progress_fraction() == 0


def test_start_step_marks_running() -> None:
    tracker = ProgressTracker(["A"])

    tracker.start_step("A")

    row = tracker.get_display_rows()[0]
    assert row["status"] == "running"
    assert row["icon"] == "🔄"


def test_complete_step_records_duration_provider_and_model() -> None:
    tracker = ProgressTracker(["A"])

    tracker.start_step("A")
    tracker.complete_step("A", provider="Groq", model="model-a")

    row = tracker.get_display_rows()[0]
    assert row["status"] == "completed"
    assert row["icon"] == "✅"
    assert row["duration_seconds"] is not None
    assert row["provider"] == "Groq"
    assert row["model"] == "model-a"
    assert tracker.get_completed_count() == 1
    assert tracker.get_progress_fraction() == 1


def test_fail_step_marks_failed() -> None:
    tracker = ProgressTracker(["A"])

    tracker.start_step("A")
    tracker.fail_step("A", "boom")

    row = tracker.get_display_rows()[0]
    assert row["status"] == "failed"
    assert row["icon"] == "❌"
    assert row["error"] == "boom"


def test_mark_fallback_marks_fallback() -> None:
    tracker = ProgressTracker(["A"])

    tracker.start_step("A")
    tracker.mark_fallback("A", "provider failed")

    row = tracker.get_display_rows()[0]
    assert row["status"] == "fallback"
    assert row["icon"] == "⚠️"
    assert row["provider"] == "Mock fallback"
    assert row["error"] == "provider failed"
