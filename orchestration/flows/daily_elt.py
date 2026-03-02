"""Flow Prefect: ELT diário completo."""
from prefect import flow, task, get_run_logger
from prefect.tasks import task_input_hash
from datetime import timedelta


@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=6), retries=3, retry_delay_seconds=60)
def extract_api_football() -> dict:
    logger = get_run_logger()
    from src.ingestion.api_football import fetch_players, fetch_injuries, fetch_fixtures, save_raw
    logger.info("📡 Extracting API-Football data...")
    players  = fetch_players()
    injuries = fetch_injuries()
    fixtures = fetch_fixtures()
    save_raw(players,  "players")
    save_raw(injuries, "injuries")
    save_raw(fixtures, "fixtures")
    logger.info(f"✅ API-Football: {len(players)} players, {len(fixtures)} fixtures")
    return {"players": len(players), "fixtures": len(fixtures), "injuries": len(injuries)}


@task(retries=2, retry_delay_seconds=30)
def extract_fbref() -> dict:
    logger = get_run_logger()
    from src.ingestion.fbref import fetch_fbref_stats, save_fbref
    logger.info("📊 Extracting FBref advanced stats...")
    df = fetch_fbref_stats()
    if not df.empty:
        save_fbref(df)
        logger.info(f"✅ FBref: {len(df)} rows")
        return {"rows": len(df)}
    logger.warning("⚠️  FBref returned empty — skipping")
    return {"rows": 0}


@task(retries=2, retry_delay_seconds=30)
def extract_understat() -> dict:
    logger = get_run_logger()
    from src.ingestion.understat import fetch_team_xg, save_understat
    logger.info("🎯 Extracting Understat xG data...")
    df = fetch_team_xg()
    if not df.empty:
        save_understat(df)
        logger.info(f"✅ Understat: {len(df)} matches with xG")
        return {"matches": len(df)}
    logger.warning("⚠️  Understat returned empty — skipping")
    return {"matches": 0}


@task
def transform_players(api_results: dict) -> dict:
    logger = get_run_logger()
    from src.transform.players import run_player_transform
    logger.info("🔄 Transforming player data...")
    shape = run_player_transform()
    logger.info(f"✅ Players transform: {shape}")
    return {"shape": shape}


@task
def transform_matches() -> dict:
    logger = get_run_logger()
    from src.transform.matches import run_match_transform
    logger.info("🔄 Transforming match data...")
    shape = run_match_transform()
    logger.info(f"✅ Matches transform: {shape}")
    return {"shape": shape}


@task(retries=2)
def load_to_supabase(player_result: dict, match_result: dict) -> None:
    logger = get_run_logger()
    from src.storage.supabase_client import upsert_players, upsert_matches
    logger.info("☁️  Loading to Supabase...")
    upsert_players()
    upsert_matches()
    logger.info("✅ Supabase upsert complete")


@flow(name="verdao-daily-elt", log_prints=True)
def daily_elt_flow():
    """ELT diário: extrai → transforma → carrega no Supabase."""
    # Extração paralela das 3 fontes
    api_result   = extract_api_football()
    fbref_result = extract_fbref()
    xg_result    = extract_understat()

    # Transformação (após extração)
    player_result = transform_players(api_result)
    match_result  = transform_matches()

    # Load final
    load_to_supabase(player_result, match_result)

    print(f"""
    ✅ Daily ELT Complete
    ━━━━━━━━━━━━━━━━━━━━
    API-Football : {api_result}
    FBref        : {fbref_result}
    Understat    : {xg_result}
    Players      : {player_result}
    Matches      : {match_result}
    """)


if __name__ == "__main__":
    daily_elt_flow()
