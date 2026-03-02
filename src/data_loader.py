import pandas as pd
import requests
from pathlib import Path
import json

class PalmeirasDataLoader:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Palmeiras IDs
        self.fbref_id = "abdce579"
        self.fbref_slug = "Palmeiras-Stats"
        # TheSportsDB - Palmeiras team ID is 134465
        self.tsdb_team_id = "134465"
        self.tsdb_api_key = "123"
        
    def fetch_fbref_squad_stats(self, season="2024"):
        """Fetch general squad stats from FBref for a given season (All Competitions)"""
        print(f"Fetching FBref stats for season {season}...")
        
        # Need to handle current vs past seasons URL structure in FBref
        if season == "2024":
            # Example: current or most recent full season usually has the base URL
            url = f"https://fbref.com/en/squads/{self.fbref_id}/{season}/{self.fbref_slug}"
        else:
            url = f"https://fbref.com/en/squads/{self.fbref_id}/{season}/{season}-{self.fbref_slug}"
            
        try:
            # We use match=".+" to grab all tables, the first one is usually 'Standard Stats'
            dfs = pd.read_html(url)
            
            # The first table is 'Standard Stats'
            df = dfs[0]
            
            # Clean MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[1] if "Unnamed" in col[0] else f"{col[0]}_{col[1]}" for col in df.columns]
                
            # Filter out the "Squad Total" and "Opponent Total" rows
            if "Player" in df.columns:
                df = df[~df["Player"].isin(["Squad Total", "Opponent Total"])]
                
            # Save to parquet
            output_path = self.processed_dir / f"squad_{season}.parquet"
            df.to_parquet(output_path)
            print(f"Saved {len(df)} players to {output_path}")
            return df
        except Exception as e:
            print(f"Error fetching FBref data: {e}")
            return pd.DataFrame()

    def fetch_tsdb_next_matches(self):
        """Fetch next upcoming matches from TheSportsDB"""
        print("Fetching next matches from TheSportsDB...")
        url = f"https://www.thesportsdb.com/api/v1/json/{self.tsdb_api_key}/eventsnext.php?id={self.tsdb_team_id}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            events = data.get("events", [])
            
            if not events:
                print("No upcoming events found.")
                return pd.DataFrame()
                
            df = pd.DataFrame(events)
            if not df.empty:
                cols_to_keep = ["idEvent", "strEvent", "strFilename", "strLeague", "strHomeTeam", "strAwayTeam", "dateEvent", "strTime", "strVenue", "strThumb"]
                existing_cols = [c for c in cols_to_keep if c in df.columns]
                df = df[existing_cols]
                
                output_path = self.processed_dir / "next_matches.parquet"
                df.to_parquet(output_path)
                print(f"Saved {len(df)} next matches.")
                return df
            return df
        except Exception as e:
            print(f"Error fetching TheSportsDB data (next): {e}")
            return pd.DataFrame()

    def fetch_tsdb_last_matches(self):
        """Fetch last matches from TheSportsDB"""
        print("Fetching last results from TheSportsDB...")
        url = f"https://www.thesportsdb.com/api/v1/json/{self.tsdb_api_key}/eventslast.php?id={self.tsdb_team_id}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            events = data.get("results", [])
            
            if not events:
                return pd.DataFrame()
                
            df = pd.DataFrame(events)
            if not df.empty:
                cols_to_keep = ["idEvent", "strEvent", "strLeague", "strHomeTeam", "strAwayTeam", "intHomeDefenseScore", "intHomeScore", "intAwayScore", "dateEvent", "strThumb"]
                existing_cols = [c for c in cols_to_keep if c in df.columns]
                df = df[existing_cols]
                
                output_path = self.processed_dir / "last_matches.parquet"
                df.to_parquet(output_path)
                return df
            return df
        except Exception as e:
            print(f"Error fetching TheSportsDB data: {e}")
            return pd.DataFrame()

    def run_all(self):
        self.fetch_fbref_squad_stats("2024")
        self.fetch_tsdb_next_matches()
        self.fetch_tsdb_last_matches()

if __name__ == "__main__":
    loader = PalmeirasDataLoader()
    loader.run_all()
