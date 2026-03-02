"""Registra e deploya todos os Prefect flows."""
from prefect import serve
from orchestration.flows.daily_elt import daily_elt_flow
from orchestration.flows.weekly_ml import weekly_ml_flow
from orchestration.flows.match_day import match_day_flow

if __name__ == "__main__":
    daily_deploy = daily_elt_flow.to_deployment(
        name="daily-elt",
        cron="0 7 * * *",    # 7h UTC = 8h Paris / 4h Brasília
        description="Daily ELT: API-Football + FBref + Understat → Supabase",
    )
    weekly_deploy = weekly_ml_flow.to_deployment(
        name="weekly-ml-retrain",
        cron="0 6 * * 1",    # toda segunda 6h UTC
        description="Weekly ML retrain: all models + SHAP reports",
    )
    match_deploy = match_day_flow.to_deployment(
        name="match-day-live",
        description="Triggered manually on match days for live updates",
    )
    serve(daily_deploy, weekly_deploy, match_deploy)
    print("✅ Prefect flows deployed. Dashboard: http://127.0.0.1:4200")
