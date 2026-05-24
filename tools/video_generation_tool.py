#!/usr/bin/env python3
"""Simple FAL-backed video generation tool."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import fal_client

from tools.managed_tool_gateway import resolve_managed_tool_gateway
from tools.registry import registry, tool_error
from tools.tool_backend_helpers import managed_nous_tools_enabled

DEFAULT_VIDEO_MODEL = "fal-ai/minimax/video-01-live"
VALID_ASPECT_RATIOS = {"landscape": "16:9", "square": "1:1", "portrait": "9:16"}

VIDEO_GENERATE_SCHEMA: Dict[str, Any] = {
    "name": "video_generate",
    "description": (
        "Generate short AI videos from text prompts. Returns a video URL or local file path in the `video` field; "
        "display it with markdown or MEDIA delivery."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "Text prompt describing the desired video.",
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["landscape", "square", "portrait"],
                "default": "landscape",
                "description": "Output aspect ratio.",
            },
            "duration_seconds": {
                "type": "integer",
                "description": "Approximate duration in seconds.",
                "default": 5,
            },
        },
        "required": ["prompt"],
    },
}



def _resolve_managed_fal_gateway():
    if os.getenv("FAL_KEY"):
        return None
    return resolve_managed_tool_gateway("fal-queue")



def check_video_generation_requirements() -> bool:
    return bool(os.getenv("FAL_KEY") or _resolve_managed_fal_gateway())



def _submit_fal_video_request(model_name: str, arguments: Dict[str, Any]):
    managed_gateway = _resolve_managed_fal_gateway()
    if managed_gateway is not None:
        raise RuntimeError(
            "Managed Nous video gateway is not implemented for this backend yet. "
            "Set FAL_KEY for direct video generation."
        )
    return fal_client.subscribe(model_name, arguments=arguments)



def _extract_video_url(result: Dict[str, Any]) -> Optional[str]:
    video = result.get("video")
    if isinstance(video, dict):
        return str(video.get("url") or "").strip() or None
    if isinstance(video, list) and video:
        first = video[0]
        if isinstance(first, dict):
            return str(first.get("url") or "").strip() or None
        return str(first).strip() or None
    if isinstance(video, str):
        return video.strip() or None
    return None



def video_generate(
    prompt: str,
    aspect_ratio: str = "landscape",
    duration_seconds: int = 5,
) -> str:
    prompt = str(prompt or "").strip()
    if not prompt:
        return tool_error("prompt is required for video_generate")

    if not check_video_generation_requirements():
        message = "FAL_KEY environment variable not set"
        if managed_nous_tools_enabled():
            message += " and managed FAL gateway is unavailable"
        return tool_error(message)

    ratio = VALID_ASPECT_RATIOS.get(str(aspect_ratio or "").strip().lower(), "16:9")
    try:
        duration_value = max(3, min(12, int(duration_seconds or 5)))
    except Exception:
        duration_value = 5

    arguments = {
        "prompt": prompt,
        "aspect_ratio": ratio,
        "duration_seconds": duration_value,
    }
    result = _submit_fal_video_request(DEFAULT_VIDEO_MODEL, arguments)
    if not isinstance(result, dict):
        return tool_error("video generation backend returned an invalid response")

    video_url = _extract_video_url(result)
    payload = {
        "success": bool(video_url),
        "video": video_url,
        "request_id": result.get("request_id"),
        "raw": result,
    }
    return json.dumps(payload, ensure_ascii=False)



def _handle_video_generate(args: Dict[str, Any], **kw) -> str:
    prompt = str(args.get("prompt") or "").strip()
    if not prompt:
        return tool_error("prompt is required for video_generate")
    return video_generate(
        prompt=prompt,
        aspect_ratio=str(args.get("aspect_ratio") or "landscape"),
        duration_seconds=args.get("duration_seconds", 5),
    )


registry.register(
    name="video_generate",
    toolset="video_gen",
    schema=VIDEO_GENERATE_SCHEMA,
    handler=_handle_video_generate,
    check_fn=check_video_generation_requirements,
    emoji="🎬",
)
