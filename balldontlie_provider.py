from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv

from services.cache_service import get_cache, get_stale_cache, set_cache

load_dotenv()

BALLDONTLIE_API_KEY = os.getenv("3f4d17d6-6bd0-403c-88fb-43c117702cd0", "").strip()
BASE_URL = "https://api.balldontlie.io/v1"


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if BALLDONTLIE_API_KEY:
        headers["Authorization"] = BALLDONTLIE_API_KEY
    return headers


def get_games_for_date(date_str: str) -> tuple[list[dict[str, Any]], str]:
    cache_key = f"baldontlie_games_{date_str}"
    cached = get_cache(cache_key, ttl_seconds=900)
    if cached is not None:
        return cached, "cache"

    try:
        resp = requests.get(
            f"{BASE_URL}/games",
            headers=_headers(),
            params={"dates[]": date_str, "per_page": 100},
            timeout=12,
        )
        resp.raise_for_status()
        payload = resp.json()
        games = payload.get("data", [])

        normalized = []
        for g in games:
            home_team = g.get("home_team", {}) or {}
            away_team = g.get("visitor_team", {}) or {}

            normalized.append(
                {
                    "event_id": str(g.get("id")),
                    "home_team": home_team.get("full_name", "Desconhecido"),
                    "away_team": away_team.get("full_name", "Desconhecido"),
                    "commence_time": g.get("date"),
                    "completed": g.get("status", "").lower() == "final",
                    "home_score": g.get("home_team_score"),
                    "away_score": g.get("visitor_team_score"),
                }
            )

        set_cache(cache_key, normalized)
        return normalized, "balldontlie"
    except Exception:
        stale = get_stale_cache(cache_key)
        if stale is not None:
            return stale, "stale_cache"
        return [], "error"