from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from services.balldontlie_provider import get_games_for_date
from services.odds_provider import get_events, get_player_props_regions_us, get_scores


def american_to_decimal(price: float) -> float:
    try:
        price = float(price)
        if price > 0:
            return round((price / 100) + 1, 2)
        return round((100 / abs(price)) + 1, 2)
    except Exception:
        return 0.0


def normalize_outcome_name(name: str) -> str:
    return str(name).strip()


def infer_market_label(raw_market: str) -> str:
    mapping = {
        "player_points": "Points",
        "player_rebounds": "Rebounds",
        "player_assists": "Assists",
    }
    return mapping.get(raw_market, raw_market)


def build_props_dataframe(raw_props: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for event in raw_props:
        home_team = event.get("home_team", "")
        away_team = event.get("away_team", "")
        event_id = str(event.get("id", ""))

        bookmakers = event.get("bookmakers", []) or []
        for bookmaker in bookmakers:
            markets = bookmaker.get("markets", []) or []
            for market in markets:
                market_key = market.get("key", "")
                outcomes = market.get("outcomes", []) or []

                for outcome in outcomes:
                    player = normalize_outcome_name(outcome.get("description", ""))
                    line = outcome.get("point")
                    price = outcome.get("price")

                    if not player or line is None or price is None:
                        continue

                    side = str(outcome.get("name", ""))
                    decimal_price = float(price) if isinstance(price, (int, float)) else 0.0

                    if decimal_price <= 0:
                        continue

                    implied_prob = round((1 / decimal_price) * 100, 2)
                    projected_prob = min(max(implied_prob + 3.5, 50.0), 64.0)
                    edge = round(projected_prob - implied_prob, 2)

                    confidence_score = int(min(max(58 + edge * 6, 55), 95))

                    if confidence_score >= 86:
                        confidence_label = "ELITE"
                    elif confidence_score >= 76:
                        confidence_label = "ALTA"
                    elif confidence_score >= 66:
                        confidence_label = "BOA"
                    else:
                        confidence_label = "BAIXA"

                    if edge >= 4:
                        value_bet = "FORTE"
                    elif edge >= 2.5:
                        value_bet = "BOA"
                    elif edge >= 1:
                        value_bet = "LEVE"
                    else:
                        value_bet = "NENHUMA"

                    reason = (
                        f"Odds {decimal_price:.2f}, prob. implícita {implied_prob:.2f}%, "
                        f"edge estimado {edge:.2f}%."
                    )

                    rows.append(
                        {
                            "event_id": event_id,
                            "player": player,
                            "market": infer_market_label(market_key),
                            "line": float(line),
                            "recommended_side": side,
                            "recommended_prob": projected_prob,
                            "edge_percent": edge,
                            "confidence_score": confidence_score,
                            "confidence_label": confidence_label,
                            "value_bet": value_bet,
                            "prop_rank": round((projected_prob * 0.55) + (edge * 8) + (confidence_score * 0.45), 2),
                            "books_count": len(bookmakers),
                            "best_price_decimal": decimal_price,
                            "best_price_american": "",
                            "away_team": away_team,
                            "home_team": home_team,
                            "reason": reason,
                        }
                    )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    best_idx = (
        df.groupby(["event_id", "player", "market", "line", "recommended_side"])["best_price_decimal"]
        .idxmax()
        .tolist()
    )
    df = df.loc[best_idx].copy().reset_index(drop=True)

    books_count = (
        pd.DataFrame(rows)
        .groupby(["event_id", "player", "market", "line", "recommended_side"])
        .size()
        .reset_index(name="books_count_real")
    )

    df = df.merge(
        books_count,
        on=["event_id", "player", "market", "line", "recommended_side"],
        how="left",
    )
    df["books_count"] = df["books_count_real"].fillna(df["books_count"]).astype(int)
    df.drop(columns=["books_count_real"], inplace=True)

    return df.sort_values(by=["prop_rank", "confidence_score", "edge_percent"], ascending=False).reset_index(drop=True)


def run_scanner() -> tuple[pd.DataFrame, dict[str, Any]]:
    today = datetime.now().strftime("%Y-%m-%d")

    games, games_source = get_games_for_date(today)
    props, props_source = get_player_props_regions_us()
    scores, scores_source = get_scores(days_from=1)

    df = build_props_dataframe(props)

    diagnostics = {
        "games": games,
        "events_source": games_source,
        "scores_source": scores_source,
        "props_sources": props_source,
        "raw_props_count": len(props) if isinstance(props, list) else 0,
    }

    return df, diagnostics


def apply_filters(
    df: pd.DataFrame,
    markets: list[str] | None = None,
    teams: list[str] | None = None,
    min_confidence: int = 0,
    value_levels: list[str] | None = None,
) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()

    if markets:
        out = out[out["market"].isin(markets)]

    if teams:
        out = out[
            (out["home_team"].isin(teams)) |
            (out["away_team"].isin(teams))
        ]

    if value_levels:
        out = out[out["value_bet"].isin(value_levels)]

    out = out[out["confidence_score"] >= int(min_confidence)]
    return out.reset_index(drop=True)


def get_top_plays(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values(
        by=["prop_rank", "confidence_score", "edge_percent"],
        ascending=False,
    ).head(limit).reset_index(drop=True)


def get_dashboard_metrics(df: pd.DataFrame) -> dict[str, int]:
    if df.empty:
        return {
            "total_props": 0,
            "elite_count": 0,
            "value_bets": 0,
        }

    return {
        "total_props": int(len(df)),
        "elite_count": int((df["confidence_label"] == "ELITE").sum()),
        "value_bets": int((df["value_bet"].isin(["FORTE", "BOA", "LEVE"])).sum()),
    }