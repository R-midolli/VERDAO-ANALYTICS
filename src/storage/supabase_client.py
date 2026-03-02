"""
Supabase client to upsert data to PostgreSQL.
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import polars as pl
from pathlib import Path

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

def get_client() -> Client | None:
    if not url or not key or url == "https://xxxxxxxx.supabase.co":
        return None
    return create_client(url, key)

def upsert_players() -> None:
    supabase = get_client()
    if not supabase:
        print("⚠️ Supabase credentials not set, skipping players upsert.")
        return
        
    path = Path("data/processed/players_features.parquet")
    if not path.exists():
        return
        
    df = pl.read_parquet(path)
    records = df.to_dicts()
    
    try:
        # In a real scenario, table MUST exist. We assume "players" table.
        # Fallback ignoring if it causes error
        supabase.table("players").upsert(records).execute()
        print(f"☁️ Supabase upserted {len(records)} players.")
    except Exception as e:
        print(f"⚠️ Supabase upsert failed: {e}")

def upsert_matches() -> None:
    supabase = get_client()
    if not supabase:
        print("⚠️ Supabase credentials not set, skipping matches upsert.")
        return
        
    path = Path("data/processed/matches_features.parquet")
    if not path.exists():
        return
        
    df = pl.read_parquet(path)
    
    # Supabase JSON serialization expects standard types
    df_pd = df.to_pandas()
    # Handle NaN values explicitly
    for col in df_pd.columns:
        if df_pd[col].dtype == 'float64' or df_pd[col].dtype == 'float32':
            df_pd[col] = df_pd[col].fillna(-1) # Placeholder missing float values
            
    records = df_pd.to_dict(orient="records")
    
    try:
        supabase.table("matches").upsert(records).execute()
        print(f"☁️ Supabase upserted {len(records)} matches.")
    except Exception as e:
        print(f"⚠️ Supabase upsert failed: {e}")
