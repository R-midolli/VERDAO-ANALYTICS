"""
Predição de resultado de partida: win / draw / loss.
Output para o Fan Layer: "Palmeiras tem 68% de chance de vencer."
"""
from dotenv import load_dotenv
import pandas as pd
import lightgbm as lgb
import optuna
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os

load_dotenv()
optuna.logging.set_verbosity(optuna.logging.WARNING)


def load_match_data() -> pd.DataFrame:
    """Carrega e normaliza dados de partidas."""
    from src.ingestion.api_football import load_raw
    raw = load_raw("fixtures")

    rows = []
    for f in raw:
        fixture  = f.get("fixture", {})
        teams    = f.get("teams", {})
        goals    = f.get("goals", {})
        f.get("score", {})
        league   = f.get("league", {})

        home_id = teams.get("home", {}).get("id")
        teams.get("away", {}).get("id")
        home_g  = goals.get("home")
        away_g  = goals.get("away")

        if home_g is None or away_g is None:
            continue  # jogo não disputado ainda

        is_palmeiras_home = (home_id == int(os.getenv("PALMEIRAS_TEAM_ID", "121")))
        palm_goals = home_g if is_palmeiras_home else away_g
        opp_goals  = away_g if is_palmeiras_home else home_g

        if palm_goals > opp_goals:
            result = "win"
        elif palm_goals == opp_goals:
            result = "draw"
        else:
            result = "loss"

        rows.append({
            "fixture_id":   fixture.get("id"),
            "is_home":      int(is_palmeiras_home),
            "round":        league.get("round", "").replace("Regular Season - ", ""),
            "palm_goals":   palm_goals,
            "opp_goals":    opp_goals,
            "result":       result,
        })

    return pd.DataFrame(rows)


def train_and_save() -> dict:
    df = load_match_data()
    if len(df) < 10:
        print("⚠️  Not enough match data to train match outcome model")
        return {"accuracy": None, "auc": None}

    le = LabelEncoder()
    df["result_encoded"] = le.fit_transform(df["result"])

    df["round_num"] = pd.to_numeric(df["round"], errors="coerce").fillna(0)
    X = df[["is_home", "round_num"]].fillna(0)
    y = df["result_encoded"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=15,
                                random_state=42, verbose=-1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc   = round(accuracy_score(y_test, preds), 3)
    print(f"⚽ Match Outcome → Accuracy: {acc}")
    print(classification_report(y_test, preds, target_names=le.classes_))

    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/match_outcome_model.pkl")
    joblib.dump(le,    "models/match_outcome_encoder.pkl")
    return {"accuracy": acc}


def predict_next_match(is_home: bool = True) -> dict:
    """Retorna % win/draw/loss para o próximo jogo."""
    if not Path("models/match_outcome_model.pkl").exists():
        return {"win": 0.45, "draw": 0.28, "loss": 0.27}  # fallback

    model = joblib.load("models/match_outcome_model.pkl")
    le    = joblib.load("models/match_outcome_encoder.pkl")
    X     = pd.DataFrame([{"is_home": int(is_home), "round_num": 0}])
    proba = model.predict_proba(X)[0]
    return dict(zip(le.classes_, [round(float(p), 3) for p in proba]))


if __name__ == "__main__":
    train_and_save()
