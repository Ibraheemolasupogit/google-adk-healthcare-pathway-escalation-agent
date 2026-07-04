"""Security-oriented tests for Milestone 2 constraints."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_env_example_contains_placeholders_only() -> None:
    """Environment example should list empty placeholders only."""
    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8").splitlines()

    assert env_example == [
        "GOOGLE_API_KEY=",
        "GOOGLE_CLOUD_PROJECT=",
        "GOOGLE_CLOUD_LOCATION=",
        "GOOGLE_GENAI_USE_VERTEXAI=",
    ]


def test_no_google_adk_or_gemini_runtime_calls() -> None:
    """Milestone 2 must not add Google ADK or Gemini runtime usage."""
    py_files = [
        path
        for path in PROJECT_ROOT.glob("**/*.py")
        if "tests" not in path.relative_to(PROJECT_ROOT).parts
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in py_files)

    assert "google.adk" not in combined
    assert "genai.Client" not in combined
    assert "GOOGLE_API_KEY" not in combined


def test_generated_artifacts_are_ignored() -> None:
    """Generated assessment artifacts should not be tracked by default."""
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "artifacts/" in gitignore
