"""
FBref stats via soccerdata.
Referência: https://soccerdata.readthedocs.io
Inspirado em: Friends of Tracking + worldfootballR approach
"""
from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path

load_dotenv()
SEASONS = [int(x) for x in os.getenv("SEASONS", "2025").split(",")]


def fetch_fbref_stats() -> pd.DataFrame:
    """
    Stats avançadas do FBref: standard, shooting, passing, possession.
    Inclui xG, xA, progressive passes, pressures.
    """
    try:
        import soccerdata as sd
        fbref = sd.FBref(leagues="BRA-Brasileirao", seasons=SEASONS)

        dfs = {}
        for stat in ["standard", "shooting", "passing", "possession", "defense"]:
            try:
                dfs[stat] = fbref.read_player_season_stats(stat_type=stat)
            except Exception as e:
                print(f"⚠️  FBref stat_type={stat} failed: {e}")

        if not dfs:
            return pd.DataFrame()

        df = dfs.get("standard", pd.DataFrame())
        for key, extra in dfs.items():
            if key != "standard" and not extra.empty:
                merge_cols = [c for c in ["player", "team", "season"] if c in extra.columns]
                df = df.merge(extra, on=merge_cols, how="left", suffixes=("", f"_{key}"))

        # Filtrar só Palmeiras
        if "team" in df.columns:
            df = df[df["team"].str.contains("Palmeiras", na=False, case=False)]

        print(f"✅ FBref: {df.shape}")
        return df.reset_index(drop=True)

    except Exception as exc:
        print(f"⚠️  FBref unavailable ({exc})")
        return pd.DataFrame()


def save_fbref(df: pd.DataFrame) -> Path:
    path = Path("data/raw/fbref_stats.parquet")
    path.parent.mkdir(parents=True, exist_ok=True)
    import polars as pl
    pl.from_pandas(df).write_parquet(path)
    print(f"💾 FBref saved → {path}")
    return path


def load_fbref() -> pd.DataFrame:
    path = Path("data/raw/fbref_stats.parquet")
    if not path.exists():
        print("⚠️  fbref_stats.parquet not found — returning empty DataFrame")
        return pd.DataFrame()
    import polars as pl
    return pl.read_parquet(path).to_pandas()


if __name__ == "__main__":
    print("🔄 Fetching from FBref...")
    df = fetch_fbref_stats()
    if not df.empty:
        save_fbref(df)
    print("✅ Done!")
