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
        "GOOGLE_GENAI_MODEL=",
    ]


def test_no_direct_gemini_client_or_hardcoded_secret_values() -> None:
    """Milestone 3 must not create direct Gemini clients or hardcode secrets."""
    py_files = [
        path
        for path in PROJECT_ROOT.glob("**/*.py")
        if "tests" not in path.relative_to(PROJECT_ROOT).parts
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in py_files)

    assert "genai.Client" not in combined
    assert "AIza" not in combined
    assert "secret-value" not in combined.replace('"secret-value"', "")


def test_generated_artifacts_are_ignored() -> None:
    """Generated assessment artifacts should not be tracked by default."""
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "artifacts/" in gitignore
