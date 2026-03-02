"""
Player Clustering (KMeans + UMAP).
Agrupa jogadores em 5 perfis táticos.
"""
from dotenv import load_dotenv
import pandas as pd
import polars as pl
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import umap
from pathlib import Path
import joblib

load_dotenv()

FEATURES = [
    "goals_p90", "assists_p90", "xg_p90", "xa_p90",
    "duel_win_pct", "dribble_success_pct", "progressive_passes_p90",
    "contributions_per_game", "minutes_played"
]

def load_data() -> pd.DataFrame:
    path = Path("data/processed/players_features.parquet")
    if not path.exists():
        raise FileNotFoundError("Run daily_elt_flow first.")
    return pl.read_parquet(path).to_pandas()


def cluster_and_save() -> dict:
    df = load_data()
    
    # Filtra jogadores com poucos minutos para clusters mais consistentes
    df_valid = df[df["minutes_played"] > 180].copy()
    
    available = [f for f in FEATURES if f in df_valid.columns]
    X = df_valid[available].fillna(0)
    
    if len(X) < 5:
        print("⚠️ Not enough players for clustering")
        return {"silhouette": None}
        
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    n_clusters = min(5, len(X))
    
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = km.fit_predict(X_scaled)
    
    if len(X) > 5:
        sil_score = round(float(silhouette_score(X_scaled, clusters)), 3)
    else:
        sil_score = 0.0
        
    print(f"🔮 Clustering → Silhouette: {sil_score}")
    
    # UMAP 2D projection
    try:
        reducer = umap.UMAP(n_neighbors=min(15, len(X)-1), min_dist=0.1, random_state=42)
        embedding = reducer.fit_transform(X_scaled)
    except Exception as e:
        print(f"⚠️ UMAP failed: {e}. Using PCA fallback.")
        from sklearn.decomposition import PCA
        pca = PCA(n_components=2)
        embedding = pca.fit_transform(X_scaled)
        
    df_valid["cluster"] = clusters
    df_valid["umap_x"] = embedding[:, 0]
    df_valid["umap_y"] = embedding[:, 1]
    
    # Save the clustered features DataFrame
    out_path = Path("data/processed/players_features_clustered.parquet")
    pl.from_pandas(df_valid).write_parquet(out_path)
    print(f"💾 Clustered features saved to {out_path}")
    
    Path("models").mkdir(exist_ok=True)
    joblib.dump(km, "models/kmeans_model.pkl")
    joblib.dump(scaler, "models/cluster_scaler.pkl")
    
    return {"silhouette": sil_score}


if __name__ == "__main__":
    cluster_and_save()
