"""Validate the Milestone 8 Kaggle submission package."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.case_tools import get_case_by_id  # noqa: E402
from tools.exceptions import CaseNotFoundError  # noqa: E402

PRIMARY_CASE_ID = "SYN-CANCER-62-003"
WRITEUP_MIN_WORDS = 1500
WRITEUP_MAX_WORDS = 2300
VIDEO_MAX_WORDS = 780
REQUIRED_SUBMISSION_FILES = [
    "submission/kaggle-writeup.md",
    "submission/title-options.md",
    "submission/elevator-pitch.md",
    "submission/course-concept-mapping.md",
    "submission/architecture-summary.md",
    "submission/video-script.md",
    "submission/video-recording-plan.md",
    "submission/video-shot-list.md",
    "submission/screenshot-plan.md",
    "submission/cover-image-brief.md",
    "submission/demo-commands.md",
    "submission/results-summary.md",
    "submission/responsible-ai.md",
    "submission/final-submission-checklist.md",
    "submission/github-metadata.md",
]
REQUIRED_DOCUMENTATION_FILES = [
    "docs/vibe-coding-workflow.md",
    "docs/development-assistants.md",
    "docs/skills-showcase.md",
    "docs/evidence/antigravity/README.md",
]
README_REQUIRED_SECTIONS = [
    "Quick Demo",
    "Kaggle Submission",
    "Acknowledgements",
    "Security and Responsible AI",
    "Development Approach: Spec-Driven Vibe Coding",
    "Disclaimer",
]
README_REQUIRED_LINKS = [
    "docs/vibe-coding-workflow.md",
    "docs/development-assistants.md",
    "docs/skills-showcase.md",
    "docs/evidence/antigravity/README.md",
]
SUBMISSION_REQUIRED_LANGUAGE = {
    "submission/kaggle-writeup.md": ["synthetic", "does not provide clinical advice"],
    "submission/video-script.md": ["synthetic", "does not call Gemini"],
    "submission/results-summary.md": ["controlled synthetic", "not production"],
    "submission/responsible-ai.md": ["synthetic", "human review"],
    "submission/final-submission-checklist.md": ["No secrets", "No unsupported claims"],
}
FORBIDDEN_CREDENTIAL_PATTERNS = [
    re.compile("AI" + r"za[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:api[_-]?key|password|secret)\s*[:=]\s*['\"][^'\"]+['\"]", re.I),
]
FAKE_URL_PATTERNS = [
    re.compile(r"https?://(?:example\.com|youtu\.be/TODO|youtube\.com/TODO)", re.I),
    re.compile(r"https?://(?:kaggle\.com/TODO|your-|placeholder)", re.I),
]
UNSUPPORTED_CLAIMS = [
    re.compile(r"\bdeployed to Cloud Run\b", re.I),
    re.compile(r"\bCloud Run deployment succeeded\b", re.I),
    re.compile(r"\blive Gemini (?:execution )?(?:was )?verified\b", re.I),
    re.compile(r"\bconnected to live NHS systems\b", re.I),
]
ANTIGRAVITY_UNSUPPORTED_CLAIMS = [
    re.compile(r"\bAntigravity\s+is\s+(?:a\s+)?runtime dependenc", re.I | re.S),
    re.compile(
        r"\bAntigravity\b.{0,80}\bbuilt "
        r"(?:the )?(?:entire|whole) (?:repo|repository|application|app)\b",
        re.I | re.S,
    ),
    re.compile(
        r"\b(?:repo|repository|application|app)\b"
        r".{0,80}\bbuilt entirely\b.{0,80}\bAntigravity\b",
        re.I | re.S,
    ),
    re.compile(
        r"\bAntigravity\s+is\s+required (?:at runtime|for deployment|to run)\b",
        re.I | re.S,
    ),
]
PROHIBITED_DATA_KEYS = {
    "nhs_number",
    "date_of_birth",
    "dob",
    "patient_name",
    "hospital_number",
    "address",
}


def main() -> int:
    """Run final submission validation."""
    errors: list[str] = []
    errors.extend(_required_files())
    errors.extend(_required_documentation())
    errors.extend(_writeup_word_count())
    errors.extend(_video_length())
    errors.extend(_readme_sections())
    errors.extend(_readme_links())
    errors.extend(_evidence_snapshot())
    errors.extend(_required_language())
    errors.extend(_scan_public_files())
    errors.extend(_development_tooling_claims())
    errors.extend(_runtime_artifacts())
    errors.extend(_data_keys())
    errors.extend(_primary_case())
    errors.extend(_presentation_mode())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Milestone 8 final submission check passed.")
    return 0


def _required_files() -> list[str]:
    return [
        f"missing required submission file: {path}"
        for path in REQUIRED_SUBMISSION_FILES
        if not (PROJECT_ROOT / path).exists()
    ]


def _required_documentation() -> list[str]:
    return [
        f"missing required documentation file: {path}"
        for path in REQUIRED_DOCUMENTATION_FILES
        if not (PROJECT_ROOT / path).exists()
    ]


def _writeup_word_count() -> list[str]:
    path = PROJECT_ROOT / "submission/kaggle-writeup.md"
    if not path.exists():
        return []
    count = _word_count(path.read_text(encoding="utf-8"))
    if count < WRITEUP_MIN_WORDS or count > WRITEUP_MAX_WORDS:
        return [
            f"kaggle write-up word count {count} is outside {WRITEUP_MIN_WORDS}-{WRITEUP_MAX_WORDS}"
        ]
    return []


def _video_length() -> list[str]:
    path = PROJECT_ROOT / "submission/video-script.md"
    if not path.exists():
        return []
    count = _word_count(path.read_text(encoding="utf-8"))
    if count > VIDEO_MAX_WORDS:
        return [f"video script word count {count} is above estimated five-minute limit"]
    return []


def _readme_sections() -> list[str]:
    text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    return [
        f"README missing section: {section}"
        for section in README_REQUIRED_SECTIONS
        if section not in text
    ]


def _readme_links() -> list[str]:
    text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    errors: list[str] = []
    for link in README_REQUIRED_LINKS:
        if link not in text:
            errors.append(f"README missing required link: {link}")
        elif not (PROJECT_ROOT / link).exists():
            errors.append(f"README link target does not exist: {link}")
    return errors


def _evidence_snapshot() -> list[str]:
    required = [
        "docs/evidence/milestone-6/evaluation-summary.md",
        "docs/evidence/milestone-6/metric-summary.csv",
        "docs/evidence/milestone-6/benchmark-summary.json",
    ]
    return [
        f"missing evidence snapshot: {path}"
        for path in required
        if not (PROJECT_ROOT / path).exists()
    ]


def _required_language() -> list[str]:
    errors: list[str] = []
    for relative, terms in SUBMISSION_REQUIRED_LANGUAGE.items():
        path = PROJECT_ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for term in terms:
            if term.lower() not in text:
                errors.append(f"{relative} missing required language: {term}")
    return errors


def _scan_public_files() -> list[str]:
    errors: list[str] = []
    for path in _public_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(PROJECT_ROOT)
        for marker in _local_path_patterns():
            if marker in text:
                errors.append(f"local absolute path marker in public file: {relative}")
        for credential_pattern in FORBIDDEN_CREDENTIAL_PATTERNS:
            if credential_pattern.search(text):
                errors.append(f"credential-like value in public file: {relative}")
        for url_pattern in FAKE_URL_PATTERNS:
            if url_pattern.search(text):
                errors.append(f"fake URL in public file: {relative}")
        if _mentions_fake_screenshot(text):
            errors.append(f"fake screenshot claim in public file: {relative}")
        for claim_pattern in UNSUPPORTED_CLAIMS:
            match = claim_pattern.search(text)
            if match is None:
                continue
            prefix = text[max(0, match.start() - 20) : match.start()].lower()
            if "not " not in prefix:
                errors.append(f"unsupported claim in public file: {relative}")
    return errors


def _development_tooling_claims() -> list[str]:
    errors: list[str] = []
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore") for path in _public_files()
    )
    for pattern in ANTIGRAVITY_UNSUPPORTED_CLAIMS:
        if pattern.search(public_text):
            errors.append("unsupported Antigravity runtime or authorship claim in public docs")
            break

    antigravity_page = PROJECT_ROOT / "docs/evidence/antigravity/README.md"
    if antigravity_page.exists():
        text = antigravity_page.read_text(encoding="utf-8")
        required = [
            "does not contain sufficient tracked evidence",
            "not a runtime dependency",
            "Do not add fake screenshots",
        ]
        for phrase in required:
            if phrase not in text:
                errors.append(f"Antigravity evidence page missing required phrase: {phrase}")

    dev_page = PROJECT_ROOT / "docs/development-assistants.md"
    if dev_page.exists():
        text = dev_page.read_text(encoding="utf-8")
        if "Runtime Technologies" not in text or "Development Assistants" not in text:
            errors.append("development assistant doc does not separate tools and runtime")
        if "not runtime dependencies" not in text and "not a runtime dependency" not in text:
            errors.append("development assistant doc does not state assistants are not runtime")
    return errors


def _mentions_fake_screenshot(text: str) -> bool:
    lowered = text.lower()
    suspicious = ["fake screenshot", "placeholder screenshot", "todo screenshot"]
    for term in suspicious:
        start = lowered.find(term)
        if start == -1:
            continue
        prefix = lowered[max(0, start - 20) : start]
        if "do not add " not in prefix:
            return True
    return False


def _runtime_artifacts() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "artifacts"],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return [f"could not inspect tracked artifacts: {exc}"]
    if result.stdout.strip():
        return ["runtime artifacts are tracked under artifacts/"]
    return []


def _data_keys() -> list[str]:
    errors: list[str] = []
    for path in [
        PROJECT_ROOT / "data/synthetic_cases.json",
        PROJECT_ROOT / "evaluation/benchmark_cases.json",
    ]:
        text = path.read_text(encoding="utf-8").lower()
        for key in PROHIBITED_DATA_KEYS:
            if f'"{key}"' in text:
                errors.append(
                    "prohibited patient-identifiable field key in "
                    f"{path.relative_to(PROJECT_ROOT)}: {key}"
                )
    return errors


def _primary_case() -> list[str]:
    try:
        case = get_case_by_id(PRIMARY_CASE_ID)
    except CaseNotFoundError:
        return [f"primary demo case does not exist: {PRIMARY_CASE_ID}"]
    if not case.synthetic:
        return [f"primary demo case is not synthetic: {PRIMARY_CASE_ID}"]
    return []


def _presentation_mode() -> list[str]:
    text = (PROJECT_ROOT / "ui/config.py").read_text(encoding="utf-8")
    if "DEMO_PRESENTATION_MODE" not in text:
        return ["presentation mode environment variable is not configured"]
    return []


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _public_files() -> list[Path]:
    roots = ["README.md", "docs", "submission", "deployment"]
    files: list[Path] = []
    for root in roots:
        path = PROJECT_ROOT / root
        if path.is_file():
            files.append(path)
        elif path.exists():
            files.extend(
                item
                for item in path.rglob("*")
                if item.is_file() and "__pycache__" not in item.parts
            )
    return files


def _local_path_patterns() -> list[str]:
    return ["/" + "Users/", "Desk" + "top/", "/private/" + "tmp/", ".venv/lib/"]


if __name__ == "__main__":
    raise SystemExit(main())
