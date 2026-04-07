from __future__ import annotations

import os
import time
from typing import Any

import requests
from dotenv import load_dotenv

from services.cache_service import get_cache, get_stale_cache, set_cache

load_dotenv()

THE_ODDS_API_KEY = os.getenv("ODDS_API_KEY", "").strip()
BASE_URL = os.getenv("ODDS_API_BASE_URL", "https://api.the-odds-api.com/v4")
SPORT_KEY = os.getenv("ODDS_API_SPORT_KEY", "basketball_nba")
REGIONS = os.getenv("ODDS_API_REGIONS", "us")
MARKETS = os.getenv("ODDS_PLAYER_PROP_MARKETS", "player_points,player_rebounds,player_assists")

_PROVIDER_COOLDOWN_UNTIL = 0.0


def _is_cooldown() -> bool:
    return time.time() < _PROVIDER_COOLDOWN_UNTIL


def _activate_cooldown(seconds: int = 600) -> None:
    global _PROVIDER_COOLDOWN_UNTIL
    _PROVIDER_COOLDOWN_UNTIL = time.time() + seconds


def _request(path: str, params: dict[str, Any], cache_key: str, ttl_seconds: int) -> tuple[Any, str]:
    if _is_cooldown():
        stale = get_stale_cache(cache_key)
        if stale is not None:
            return stale, "cooldown_stale_cache"
        return [], "cooldown"

    cached = get_cache(cache_key, ttl_seconds=ttl_seconds)
    if cached is not None:
        return cached, "cache"

    try:
        url = f"{BASE_URL}{path}"
        final_params = {"apiKey": THE_ODDS_API_KEY, **params}
        resp = requests.get(url, params=final_params, timeout=15)

        if resp.status_code in (403, 429):
            _activate_cooldown()
            stale = get_stale_cache(cache_key)
            if stale is not None:
                return stale, f"http_{resp.status_code}_stale_cache"
            return [], f"http_{resp.status_code}"

        resp.raise_for_status()
        data = resp.json()
        set_cache(cache_key, data)
        return data, "the_odds_api"
    except Exception:
        stale = get_stale_cache(cache_key)
        if stale is not None:
            return stale, "stale_cache"
        return [], "error"


def get_events() -> tuple[list[dict[str, Any]], str]:
    return _request(
        path=f"/sports/{SPORT_KEY}/events",
        params={},
        cache_key="theodds_events",
        ttl_seconds=600,
    )


def get_scores(days_from: int = 1) -> tuple[list[dict[str, Any]], str]:
    return _request(
        path=f"/sports/{SPORT_KEY}/scores",
        params={"daysFrom": days_from},
        cache_key=f"theodds_scores_{days_from}",
        ttl_seconds=900,
    )


def get_player_props_regions_us() -> tuple[list[dict[str, Any]], str]:
    markets = ",".join(
        [
            "player_points",
            "player_rebounds",
            "player_assists",
        ]
    )

    return _request(
        path=f"/sports/{SPORT_KEY}/odds",
        params={
            "regions": "us",
            "markets": markets,
            "oddsFormat": "decimal",
            "dateFormat": "iso",
        },
        cache_key="theodds_player_props_us",
        ttl_seconds=300,
    )