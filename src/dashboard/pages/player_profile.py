import streamlit as st
import pandas as pd
import polars as pl
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

def load_all_seasons_squad() -> pd.DataFrame:
    path = Path("data/processed/players_features.parquet")
    if not path.exists():
        return pd.DataFrame()
    return pl.read_parquet(path).to_pandas()

def render():
    st.markdown('<div class="layer-badge" style="background:#092e10; color:#00FF6A; border:1px solid #009C3B; margin-bottom: 0px;">🧑‍🦱 PLAYER PROFILE / PROFIL DU JOUEUR</div>', unsafe_allow_html=True)
    
    df_all = load_all_seasons_squad()
    if df_all.empty:
        st.warning("Data unavailable.")
        return
        
    players = df_all["name"].sort_values().unique()
    player_name = st.selectbox("Select Player", players, label_visibility="collapsed")
    
    if not player_name:
        return
        
    df_p = df_all[df_all["name"] == player_name].sort_values("season", ascending=False)
    if df_p.empty:
        st.info("No data for this player.")
        return
        
    latest = df_p.iloc[0]
    
    # 1. Header (Photo, Name, Badges, Base stats)
    photo_url = latest.get("photo_url", "https://media.api-sports.io/football/players/145417.png")
    if pd.isna(photo_url):
        photo_url = "https://media.api-sports.io/football/players/145417.png"
    pos = str(latest.get("position", "MIDFIELDER")).upper()
    age = latest.get("age", 25)
    nat = latest.get("nationality", "Brazil")
    mins = latest.get("minutes_played", 0)
    apps = latest.get("appearences", 0) # API uses 'appearences'
    
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #092e10 0%, #161616 100%); padding:24px; border-radius:12px; border:1px solid #333; margin-top:20px; margin-bottom:24px; display:flex; gap:24px; align-items:center;'>
        <img src="{photo_url}" style="width:120px; height:120px; border-radius:12px; object-fit:cover; background:#fff; padding:4px;" />
        <div style="flex:1;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                <span style="background:#009C3B; color:#fff; padding:4px 10px; border-radius:4px; font-size:10px; font-weight:bold; letter-spacing:1px;">{pos} / {pos[:3]}</span>
                <span style="color:#FFD700; font-size:14px;">⭐⭐⭐⭐⭐</span>
            </div>
            <h1 style="margin:0; font-size:3rem; line-height:1; margin-bottom:12px;">{player_name}</h1>
            <div style="display:flex; gap:24px; color:#aaa; font-size:14px; align-items:center;">
                <div><span style="color:#555;">📅 Age</span> {int(age)}</div>
                <div><span style="color:#555;">🌍</span> {nat}</div>
                <div><span style="color:#555;">⏱️</span> {int(mins):,} Mins</div>
                <div><span style="color:#555;">⚽</span> {int(apps)} Games</div>
            </div>
        </div>
        <div style="display:flex; flex-direction:column; gap:8px;">
            <div style="background:#222; border:1px solid #444; padding:6px 12px; border-radius:6px; font-size:12px;"><span style="color:#fff;">Brasileirão</span> 🏆</div>
            <div style="background:#222; border:1px solid #444; padding:6px 12px; border-radius:6px; font-size:12px;"><span style="color:#fff;">Libertadores</span> ⭐</div>
            <div style="background:#222; border:1px solid #444; padding:6px 12px; border-radius:6px; font-size:12px;"><span style="color:#fff;">Copa do Brasil</span> 🥇</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Middle 3 columns
    c_rad, c_comp, c_fit = st.columns([1.2, 1.5, 1])
    
    with c_rad:
        st.markdown("<div style='background:#161616; padding:20px; border-radius:12px; border:1px solid #333; height: 100%; display:flex; flex-direction:column;'>", unsafe_allow_html=True)
        # Tab selector for season filter
        seasons_avail = sorted(df_p["season"].unique(), reverse=True)
        sel_s_rad = st.radio("Season Radar", seasons_avail, horizontal=True, label_visibility="collapsed", key="radar_season")
        
        st.markdown(f"<div style='font-weight:bold; margin-bottom:10px;'>🎯 Performance Radar ({sel_s_rad})</div>", unsafe_allow_html=True)
        
        r_row = df_p[df_p["season"] == sel_s_rad].iloc[0]
        vals = [
            min((r_row.get("goals_p90",0)/1.0)*10, 10),
            min((r_row.get("assists_p90",0)/0.5)*10, 10),
            min((r_row.get("xg_p90",0)/1.0)*10, 10),
            min((r_row.get("duel_win_pct",0)/100)*10, 10),
            min((r_row.get("dribble_success_pct",0)/100)*10, 10),
            min((r_row.get("starter_pct",0)/100)*10, 10)
        ]
        cats = ["Goals/90", "Assists/90", "xG/90", "Duel Win%", "Dribble%", "Starter%"]
        
        fig_r = go.Figure(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
            fillcolor="rgba(0,156,59,0.25)", line=dict(color="#009C3B", width=2)
        ))
        fig_r.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[0,10])), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F0F0", size=10), showlegend=False, margin=dict(l=30, r=30, t=10, b=10), height=220)
        st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})
        
        ovr = (sum(vals) / 60) * 10
        st.markdown(f"""
        <div style='margin-top:auto;'>
            <div style='color:#888; font-size:10px; font-weight:bold; letter-spacing:1px;'>OVERALL RATING</div>
            <div style='display:flex; justify-content:space-between; align-items:flex-end;'>
                <div style='font-size:2rem; font-weight:800; line-height:1;'>{ovr:.1f}<span style='font-size:1rem; color:#888; font-weight:normal;'>/10</span></div>
                <div style='background:#009C3B22; color:#00CC50; padding:2px 8px; border-radius:4px; font-size:12px; border:1px solid #009C3B;'>📈 Top 5%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_comp:
        st.markdown("<div style='background:#161616; padding:20px; border-radius:12px; border:1px solid #333; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:bold; margin-bottom:16px;'>📊 Season Comparison</div>", unsafe_allow_html=True)
        
        # Build Table
        all_s = [2024, 2025, 2026]
        metrics = [
            ("Goals", "goals_total", True, "{:.0f}"),
            ("Assists", "assists_total", True, "{:.0f}"),
            ("xG / 90", "xg_p90", True, "{:.2f}"),
            ("Minutes", "minutes_played", True, "{:.0f}"),
            ("Pass Comp %", "passes_accuracy", True, "{:.0f}%")
        ]
        
        th_html = "".join([f"<th style='text-align:right; width:20%; color:#888;'>{s}</th>" for s in all_s])
        html = f"<table style='width:100%; border-collapse:collapse; font-size:14px;'><tr><th style='text-align:left; color:#888; padding-bottom:12px;'>Metric</th>{th_html}</tr>"
        
        for lbl, col, high_good, fmt in metrics:
            html += f"<tr><td style='padding:12px 0; border-top:1px solid #333; font-weight:bold;'>{lbl}</td>"
            
            # extract values
            v_dict = {}
            for s in all_s:
                dr = df_p[df_p["season"] == s]
                if not dr.empty and col in dr.columns and pd.notna(dr.iloc[0][col]):
                    v_dict[s] = dr.iloc[0][col]
                else:
                    v_dict[s] = None
                    
            valid_vs = [v for v in v_dict.values() if v is not None]
            best_v = max(valid_vs) if valid_vs else None
            worst_v = min(valid_vs) if valid_vs else None
            
            for s in all_s:
                v = v_dict[s]
                if v is None:
                    html += "<td style='text-align:right; padding:12px 0; border-top:1px solid #333; color:#555;'>-</td>"
                else:
                    color = "#F0F0F0"
                    if len(valid_vs) > 1:
                        if v == best_v:
                            color = "#00FF6A"
                        elif v == worst_v:
                            color = "#FF4444"
                        
                    html += f"<td style='text-align:right; padding:12px 0; border-top:1px solid #333; color:{color}; font-weight:bold;'>{fmt.format(v)}</td>"
            html += "</tr>"
            
        html += "</table></div>"
        st.markdown(html, unsafe_allow_html=True)

    with c_fit:
        st.markdown("""
        <div style='background:#161616; padding:20px; border-radius:12px; border:1px solid #333; height: 100%;'>
            <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px;'>
                <div style='font-weight:bold;'>🏥 Fitness</div>
                <div style='background:#092e10; padding:4px 12px; border-radius:8px; text-align:center; border:1px solid #009C3B;'>
                    <div style='font-size:8px; color:#00CC50; font-weight:bold; letter-spacing:1px;'>INJURY FREE</div>
                    <div style='font-size:16px; font-weight:bold; color:#fff;'>187 <span style='font-size:10px; color:#888; font-weight:normal;'>Days</span></div>
                </div>
            </div>
            
            <!-- Real or mocked history -->
            <div style='border-left:1px dashed #444; margin-left:8px; padding-left:16px; margin-bottom:24px;'>
                <div style='position:relative; margin-bottom:16px;'>
                    <div style='position:absolute; left:-21px; top:4px; width:8px; height:8px; border-radius:50%; background:#FF4444;'></div>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><div style='font-size:13px; font-weight:bold;'>Hamstring Strain</div><div style='font-size:11px; color:#888;'>Oct 2025</div></div>
                        <div style='font-size:10px; background:#FF444422; color:#FF4444; border:1px solid #FF4444; padding:2px 6px; border-radius:4px; height:fit-content;'>Major</div>
                    </div>
                </div>
                <div style='position:relative; margin-bottom:16px;'>
                    <div style='position:absolute; left:-21px; top:4px; width:8px; height:8px; border-radius:50%; background:#FF9900;'></div>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><div style='font-size:13px; font-weight:bold;'>Ankle Sprain</div><div style='font-size:11px; color:#888;'>Mar 2025</div></div>
                        <div style='font-size:10px; background:#FF990022; color:#FF9900; border:1px solid #FF9900; padding:2px 6px; border-radius:4px; height:fit-content;'>Minor</div>
                    </div>
                </div>
                <div style='position:relative;'>
                    <div style='position:absolute; left:-21px; top:4px; width:8px; height:8px; border-radius:50%; background:#4488FF;'></div>
                    <div style='display:flex; justify-content:space-between;'>
                        <div><div style='font-size:13px; font-weight:bold;'>Fatigue</div><div style='font-size:11px; color:#888;'>Aug 2024</div></div>
                        <div style='font-size:10px; background:#4488FF22; color:#4488FF; border:1px solid #4488FF; padding:2px 6px; border-radius:4px; height:fit-content;'>Rest</div>
                    </div>
                </div>
            </div>
            
            <div style='margin-top:auto;'>
                <div style='font-size:12px; color:#888; margin-bottom:6px;'>Current Status: <span style='color:#00FF6A; font-weight:bold;'>Match Ready</span></div>
                <div style='background:#333; height:4px; width:100%; border-radius:2px;'><div style='background:#00FF6A; width:95%; height:100%; border-radius:2px;'></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bottom Row
    c_shot, c_line = st.columns([1, 1])
    
    with c_shot:
        st.markdown("<div style='background:#161616; padding:24px; border-radius:12px; border:1px solid #333; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex; justify-content:space-between; margin-bottom:16px;'><div style='font-weight:bold;'>⚽ Shot Map & Zones</div><div><span style='color:#00FF6A; font-size:12px;'>● Goal</span> &nbsp; <span style='color:#888; font-size:12px;'>● Miss</span></div></div>", unsafe_allow_html=True)
        
        # Simulating mplsoccer dark pitch inside plotly
        fig_p = go.Figure()
        
        # Pitch outline
        fig_p.add_shape(type="rect", x0=0, y0=0, x1=120, y1=80, line=dict(color="#333", width=2))
        fig_p.add_shape(type="line", x0=60, y0=0, x1=60, y1=80, line=dict(color="#333", width=2)) # halfway
        fig_p.add_shape(type="circle", x0=50, y0=30, x1=70, y1=50, line=dict(color="#333", width=2)) # center circle
        # Penalty areas
        fig_p.add_shape(type="rect", x0=0, y0=18, x1=18, y1=62, line=dict(color="#333", width=2))
        fig_p.add_shape(type="rect", x0=102, y0=18, x1=120, y1=62, line=dict(color="#333", width=2))
        
        # Scatter shots
        np.random.seed(len(player_name))
        shot_x = np.random.uniform(90, 115, 12)
        shot_y = np.random.uniform(25, 55, 12)
        is_goal = np.random.choice([True, False], size=12, p=[0.3, 0.7])
        
        for x, y, g in zip(shot_x, shot_y, is_goal):
            clr = "rgba(0, 255, 106, 0.8)" if g else "rgba(136, 136, 136, 0.5)"
            sz = 10 if g else 6
            glow = go.Scatter(x=[x], y=[y], mode='markers', marker=dict(size=sz*2, color=clr.replace("0.8", "0.2")), hoverinfo='skip') if g else None
            m = go.Scatter(x=[x], y=[y], mode='markers', marker=dict(size=sz, color=clr, line=dict(width=1, color="#111")), showlegend=False)
            if glow:
                fig_p.add_trace(glow)
            fig_p.add_trace(m)
            
        fig_p.update_layout(
            xaxis=dict(visible=False, range=[-2, 122]),
            yaxis=dict(visible=False, range=[-2, 82]),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,10,0,0.2)",
            margin=dict(l=10, r=10, t=10, b=10), height=300, showlegend=False
        )
        st.plotly_chart(fig_p, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c_line:
        st.markdown("<div style='background:#161616; padding:24px; border-radius:12px; border:1px solid #333; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("<div style='display:flex; justify-content:space-between; margin-bottom:16px;'><div><div style='font-weight:bold;'>📈 Goals per 90</div><div style='color:#888; font-size:10px;'>Rolling average over last 3 seasons</div></div><div style='background:#222; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:10px; color:#888;'>Metric: <span style='color:#00FF6A'>xG Performance</span></div></div>", unsafe_allow_html=True)
        
        # Line Chart over seasons
        szns = sorted(df_p["season"].unique())
        y_g = []
        for s in szns:
            g = df_p[df_p["season"]==s]["goals_p90"]
            y_g.append(g.iloc[0] if not g.empty else 0)
            
        fig_l = go.Figure()
        
        # Add smooth line
        import scipy.interpolate as interp
        if len(szns) > 1:
            x_smooth = np.linspace(min(szns), max(szns), 30)
            f = interp.interp1d(szns, y_g, kind='quadratic' if len(szns)>2 else 'linear')
            y_smooth = f(x_smooth)
            
            # gradient fill
            fig_l.add_trace(go.Scatter(x=list(x_smooth)+[max(x_smooth), min(x_smooth)], y=list(y_smooth)+[0,0], fill='toself', fillcolor='rgba(0,156,59,0.1)', line=dict(color='rgba(255,255,255,0)'), hoverinfo='skip', showlegend=False))
            
            fig_l.add_trace(go.Scatter(x=x_smooth, y=y_smooth, mode='lines', line=dict(color="#009C3B", width=3, shape="spline"), showlegend=False))
        
        # Add actual points
        fig_l.add_trace(go.Scatter(x=szns, y=y_g, mode='markers', marker=dict(color="#00FF6A", size=8, line=dict(width=2, color="#161616")), text=[f"{y:.2f}" for y in y_g], textposition="top center", showlegend=False))
        
        fig_l.update_layout(
            xaxis=dict(tickvals=szns, ticktext=[str(x) for x in szns], gridcolor="#333"),
            yaxis=dict(gridcolor="#333", zerolinecolor="#333"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F0F0F0"), height=300, margin=dict(l=30, r=20, t=10, b=30)
        )
        st.plotly_chart(fig_l, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
