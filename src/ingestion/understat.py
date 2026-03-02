"""
Understat xG data — alternativa gratuita ao API-Football para xG.
Site: https://understat.com — tem dados do Brasileirão desde 2014.
"""
import pandas as pd
from pathlib import Path
import json


def fetch_team_xg(team_name: str = "Palmeiras") -> pd.DataFrame:
    """
    Busca dados de xG por partida do Palmeiras via Understat.
    Fallback: retorna DataFrame vazio se indisponível.
    """
    try:
        import httpx
        from bs4 import BeautifulSoup
        import re
        import os
        from dotenv import load_dotenv

        load_dotenv()
        seasons = [int(x) for x in os.getenv("SEASONS", "2025").split(",")]
        
        headers = {"User-Agent": "Mozilla/5.0 (compatible; research bot)"}
        all_dfs = []

        with httpx.Client(timeout=20, headers=headers) as client:
            for s in seasons:
                # Understat uses starting year of the season (e.g. 2024 for 24/25)
                url = f"https://understat.com/team/{team_name}/{s}"
                resp = client.get(url)
                if resp.status_code != 200:
                    continue

                soup    = BeautifulSoup(resp.text, "html.parser")
                scripts = soup.find_all("script")

                for script in scripts:
                    if "datesData" in str(script):
                        content   = str(script)
                        json_str  = re.search(r"JSON\.parse\('(.+?)'\)", content)
                        if json_str:
                            data = json.loads(json_str.group(1).encode().decode("unicode_escape"))
                            df   = pd.DataFrame(data)
                            df["team"] = team_name
                            df["query_season"] = s
                            all_dfs.append(df)
                            break
                            
        if all_dfs:
            final_df = pd.concat(all_dfs, ignore_index=True)
            print(f"✅ Understat: {len(final_df)} matches for {team_name}")
            return final_df

        return pd.DataFrame()

    except Exception as e:
        print(f"⚠️  Understat unavailable ({e}) — returning empty DataFrame")
        return pd.DataFrame()


def save_understat(df: pd.DataFrame) -> Path:
    path = Path("data/raw/understat_xg.parquet")
    path.parent.mkdir(parents=True, exist_ok=True)
    import polars as pl
    pl.from_pandas(df.astype(str)).write_parquet(path)
    return path


if __name__ == "__main__":
    print("🔄 Fetching from Understat...")
    df = fetch_team_xg()
    if not df.empty:
        save_understat(df)
    print("✅ Done!")
