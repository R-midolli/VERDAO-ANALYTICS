import streamlit as st

st.set_page_config(
    page_title="Verdão Analytics",
    page_icon="🟢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Palmeiras Theme and Shield
st.markdown("""
<style>
/* Sidebar Logo */
[data-testid="stSidebar"] {
    background-color: #051A10;
    border-right: 1px solid #00813D;
}
.sidebar-logo {
    display: flex;
    justify-content: center;
    padding: 20px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #00813D;
}
.sidebar-logo img {
    width: 60%;
    max-width: 120px;
}
/* Main Content */
.stApp {
    background-color: #0d0d0d;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div class="sidebar-logo">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/500px-Palmeiras_logo.svg.png" alt="SE Palmeiras">
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Atualizar Dados Agora", use_container_width=True):
    with st.spinner("Baixando dados reais (FBref + TheSportsDB)..."):
        try:
            from src.data_loader import PalmeirasDataLoader
            loader = PalmeirasDataLoader()
            loader.run_all()
            st.sidebar.success("✅ Dados atualizados!")
        except Exception as e:
            st.sidebar.error(f"Erro na atualização: {e}")


st.title("🟢 Verdão Analytics — Centro de Inteligência")

st.markdown("""
Bem-vindo ao **Verdão Analytics**, a plataforma de dados de ponta a ponta para a **Sociedade Esportiva Palmeiras**. 
Utilizamos dados atualizados do FBref e TheSportsDB para trazer insights precisos sobre a performance do Maior Campeão do Brasil.

### 🧭 Navegação via Menu Lateral
- **🏠 Início:** Resumo geral e próximos jogos.
- **👥 Elenco:** Visão analítica completa do esquadrão alviverde.
- **📅 Jogos & Predições:** Calendário e Machine Learning predictivo.
- **🔍 Perfil Jogador:** Drill-down e radar charts por atleta.
- **📊 Análises Avançadas:** Modelos SHAP e Clusters (Expert Layer).

> *Atualização de dados automática com cache inteligente.*
""")

col1, col2 = st.columns(2)

with col1:
    st.info("💡 **Dica de Uso:** Utilize a barra lateral à esquerda para navegar pelas diferentes camadas de análise.")
    st.image("https://images.unsplash.com/photo-1518605368461-1ee7e543666b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", use_container_width=True, caption="Allianz Parque Database")

with col2:
    st.success("✅ **Sistemas Operacionais:**")
    st.markdown("""
    - **Data Loader:** `OK` (FBref + TheSportsDB)
    - **DuckDB Storage:** `OK` (Parquet local)
    - **Machine Learning Inference:** `OK`
    """)
