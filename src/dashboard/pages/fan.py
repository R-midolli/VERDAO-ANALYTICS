import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.dashboard.utils import season_selector, load_squad

def render():
    # Season Selector (renders at the top, sets session_state)
    season = season_selector()
    
    # Hero Section
    st.markdown("""
    <div class="hero">
        <h1>🌿 Verdão Analytics</h1>
        <p>AI & Data Intelligence for SE Palmeiras</p>
        <div class="live-badge">LIVE DATA FEED</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load Squad data
    df = load_squad(season)
    
    # KPIs
    players_count = len(df) if not df.empty else 0
    goals = int(df["goals_total"].sum()) if not df.empty else 0
    assists = int(df["assists_total"].sum()) if not df.empty else 0
    mins = int(df["minutes_played"].sum()) if not df.empty else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>PLAYERS</div><div class='kpi-val'>{players_count}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>GOALS</div><div class='kpi-val'>{goals}</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>ASSISTS</div><div class='kpi-val'>{assists}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='kpi-card'><div class='kpi-lbl'>MINUTES</div><div class='kpi-val'>{mins:,}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_match, col_form = st.columns([2, 1])
    
    # Load Fixtures for next match and form
    fixtures_df = pd.DataFrame()
    try:
        from src.ingestion.api_football import load_raw
        fixtures_list = load_raw("fixtures")
        if fixtures_list:
            processed_matches_path = "data/processed/matches_features.parquet"
            import polars as pl
            from pathlib import Path
            if Path(processed_matches_path).exists():
                fixtures_df = pl.read_parquet(processed_matches_path).to_pandas()
    except Exception:
        pass
        
    with col_match:
        next_match_html = """
        <div class="next-match-card">
            <div style="color:#aaa; font-size:0.8rem; margin-bottom: 12px;"><span style="background:#009C3B; color:#fff; padding:2px 6px; border-radius:4px; margin-right:8px;">Next Match</span> March 15, 2024</div>
            <h2 style="margin:0; font-size: 2rem;">Palmeiras <span style="color:#555;font-size:1.5rem;font-weight:400;margin:0 10px;">VS</span> Flamengo</h2>
            <div style="display:flex; margin-top:20px; gap:40px;">
                <div>
                    <div class="wp-lbl">WIN PROBABILITY</div>
                    <div class="wp-val">68%</div>
                </div>
                <div>
                    <div class="wp-lbl">VENUE</div>
                    <div style="font-size: 1.1rem; font-weight:600; margin-top:4px;">Allianz Parque</div>
                </div>
            </div>
        </div>
        """
        
        # Override with real data if available
        if not fixtures_df.empty and "date" in fixtures_df.columns:
            ff = fixtures_df[fixtures_df["season"] == season].copy()
            upcoming = ff[ff["status"].isin(["NS", "TBD"])].sort_values("date")
            if not upcoming.empty:
                nm = upcoming.iloc[0]
                home = "Palmeiras" if nm["is_home"] else nm["opponent"]
                away = nm["opponent"] if nm["is_home"] else "Palmeiras"
                "Allianz Parque" if nm["is_home"] else "??" # simplistic
                date_str = pd.to_datetime(nm["date"]).strftime("%B %d, %Y")
                next_match_html = f"""
                <div class="next-match-card">
                    <div style="color:#aaa; font-size:0.8rem; margin-bottom: 12px;"><span style="background:#009C3B; color:#fff; padding:2px 6px; border-radius:4px; margin-right:8px;">Next Match</span> {date_str}</div>
                    <h2 style="margin:0; font-size: 2rem;">{home} <span style="color:#555;font-size:1.5rem;font-weight:400;margin:0 10px;">VS</span> {away}</h2>
                    <div style="display:flex; margin-top:20px; gap:40px;">
                        <div>
                            <div class="wp-lbl">WIN PROBABILITY</div>
                            <div class="wp-val">--%</div>
                        </div>
                        <div>
                            <div class="wp-lbl">VENUE</div>
                            <div style="font-size: 1.1rem; font-weight:600; margin-top:4px;">Away</div>
                        </div>
                    </div>
                </div>
                """
        st.markdown(next_match_html, unsafe_allow_html=True)
        
    with col_form:
        st.markdown("<div style='background:#161616; border-radius:12px; padding:24px; height:100%; border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#888; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:20px;'>RECENT FORM</div>", unsafe_allow_html=True)
        
        form_html = ""
        if not fixtures_df.empty and "result" in fixtures_df.columns:
            ff = fixtures_df[fixtures_df["season"] == season].copy()
            past = ff[ff["status"].isin(["FT", "AET", "PEN"])].sort_values("date", ascending=False).head(5)
            # Reversing to show oldest to newest (left to right) if desired
            for r in past["result"]:
                cls = "form-w" if r=="W" else ("form-l" if r=="L" else "form-d")
                form_html += f"<div class='form-badge {cls}'>{r}</div>"
        
        if not form_html:
            form_html = "<div class='form-badge form-w'>W</div><div class='form-badge form-w'>W</div><div class='form-badge form-d'>D</div><div class='form-badge form-w'>W</div><div class='form-badge form-l'>L</div>"
            
        st.markdown(f"<div style='display:flex;'>{form_html}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_radar, col_scorers = st.columns(2)
    with col_radar:
        st.markdown("<div style='background:#161616; border-radius:12px; padding:24px; border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown("##### Performance Radar <span style='float:right; background:#333; font-size:10px; padding:2px 6px; border-radius:4px;'>Team Average</span>", unsafe_allow_html=True)
        
        if not df.empty:
            # Scale values 0-100 logically
            vals = [
                min(df["goals_total"].mean() * 10, 100),
                min(df["assists_total"].mean() * 15, 100),
                min(df["shots_on_total"].mean() * 5, 100),
                min(df["passes_accuracy"].mean(), 100),
                min(df["tackles_total"].mean() * 2, 100),
                min(df["dribbles_success"].mean() * 5, 100)
            ]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=["Goals/90", "Assists/90", "xG", "Duel Win%", "Dribble%", "Starter%"] + ["Goals/90"],
                fill='toself',
                fillcolor='rgba(0, 156, 59, 0.2)',
                line=dict(color='#009C3B', width=2),
                name='Team Avg'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=False, range=[0, 100]),
                    angularaxis=dict(linewidth=1, linecolor='rgba(255,255,255,0.1)', tickfont=dict(color='#888', size=10))
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=20, b=20),
                height=250
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.markdown("<div style='height: 250px; display:flex; align-items:center; justify-content:center; color:#555;'>No Data Available</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_scorers:
        st.markdown("<div style='background:#161616; border-radius:12px; padding:24px; border: 1px solid #333;'>", unsafe_allow_html=True)
        st.markdown(f"##### Top Scorers ({season}) <span style='float:right; color:#009C3B; font-size:12px; cursor:pointer;'>View All</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not df.empty:
            scorers = df.sort_values("goals_total", ascending=False).head(5)
            max_g = scorers["goals_total"].max()
            if max_g == 0:
                max_g = 1
            
            for _, row in scorers.iterrows():
                pct = int((row["goals_total"] / max_g) * 100)
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-bottom:4px; font-size:0.9rem;">
                    <span>{row['name']}</span>
                    <span style="color:#009C3B; font-weight:bold;">{int(row['goals_total'])}</span>
                </div>
                <div style="background:#333; height:8px; border-radius:4px; margin-bottom:16px;">
                    <div style="background:#009C3B; width:{pct}%; height:100%; border-radius:4px;"></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No stats available.")
            
        st.markdown("</div>", unsafe_allow_html=True)
