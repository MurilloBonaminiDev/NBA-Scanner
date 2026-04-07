from __future__ import annotations

import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import plotly.express as px  # pyright: ignore[reportMissingImports]
import streamlit as st  # pyright: ignore[reportMissingImports]
import html

from services.scanner_service import (
    apply_filters,
    get_dashboard_metrics,
    get_top_plays,
    run_scanner,
)
from services.history_service import (
    get_history_by_date,
    get_history_summary,
    save_picks_from_scanner,
    update_pick_result,
)

st.set_page_config(
    page_title="NBA Scanner Pro VIP V18.1",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #030712;
            --bg-2: #07111f;
            --bg-3: #081423;
            --card: rgba(9, 16, 30, 0.92);
            --card-2: rgba(13, 21, 38, 0.96);
            --stroke: rgba(255,255,255,0.08);
            --muted: #94a3b8;
            --text: #f8fafc;
            --green: #22c55e;
            --yellow: #f59e0b;
            --red: #ef4444;
            --cyan: #22d3ee;
            --blue: #3b82f6;
        }

        .stApp {
            background:
                radial-gradient(circle at 0% 0%, rgba(34,211,238,0.14), transparent 26%),
                radial-gradient(circle at 100% 0%, rgba(59,130,246,0.15), transparent 24%),
                radial-gradient(circle at 50% 100%, rgba(34,197,94,0.08), transparent 18%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 42%, var(--bg-3) 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1540px;
            padding-top: 1.3rem;
            padding-bottom: 2rem;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #08111d 0%, #0c1727 100%);
            border-right: 1px solid rgba(255,255,255,0.06);
        }

        .hero-wrap {
            position: relative;
            overflow: hidden;
            background:
                radial-gradient(circle at top left, rgba(34,211,238,0.24), transparent 28%),
                radial-gradient(circle at right center, rgba(59,130,246,0.18), transparent 28%),
                linear-gradient(135deg, rgba(7, 18, 32, 0.98), rgba(5, 10, 22, 0.96));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 28px;
            padding: 30px 30px 24px 30px;
            box-shadow: 0 22px 50px rgba(0,0,0,0.28);
            margin-bottom: 1.2rem;
        }

        .hero-kicker {
            display: inline-flex;
            gap: 8px;
            align-items: center;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(34,211,238,0.12);
            border: 1px solid rgba(34,211,238,0.24);
            color: #a5f3fc;
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.3px;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 3rem;
            line-height: 1.02;
            font-weight: 950;
            color: #ffffff;
            letter-spacing: -1.5px;
            margin-bottom: 0.75rem;
            max-width: 820px;
        }

        .hero-subtitle {
            max-width: 760px;
            color: #cbd5e1;
            line-height: 1.6;
            font-size: 1rem;
            margin-bottom: 1.1rem;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            margin-top: 0.8rem;
        }

        .hero-stat {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            padding: 14px 16px;
            backdrop-filter: blur(8px);
        }

        .hero-stat-label {
            color: #9fb2c8;
            font-size: 0.78rem;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .hero-stat-value {
            color: #fff;
            font-size: 1.45rem;
            font-weight: 900;
        }

        .hero-cta-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 1rem;
        }

        .cta-primary,
        .cta-secondary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            padding: 0.95rem 1.2rem;
            font-weight: 900;
            font-size: 0.96rem;
            text-decoration: none;
        }

        .cta-primary {
            background: linear-gradient(90deg, #22d3ee 0%, #3b82f6 100%);
            color: #04111f;
            box-shadow: 0 12px 24px rgba(34,211,238,0.22);
        }

        .cta-secondary {
            background: rgba(255,255,255,0.05);
            color: #e2e8f0;
            border: 1px solid rgba(255,255,255,0.10);
        }

        .section-title {
            font-size: 1.18rem;
            font-weight: 900;
            color: #ffffff;
            margin-top: 0.8rem;
            margin-bottom: 0.85rem;
        }

        .subtle-text {
            color: #8fa4bb;
            font-size: 0.94rem;
            margin-top: -0.2rem;
            margin-bottom: 1rem;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(15,23,42,0.96) 0%, rgba(3,7,18,0.98) 100%);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 16px 18px;
            box-shadow: 0 10px 24px rgba(0,0,0,0.22);
            min-height: 110px;
        }

        .metric-label {
            color: #93a7bd;
            font-size: 0.85rem;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .metric-value {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 950;
            line-height: 1.05;
        }

        .metric-foot {
            color: #7dd3fc;
            margin-top: 8px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .pick-card {
            border-radius: 24px;
            padding: 22px;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 16px 34px rgba(0,0,0,0.24);
            margin-bottom: 18px;
            position: relative;
            overflow: hidden;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }

        .pick-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 22px 42px rgba(0,0,0,0.30);
        }

        .pick-card::after {
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top right, rgba(255,255,255,0.10), transparent 22%);
            pointer-events: none;
        }

        .pick-strong {
            background: linear-gradient(135deg, rgba(8,32,20,0.96), rgba(5,12,20,0.98));
            border-color: rgba(34,197,94,0.32);
        }

        .pick-caution {
            background: linear-gradient(135deg, rgba(40,24,5,0.96), rgba(10,12,20,0.98));
            border-color: rgba(245,158,11,0.30);
        }

        .pick-avoid {
            background: linear-gradient(135deg, rgba(40,10,10,0.96), rgba(10,12,20,0.98));
            border-color: rgba(239,68,68,0.30);
        }

        .pick-topline {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: center;
            margin-bottom: 14px;
            flex-wrap: wrap;
        }

        .pick-market {
            color: #dbeafe;
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .pick-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            font-weight: 900;
            font-size: 0.8rem;
            border: 1px solid rgba(255,255,255,0.14);
        }

        .pick-badge-strong { background: rgba(34,197,94,0.15); color: #86efac; }
        .pick-badge-caution { background: rgba(245,158,11,0.15); color: #fde68a; }
        .pick-badge-avoid { background: rgba(239,68,68,0.15); color: #fca5a5; }

        .pick-player {
            font-size: 1.65rem;
            font-weight: 950;
            color: #fff;
            line-height: 1.08;
            margin-bottom: 4px;
        }

        .pick-line {
            font-size: 1.02rem;
            font-weight: 800;
            color: #dbeafe;
            margin-bottom: 12px;
        }

        .pick-matchup {
            color: #a8bdd3;
            font-size: 0.95rem;
            margin-bottom: 14px;
        }

        .pick-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }

        .pick-stat {
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 16px;
            padding: 12px;
        }

        .pick-stat-label {
            color: #8fa4bb;
            font-size: 0.75rem;
            margin-bottom: 4px;
            text-transform: uppercase;
        }

        .pick-stat-value {
            color: #fff;
            font-size: 1.08rem;
            font-weight: 900;
        }

        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.42rem 0.8rem;
            font-size: 0.78rem;
            font-weight: 800;
            border: 1px solid rgba(255,255,255,0.09);
            background: rgba(255,255,255,0.05);
            color: #e2e8f0;
        }


        .pick-progress-wrap {
            margin-top: 12px;
            margin-bottom: 14px;
        }

        .pick-progress-label {
            display: flex;
            justify-content: space-between;
            color: #b7c7d9;
            font-size: 0.76rem;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }

        .pick-progress-track {
            width: 100%;
            height: 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.08);
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.06);
        }

        .pick-progress-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #22d3ee 0%, #22c55e 100%);
        }

        .pick-bottom-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 12px;
            align-items: stretch;
        }

        .reason-box {
            color: #d0d9e5;
            line-height: 1.6;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 14px 15px;
        }

        .pick-side-box {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 14px 15px;
        }

        .pick-side-label {
            color: #8fa4bb;
            font-size: 0.74rem;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .pick-side-value {
            color: #fff;
            font-size: 1.05rem;
            font-weight: 900;
            line-height: 1.25;
        }

        .games-wrap, .provider-wrap, .offer-box {
            background: linear-gradient(180deg, rgba(13,20,36,0.96), rgba(7,12,24,0.98));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 22px;
            padding: 18px;
            box-shadow: 0 12px 28px rgba(0,0,0,0.18);
        }

        .offer-box {
            padding: 24px;
            background:
                radial-gradient(circle at top right, rgba(34,211,238,0.14), transparent 24%),
                radial-gradient(circle at bottom left, rgba(34,197,94,0.10), transparent 20%),
                linear-gradient(135deg, rgba(10,16,30,0.98), rgba(7,11,24,0.98));
        }

        .offer-price {
            font-size: 2.4rem;
            font-weight: 950;
            color: #fff;
            line-height: 1;
            margin-top: 8px;
        }

        .offer-sub {
            color: #a9bdd1;
            line-height: 1.6;
            margin-top: 10px;
            margin-bottom: 16px;
        }

        div[data-testid="stDataFrame"] {
            background: transparent;
            border: none;
            padding: 0;
        }

        div[data-testid="stTabs"] button {
            font-weight: 800;
        }

        .stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #22d3ee 0%, #3b82f6 100%);
            color: #04111f;
            border: none;
            border-radius: 14px;
            font-weight: 900;
            padding: 0.82rem 1rem;
            box-shadow: 0 10px 20px rgba(34,211,238,0.18);
        }

        .stButton > button:hover {
            filter: brightness(1.05);
            transform: translateY(-1px);
        }

        @media (max-width: 1100px) {
            .hero-grid, .pick-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .pick-bottom-grid {
                grid-template-columns: 1fr;
            }
            .hero-title {
                font-size: 2.3rem;
            }
        }

        @media (max-width: 700px) {
            .hero-grid, .pick-grid {
                grid-template-columns: 1fr;
            }
            .hero-title {
                font-size: 1.9rem;
            }
            .pick-player {
                font-size: 1.35rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_datetime_br(value):
    try:
        dt = pd.to_datetime(value, utc=True, errors="coerce")
        if pd.isna(dt):
            dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return value
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return value


def format_date_br(value):
    try:
        dt = pd.to_datetime(value, errors="coerce")
        if pd.isna(dt):
            return value
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return value


def render_metric(label: str, value: str, foot: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diag_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="font-size:1.2rem;">{value}</div>
            <div class="metric-foot">Status do provider</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def confidence_class(label: str) -> str:
    return {
        "ELITE": "Confiança ELITE",
        "ALTA": "Confiança ALTA",
        "BOA": "Confiança BOA",
        "BAIXA": "Confiança BAIXA",
    }.get(label, "Confiança BAIXA")


def market_icon(market: str) -> str:
    m = str(market).lower()
    if "point" in m:
        return "🏀"
    if "rebound" in m:
        return "🧱"
    if "assist" in m:
        return "🎯"
    if "three" in m or "3pt" in m:
        return "🎯"
    return "📊"


def recommendation_data(row: pd.Series) -> tuple[str, str, str]:
    confidence = int(row.get("confidence_score", 0))
    confidence_label = str(row.get("confidence_label", "BAIXA"))
    value_bet = str(row.get("value_bet", "NENHUMA"))
    edge = float(row.get("edge_percent", 0))
    prob = float(row.get("recommended_prob", 0))
    books = int(row.get("books_count", 0))

    if confidence_label == "ELITE" and prob >= 54:
        if value_bet in {"FORTE", "BOA"} or edge >= 1.0 or books >= 3:
            return "🟢 ENTRADA FORTE", "pick-strong", "pick-badge-strong"
        return "🟡 CAUTELA", "pick-caution", "pick-badge-caution"

    if confidence >= 74 and prob >= 54:
        if value_bet in {"FORTE", "BOA"} or edge >= 1.5:
            return "🟢 ENTRADA FORTE", "pick-strong", "pick-badge-strong"
        return "🟡 CAUTELA", "pick-caution", "pick-badge-caution"

    if confidence >= 66 and prob >= 52:
        if value_bet in {"FORTE", "BOA", "LEVE"} or edge >= 0.8:
            return "🟡 CAUTELA", "pick-caution", "pick-badge-caution"

    return "🔴 EVITAR", "pick-avoid", "pick-badge-avoid"


def translate_games_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    translated = df.copy()

    if "commence_time" in translated.columns:
        translated["commence_time"] = translated["commence_time"].apply(format_datetime_br)

    translated = translated.rename(
        columns={
            "away_team": "Visitante",
            "home_team": "Mandante",
            "commence_time": "Horário",
            "completed": "Finalizado",
            "home_score": "Pts Mandante",
            "away_score": "Pts Visitante",
        }
    )

    cols = [
        c for c in
        ["Visitante", "Mandante", "Horário", "Finalizado", "Pts Mandante", "Pts Visitante"]
        if c in translated.columns
    ]
    return translated[cols]


def format_percent(series: pd.Series) -> pd.Series:
    return series.map(lambda x: f"{float(x):.2f}%")


def format_decimal(series: pd.Series, digits: int = 2) -> pd.Series:
    return series.map(lambda x: f"{float(x):.{digits}f}")


def build_main_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    out["Ícone"] = out["market"].map(market_icon)
    out["Linha"] = format_decimal(out["line"], 1)
    out["Probabilidade"] = format_percent(out["recommended_prob"])
    out["Edge"] = format_percent(out["edge_percent"])
    out["Confiança"] = out["confidence_score"].astype(int)
    out["Melhor Odd"] = format_decimal(out["best_price_decimal"], 2)

    actions = out.apply(recommendation_data, axis=1)
    out["Semáforo"] = [a[0] for a in actions]

    out = out.rename(
        columns={
            "player": "Jogador",
            "away_team": "Visitante",
            "home_team": "Mandante",
            "market": "Mercado",
            "recommended_side": "Lado",
            "confidence_label": "Nível",
            "value_bet": "Value Bet",
            "prop_rank": "Rank",
            "books_count": "Casas",
            "best_price_american": "Odd Americana",
            "reason": "Motivo",
        }
    )

    return out[
        [
            "Ícone",
            "Jogador",
            "Visitante",
            "Mandante",
            "Mercado",
            "Linha",
            "Lado",
            "Probabilidade",
            "Edge",
            "Confiança",
            "Nível",
            "Value Bet",
            "Rank",
            "Casas",
            "Melhor Odd",
            "Odd Americana",
            "Semáforo",
            "Motivo",
        ]
    ]


def filter_top_elite(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df[
        (df["confidence_label"].isin(["ELITE", "ALTA"])) &
        (df["recommended_prob"] >= 54)
    ].sort_values(
        by=["prop_rank", "confidence_score", "edge_percent"],
        ascending=False,
    ).reset_index(drop=True)


def filter_props_ruins(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df[
        (df["confidence_label"] == "BAIXA") |
        ((df["recommended_prob"] < 52) & (df["edge_percent"] < 1.0))
    ].sort_values(
        by=["confidence_score", "edge_percent"],
        ascending=[True, True],
    ).reset_index(drop=True)


def build_history_display(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    out["date"] = out["date"].apply(format_date_br)
    out["Linha"] = out["line"].map(lambda x: f"{float(x):.1f}")
    out["Probabilidade"] = out["recommended_prob"].map(lambda x: f"{float(x):.2f}%")
    out["Edge"] = out["edge_percent"].map(lambda x: f"{float(x):.2f}%")
    out["Odd"] = out["best_price_decimal"].map(lambda x: f"{float(x):.2f}")
    out["Lucro"] = out["profit"].map(lambda x: f"{float(x):.2f}")

    out = out.rename(
        columns={
            "date": "Data",
            "player": "Jogador",
            "market": "Mercado",
            "recommended_side": "Lado",
            "confidence_score": "Confiança",
            "result": "Resultado",
            "home_team": "Mandante",
            "away_team": "Visitante",
        }
    )

    return out[
        [
            "Data",
            "Jogador",
            "Mercado",
            "Linha",
            "Lado",
            "Probabilidade",
            "Edge",
            "Confiança",
            "Odd",
            "Resultado",
            "Lucro",
            "Visitante",
            "Mandante",
        ]
    ]


def render_hero(metrics: dict, history_summary: dict, filtered_df: pd.DataFrame) -> None:
    top_count = len(filtered_df[filtered_df["recommended_prob"] >= 54]) if not filtered_df.empty else 0
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="hero-kicker">🔥 Scanner premium • interface de venda</div>
            <div class="hero-title">Tome decisão em segundos.<br>Entre forte, cautela ou evite.</div>
            <div class="hero-subtitle">
                Uma tela feita para parecer produto profissional de apostas: picks em cards grandes,
                semáforo dominante, leitura rápida e oferta VIP pronta para conversão.
            </div>
            <div class="hero-cta-row">
                <div class="cta-primary">🔥 LIBERAR SCANNER VIP</div>
                <div class="cta-secondary">🏀 TOP PLAYS DO DIA</div>
            </div>
            <div class="hero-grid">
                <div class="hero-stat">
                    <div class="hero-stat-label">Props encontradas</div>
                    <div class="hero-stat-value">{metrics.get('total_props', 0)}</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Entradas fortes</div>
                    <div class="hero-stat-value">{top_count}</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Hit rate histórico</div>
                    <div class="hero-stat-value">{history_summary.get('hit_rate', 0)}%</div>
                </div>
                <div class="hero-stat">
                    <div class="hero-stat-label">Value bets</div>
                    <div class="hero-stat-value">{metrics.get('value_bets', 0)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pick_card(row: pd.Series, number: int | None = None) -> None:
    action_text, _card_class, _badge_class = recommendation_data(row)
    icon = market_icon(str(row.get("market", "")))
    prefix = f"TOP {number}" if number is not None else str(row.get("confidence_label", "BAIXA"))

    prob = float(row.get("recommended_prob", 0))
    edge = float(row.get("edge_percent", 0))
    odd = float(row.get("best_price_decimal", 0))
    books = int(row.get("books_count", 0))
    line = float(row.get("line", 0))
    confidence_score = int(row.get("confidence_score", 0))
    prop_rank = float(row.get("prop_rank", 0))

    player = str(row.get("player", "-"))
    market = str(row.get("market", "-"))
    recommended_side = str(row.get("recommended_side", "-"))
    away_team = str(row.get("away_team", "-"))
    home_team = str(row.get("home_team", "-"))
    confidence_label = str(row.get("confidence_label", "BAIXA"))
    value_bet = str(row.get("value_bet", "NENHUMA"))
    reason = str(row.get("reason", "Sem leitura disponível."))

    progress = max(0, min(int(round(prob)), 100))

    with st.container(border=True):
        top_left, top_right = st.columns([4.8, 2.2])
        with top_left:
            st.caption(f"{prefix} • {icon} {market}")
        with top_right:
            st.markdown(f"**{action_text}**")

        st.markdown(f"### {player}")
        st.markdown(f"**{recommended_side} {line:.1f}**")
        st.caption(f"{away_team} vs {home_team}")
        st.progress(progress, text=f"Força do sinal: {progress}%")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Probabilidade", f"{prob:.2f}%")
        with m2:
            st.metric("Edge", f"{edge:.2f}%")
        with m3:
            st.metric("Odd", f"{odd:.2f}")
        with m4:
            st.metric("Casas", str(books))

        st.markdown(
            f"**Confiança:** {confidence_label} ({confidence_score}) &nbsp;&nbsp;&nbsp; "
            f"**Value Bet:** {value_bet} &nbsp;&nbsp;&nbsp; **Rank:** {prop_rank:.2f}",
            unsafe_allow_html=True,
        )

        b1, b2 = st.columns([3.2, 1.8])
        with b1:
            st.info(f"Leitura do scanner: {reason}")
        with b2:
            st.success(f"Decisão sugerida: {recommended_side} {line:.1f} {market}")

def main() -> None:
    inject_custom_css()

    df, diagnostics = run_scanner()
    metrics = get_dashboard_metrics(df)
    games = diagnostics.get("games", [])
    history_summary = get_history_summary()

    with st.sidebar:
        st.header("Filtros rápidos")
        st.caption("Deixe a leitura simples: escolha mercado, time e confiança mínima.")

        market_options = sorted(df["market"].dropna().unique().tolist()) if not df.empty else []
        team_options = sorted(
            set(df["home_team"].dropna().tolist() + df["away_team"].dropna().tolist())
        ) if not df.empty else []
        value_options = sorted(df["value_bet"].dropna().unique().tolist()) if not df.empty else []

        selected_markets = st.multiselect("Mercados", market_options, default=market_options)
        selected_teams = st.multiselect("Times", team_options)
        selected_values = st.multiselect("Value Bet", value_options)
        min_confidence = st.slider("Confiança mínima", 0, 100, 60, 1)
        st.markdown("---")
        st.button("🔥 LIBERAR SCANNER VIP")
        st.button("✅ SALVAR PICKS DE HOJE")

    filtered_df = apply_filters(
        df,
        markets=selected_markets,
        teams=selected_teams,
        min_confidence=min_confidence,
        value_levels=selected_values,
    )

    elite_df = filter_top_elite(filtered_df)
    ruins_df = filter_props_ruins(filtered_df)
    top_plays = get_top_plays(filtered_df, limit=6)

    render_hero(metrics, history_summary, filtered_df)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric("Props no radar", str(metrics["total_props"]), "Scanner ativo hoje")
    with m2:
        render_metric("Picks ELITE", str(metrics["elite_count"]), "Melhores sinais do dia")
    with m3:
        render_metric("Greens / Reds", f"{history_summary['greens']} / {history_summary['reds']}", "Histórico salvo")
    with m4:
        render_metric("Hit Rate", f"{history_summary['hit_rate']}%", "Performance registrada")

    st.markdown('<div class="section-title">Tela inicial matadora</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle-text">Os melhores picks aparecem primeiro, em cards grandes e leitura imediata.</div>', unsafe_allow_html=True)

    if top_plays.empty:
        st.warning("Nenhuma prop encontrada com os filtros atuais.")
    else:
        for idx, (_, row) in enumerate(top_plays.iterrows(), start=1):
            render_pick_card(row, number=idx)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🔥 Vitrine VIP", "🟢 Top Elite", "🔴 Evitar", "📊 Scanner Completo", "✅ Histórico"]
    )

    with tab1:
        left, right = st.columns([1.35, 0.95])

        with left:
            st.markdown('<div class="section-title">Jogos de hoje</div>', unsafe_allow_html=True)
            st.markdown('<div class="games-wrap">', unsafe_allow_html=True)
            if not games:
                st.warning("Nenhum jogo encontrado na The Odds API/cache.")
            else:
                games_df = pd.DataFrame(games)
                st.dataframe(
                    translate_games_df(games_df),
                    hide_index=True,
                    use_container_width=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">Top Elite do dia</div>', unsafe_allow_html=True)
            if elite_df.empty:
                st.info("Nenhuma entrada elite encontrada com os filtros atuais.")
            else:
                for idx, (_, row) in enumerate(elite_df.head(4).iterrows(), start=1):
                    render_pick_card(row, number=idx)

        with right:
            st.markdown('<div class="section-title">Oferta pronta para vender</div>', unsafe_allow_html=True)
            st.markdown(
                """
                <div class="offer-box">
                    <div class="hero-kicker" style="margin-bottom:0.6rem;">ACESSO VIP</div>
                    <div style="font-size:1.55rem; font-weight:950; color:#fff;">NBA Scanner Pro VIP</div>
                    <div class="offer-price">R$ 49,90<span style="font-size:0.95rem; color:#93c5fd; font-weight:700;"> / mês</span></div>
                    <div class="offer-sub">
                        Semáforo visual, picks do dia, scanner completo, histórico de greens e reds,
                        leitura rápida e interface premium para assinatura.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button("🔥 ASSINAR AGORA")
            st.button("💬 FALAR NO WHATSAPP")

            st.markdown('<div class="section-title">Diagnóstico do provider</div>', unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            with p1:
                render_diag_card("Eventos", str(diagnostics.get("events_source", "-")))
            with p2:
                render_diag_card("Placar", str(diagnostics.get("scores_source", "-")))
            p3, p4 = st.columns(2)
            with p3:
                render_diag_card("Props", str(diagnostics.get("props_sources", "-")))
            with p4:
                render_diag_card("Props brutas", str(diagnostics.get("raw_props_count", 0)))

    with tab2:
        st.markdown('<div class="section-title">Top Elite</div>', unsafe_allow_html=True)
        if elite_df.empty:
            st.info("Nenhuma entrada elite encontrada com os filtros atuais.")
        else:
            for _, row in elite_df.head(15).iterrows():
                render_pick_card(row)

    with tab3:
        st.markdown('<div class="section-title">Props para evitar</div>', unsafe_allow_html=True)
        if ruins_df.empty:
            st.info("Nenhuma prop ruim encontrada.")
        else:
            for _, row in ruins_df.head(15).iterrows():
                render_pick_card(row)

    with tab4:
        st.markdown('<div class="section-title">Scanner completo</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtle-text">A tabela continua disponível, mas o foco principal agora está nos cards e na decisão rápida.</div>', unsafe_allow_html=True)
        if filtered_df.empty:
            st.info("Nenhuma linha disponível após os filtros.")
        else:
            st.dataframe(
                build_main_table(filtered_df),
                hide_index=True,
                use_container_width=True,
            )

        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.markdown('<div class="section-title">Distribuição por confiança</div>', unsafe_allow_html=True)
            if not filtered_df.empty:
                conf_counts = (
                    filtered_df["confidence_label"]
                    .value_counts()
                    .rename_axis("confidence_label")
                    .reset_index(name="count")
                )
                fig = px.bar(conf_counts, x="confidence_label", y="count", title="Props por confiança")
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

        with chart_right:
            st.markdown('<div class="section-title">Ranking do scanner</div>', unsafe_allow_html=True)
            if not filtered_df.empty:
                rank_df = filtered_df.nlargest(8, "prop_rank")[["player", "prop_rank"]]
                fig = px.bar(rank_df, x="player", y="prop_rank", title="Top ranks do dia")
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-title">Salvar picks do dia</div>', unsafe_allow_html=True)
        selected_date = st.date_input("Data dos picks", value=datetime.now())
        replace_same_date = st.checkbox("Substituir picks já salvos nesta data", value=False)

        if st.button("Salvar picks do scanner no histórico"):
            saved = save_picks_from_scanner(
                filtered_df,
                date_str=str(selected_date),
                replace_same_date=replace_same_date,
            )
            st.success(f"{saved} palpites salvos no histórico.")

    with tab5:
        st.markdown('<div class="section-title">Histórico de greens e reds</div>', unsafe_allow_html=True)

        h1, h2, h3, h4, h5, h6 = st.columns(6)
        with h1:
            render_metric("Total", str(history_summary["total"]), "Picks salvos")
        with h2:
            render_metric("Greens", str(history_summary["greens"]), "Acertos")
        with h3:
            render_metric("Reds", str(history_summary["reds"]), "Erros")
        with h4:
            render_metric("Pushes", str(history_summary["pushes"]), "Neutros")
        with h5:
            render_metric("Lucro", f"{history_summary['profit']:.2f}", "Resultado acumulado")
        with h6:
            render_metric("ROI", f"{history_summary['roi']}%", "Retorno histórico")

        st.markdown('<div class="section-title">Marcar resultado manualmente</div>', unsafe_allow_html=True)
        history_df = get_history_by_date()

        if history_df.empty:
            st.info("Nenhum palpite salvo ainda. Vá na aba Scanner Completo e clique em salvar picks.")
        else:
            unique_dates = sorted(history_df["date"].astype(str).unique().tolist(), reverse=True)
            selected_history_date = st.selectbox("Escolha a data", unique_dates)
            day_df = get_history_by_date(selected_history_date)

            if day_df.empty:
                st.info("Nenhum palpite nesta data.")
            else:
                options = []
                for _, row in day_df.iterrows():
                    label = f'{row["player"]} | {row["market"]} | {row["line"]} | {row["recommended_side"]}'
                    options.append(label)

                selected_pick_label = st.selectbox("Escolha o palpite", options)
                selected_row = day_df.iloc[options.index(selected_pick_label)]
                result_choice = st.selectbox("Resultado", ["GREEN", "RED", "PUSH"])
                stake_value = st.number_input("Stake usada", min_value=0.01, value=1.00, step=0.50)

                if st.button("Salvar resultado do palpite"):
                    update_pick_result(
                        date_str=str(selected_row["date"]),
                        event_id=str(selected_row["event_id"]),
                        player=str(selected_row["player"]),
                        market=str(selected_row["market"]),
                        line=float(selected_row["line"]),
                        recommended_side=str(selected_row["recommended_side"]),
                        result=result_choice,
                        stake=float(stake_value),
                    )
                    st.success("Resultado atualizado com sucesso.")

                st.markdown('<div class="section-title">Histórico salvo</div>', unsafe_allow_html=True)
                updated_df = get_history_by_date(selected_history_date)
                st.dataframe(
                    build_history_display(updated_df),
                    hide_index=True,
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
