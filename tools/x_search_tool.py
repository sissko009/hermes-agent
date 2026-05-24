#!/usr/bin/env python3
"""Search X/Twitter posts through xAI's Responses API ``x_search`` tool."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import requests

from tools.registry import registry, tool_error

DEFAULT_XAI_BASE_URL = "https://api.x.ai/v1"
DEFAULT_X_SEARCH_MODEL = "grok-4.20-reasoning"
MAX_HANDLES = 10


X_SEARCH_SCHEMA: Dict[str, Any] = {
    "name": "x_search",
    "description": (
        "Search X (Twitter) posts, profiles, and threads using xAI's built-in X Search tool. "
        "Use this for current discussion, reactions, or claims on X rather than general web pages."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to look up on X."},
            "allowed_x_handles": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of X handles to include exclusively (max 10).",
            },
            "excluded_x_handles": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of X handles to exclude (max 10).",
            },
            "from_date": {"type": "string", "description": "Optional start date in YYYY-MM-DD format."},
            "to_date": {"type": "string", "description": "Optional end date in YYYY-MM-DD format."},
            "enable_image_understanding": {
                "type": "boolean",
                "description": "Whether xAI should analyze images attached to matching X posts.",
                "default": False,
            },
            "enable_video_understanding": {
                "type": "boolean",
                "description": "Whether xAI should analyze videos attached to matching X posts.",
                "default": False,
            },
        },
        "required": ["query"],
    },
}


def _get_xai_api_key() -> str:
    return str(os.getenv("XAI_API_KEY") or "").strip()



def check_x_search_requirements() -> bool:
    return bool(_get_xai_api_key())



def _normalize_handles(handles: Optional[List[str]], field_name: str) -> List[str]:
    cleaned = [str(handle or "").strip().lstrip("@") for handle in handles or []]
    cleaned = [handle for handle in cleaned if handle]
    if len(cleaned) > MAX_HANDLES:
        raise ValueError(f"{field_name} supports at most {MAX_HANDLES} handles")
    return cleaned



def x_search(
    query: str,
    allowed_x_handles: Optional[List[str]] = None,
    excluded_x_handles: Optional[List[str]] = None,
    from_date: str = "",
    to_date: str = "",
    enable_image_understanding: bool = False,
    enable_video_understanding: bool = False,
) -> str:
    query = str(query or "").strip()
    if not query:
        return tool_error("query is required for x_search")

    api_key = _get_xai_api_key()
    if not api_key:
        return tool_error("XAI_API_KEY is required for x_search")

    try:
        allowed = _normalize_handles(allowed_x_handles, "allowed_x_handles")
        excluded = _normalize_handles(excluded_x_handles, "excluded_x_handles")
    except ValueError as exc:
        return tool_error(str(exc))

    if allowed and excluded:
        return tool_error("allowed_x_handles and excluded_x_handles cannot both be set")

    tool_def: Dict[str, Any] = {"type": "x_search"}
    if allowed:
        tool_def["allowed_x_handles"] = allowed
    if excluded:
        tool_def["excluded_x_handles"] = excluded
    if str(from_date or "").strip():
        tool_def["from_date"] = str(from_date).strip()
    if str(to_date or "").strip():
        tool_def["to_date"] = str(to_date).strip()
    if enable_image_understanding:
        tool_def["enable_image_understanding"] = True
    if enable_video_understanding:
        tool_def["enable_video_understanding"] = True

    payload = {
        "model": DEFAULT_X_SEARCH_MODEL,
        "input": query,
        "tools": [tool_def],
        "store": False,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(
        f"{DEFAULT_XAI_BASE_URL}/responses",
        json=payload,
        headers=headers,
        timeout=180,
    )
    response.raise_for_status()
    raw = response.json()

    text = str(raw.get("output_text") or "").strip()
    result = {
        "success": True,
        "query": query,
        "model": payload["model"],
        "credential_source": "api_key",
        "text": text,
        "raw": raw,
    }
    return json.dumps(result, ensure_ascii=False)



def _handle_x_search(args: Dict[str, Any], **kw) -> str:
    query = str(args.get("query") or "").strip()
    if not query:
        return tool_error("query is required for x_search")
    return x_search(
        query=query,
        allowed_x_handles=args.get("allowed_x_handles"),
        excluded_x_handles=args.get("excluded_x_handles"),
        from_date=str(args.get("from_date") or ""),
        to_date=str(args.get("to_date") or ""),
        enable_image_understanding=bool(args.get("enable_image_understanding", False)),
        enable_video_understanding=bool(args.get("enable_video_understanding", False)),
    )


registry.register(
    name="x_search",
    toolset="x_search",
    schema=X_SEARCH_SCHEMA,
    handler=_handle_x_search,
    check_fn=check_x_search_requirements,
    emoji="𝕏",
)
