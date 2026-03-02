import pytest
from unittest.mock import patch


def test_save_and_load_raw(tmp_path, monkeypatch):
    from src.ingestion.api_football import save_raw, load_raw
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "raw").mkdir(parents=True)
    data = [{"player": {"id": 1, "name": "Endrick"}}]
    save_raw(data, "players")
    loaded = load_raw("players")
    assert loaded[0]["player"]["name"] == "Endrick"


def test_load_raw_missing_raises(tmp_path, monkeypatch):
    from src.ingestion.api_football import load_raw
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data" / "raw").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        load_raw("nonexistent")


def test_statsbomb_fallback():
    """StatsBomb should return empty DataFrame on failure."""
    with patch("statsbombpy.sb.competitions", side_effect=Exception("network")):
        from src.ingestion.statsbomb import fetch_open_competitions
        df = fetch_open_competitions()
        assert df.empty


def test_understat_fallback():
    """Understat should return empty DataFrame on failure."""
    with patch("httpx.Client") as mock:
        mock.side_effect = Exception("network error")
        from src.ingestion.understat import fetch_team_xg
        df = fetch_team_xg()
        assert df.empty
