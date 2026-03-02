import streamlit as st
import pandas as pd
import polars as pl
from pathlib import Path

LEAGUES = {
    "All Competitions": None,
    "🇧🇷 Brasileirão": 71,
    "🌎 Libertadores": 13,
    "🏆 Paulistão": 475,
    "🥇 Copa do Brasil": 73,
}

def season_selector() -> int:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        try:
            curr_index = [2024, 2025, 2026].index(st.session_state.get("selected_season", 2025))
        except ValueError:
            curr_index = 1
            
        st.markdown("<div style='text-align:center;color:#888;font-size:12px;margin-bottom:-10px;'>SEASON / SAISON</div>", unsafe_allow_html=True)
        season = st.radio(
            "Season",
            options=[2024, 2025, 2026],
            index=curr_index,
            horizontal=True,
            label_visibility="collapsed",
            key="global_season_selector"
        )
    st.session_state["selected_season"] = season
    st.markdown("<br>", unsafe_allow_html=True)
    return season

def competition_selector() -> int | None:
    label = st.selectbox("Competition / Compétition", list(LEAGUES.keys()))
    return LEAGUES[label]

@st.cache_data(ttl=3600)
def load_squad(season: int, league_id: int | None = None) -> pd.DataFrame:
    """
    Load players for a specific season.
    NEVER returns players from other seasons.
    """
    path = Path("data/processed/players_features.parquet")
    if not path.exists():
        return pd.DataFrame()
    df = pl.read_parquet(path).to_pandas()
    df = df[df["season"] == season]
    df = df[df["minutes_played"] > 0]  # exclude non-participants
    if league_id:
        df = df[df["league_id"] == league_id]
    return df.reset_index(drop=True)
