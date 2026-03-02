import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from src.dashboard.utils import season_selector, load_squad

def render():
    st.markdown('<div class="layer-badge badge-analyst" style="margin-bottom: 0;">📊 ANALYST LAYER</div>', unsafe_allow_html=True)
    
    col_title, col_season = st.columns([2, 1])
    with col_title:
        st.markdown("<h2 style='margin-top:0;'>🌿 Verdão Analytics - Analyst Layer</h2>", unsafe_allow_html=True)
    with col_season:
        season = season_selector()

    df = load_squad(season)
    if df.empty:
        st.warning("Data unavailable. Run `make data && make transform`.")
        return

    # Filter Box
    st.markdown("<div style='background:#161616; padding:20px; border-radius:12px; border:1px solid #333; margin-bottom:24px;'>", unsafe_allow_html=True)
    
    c_play, c_pos = st.columns([2, 2])
    
    with c_pos:
        pos = st.radio("Position", ["All", "Goalkeeper", "Defender", "Midfielder", "Attacker"], horizontal=True, label_visibility="collapsed")
        min_min = st.slider("MIN MINS", 0, 3000, 300, 50, label_visibility="collapsed")
        
    df_f = df.copy()
    if pos != "All":
        df_f = df_f[df_f["position"] == pos]
    df_f = df_f[df_f["minutes_played"] >= min_min]
    
    player_list = df_f["name"].sort_values().unique()
    with c_play:
        player = st.selectbox("Select Player / Joueur", player_list) if len(player_list) > 0 else None
        
    st.markdown("</div>", unsafe_allow_html=True)

    if not player:
        st.info("No player matches filters.")
        return

    # Team averages for trend
    avg_goals   = df["goals_p90"].mean()
    avg_assists = df["assists_p90"].mean()
    avg_xg      = df["xg_p90"].mean() if "xg_p90" in df.columns else 0.0
    avg_duel    = df["duel_win_pct"].mean()
    
    row = df_f[df_f["name"] == player].iloc[0]
    p_g     = row.get("goals_p90", 0)
    p_a     = row.get("assists_p90", 0)
    p_xg    = row.get("xg_p90", 0)
    p_duel  = row.get("duel_win_pct", 0)

    def trend_html(val, avg, is_pct=False):
        if avg == 0 or pd.isna(avg) or pd.isna(val):
            return ""
        diff = ((val - avg) / avg) * 100 if not is_pct else (val - avg)
        if diff > 0:
            return f"<span style='color:#00CC50; font-size:12px;'>📈 +{diff:.1f}% vs Avg</span>"
        elif diff < 0:
            return f"<span style='color:#FF4444; font-size:12px;'>📉 {diff:.1f}% vs Avg</span>"
        return "<span style='color:#888; font-size:12px;'>➖ Avg</span>"

    # Layout: Metrics (left) & Radar (right)
    col_mets, col_rad = st.columns([1, 1])
    
    with col_mets:
        c1, c2 = st.columns(2)
        c1.markdown(f"""
        <div style="background:#161616; padding:16px; border-radius:12px; border:1px solid #333; margin-bottom:12px;">
            <div style="color:#888; font-size:11px; font-weight:bold;">GOALS / 90</div>
            <div style="font-size:24px; font-weight:bold; color:#00FF6A;">{p_g:.3f}</div>
            {trend_html(p_g, avg_goals)}
        </div>
        """, unsafe_allow_html=True)
        c2.markdown(f"""
        <div style="background:#161616; padding:16px; border-radius:12px; border:1px solid #333; margin-bottom:12px;">
            <div style="color:#888; font-size:11px; font-weight:bold;">ASSISTS / 90</div>
            <div style="font-size:24px; font-weight:bold; color:#00FF6A;">{p_a:.3f}</div>
            {trend_html(p_a, avg_assists)}
        </div>
        """, unsafe_allow_html=True)
        
        c3, c4 = st.columns(2)
        c3.markdown(f"""
        <div style="background:#161616; padding:16px; border-radius:12px; border:1px solid #333;">
            <div style="color:#888; font-size:11px; font-weight:bold;">XG / 90</div>
            <div style="font-size:24px; font-weight:bold; color:#F0F0F0;">{p_xg:.3f}</div>
            {trend_html(p_xg, avg_xg)}
        </div>
        """, unsafe_allow_html=True)
        c4.markdown(f"""
        <div style="background:#161616; padding:16px; border-radius:12px; border:1px solid #333;">
            <div style="color:#888; font-size:11px; font-weight:bold;">DUEL WIN %</div>
            <div style="font-size:24px; font-weight:bold; color:#F0F0F0;">{p_duel:.1f}%</div>
            {trend_html(p_duel, avg_duel, True)}
        </div>
        """, unsafe_allow_html=True)

    with col_rad:
        st.markdown("<div style='background:#161616; padding:16px; border-radius:12px; border:1px solid #333; height: 100%;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:bold; margin-bottom:8px;'>🟢 Performance Radar - {player}</div>", unsafe_allow_html=True)
        
        def build_radar(p_name, fill_col, line_col):
            r = df[df["name"] == p_name].iloc[0]
            vals = [
                min((r.get("goals_p90",0)/1.0)*10, 10),
                min((r.get("assists_p90",0)/0.5)*10, 10),
                min((r.get("xg_p90",0)/1.0)*10, 10),
                min((r.get("duel_win_pct",0)/100)*10, 10),
                min((r.get("dribble_success_pct",0)/100)*10, 10),
                min((r.get("starter_pct",0)/100)*10, 10)
            ]
            cats = ["Goals/90", "Assists/90", "xG/90", "Duel Win%", "Dribble%", "Starter%"]
            return go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
                fillcolor=fill_col, line=dict(color=line_col, width=2), name=p_name
            )

        fig = go.Figure(build_radar(player, "rgba(0,156,59,0.25)", "#009C3B"))
        fig.update_layout(
            polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[0,10])),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F0F0", size=10), showlegend=False,
            margin=dict(l=30, r=30, t=20, b=20), height=250
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚖️ Compare Players / Comparer les joueurs")
    
    col_cmpr_rad, col_cmpr_tab = st.columns([1, 1.5])
    
    with col_cmpr_rad:
        players_cmp = st.multiselect("Select players (Max 3)", df["name"].sort_values().unique(), default=[player], max_selections=3)
        colors = [("rgba(0,156,59,0.1)", "#009C3B"), ("rgba(0,68,255,0.1)", "#4488FF"), ("rgba(255,153,0,0.1)", "#FF9900")]
        
        fig_c = go.Figure()
        for i, p in enumerate(players_cmp):
            fc, lc = colors[i % len(colors)]
            fig_c.add_trace(build_radar(p, fc, lc))
            
        fig_c.update_layout(
            polar=dict(bgcolor="#161616", radialaxis=dict(visible=True, range=[0,10], color="#333", gridcolor="#333")),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F0F0"), showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20), height=350
        )
        st.plotly_chart(fig_c, use_container_width=True, config={'displayModeBar': False})

    with col_cmpr_tab:
        if players_cmp:
            st.markdown("<div style='background:#161616; padding:16px; border-radius:12px; border:1px solid #333;'>", unsafe_allow_html=True)
            
            # Header row
            hdrs = "".join([f"<th style='text-align:center; color:{colors[i%3][1]}; width: 25%;'>{p}</th>" for i, p in enumerate(players_cmp)])
            table_html = "<table style='width:100%; text-align:left; border-collapse:collapse; font-size:14px;'>"
            table_html += f"<tr><th style='color:#888; border-bottom:1px solid #333; padding:8px 0;'>METRIC</th>{hdrs}</tr>"
            
            cmp_df = df[df["name"].isin(players_cmp)]
            metrics = [
                ("Goals / 90", "goals_p90", True),
                ("Assists / 90", "assists_p90", True),
                ("xG / 90", "xg_p90", True),
                ("Progressive Carries", "dribbles_success", True), # Proxy
                ("Key Passes", "passes_key", True)
            ]
            
            for lbl, col, higher_is_better in metrics:
                if col not in cmp_df.columns:
                    continue
                vals = [cmp_df[cmp_df["name"]==p][col].iloc[0] for p in players_cmp]
                best_val = max(vals) if higher_is_better else min(vals)
                
                row_html = f"<tr><td style='padding:12px 0; border-bottom:1px solid #333; color:#aaa;'>{lbl}</td>"
                for v in vals:
                    bg = "color:#00FF6A; font-weight:bold;" if v == best_val and v > 0 else "color:#E0E0E0;"
                    dv = f"{v:.2f}" if isinstance(v, float) else f"{v}"
                    row_html += f"<td style='text-align:center; padding:12px 0; border-bottom:1px solid #333; {bg}'>{dv}</td>"
                row_html += "</tr>"
                table_html += row_html
                
            table_html += "</table></div>"
            st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### XG VS ACTUAL GOALS / XG VS BUTS RÉELS")
    
    st.markdown("<div style='background:#161616; padding:24px; border-radius:12px; border:1px solid #333;'>", unsafe_allow_html=True)
    if "xg_p90" in df.columns and df["xg_p90"].sum() > 0:
        fig_scat = go.Figure()
        
        # Determine over/under performance
        df["perf"] = df["goals_p90"] - df["xg_p90"]
        
        fig_scat.add_trace(go.Scatter(
            x=df["xg_p90"], y=df["goals_p90"],
            mode="markers+text", text=df["name"],
            textposition="top center",
            marker=dict(
                size=np.clip(df["minutes_played"]/100, 8, 25), 
                color=df["perf"], colorscale="RdYlGn", 
                showscale=False, line=dict(width=1, color="#111")
            ),
            textfont=dict(color="#aaa", size=10)
        ))
        
        max_val = max(df["xg_p90"].max(), df["goals_p90"].max()) + 0.2
        fig_scat.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="#555", width=1, dash="dash"))
        
        fig_scat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F0F0"),
            xaxis=dict(title="Expected Goals (xG) / 90", gridcolor="#333", zerolinecolor="#333"),
            yaxis=dict(title="Actual Goals / 90", gridcolor="#333", zerolinecolor="#333"),
            height=400, margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_scat, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("xG data generally requires FBref/Understat mapping which might be missing for some players in this season.")
    st.markdown("</div>", unsafe_allow_html=True)
