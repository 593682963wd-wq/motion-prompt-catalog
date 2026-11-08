"""Core data access for the local personal UI design sharing library."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH=BASE_DIR/'catalog.json'
PREVIEWS_PATH=BASE_DIR/'previews.json'
REQUIRED_ITEM_FIELDS = {
    "id",
    "source_title",
    "source_kind",
    "source_locked",
    "category",
    "style_family",
    "style_family_label",
    "theme_class",
    "original_prompt_zh",
    "original_prompt_en",
    "prompt_notice",
}
OPTIONAL_PREVIEW_FIELDS = (
    "preview_local_url",
    "preview_source_kind",
    "preview_source_url",
    "preview_media_type",
    "preview_is_animated",
)


class CatalogError(RuntimeError):
    """Raised when the bundled catalog is missing or malformed."""


def preview_is_animated(preview: dict[str, Any]) -> bool:
    """Best-effort animated preview detection for local ordering.

    The local library stores only public previews. Animated cards are the files
    that can actually play in the browser: GIFs, source URLs explicitly named
    `animated`, Mux animated stills, or video-derived public URLs. Public card
    screenshots remain static and should not be promoted as moving previews.
    """
    local_url = str(preview.get("local_url") or "").lower()
    source_url = str(preview.get("source_url") or "").lower()
    if local_url.endswith(".gif"):
        return True
    animated_markers = (
        "animated",
        "image.mux.com",
        ".mp4",
        ".m3u8",
        ".mov",
        ".webm",
    )
    return any(marker in source_url for marker in animated_markers)


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    if not CATALOG_PATH.exists():
        raise CatalogError(f"目录文件不存在：{CATALOG_PATH}")
    try:
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"目录文件无法读取：{exc}") from exc
    items = payload.get("items")
    if not isinstance(items, list):
        raise CatalogError("目录 items 必须是数组")
    if payload.get("count") != len(items):
        raise CatalogError("目录 count 与 items 长度不一致")
    seen: set[str] = set()
    previews = load_previews()
    preview_items = previews.get("items", {})
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise CatalogError(f"第 {index + 1} 条记录不是对象")
        missing = REQUIRED_ITEM_FIELDS - set(item)
        if missing:
            raise CatalogError(f"第 {index + 1} 条记录缺少字段：{sorted(missing)}")
        item_id = str(item["id"])
        if item_id in seen:
            raise CatalogError(f"目录 ID 重复：{item_id}")
        seen.add(item_id)
        if any(not isinstance(item[field],str) or not item[field].strip() for field in ["original_prompt_zh","original_prompt_en"]):
            raise CatalogError(f"提示词为空：{item_id}")
        preview = preview_items.get(item_id)
        if isinstance(preview, dict):
            for field in OPTIONAL_PREVIEW_FIELDS:
                item.pop(field, None)
        if isinstance(preview, dict):
            local_url = str(preview.get("local_url") or "").strip()
            if local_url:
                item["preview_local_url"] = local_url
                item["preview_source_kind"] = str(preview.get("source_kind") or "public_preview")
                item["preview_source_url"] = str(preview.get("source_url") or "")
                item["preview_media_type"] = str(preview.get("media_type") or "image")
                item["preview_is_animated"] = preview_is_animated(preview)
    return payload


@lru_cache(maxsize=1)
def load_previews() -> dict[str, Any]:
    if not PREVIEWS_PATH.exists():
        return {"schema_version": "1.0", "count": 0, "items": {}}
    try:
        payload = json.loads(PREVIEWS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogError(f"预览图清单无法读取：{exc}") from exc
    items = payload.get("items")
    if not isinstance(items, dict):
        raise CatalogError("预览图清单 items 必须是对象")
    return payload


def get_style(style_id: str) -> dict[str, Any] | None:
    for item in load_catalog()["items"]:
        if item["id"] == style_id:
            return item
    return None


def catalog_summary() -> dict[str, Any]:
    catalog = load_catalog()
    return {
        "count": catalog["count"],
        "stats": catalog["stats"],
        "source_policy": catalog["source_policy"],
        "schema_version": catalog["schema_version"],
    }
