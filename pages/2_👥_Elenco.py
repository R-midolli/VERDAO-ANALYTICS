import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

st.set_page_config(page_title="Elenco", page_icon="👥", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #051A10; border-right: 1px solid #00813D; }
.sidebar-logo { display: flex; justify-content: center; padding: 20px 0; margin-bottom: 20px; border-bottom: 1px solid #00813D; }
.sidebar-logo img { width: 60%; max-width: 120px; }
.stApp { background-color: #0d0d0d; }
</style>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="sidebar-logo"><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/500px-Palmeiras_logo.svg.png"></div>
""", unsafe_allow_html=True)

st.title("👥 Análise do Elenco (FBref Data)")

@st.cache_data(ttl=3600)
def load_squad(season="2024"):
    p = Path(f"data/processed/squad_{season}.parquet")
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()

season = st.selectbox("Temporada", ["2024", "2025"], index=0)
df = load_squad(season)

if df.empty:
    st.warning("Dados não encontrados. Rode `python src/data_loader.py` ou atualize os dados.")
else:
    # Filter columns to show a clean table
    # Standard DB from FBref has cols like 'Player', 'Nation', 'Pos', 'Age', 'Playing Time_Min', 'Performance_Gls'
    clean_cols = {}
    for c in df.columns:
        if c == 'Player': clean_cols[c] = 'Jogador'
        elif c == 'Pos': clean_cols[c] = 'Posição'
        elif c == 'Age': clean_cols[c] = 'Idade'
        elif 'Min' in c and 'Playing Time' in c: clean_cols[c] = 'Minutos'
        elif 'Gls' in c and 'Performance' in c: clean_cols[c] = 'Gols'
        elif 'Ast' in c and 'Performance' in c: clean_cols[c] = 'Assistências'
        elif 'xG' in c and 'Expected' in c and not 'npxG' in c: clean_cols[c] = 'xG'
        elif 'PrgC' in c and 'Progression' in c: clean_cols[c] = 'Conduções Prog.'
        
    df_clean = df[list(clean_cols.keys())].rename(columns=clean_cols)
    # Convert numeric where possible
    for c in df_clean.columns:
        if c not in ['Jogador', 'Posição']:
            df_clean[c] = pd.to_numeric(df_clean[c], errors='coerce')
            
    df_clean = df_clean.dropna(subset=['Minutos'])
    df_clean = df_clean.sort_values("Minutos", ascending=False)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Jogadores (com Minutos)", len(df_clean))
    col2.metric("Gols Totais", int(df_clean['Gols'].sum()) if 'Gols' in df_clean else 0)
    col3.metric("xG Total", f"{df_clean['xG'].sum():.1f}" if 'xG' in df_clean else 0)
    
    st.dataframe(df_clean, use_container_width=True, hide_index=True)
    
    if 'Gols' in df_clean and 'xG' in df_clean:
        st.subheader("Performance xG vs Gols Reais")
        fig = px.scatter(df_clean, x='xG', y='Gols', hover_name='Jogador', text='Jogador',
                         size='Minutos', color='Gols', template="plotly_dark",
                         color_continuous_scale="Greens")
        fig.update_traces(textposition='top center')
        # Add x=y line
        max_val = max(df_clean['Gols'].max(), df_clean['xG'].max()) + 1
        fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="White", dash="dash"))
        st.plotly_chart(fig, use_container_width=True)
