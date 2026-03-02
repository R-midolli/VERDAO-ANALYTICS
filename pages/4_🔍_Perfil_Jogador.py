import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go

st.set_page_config(page_title="Perfil Jogador", page_icon="🔍", layout="wide")

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

st.title("🔍 Perfil do Jogador")

@st.cache_data
def load_squad(season="2024"):
    p = Path(f"data/processed/squad_{season}.parquet")
    if p.exists():
        return pd.read_parquet(p)
    return pd.DataFrame()

df = load_squad("2024")

if df.empty:
    st.warning("Dados não carregados. Execute Make Data.")
else:
    players = df['Player'].dropna().unique()
    player = st.selectbox("Selecione um jogador", sorted(players))
    
    p_data = df[df['Player'] == player].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #051A10, #161616); border: 1px solid #004d24; padding: 20px; border-radius: 12px;">
            <h2 style="margin-top:0;">{player}</h2>
            <div style="color:#aaa;">Idade: {p_data.get('Age', '-')} | Posição: {p_data.get('Pos', '-')} | Nação: {p_data.get('Nation', '-')}</div>
            <hr style="border-color:#333;">
            <div style="display:flex; justify-content:space-between; font-size:18px;">
                <b>Minutos:</b> <span style="color:#00FF6A;">{p_data.get('Playing Time_Min', 0)}</span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:18px;">
                <b>Gols (xG):</b> <span>{p_data.get('Performance_Gls', 0)} <span style="font-size:12px; color:#888;">({p_data.get('Expected_xG', 0)})</span></span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:18px;">
                <b>Assist. (xAG):</b> <span>{p_data.get('Performance_Ast', 0)} <span style="font-size:12px; color:#888;">({p_data.get('Expected_xAG', 0)})</span></span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:18px;">
                <b>Prog. Carries:</b> <span style="color:#4488FF;">{p_data.get('Progression_PrgC', 0)}</span>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:18px;">
                <b>Prog. Passes:</b> <span style="color:#4488FF;">{p_data.get('Progression_PrgP', 0)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("### Radar de DNA de Jogo")
        # Scale values to 10 for radar based on some team maxima
        max_g = max([0.1, df['Performance_Gls'].astype(float).max()])
        max_a = max([0.1, df['Performance_Ast'].astype(float).max()])
        max_pc = max([0.1, df['Progression_PrgC'].astype(float).max()])
        max_pp = max([0.1, df['Progression_PrgP'].astype(float).max()])
        max_xg = max([0.1, df['Expected_xG'].astype(float).max()])

        vals = [
            (float(p_data.get('Performance_Gls', 0)) / max_g) * 10,
            (float(p_data.get('Performance_Ast', 0)) / max_a) * 10,
            (float(p_data.get('Expected_xG', 0)) / max_xg) * 10,
            (float(p_data.get('Progression_PrgC', 0)) / max_pc) * 10,
            (float(p_data.get('Progression_PrgP', 0)) / max_pp) * 10,
        ]
        cats = ['Gols', 'Assistências', 'xG', 'Prog. Carries', 'Prog. Passes']
        
        fig = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]], fill='toself',
            fillcolor='rgba(0,156,59,0.5)', line=dict(color='#00FF6A')
        ))
        fig.update_layout(polar=dict(bgcolor='#111', radialaxis=dict(visible=True, range=[0, 10])), 
                          paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#FFF', size=14),
                          margin=dict(l=40, r=40, t=20, b=20), height=350)
        st.plotly_chart(fig, use_container_width=True)
