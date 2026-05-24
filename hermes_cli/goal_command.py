"""Shared formatter for the built-in /goal slash command."""

from __future__ import annotations


def build_goal_command_output(goal: str) -> str:
    """Return usage text or a deterministic /goal expansion scaffold."""
    normalized = " ".join((goal or "").strip().split())
    if not normalized:
        return (
            "Usage: /goal <goal>\n"
            "Example: /goal Build OAuth login\n\n"
            "Expands one high-level goal into a Codex implementation /goal and a "
            "Claude Code review /goal."
        )

    return (
        "Hermes /goal Expansion\n\n"
        f"User goal: {normalized}\n\n"
        "Codex /goal\n"
        f"/goal {normalized}.\n"
        "Done means relevant tests pass, relevant build/check commands pass, and git status only shows intended project files.\n"
        "Verifier: <replace with your project's test/build command>\n\n"
        "Claude Code /goal\n"
        "Review the Codex diff for this goal.\n"
        "Done means PASS or BLOCKED with prioritized findings.\n"
        "Findings format: severity(CRITICAL/MAJOR/MINOR) | file:line | issue | fix suggestion\n\n"
        "Loop\n"
        "1. Run the Codex /goal.\n"
        "2. Hand the diff to Claude Code for review.\n"
        "3. If review is BLOCKED, issue a follow-up fix /goal and repeat."
    )
