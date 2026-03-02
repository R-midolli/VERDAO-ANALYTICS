"""
Parquet storage utilities powered by Polars.
"""
import polars as pl
import pandas as pd
from pathlib import Path


def save_parquet(df: pd.DataFrame | pl.DataFrame, filename: str) -> Path:
    """Save DataFrame to a Parquet file."""
    path = Path("data/processed") / f"{filename}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if isinstance(df, pd.DataFrame):
        df = pl.from_pandas(df)
        
    df.write_parquet(path)
    print(f"💾 Saved {path} ({df.shape[0]} rows)")
    return path


def load_parquet(filename: str, as_pandas: bool = False) -> pd.DataFrame | pl.DataFrame:
    """Load DataFrame from a Parquet file."""
    path = Path("data/processed") / f"{filename}.parquet"
    if not path.exists():
        path = Path(f"data/{filename}.parquet")
        if not path.exists():
            print(f"⚠️  {path} not found.")
            return pd.DataFrame() if as_pandas else pl.DataFrame()
            
    df = pl.read_parquet(path)
    return df.to_pandas() if as_pandas else df
