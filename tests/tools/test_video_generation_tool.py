import json

from tools import video_generation_tool as mod


def test_video_generate_requires_prompt():
    result = json.loads(mod._handle_video_generate({}))
    assert "error" in result
    assert "prompt" in result["error"].lower()


def test_video_generation_requirements_follow_fal_key(monkeypatch):
    monkeypatch.delenv("FAL_KEY", raising=False)
    monkeypatch.setattr(mod, "_resolve_managed_fal_gateway", lambda: None)
    assert mod.check_video_generation_requirements() is False

    monkeypatch.setenv("FAL_KEY", "fal-test-key")
    assert mod.check_video_generation_requirements() is True


def test_video_generate_invokes_fal_submit(monkeypatch):
    captured = {}

    monkeypatch.setenv("FAL_KEY", "fal-test-key")

    def fake_submit(model_name, arguments):
        captured["model_name"] = model_name
        captured["arguments"] = arguments
        return {
            "video": {"url": "https://cdn.example/video.mp4"},
            "request_id": "vid-123",
        }

    monkeypatch.setattr(mod, "_submit_fal_video_request", fake_submit)

    result = json.loads(mod.video_generate("A cat surfing", aspect_ratio="portrait", duration_seconds=8))

    assert result["video"] == "https://cdn.example/video.mp4"
    assert result["request_id"] == "vid-123"
    assert captured["model_name"] == mod.DEFAULT_VIDEO_MODEL
    assert captured["arguments"]["prompt"] == "A cat surfing"
    assert captured["arguments"]["aspect_ratio"] == "9:16"
    assert captured["arguments"]["duration_seconds"] == 8
