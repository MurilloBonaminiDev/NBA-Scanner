from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def _safe_key(key: str) -> str:
    return "".join(c if c.isalnum() or c in ("_", "-", ".") else "_" for c in key)


def _path_for(key: str) -> Path:
    return CACHE_DIR / f"{_safe_key(key)}.json"


def get_cache(key: str, ttl_seconds: int) -> Any | None:
    path = _path_for(key)
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        return None

    timestamp = payload.get("timestamp")
    if timestamp is None:
        return None

    age = time.time() - float(timestamp)
    if age > ttl_seconds:
        return None

    return payload.get("data")


def get_stale_cache(key: str) -> Any | None:
    path = _path_for(key)
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("data")
    except Exception:
        return None


def set_cache(key: str, data: Any) -> None:
    path = _path_for(key)
    payload = {
        "timestamp": time.time(),
        "data": data,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def clear_cache(key: str) -> None:
    path = _path_for(key)
    if path.exists():
        path.unlink()