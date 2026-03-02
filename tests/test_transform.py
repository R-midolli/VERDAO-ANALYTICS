import polars as pl


MOCK_PLAYERS = [
    {
        "player": {"id": 1, "name": "Endrick", "age": 18, "nationality": "Brazil", "photo": ""},
        "statistics": [{
            "games":    {"position": "Attacker", "minutes": 1500, "appearences": 22, "lineups": 18},
            "goals":    {"total": 10, "assists": 4},
            "passes":   {"accuracy": 75},
            "dribbles": {"success": 18, "attempts": 25},
            "duels":    {"total": 90, "won": 52},
        }],
    },
    {
        "player": {"id": 2, "name": "Marcos Rocha", "age": 34, "nationality": "Brazil", "photo": ""},
        "statistics": [{
            "games":    {"position": "Defender", "minutes": 2100, "appearences": 28, "lineups": 25},
            "goals":    {"total": 1, "assists": 2},
            "passes":   {"accuracy": 82},
            "dribbles": {"success": 5, "attempts": 9},
            "duels":    {"total": 150, "won": 95},
        }],
    },
]


def test_parse_returns_correct_shape():
    from src.transform.players import parse_api_football
    df = parse_api_football(MOCK_PLAYERS)
    assert df.shape[0] == 2
    assert "player_id" in df.columns
    assert "goals_total" in df.columns


def test_build_features_creates_expected_columns():
    from src.transform.players import parse_api_football, build_features
    df = build_features(parse_api_football(MOCK_PLAYERS))
    for col in ["goals_p90", "assists_p90", "duel_win_pct", "position_encoded", "contributions_per_game"]:
        assert col in df.columns, f"Missing column: {col}"


def test_goals_p90_calculation():
    from src.transform.players import parse_api_football, build_features
    df = build_features(parse_api_football(MOCK_PLAYERS))
    endrick = df.filter(pl.col("name") == "Endrick")
    expected = round(10 / (1500 / 90), 3)
    assert abs(endrick["goals_p90"][0] - expected) < 0.01


def test_position_encoding():
    from src.transform.players import parse_api_football, build_features
    df = build_features(parse_api_football(MOCK_PLAYERS))
    attacker = df.filter(pl.col("name") == "Endrick")["position_encoded"][0]
    defender = df.filter(pl.col("name") == "Marcos Rocha")["position_encoded"][0]
    assert attacker == 3
    assert defender == 1
