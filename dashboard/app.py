import os
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://qsim-gateway-svc")
REFRESH_INTERVAL = 3

st.set_page_config(page_title="QSIM Control Room", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');
* { font-family: 'Exo 2', sans-serif; }
.stApp { background: #030712; }
.main .block-container { padding: 1.5rem 2rem; max-width: 100%; }
#MainMenu, footer, header { visibility: hidden; }
.asset-card { border-radius: 12px; padding: 16px; margin-bottom: 8px; border: 1px solid #1e3a5f; }
.asset-card.FAULT { border-color: #ff4444; background: rgba(255,68,68,0.05); }
.asset-card.RUNNING { border-color: #00ff88; background: rgba(0,255,136,0.03); }
.asset-card.IDLE { border-color: #f59e0b; background: rgba(245,158,11,0.04); }
.asset-card.MAINTENANCE { border-color: #7c3aed; background: rgba(124,58,237,0.05); }
</style>
""", unsafe_allow_html=True)

ASSET_COLORS = {"ASSET-001":"#00d4ff","ASSET-002":"#00ff88","ASSET-003":"#f59e0b","ASSET-004":"#7c3aed","ASSET-005":"#ff4444"}
STATE_COLORS = {"RUNNING":"#00ff88","IDLE":"#f59e0b","FAULT":"#ff4444","MAINTENANCE":"#a78bfa"}

def fetch(path, timeout=4):
    try:
        r = requests.get(f"{GATEWAY_URL}{path}", timeout=timeout)
        return r.json()
    except:
        return None

health   = fetch("/health")
assets   = fetch("/assets")
tel_data = fetch("/telemetry?limit=300")

if not health:
    st.error(f"Cannot reach QSIM Gateway at {GATEWAY_URL}")
    time.sleep(5)
    st.rerun()

assets_map = assets.get("assets", {}) if assets else {}
records    = tel_data.get("records", []) if tel_data else []

latest = {}
for r in records:
    aid = r.get("asset_id")
    if aid not in latest:
        latest[aid] = r

total  = health.get("total_records", 0)
uptime = health.get("uptime_seconds", 0)
n_assets = health.get("unique_assets", 0)
fault_count = sum(1 for a in assets_map.values() if a.get("state") == "FAULT")

st.markdown(f"""
<div style="background:linear-gradient(135deg,#0a0f1e,#0d1b2a);border:1px solid #1e3a5f;border-radius:16px;padding:24px 32px;margin-bottom:24px;border-top:2px solid #00d4ff">
    <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
            <h1 style="font-family:Share Tech Mono,monospace;color:#00d4ff;margin:0;letter-spacing:2px;font-size:1.8rem">⚡ QSIM CONTROL ROOM</h1>
            <p style="color:#4a7fa5;font-size:0.8rem;margin:4px 0 0;letter-spacing:1px">QUANTUM-SAFE INDUSTRIAL MESH · SMART FACTORY DIGITAL TWIN · LIVE</p>
        </div>
        <div style="text-align:right;font-family:Share Tech Mono,monospace;font-size:0.8rem;color:#4a7fa5">
            <div style="color:#00ff88">● GATEWAY ONLINE</div>
            <div>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
c1.metric("🟢 Status", "HEALTHY")
c2.metric("📦 Records", f"{total:,}")
c3.metric("🏭 Assets", n_assets)
c4.metric("⏱ Uptime", f"{uptime/3600:.1f}h")

st.markdown("---")
st.markdown("<p style='color:#4a7fa5;font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00d4ff;padding-left:10px'>// FACTORY ASSETS — LIVE DIGITAL TWIN STATE</p>", unsafe_allow_html=True)

if assets_map:
    cols = st.columns(5)
    for i, (asset_id, info) in enumerate(assets_map.items()):
        state = info.get("state","UNKNOWN")
        tel   = latest.get(asset_id, {})
        color = STATE_COLORS.get(state,"#888")
        hlth  = tel.get("health_score", 0)
        hlth_pct = int(float(hlth)*100) if hlth else 0
        hlth_color = "#00ff88" if hlth_pct>70 else "#f59e0b" if hlth_pct>40 else "#ff4444"
        with cols[i]:
            st.markdown(f"""
            <div class="asset-card {state}">
                <div style="font-family:Share Tech Mono,monospace;font-size:1rem;font-weight:700;color:{color}">{asset_id}</div>
                <div style="font-size:0.7rem;color:#4a7fa5;text-transform:uppercase;margin-bottom:10px">{tel.get("asset_type","—")}</div>
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin:3px 0"><span style="color:#4a7fa5">TEMP</span><span style="font-family:Share Tech Mono,monospace;color:#e2e8f0">{tel.get("temperature","—")}°C</span></div>
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin:3px 0"><span style="color:#4a7fa5">VIBR</span><span style="font-family:Share Tech Mono,monospace;color:#e2e8f0">{tel.get("vibration","—")}</span></div>
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin:3px 0"><span style="color:#4a7fa5">HLTH</span><span style="font-family:Share Tech Mono,monospace;color:{hlth_color}">{hlth}</span></div>
                <div style="background:#1e3a5f;border-radius:4px;height:4px;margin:8px 0"><div style="width:{hlth_pct}%;height:4px;border-radius:4px;background:{hlth_color}"></div></div>
                <span style="background:rgba(0,0,0,0.3);border:1px solid {color};color:{color};padding:2px 8px;border-radius:20px;font-size:0.7rem;font-family:Share Tech Mono,monospace">{state}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

if records:
    df = pd.DataFrame(records)
    df["ingested_at"] = pd.to_datetime(df["ingested_at"])
    df = df.sort_values("ingested_at")
    PLOT_BG = "#0a0f1e"; PAPER_BG = "#030712"; GRID_CLR = "#1e3a5f"; FONT_CLR = "#4a7fa5"

    st.markdown("<p style='color:#4a7fa5;font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00d4ff;padding-left:10px'>// TELEMETRY ANALYTICS</p>", unsafe_allow_html=True)
    cc1, cc2 = st.columns(2)

    with cc1:
        fig = go.Figure()
        for aid in df["asset_id"].unique():
            d = df[df["asset_id"]==aid]
            fig.add_trace(go.Scatter(x=d["ingested_at"],y=d["temperature"],name=aid,mode="lines",line=dict(color=ASSET_COLORS.get(aid,"#888"),width=1.5)))
        fig.update_layout(title=dict(text="TEMPERATURE °C",font=dict(color=FONT_CLR,size=11),x=0),paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,xaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),yaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=FONT_CLR,size=10)),margin=dict(l=40,r=20,t=40,b=40),height=280)
        st.plotly_chart(fig, use_container_width=True)

    with cc2:
        fig2 = go.Figure()
        for aid in df["asset_id"].unique():
            d = df[df["asset_id"]==aid]
            fig2.add_trace(go.Scatter(x=d["ingested_at"],y=d["health_score"],name=aid,mode="lines",line=dict(color=ASSET_COLORS.get(aid,"#888"),width=1.5)))
        fig2.add_hline(y=0.6,line_dash="dash",line_color="#ff4444",annotation_text="CRITICAL",annotation_font_color="#ff4444",annotation_font_size=10)
        fig2.update_layout(title=dict(text="HEALTH SCORE",font=dict(color=FONT_CLR,size=11),x=0),paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,xaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),yaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR,range=[0,1.05]),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=FONT_CLR,size=10)),margin=dict(l=40,r=20,t=40,b=40),height=280)
        st.plotly_chart(fig2, use_container_width=True)

    cc3, cc4 = st.columns(2)
    with cc3:
        sc = df.groupby(["asset_id","operational_state"]).size().reset_index(name="count")
        fig3 = px.bar(sc,x="asset_id",y="count",color="operational_state",color_discrete_map={"RUNNING":"#00ff88","IDLE":"#f59e0b","FAULT":"#ff4444","MAINTENANCE":"#7c3aed"},template="plotly_dark")
        fig3.update_layout(title=dict(text="STATE DISTRIBUTION",font=dict(color=FONT_CLR,size=11),x=0),paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,xaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),yaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=FONT_CLR,size=10),title_text=""),margin=dict(l=40,r=20,t=40,b=40),height=280)
        st.plotly_chart(fig3, use_container_width=True)

    with cc4:
        ldf = pd.DataFrame(latest.values())
        if not ldf.empty:
            fig4 = px.scatter(ldf,x="vibration",y="health_score",color="asset_id",size="temperature",color_discrete_map=ASSET_COLORS,template="plotly_dark",hover_data=["asset_type","operational_state"])
            fig4.add_hline(y=0.6,line_dash="dash",line_color="#ff4444")
            fig4.add_vline(x=60,line_dash="dash",line_color="#f59e0b")
            fig4.update_layout(title=dict(text="VIBRATION vs HEALTH",font=dict(color=FONT_CLR,size=11),x=0),paper_bgcolor=PAPER_BG,plot_bgcolor=PLOT_BG,xaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),yaxis=dict(gridcolor=GRID_CLR,color=FONT_CLR),legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=FONT_CLR,size=10)),margin=dict(l=40,r=20,t=40,b=40),height=280)
            st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.markdown("<p style='color:#4a7fa5;font-size:0.75rem;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00d4ff;padding-left:10px'>// LIVE TELEMETRY FEED</p>", unsafe_allow_html=True)

if records:
    display_df = pd.DataFrame(records[-20:])[::-1][["ingested_at","asset_id","asset_type","temperature","vibration","health_score","operational_state"]]
    display_df["ingested_at"] = display_df["ingested_at"].str[:19].str.replace("T"," ")
    def color_rows(row):
        c = {"FAULT":"background-color:#1a0505","MAINTENANCE":"background-color:#120a1e","IDLE":"background-color:#141009","RUNNING":"background-color:#050f0a"}
        return [c.get(row["operational_state"],"")] * len(row)
    st.dataframe(display_df.style.apply(color_rows,axis=1), use_container_width=True, height=380)

ts = datetime.now().strftime("%H:%M:%S")
st.markdown(f"<p style='color:#1e3a5f;font-size:0.7rem;margin-top:16px'>QSIM v1.0 · {ts} · {total:,} records</p>", unsafe_allow_html=True)

time.sleep(REFRESH_INTERVAL)
st.rerun()
