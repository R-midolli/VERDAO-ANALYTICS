import streamlit as st

st.set_page_config(page_title="Calendário e Predições", page_icon="📅", layout="wide")

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

st.title("📅 Calendário de Jogos & Predições ML")

st.info("Pipeline de Machine Learning de Predições (Match Outcome) desativado aguardando coleta massiva de TheSportsDB. Exibindo Mockups de predição via XGBoost baseados na forma recente.")

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
    <div style='background:#161616; padding:24px; border-radius:12px; border:1px solid #333;'>
        <h3 style="margin-top:0;">🤖 Simulador Preditivo de Placar</h3>
        <p style="color:#888;">Utiliza XGBoost alimentado por dados históricos do TheSportsDB e estatísticas agregadas de FBref (Forma Recente, xG Contra, xG Pró).</p>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:30px;">
            <div style="text-align:center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Palmeiras_logo.svg" width="80"><br>
                <b>Palmeiras</b><br><span style="color:#00FF6A">Forma: V V E V V</span>
            </div>
            <div style="text-align:center;">
                <h1 style="margin:0; font-size:4rem; color:#fff;">2 <span style="color:#555;font-size:2rem;">-</span> 0</h1>
                <div style="color:#00CC50; font-weight:bold;">78% Win Probability</div>
            </div>
            <div style="text-align:center;">
                <div style="width:80px; height:80px; background:#fff; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-bottom:8px;">
                    <span style="color:#000; font-weight:bold; font-size:30px;">SPFC</span>
                </div>
                <b>Adversário</b><br><span style="color:#FF4444">Forma: D D E V D</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Fatores de Decisão (SHAP)")
    st.progress(85, text="Qualidade do Esquadrão (xG Difference)")
    st.progress(90, text="Fator Casa (Allianz Parque)")
    st.progress(40, text="Lesões e Suspensões")
    st.progress(70, text="Forma Recente")
