"""
Feature engineering de jogadores.
Inspirado em: Friends of Tracking + Soccermatics feature sets.
"""
from dotenv import load_dotenv
import polars as pl
from pathlib import Path
from datetime import datetime

load_dotenv()


def parse_api_football(raw: list[dict]) -> pl.DataFrame:
    rows = []
    for entry in raw:
        p     = entry.get("player", {})
        query_season = entry.get("query_season")
        stats = entry.get("statistics", [{}])[0]
        g, go, pa, dr, du = (
            stats.get("games", {}), stats.get("goals", {}),
            stats.get("passes", {}), stats.get("dribbles", {}),
            stats.get("duels", {}),
        )
        lg = stats.get("league", {})
        rows.append({
            "player_id":          p.get("id"),
            "season":             query_season,
            "league_id":          lg.get("id"),
            "league_name":        lg.get("name"),
            "name":               p.get("name", ""),
            "age":                p.get("age") or 0,
            "nationality":        p.get("nationality", ""),
            "photo_url":          p.get("photo", ""),
            "position":           g.get("position", ""),
            "minutes_played":     g.get("minutes") or 0,
            "games_total":        g.get("appearences") or 0,
            "games_started":      g.get("lineups") or 0,
            "goals_total":        go.get("total") or 0,
            "assists_total":      go.get("assists") or 0,
            "passes_accuracy":    pa.get("accuracy") or 0,
            "dribbles_success":   dr.get("success") or 0,
            "dribbles_attempts":  dr.get("attempts") or 0,
            "duels_total":        du.get("total") or 0,
            "duels_won":          du.get("won") or 0,
        })
    return pl.DataFrame(rows)


def build_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Engenharia de features seguindo o padrão de Soccermatics:
    - Métricas por 90min (normalização de tempo)
    - Ratios e percentuais
    - Encoding de posição
    """
    df = df.with_columns([
        (pl.col("goals_total") / (pl.col("minutes_played") / 90).clip(lower_bound=0.1)).alias("goals_p90"),
        (pl.col("assists_total") / (pl.col("minutes_played") / 90).clip(lower_bound=0.1)).alias("assists_p90"),
        (pl.col("duels_won") / pl.col("duels_total").clip(lower_bound=1) * 100).alias("duel_win_pct"),
        (pl.col("dribbles_success") / pl.col("dribbles_attempts").clip(lower_bound=1) * 100).alias("dribble_success_pct"),
        (pl.col("games_started") / pl.col("games_total").clip(lower_bound=1) * 100).alias("starter_pct"),
        (pl.col("goals_total") + pl.col("assists_total")).alias("goal_contributions"),
        ((pl.col("goals_total") + pl.col("assists_total")) / pl.col("games_total").clip(lower_bound=1)).alias("contributions_per_game"),
    ])

    pos_map = {"Goalkeeper": 0, "Defender": 1, "Midfielder": 2, "Attacker": 3}
    df = df.with_columns(
        pl.col("position").replace(pos_map, default=2).alias("position_encoded")
    )

    # xG/xA placeholders (sobrescritos pelo enrich_with_fbref)
    df = df.with_columns([
        pl.lit(0.0).alias("xg_p90"),
        pl.lit(0.0).alias("xa_p90"),
        pl.lit(0.0).alias("progressive_passes_p90"),
        pl.lit(0.0).alias("pressures_p90"),
        pl.lit(0).alias("days_since_injury"),
        pl.lit(0).alias("injury_history_count"),
    ])
    return df


def enrich_with_fbref(df: pl.DataFrame) -> pl.DataFrame:
    """Adiciona xG, xA, progressive passes do FBref se disponível."""
    from src.ingestion.fbref import load_fbref
    fbref_df = load_fbref()
    if fbref_df.empty:
        return df

    rename_map = {}
    for col in ["npxG", "xAG", "PrgP"]:
        if col in fbref_df.columns:
            rename_map[col] = {"npxG": "xg_p90", "xAG": "xa_p90", "PrgP": "progressive_passes_p90"}[col]

    if not rename_map:
        return df
        
    fb_cols = ["player"] + (["season"] if "season" in fbref_df.columns else []) + list(rename_map.keys())

    fbref_slim = pl.from_pandas(
        fbref_df[fb_cols].rename(columns={"player": "name", **rename_map})
    )
    
    # Cast season to Int if present in both
    if "season" in fbref_slim.columns and "season" in df.columns:
        # FBref returns strings like "2024" usually
        fbref_slim = fbref_slim.with_columns(pl.col("season").cast(pl.Int64, strict=False))
        df = df.with_columns(pl.col("season").cast(pl.Int64, strict=False))
        join_cols = ["name", "season"]
    else:
        join_cols = "name"
        
    return df.join(fbref_slim, on=join_cols, how="left", suffix="_fbref").with_columns([
        pl.coalesce([pl.col(f"{c}_fbref"), pl.col(c)]).fill_null(0).alias(c)
        for c in rename_map.values()
    ]).drop([f"{c}_fbref" for c in rename_map.values()])


def enrich_with_injuries(df: pl.DataFrame, raw_injuries: list[dict]) -> pl.DataFrame:
    """Dias desde última lesão + contagem histórica."""
    from collections import defaultdict
    today         = datetime.today()
    count: dict   = defaultdict(int)
    last:  dict   = {}

    for entry in raw_injuries:
        pid = entry.get("player", {}).get("id")
        if not pid:
            continue
        count[pid] += 1
        date_str = entry.get("fixture", {}).get("date", "")
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str[:10])
                if pid not in last or dt > last[pid]:
                    last[pid] = dt
            except ValueError:
                pass

    return df.with_columns([
        pl.col("player_id").map_elements(lambda p: count.get(p, 0), return_dtype=pl.Int32).alias("injury_history_count"),
        pl.col("player_id").map_elements(
            lambda p: (today - last[p]).days if p in last else 365,
            return_dtype=pl.Int32,
        ).alias("days_since_injury"),
    ])


def run_player_transform() -> tuple:
    from src.ingestion.api_football import load_raw
    raw_players  = load_raw("players")
    raw_injuries = load_raw("injuries") if Path("data/raw/injuries.json").exists() else []

    df = parse_api_football(raw_players)
    df = build_features(df)
    df = enrich_with_fbref(df)
    if raw_injuries:
        df = enrich_with_injuries(df, raw_injuries)

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.write_parquet("data/processed/players_features.parquet")
    print(f"✅ Players transform: {df.shape}")
    return df.shape


if __name__ == "__main__":
    run_player_transform()
