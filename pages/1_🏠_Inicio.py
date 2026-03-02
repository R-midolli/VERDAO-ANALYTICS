import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Início", page_icon="🏠", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #051A10;
    border-right: 1px solid #00813D;
}
.sidebar-logo {
    display: flex; justify-content: center; padding: 20px 0; margin-bottom: 20px; border-bottom: 1px solid #00813D;
}
.sidebar-logo img { width: 60%; max-width: 120px; }
.stApp { background-color: #0d0d0d; }
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/500px-Palmeiras_logo.svg.png" alt="SE Palmeiras"></div>
""", unsafe_allow_html=True)

st.title("🏠 Dashboard: Início")

def load_next_matches():
    p = Path("data/processed/next_matches.parquet")
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()
    
def load_last_matches():
    p = Path("data/processed/last_matches.parquet")
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🟢 Últimos Resultados")
    df_last = load_last_matches()
    if not df_last.empty:
        for _, row in df_last.iterrows():
            st.markdown(f"""
            <div style="background:#161616; padding:12px; border-radius:8px; border-left:4px solid #009C3B; margin-bottom:8px;">
                <div style="font-size:12px; color:#888;">{row['dateEvent']} • {row['strLeague']}</div>
                <div style="font-size:16px; font-weight:bold;">{row['strHomeTeam']} <span style="color:#00FF6A;">{row['intHomeScore']} x {row['intAwayScore']}</span> {row['strAwayTeam']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum resultado recente encontrado.")

with col2:
    st.subheader("📅 Próximos Jogos")
    df_next = load_next_matches()
    if not df_next.empty:
        for _, row in df_next.iterrows():
            tm = row.get('strTime', '')
            st.markdown(f"""
            <div style="background:#161616; padding:12px; border-radius:8px; border-left:4px solid #4488FF; margin-bottom:8px;">
                <div style="font-size:12px; color:#888;">{row['dateEvent']} {tm} • {row['strLeague']} • {row.get('strVenue', '')}</div>
                <div style="font-size:16px; font-weight:bold;">{row['strHomeTeam']} x {row['strAwayTeam']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum próximo jogo encontrado.")
