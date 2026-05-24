"""Tests for the /kanban CLI slash command."""

from unittest.mock import MagicMock, patch

from cli import HermesCLI


def _make_cli():
    cli_obj = HermesCLI.__new__(HermesCLI)
    cli_obj.config = {}
    cli_obj.console = MagicMock()
    cli_obj.agent = None
    cli_obj.conversation_history = []
    cli_obj.session_id = "sess-123"
    cli_obj._pending_input = MagicMock()
    return cli_obj


class TestCLIKanbanCommand:
    def test_kanban_command_queues_prompt(self):
        cli_obj = _make_cli()

        with patch("cli._cprint") as mock_cprint:
            result = cli_obj.process_command("/kanban Build OAuth login")

        assert result is True
        cli_obj._pending_input.put.assert_called_once()
        queued_prompt = cli_obj._pending_input.put.call_args.args[0]
        assert "Operate in kanban mode" in queued_prompt
        assert "Build OAuth login" in queued_prompt
        assert "todo" in queued_prompt
        assert "delegate_task" in queued_prompt

        printed = "\n".join(call.args[0] for call in mock_cprint.call_args_list if call.args)
        assert "Kanban mode queued" in printed

    def test_kanban_without_args_shows_usage(self):
        cli_obj = _make_cli()

        with patch("cli._cprint") as mock_cprint:
            result = cli_obj.process_command("/kanban")

        assert result is True
        cli_obj._pending_input.put.assert_not_called()
        printed = "\n".join(call.args[0] for call in mock_cprint.call_args_list if call.args)
        assert "Usage:" in printed
        assert "/kanban <request>" in printed
