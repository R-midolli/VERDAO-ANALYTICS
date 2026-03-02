"""
Verdão Analytics — Multi-page Streamlit App
3 camadas: Fan | Analyst | Expert
"""
import streamlit as st

st.set_page_config(
    page_title="🌿 Verdão Analytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* Global dark Palmeiras theme */
[data-testid="stSidebar"] { background: #0a0a0a; border-right: 1px solid #009C3B33; }
.hero { background: linear-gradient(135deg, #002200, #001a00);
        border: 1px solid #009C3B; border-radius: 16px;
        padding: 32px; margin-bottom: 24px; position: relative;}
.hero h1 { font-size: 2.8rem; background: linear-gradient(90deg, #009C3B, #00FF6A);
           -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
.hero p { color: #888; font-size: 1.1rem; margin-top: 4px; }
.live-badge { position: absolute; top: 32px; right: 32px; background: #111; border: 1px solid #333; 
              color: #888; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; }
.live-badge::before { content: '●'; color: #00CC50; margin-right: 6px; }

.kpi-row { display: flex; gap: 16px; margin: 24px 0; flex-wrap: wrap; }
.kpi-card { flex: 1; min-width: 140px; background: #161616;
            border-radius: 12px; padding: 20px 16px; position: relative; }
.kpi-card::after { content: ''; position: absolute; bottom: 0; left: 16px; width: 40%; height: 3px; background: #009C3B; border-radius: 3px; }
.kpi-val  { font-size: 2.5rem; font-weight: 800; margin: 8px 0; }
.kpi-lbl  { font-size: 0.75rem; color: #888; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; }

.next-match-card { background: #092e10; border-radius: 12px; padding: 24px; position: relative; }
.wp-val { font-size: 2rem; color: #00FF6A; font-weight: 800; margin: 0; }
.wp-lbl { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 1px;}

.form-badge { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; 
              border-radius: 50%; border: 1px solid #333; font-weight: bold; font-size: 0.85rem; margin-right: 8px; }
.form-w { color: #00CC50; border-color: #00CC5044; }
.form-d { color: #FF9900; border-color: #FF990044; }
.form-l { color: #FF4444; border-color: #FF444444; }

.layer-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("<h2 style='color: white; margin-bottom: 0;'>🌿 Verdão Analytics</h2><p style='color: #009C3B; margin-top: 0; font-size: 0.9rem;'>Palmeiras Analytics</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

layer = st.sidebar.radio(
    "Navigation",
    ["🟢 Fan Layer", "📊 Analyst Layer", "🤖 Expert Layer", "🧑‍🦱 Player Profile"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='margin-top: auto; padding-top: 20px; font-size: 0.8rem; color: #666; text-align: center;'>by Rafael Midolli 🇫🇷🇧🇷</div>", unsafe_allow_html=True)

# Route to pages
if layer == "🟢 Fan Layer":
    from src.dashboard.pages import fan
    fan.render()
elif layer == "📊 Analyst Layer":
    from src.dashboard.pages import analyst
    analyst.render()
elif layer == "🤖 Expert Layer":
    from src.dashboard.pages import expert
    expert.render()
elif layer == "🧑‍🦱 Player Profile":
    from src.dashboard.pages import player_profile
    player_profile.render()
