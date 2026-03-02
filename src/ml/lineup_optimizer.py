"""
Lineup Optimizer (PuLP MILP).
Seleciona os 11 melhores jogadores baseados no performance score.
"""
import pandas as pd
import pulp


def optimize_lineup(df: pd.DataFrame, formation: dict) -> pd.DataFrame | None:
    """
    Otimiza a escalação inicial para maximizar gols e assistências projetados,
    respeitando restrições de posição.
    """
    if df.empty:
        return None
        
    # Usa predict do performance model, senão gols e assistências como heuristica
    from src.ml.performance import predict
    
    players = []
    
    for i, row in df.iterrows():
        try:
            perf = predict(row.to_dict())["prediction"]
        except Exception:
            perf = row.get("goals_total", 0) + row.get("assists_total", 0)
            
        pos = row.get("position", "")
        # Normaliza posições
        if "Goal" in pos:
            cat = "GK"
        elif "Defen" in pos:
            cat = "DF"
        elif "Midfi" in pos:
            cat = "MF"
        elif "Attack" in pos:
            cat = "FW"
        else:
            cat = "MF"  # fallback
        
        minutes = row.get("minutes_played", 0)
        if minutes > 0: # Apenas jogadores ativos
            players.append({
                "idx": i,
                "name": row.get("name"),
                "cat": cat,
                "perf": perf,
            })
            
    if len(players) < 11:
        print("⚠️  Not enough players to form a lineup.")
        return None
        
    prob = pulp.LpProblem("LineupOptimization", pulp.LpMaximize)
    
    player_vars = {p["idx"]: pulp.LpVariable(f"player_{p['idx']}", cat="Binary") for p in players}
    
    # Objetivo: Maximizar performance total
    prob += pulp.lpSum([p["perf"] * player_vars[p["idx"]] for p in players])
    
    # Restrições: Total de 11 jogadores
    prob += pulp.lpSum([player_vars[p["idx"]] for p in players]) == 11
    
    # Restrições de Posição
    for pos_cat, req_count in formation.items():
        prob += pulp.lpSum([player_vars[p["idx"]] for p in players if p["cat"] == pos_cat]) == req_count
        
    try:
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
    except Exception as e:
        print(f"⚠️  Optimizer failed: {e}")
        return None
        
    if pulp.LpStatus[prob.status] != "Optimal":
        print("⚠️  Optimal lineup not found. Adjust formation constraints.")
        return None
        
    selected_indices = [p["idx"] for p in players if player_vars[p["idx"]].varValue == 1.0]
    
    lineup_df = df.loc[selected_indices].copy()
    
    print(f"✅ Lineup generated for formation {formation}")
    return lineup_df


if __name__ == "__main__":
    from src.ml.performance import load_data
    df = load_data()
    formation = {"GK":1, "DF":4, "MF":3, "FW":3}
    lineup = optimize_lineup(df, formation)
    if lineup is not None:
        print(lineup[["name", "position"]])
