"""Tests for the /kanban gateway slash command."""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from gateway.config import GatewayConfig, Platform, PlatformConfig
from gateway.platforms.base import MessageEvent
from gateway.session import SessionEntry, SessionSource


def _make_runner():
    from gateway.run import GatewayRunner

    runner = object.__new__(GatewayRunner)
    runner.config = GatewayConfig(
        platforms={Platform.TELEGRAM: PlatformConfig(enabled=True, token="***")}
    )
    runner.adapters = {}
    runner._voice_mode = {}
    runner.hooks = SimpleNamespace(emit=AsyncMock(), loaded_hooks=False)
    runner.session_store = MagicMock()
    runner.session_store.get_or_create_session.return_value = SessionEntry(
        session_key="agent:main:telegram:dm:c1:u1",
        session_id="sess-1",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        platform=Platform.TELEGRAM,
        chat_type="dm",
    )
    runner.session_store.load_transcript.return_value = []
    runner.session_store.has_any_sessions.return_value = True
    runner.session_store.append_to_transcript = MagicMock()
    runner.session_store.rewrite_transcript = MagicMock()
    runner._running_agents = {}
    runner._pending_messages = {}
    runner._pending_approvals = {}
    runner._session_db = None
    runner._reasoning_config = None
    runner._provider_routing = {}
    runner._fallback_model = None
    runner._show_reasoning = False
    runner._is_user_authorized = lambda _source: True
    runner._set_session_env = lambda _context: None
    runner._run_agent = AsyncMock(return_value={"final_response": "unused", "messages": [], "tools": [], "history_offset": 0, "last_prompt_tokens": 0})
    return runner


def _make_event(text="/kanban"):
    return MessageEvent(
        text=text,
        source=SessionSource(
            platform=Platform.TELEGRAM,
            user_id="u1",
            chat_id="c1",
            user_name="tester",
            chat_type="dm",
        ),
        message_id="m1",
    )


class TestGatewayKanbanCommand:
    @pytest.mark.asyncio
    async def test_kanban_without_args_shows_usage(self):
        runner = _make_runner()
        event = _make_event("/kanban")

        result = await runner._handle_kanban_command(event)

        assert "Usage:" in result
        assert "/kanban <request>" in result

    @pytest.mark.asyncio
    async def test_kanban_command_is_rewritten_into_agent_prompt(self):
        runner = _make_runner()
        event = _make_event("/kanban Build OAuth login")

        result = await runner._handle_kanban_command(event)

        assert result is None
        assert "Operate in kanban mode" in event.text
        assert "Build OAuth login" in event.text
        assert "todo" in event.text
        assert "delegate_task" in event.text
