<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Palmeiras_logo.svg" alt="Palmeiras Logo" width="120">
  
  # Verdão Analytics — The Empire 🌿🏆
  **Data Science & Machine Learning Platform for SE Palmeiras**

  [![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
  [![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
  [![Prefect](https://img.shields.io/badge/Prefect-Orchestration-0052CC?logo=prefect&logoColor=white)](https://prefect.io)
  [![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)
  
  [**🇺🇸 English Version**](#english) | [**🇧🇷 Versão em Português**](#português)
</div>

---

<a name="english"></a>
## 🇺🇸 English

**Verdão Analytics** is a production-grade Big Data & Machine Learning platform built exclusively for tracking, predicting, and analyzing SE Palmeiras squad metrics. This project consolidates raw football data, transforms it through statistical learning pipelines, and visualizes insights using a cutting-edge Streamlit dashboard.

### 🌟 Features by User Layer
- **Fan Layer:** High-level season goals, general squad form, live KPIs, and standard league tracking.
- **Analyst Layer:** In-depth player comparisons, season-to-season radar charts, and trend metrics.
- **Expert Layer:** Advanced SHAP outputs for XGBoost performance models, CatBoost injury risk models, K-Means clustering, and PuLP-optimized lineup recommendations.
- **Player Profile:** Detailed individual drill-down including fitness trajectory, shot maps, and historic goals data.

### 🛠 Tech Stack
- **Data Engineering:** `API-Football`, `Pandas`, `Prefect` (Orchestration)
- **Machine Learning:** `scikit-learn`, `XGBoost`, `CatBoost`, `PuLP`, `SHAP`
- **Frontend & App:** `Streamlit`, `Plotly`, `duckdb`
- **Database:** `Supabase` (PostgreSQL)
- **CI/CD:** `pytest`, `GitHub Actions`

### 🚀 Getting Started
```bash
# Clone the repository
git clone https://github.com/R-midolli/VERDAO-ANALYTICS.git
cd VERDAO-ANALYTICS

# Install dependencies with UV
uv venv .venv
source .venv/Scripts/activate # Windows
uv pip install -r requirements.txt

# Run the ingestion layer and dashboard
make data
make explore
make run
```

*Architected by: Rafael Midolli*

---

<a name="português"></a>
## 🇧🇷 Português

**Verdão Analytics** é uma plataforma analítica de Big Data e Machine Learning em nível de produção construída exclusivamente para rastrear, prever e analisar as métricas do elenco da SE Palmeiras. Este projeto consolida dados brutos de futebol, os transforma através de pipelines estatísticos e exibe os insights usando um dashboard avançado no Streamlit.

### 🌟 Funcionalidades por Camada
- **Camada Fan (Torcedor):** Resumo executivo da temporada, forma geral do time, KPIs em tempo real e evolução nos campeonatos.
- **Camada Analista:** Comparações aprofundadas de jogadores, gráficos de radar para comparação entre temporadas e métricas de tendência.
- **Camada Especialista (Expert):** Explicabilidade visual SHAP para modelos XGBoost de performance, modelos CatBoost de risco de lesão, agrupamentos K-Means e escalação otimizada por otimização linear via PuLP.
- **Perfil do Jogador:** Drill-down detalhado do jogador, histórico de preparo físico (fitness), mapa de finalizações (shot map) e radar de gols historicos.

### 🛠 Stack Tecnológico
- **Engenharia de Dados:** `API-Football`, `Pandas`, `Prefect` (Orquestração)
- **Machine Learning:** `scikit-learn`, `XGBoost`, `CatBoost`, `PuLP`, `SHAP`
- **Frontend / Dashboard:** `Streamlit`, `Plotly`
- **Banco de Dados:** `Supabase` (PostgreSQL)
- **CI/CD & Qualidade:** `pytest`, `GitHub Actions`, `ruff`

### 🚀 Como Executar
```bash
# Clone o repositório
git clone https://github.com/R-midolli/VERDAO-ANALYTICS.git
cd VERDAO-ANALYTICS

# Instale as dependências usando uv
uv venv .venv
# Para Windows:
.venv\Scripts\activate 
uv pip install -r requirements.txt

# Execute a extração e depois o painel (Dashboard)
make data
make run
```

*Idealizado e Construído por: Rafael Midolli*
