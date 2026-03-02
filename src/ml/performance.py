"""
Modelo de predição de performance (gols + assists).
Referência: Soccermatics + socceraction approach.
"""
from dotenv import load_dotenv
import pandas as pd
import polars as pl
import xgboost as xgb
import optuna
import shap
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

load_dotenv()
optuna.logging.set_verbosity(optuna.logging.WARNING)

FEATURES = [
    "goals_p90", "assists_p90", "xg_p90", "xa_p90",
    "duel_win_pct", "dribble_success_pct", "starter_pct",
    "progressive_passes_p90", "minutes_played", "games_total",
    "age", "position_encoded", "contributions_per_game",
]


def load_data() -> pd.DataFrame:
    path = Path("data/processed/players_features.parquet")
    if not path.exists():
        raise FileNotFoundError("Run daily_elt_flow first.")
    return pl.read_parquet(path).to_pandas()


def train_and_save() -> dict:
    df = load_data()
    df["target"] = df["goals_total"] + df["assists_total"]

    available = [f for f in FEATURES if f in df.columns]
    X = df[available].fillna(0)
    y = df["target"].fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    def objective(trial):
        p = {
            "n_estimators":     trial.suggest_int("n_estimators", 100, 400),
            "max_depth":        trial.suggest_int("max_depth", 3, 7),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "random_state": 42,
        }
        m = xgb.XGBRegressor(**p, verbosity=0)
        m.fit(X_train, y_train)
        return mean_absolute_error(y_test, m.predict(X_test))

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=40, show_progress_bar=True)

    model = xgb.XGBRegressor(**study.best_params, random_state=42, verbosity=0)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    metrics = {
        "mae":  round(float(mean_absolute_error(y_test, preds)), 3),
        "rmse": round(float(root_mean_squared_error(y_test, preds)), 3),
    }
    print(f"📈 Performance → MAE: {metrics['mae']} | RMSE: {metrics['rmse']}")

    # SHAP
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    Path("data/outputs").mkdir(parents=True, exist_ok=True)
    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    plt.savefig("data/outputs/shap_performance.png", dpi=150, bbox_inches="tight", facecolor="#0D0D0D")
    plt.close()

    Path("models").mkdir(exist_ok=True)
    joblib.dump(model,     "models/performance_model.pkl")
    joblib.dump(explainer, "models/performance_explainer.pkl")
    return metrics


def predict(player_row: dict) -> dict:
    model     = joblib.load("models/performance_model.pkl")
    explainer = joblib.load("models/performance_explainer.pkl")
    X         = pd.DataFrame([player_row])[[f for f in FEATURES if f in player_row]].fillna(0)
    pred      = model.predict(X)[0]
    sv        = explainer.shap_values(X)[0]
    return {"prediction": round(float(pred), 2), "shap": dict(zip(FEATURES, sv.tolist()))}


if __name__ == "__main__":
    train_and_save()
