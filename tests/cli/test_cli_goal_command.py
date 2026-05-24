"""Tests for the /goal CLI slash command."""

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


class TestCLIGoalCommand:
    def test_goal_command_prints_scaffold(self):
        cli_obj = _make_cli()

        with patch("cli._cprint") as mock_cprint:
            result = cli_obj.process_command("/goal Build OAuth login")

        assert result is True
        printed = "\n".join(call.args[0] for call in mock_cprint.call_args_list if call.args)
        assert "Hermes /goal Expansion" in printed
        assert "/goal Build OAuth login" in printed
        assert "Claude Code" in printed
        assert "Verifier:" in printed

    def test_goal_without_args_shows_usage(self):
        cli_obj = _make_cli()

        with patch("cli._cprint") as mock_cprint:
            result = cli_obj.process_command("/goal")

        assert result is True
        printed = "\n".join(call.args[0] for call in mock_cprint.call_args_list if call.args)
        assert "Usage:" in printed
        assert "/goal <goal>" in printed
