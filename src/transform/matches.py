"""
Feature engineering para partidas.
Inspirado na estrutura de players.py.
"""
import polars as pl
from pathlib import Path
from src.ingestion.api_football import load_raw


def parse_fixtures(raw: list[dict]) -> pl.DataFrame:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    team_id = int(os.getenv("PALMEIRAS_TEAM_ID", "121"))
    
    rows = []
    for f in raw:
        fixture = f.get("fixture", {})
        teams   = f.get("teams", {})
        goals   = f.get("goals", {})
        league  = f.get("league", {})
        query_season = f.get("query_season")
        
        home_id = teams.get("home", {}).get("id")
        away_id = teams.get("away", {}).get("id")
        
        if home_id != team_id and away_id != team_id:
            continue
            
        home_name = teams.get("home", {}).get("name")
        away_name = teams.get("away", {}).get("name")
        
        is_home = (home_id == team_id)
        opponent = away_name if is_home else home_name
        
        palm_goals = goals.get("home") if is_home else goals.get("away")
        opp_goals  = goals.get("away") if is_home else goals.get("home")
        
        status = fixture.get("status", {}).get("short", "")
        if palm_goals is not None and opp_goals is not None:
            if palm_goals > opp_goals:
                result = "W"
            elif palm_goals == opp_goals:
                result = "D"
            else:
                result = "L"
        else:
            result = "TBD"

        rows.append({
            "fixture_id": fixture.get("id"),
            "season":     query_season,
            "league_id":  league.get("id"),
            "league_name": league.get("name"),
            "date":       fixture.get("date", "")[:10],
            "timestamp":  fixture.get("timestamp"),
            "opponent":   opponent,
            "is_home":    is_home,
            "palm_goals": palm_goals,
            "opp_goals":  opp_goals,
            "result":     result,
            "status":     status,
            "round":      league.get("round", "")
        })
        
    return pl.DataFrame(rows)


def run_match_transform() -> tuple:
    try:
        raw_fixtures = load_raw("fixtures")
    except FileNotFoundError:
        print("⚠️ No raw fixtures data found.")
        return (0, 0)
        
    df = parse_fixtures(raw_fixtures)
    
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    df.write_parquet("data/processed/matches_features.parquet")
    print(f"✅ Matches transform: {df.shape}")
    
    return df.shape

if __name__ == "__main__":
    run_match_transform()
