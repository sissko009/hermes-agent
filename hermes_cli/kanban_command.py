"""Shared helpers for the built-in /kanban slash command."""

from __future__ import annotations


def build_kanban_command_usage() -> str:
    """Return usage text for /kanban."""
    return (
        "Usage: /kanban <request>\n"
        "Example: /kanban Build OAuth login\n\n"
        "Queues a kanban-style execution prompt that uses todo tracking first and "
        "delegate_task only for parallelizable subtasks."
    )


def build_kanban_command_prompt(request: str) -> str | None:
    """Return an agent prompt for kanban execution, or None when request is blank."""
    normalized = " ".join((request or "").strip().split())
    if not normalized:
        return None

    return (
        f"Operate in kanban mode for this request: {normalized}\n\n"
        "Workflow requirements:\n"
        "1. Use the todo tool immediately to create a compact kanban board for this request.\n"
        "2. Map kanban columns onto todo statuses as follows: Backlog= pending, Doing= in_progress, Done= completed, Blocked= cancelled with an explanation.\n"
        "3. Keep exactly one todo item in_progress at a time.\n"
        "4. Do the highest-leverage item now instead of stopping at planning.\n"
        "5. Use delegate_task only when workstreams are independent and parallelizable; otherwise stay in the main agent loop.\n"
        "6. Update the todo board as each step finishes, and continue until the request is completed or explicitly blocked.\n"
        "7. Final response must be a short kanban summary: completed, remaining, blocked, and next recommended move if anything is still open.\n\n"
        "Execution style:\n"
        "- Prefer the smallest shippable slice first.\n"
        "- Do not ask for routine confirmations.\n"
        "- Ground claims in tool output.\n"
        "- If blocked, say exactly what is blocked and why."
    )


def build_kanban_command_notice(request: str) -> str:
    """Return the CLI notice after queueing /kanban."""
    normalized = " ".join((request or "").strip().split())
    preview = normalized[:80] + ("..." if len(normalized) > 80 else "")
    return f"  📋 Kanban mode queued: {preview}"
