"""Safe placeholder command-line entry point for Milestone 1."""

from app.config import AppConfig


def main() -> None:
    """Print current project status without calling external services."""
    config = AppConfig()
    print(config.project_name)
    print(f"{config.milestone} foundation is installed.")
    print("Functional agent execution is not yet implemented.")
    print("No Gemini, Google ADK, MCP, or external service calls were made.")


if __name__ == "__main__":
    main()
