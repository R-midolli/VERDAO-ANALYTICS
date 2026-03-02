"""
StatsBomb Open Data — dados gratuitos para treino e exploração.
Referência: https://github.com/statsbomb/open-data
Use como fallback e para treinar modelos de eventos (xG, etc.)
"""
import pandas as pd


def fetch_open_competitions() -> pd.DataFrame:
    """Lista todas as competições gratuitas do StatsBomb."""
    try:
        from statsbombpy import sb
        return sb.competitions()
    except Exception as e:
        print(f"⚠️  StatsBomb competitions failed: {e}")
        return pd.DataFrame()


def fetch_open_matches(competition_id: int = 11, season_id: int = 281) -> pd.DataFrame:
    """
    Busca partidas gratuitas.
    Defaults: Copa América 2024 (competition=11, season=281)
    Útil para treinar modelos de eventos com dados reais de qualidade.
    """
    try:
        from statsbombpy import sb
        return sb.matches(competition_id=competition_id, season_id=season_id)
    except Exception as e:
        print(f"⚠️  StatsBomb matches failed: {e}")
        return pd.DataFrame()


def fetch_open_events(match_id: int) -> pd.DataFrame:
    """
    Busca eventos de uma partida (passes, chutes, dribles, pressures).
    Estrutura: type, location, player, team, timestamp + atributos específicos.
    Usar para: xG model, heatmaps, passing networks, process mining.
    """
    try:
        from statsbombpy import sb
        return sb.events(match_id=match_id)
    except Exception as e:
        print(f"⚠️  StatsBomb events failed: {e}")
        return pd.DataFrame()


def build_xg_training_data() -> pd.DataFrame:
    """
    Constrói dataset de treino para modelo xG usando StatsBomb open data.
    Inspirado em: Soccermatics (David Sumpter) + Friends of Tracking.
    Features: distância ao gol, ângulo, parte do corpo, tipo de jogo.
    """
    comps = fetch_open_competitions()
    if comps.empty:
        return pd.DataFrame()

    shots_all = []
    # Usar partidas gratuitas disponíveis
    sample_matches = fetch_open_matches(competition_id=11, season_id=281)
    if sample_matches.empty:
        return pd.DataFrame()

    for match_id in sample_matches["match_id"].head(20):  # sample de 20 partidas
        events = fetch_open_events(match_id)
        if events.empty:
            continue
        shots = events[events["type"] == "Shot"].copy()
        if shots.empty:
            continue
        shots["is_goal"] = (shots["shot_outcome"] == "Goal").astype(int)
        shots_all.append(shots[["location", "shot_end_location", "shot_body_part",
                                 "shot_technique", "shot_type", "under_pressure",
                                 "is_goal"]].copy())

    if not shots_all:
        return pd.DataFrame()

    df = pd.concat(shots_all, ignore_index=True)

    # Extrair coordenadas de location (lista [x, y])
    df["x"]     = df["location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
    df["y"]     = df["location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None)
    df["end_x"] = df["shot_end_location"].apply(lambda loc: loc[0] if isinstance(loc, list) else None)
    df["end_y"] = df["shot_end_location"].apply(lambda loc: loc[1] if isinstance(loc, list) else None)

    # Features de xG (inspirado em Soccermatics)
    import numpy as np
    goal_x, goal_y = 120.0, 40.0  # coordenadas do gol no sistema StatsBomb
    df["distance_to_goal"] = np.sqrt((df["x"] - goal_x)**2 + (df["y"] - goal_y)**2)
    df["angle_to_goal"]    = np.abs(np.arctan2(np.abs(df["y"] - goal_y), np.abs(df["x"] - goal_x)))

    print(f"✅ StatsBomb xG training data: {df.shape} ({df['is_goal'].sum()} goals)")
    return df.dropna(subset=["x", "y", "distance_to_goal"])
