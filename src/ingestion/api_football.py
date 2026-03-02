from dotenv import load_dotenv
import os
import httpx
import json
from pathlib import Path

load_dotenv()

_KEY = os.getenv("API_FOOTBALL_KEY")
assert _KEY, "API_FOOTBALL_KEY missing"
_HOST = os.getenv("API_FOOTBALL_HOST")
assert _HOST, "API_FOOTBALL_HOST missing"
HEADERS  = {"x-rapidapi-key": _KEY, "x-rapidapi-host": _HOST}
BASE_URL = "https://v3.football.api-sports.io"
TEAM_ID  = int(os.getenv("PALMEIRAS_TEAM_ID", "121"))
SEASONS  = [int(x) for x in os.getenv("SEASONS", "2025").split(",")]
LEAGUE_IDS = [int(x) for x in os.getenv("LEAGUE_IDS", "71").split(",")]


def _get(endpoint: str, params: dict) -> dict:
    import time
    with httpx.Client(headers=HEADERS, timeout=30) as c:
        for _ in range(5):
            resp = c.get(f"{BASE_URL}/{endpoint}", params=params)
            resp.raise_for_status()
            data = resp.json()
            errs = data.get("errors", {})
            
            # API-Football returns a dict of errors if rate limited
            if isinstance(errs, dict) and "requests" in errs:
                if "limit" in str(errs["requests"]).lower():
                    print("⚠️ Rate limit reached... Sleeping 60s")
                    time.sleep(65)
                    continue
            elif isinstance(errs, list) and errs and "rate limit" in str(errs[0]).lower():
                print("⚠️ Rate limit reached... Sleeping 60s")
                time.sleep(65)
                continue
                
            return data
        return {}


def fetch_players() -> list[dict]:
    players = []
    for s in SEASONS:
        page = 1
        while True:
            data = _get("players", {"team": TEAM_ID, "season": s, "page": page})
            for p in data["response"]:
                p["query_season"] = s
                players.append(p)
            if page >= data.get("paging", {}).get("total", 1):
                break
            page += 1
    return players


def fetch_injuries() -> list[dict]:
    injuries = []
    for s in SEASONS:
        data = _get("injuries", {"team": TEAM_ID, "season": s})
        for i in data["response"]:
            i["query_season"] = s
            injuries.append(i)
    return injuries


def fetch_fixtures() -> list[dict]:
    fixtures = []
    for s in SEASONS:
        data = _get("fixtures", {"team": TEAM_ID, "season": s})
        for f in data["response"]:
            f["query_season"] = s
            fixtures.append(f)
    return fixtures


def fetch_next_fixture() -> dict | None:
    """Retorna o próximo jogo do Palmeiras."""
    # try looking for next fixture across available seasons
    for s in SEASONS:
        data = _get("fixtures", {"team": TEAM_ID, "season": s, "next": 1})
        resp = data.get("response", [])
        if resp:
            return resp[0]
    return None


def fetch_standings() -> list[dict]:
    all_standings = []
    for s in SEASONS:
        for lid in LEAGUE_IDS:
            data = _get("standings", {"league": lid, "season": s})
            resp = data.get("response")
            if not resp:
                continue
            
            league_data = resp[0].get("league", {})
            st_list = league_data.get("standings", [])
            
            if st_list and len(st_list) > 0:
                st = st_list[0]
                for row in st:
                    row["query_season"] = s
                    row["league_id"] = lid
                all_standings.extend(st)
    return all_standings


def save_raw(data: list[dict], name: str) -> Path:
    path = Path("data/raw") / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 {path}  ({len(data)} records)")
    return path


def load_raw(name: str) -> list[dict]:
    path = Path("data/raw") / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Run daily_elt first. Missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    print("🔄 Fetching from API-Football...")
    save_raw(fetch_players(), "players")
    save_raw(fetch_injuries(), "injuries")
    save_raw(fetch_fixtures(), "fixtures")
    save_raw(fetch_standings(), "standings")
    print("✅ Done!")
