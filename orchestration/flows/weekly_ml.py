"""Flow Prefect: retrain semanal de todos os modelos."""
from prefect import flow, task, get_run_logger


@task
def retrain_performance() -> dict:
    logger = get_run_logger()
    from src.ml.performance import train_and_save
    logger.info("🤖 Retraining performance predictor...")
    metrics = train_and_save()
    logger.info(f"✅ Performance: {metrics}")
    return metrics


@task
def retrain_injury() -> dict:
    logger = get_run_logger()
    from src.ml.injury import train_and_save
    logger.info("🏥 Retraining injury risk model...")
    metrics = train_and_save()
    logger.info(f"✅ Injury: {metrics}")
    return metrics


@task
def retrain_match_outcome() -> dict:
    logger = get_run_logger()
    from src.ml.match_outcome import train_and_save
    logger.info("⚽ Retraining match outcome model...")
    metrics = train_and_save()
    logger.info(f"✅ Match Outcome: {metrics}")
    return metrics


@task
def retrain_clustering() -> dict:
    logger = get_run_logger()
    from src.ml.clustering import cluster_and_save
    logger.info("🔮 Retraining player clusters...")
    result = cluster_and_save()
    logger.info(f"✅ Clustering: {result}")
    return result


@flow(name="verdao-weekly-ml", log_prints=True)
def weekly_ml_flow():
    """Retrain semanal + gera relatório com métricas reais."""
    perf    = retrain_performance()
    injury  = retrain_injury()
    outcome = retrain_match_outcome()
    cluster = retrain_clustering()

    print(f"""
    ✅ Weekly ML Retrain Complete
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Performance : MAE={perf.get('mae','N/A')} | RMSE={perf.get('rmse','N/A')}
    Injury Risk : AUC={injury.get('auc','N/A')}
    Match Result: Accuracy={outcome.get('accuracy','N/A')} | AUC={outcome.get('auc','N/A')}
    Clustering  : Silhouette={cluster.get('silhouette','N/A')}
    """)


if __name__ == "__main__":
    weekly_ml_flow()
