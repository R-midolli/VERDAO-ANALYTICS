"""
Modelo de risco de lesão (Injury Risk).
Referência: CatBoostClassifier com features de carga de trabalho e histórico.
"""
from dotenv import load_dotenv
import pandas as pd
import polars as pl
import numpy as np
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from pathlib import Path
import optuna
import joblib

load_dotenv()
optuna.logging.set_verbosity(optuna.logging.WARNING)

FEATURES = [
    "age", "minutes_played", "games_total", "games_started",
    "days_since_injury", "injury_history_count", 
    "duel_win_pct", "contributions_per_game"
]

def load_data() -> pd.DataFrame:
    path = Path("data/processed/players_features.parquet")
    if not path.exists():
        raise FileNotFoundError("Run daily_elt_flow first.")
    return pl.read_parquet(path).to_pandas()


def train_and_save() -> dict:
    df = load_data()
    
    available = [f for f in FEATURES if f in df.columns]
    X = df[available].fillna(0)
    
    # Simulate a target "injury_risk" if exact injuries for next match are unknown
    # High risk correlates with high minutes, low days since injury, high injury history count
    # In a real scenario, this target comes from actual next-match injury history
    np.random.seed(42)
    risk_score = (X.get("minutes_played", 0) / 3000) * 0.4 + \
                 (X.get("injury_history_count", 0) / 10) * 0.4 + \
                 (1 - (X.get("days_since_injury", 365).clip(0, 365) / 365)) * 0.2
    
    # Inject some noise and binarize
    y = (risk_score + np.random.normal(0, 0.1, size=len(risk_score)) > 0.4).astype(int)

    # Need at least 2 classes
    if len(np.unique(y)) < 2:
        y[0] = 1 - y[0]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    def objective(trial):
        p = {
            "iterations": trial.suggest_int("iterations", 50, 200),
            "depth": trial.suggest_int("depth", 3, 6),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
            "verbose": 0,
            "random_seed": 42
        }
        m = CatBoostClassifier(**p)
        m.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=20)
        return m.get_best_score().get("validation").get("Logloss")

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=15, show_progress_bar=True)
    
    model = CatBoostClassifier(**study.best_params, verbose=0, random_seed=42)
    model.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=20)
    
    preds_proba = model.predict_proba(X_test)[:, 1]
    auc = round(float(roc_auc_score(y_test, preds_proba)), 3)
    
    print(f"🏥 Injury Risk → AUC: {auc}")
    
    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/injury_risk.pkl")
    return {"auc": auc}


def predict(player_row: dict) -> dict:
    if not Path("models/injury_risk.pkl").exists():
        return {"prediction": 0.1}  # fallback
        
    model = joblib.load("models/injury_risk.pkl")
    X = pd.DataFrame([player_row])[[f for f in FEATURES if f in player_row]].fillna(0)
    proba = model.predict_proba(X)[0][1]
    return {"prediction": round(float(proba), 3)}


if __name__ == "__main__":
    train_and_save()
