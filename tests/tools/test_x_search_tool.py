import json

from tools import x_search_tool as mod


def test_x_search_requires_query():
    result = json.loads(mod._handle_x_search({}))
    assert "error" in result
    assert "query" in result["error"].lower()


def test_x_search_requirements_follow_env(monkeypatch):
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    assert mod.check_x_search_requirements() is False

    monkeypatch.setenv("XAI_API_KEY", "xai-test-key")
    assert mod.check_x_search_requirements() is True


def test_x_search_invokes_client(monkeypatch):
    captured = {}

    class FakeResponse:
        def json(self):
            return {"output_text": "hello from X", "id": "resp_123"}

        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=None):
        captured["url"] = url
        captured["payload"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setenv("XAI_API_KEY", "xai-test-key")
    monkeypatch.setattr(mod.requests, "post", fake_post)

    result = json.loads(mod.x_search("hermes agent", from_date="2026-05-01", enable_image_understanding=True))

    assert result["text"] == "hello from X"
    assert result["success"] is True
    assert captured["url"].endswith("/responses")
    assert captured["payload"]["input"] == "hermes agent"
    tool_def = captured["payload"]["tools"][0]
    assert tool_def["from_date"] == "2026-05-01"
    assert tool_def["enable_image_understanding"] is True
    assert captured["headers"]["Authorization"] == "Bearer xai-test-key"
