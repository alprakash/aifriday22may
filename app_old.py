"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     OPTIMA — AI-Powered Resource & Capacity Intelligence Platform           ║
║     Enterprise Hackathon Edition | Exercise 10: Resource Optimization       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Run:  streamlit run app.py
Deps: pip install streamlit plotly pandas anthropic numpy openpyxl xlsxwriter
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import time
import io
from datetime import datetime, timedelta
from anthropic import Anthropic

# ─── PAGE CONFIG (MUST BE FIRST STREAMLIT CALL) ────────────────────────────
st.set_page_config(
    page_title="OPTIMA | Resource Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "OPTIMA v2.0 — Enterprise Resource & Capacity AI Platform"},
)

# ─── GLOBAL STYLES ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root & Body ── */
:root {
    --bg-void:       #050810;
    --bg-deep:       #0A0E1A;
    --bg-surface:    #0F1525;
    --bg-card:       #141928;
    --bg-elevated:   #1A2035;
    --accent-primary:#4F8EF7;
    --accent-cyan:   #00D4C8;
    --accent-gold:   #F5A623;
    --accent-red:    #FF4D6A;
    --accent-green:  #00C896;
    --accent-purple: #8B5CF6;
    --text-primary:  #E8EDF8;
    --text-secondary:#8A9BBE;
    --text-muted:    #4A5568;
    --border-subtle: rgba(79,142,247,0.12);
    --border-glow:   rgba(79,142,247,0.35);
    --grid-line:     rgba(255,255,255,0.03);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-void) !important;
    color: var(--text-primary);
}

/* ── Streamlit overrides ── */
.stApp { background-color: var(--bg-void) !important; }
.main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1600px; }
section[data-testid="stSidebar"] { background: var(--bg-deep) !important; border-right: 1px solid var(--border-subtle); }
section[data-testid="stSidebar"] > div { background: transparent !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--bg-surface); border-radius: 12px; padding: 4px; gap: 2px; border: 1px solid var(--border-subtle); }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--text-secondary); border-radius: 8px; font-family: 'Inter', sans-serif; font-size: 13px; font-weight: 500; padding: 8px 18px; border: none; transition: all 0.2s; }
.stTabs [aria-selected="true"] { background: var(--accent-primary) !important; color: #fff !important; box-shadow: 0 0 16px rgba(79,142,247,0.4); }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }
div[data-testid="stMetric"] { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 16px 20px; }
div[data-testid="stMetric"] label { color: var(--text-secondary) !important; font-size: 12px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text-primary) !important; font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 700; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 12px !important; }
.stButton > button { background: var(--bg-elevated); color: var(--text-primary); border: 1px solid var(--border-glow); border-radius: 8px; font-family: 'Inter', sans-serif; font-weight: 500; font-size: 13px; padding: 8px 18px; transition: all 0.2s ease; letter-spacing: 0.02em; }
.stButton > button:hover { background: var(--accent-primary); color: #fff; border-color: var(--accent-primary); box-shadow: 0 0 20px rgba(79,142,247,0.35); transform: translateY(-1px); }
.stSelectbox > div > div, .stMultiSelect > div > div { background: var(--bg-card) !important; border: 1px solid var(--border-subtle) !important; color: var(--text-primary) !important; border-radius: 8px !important; }
.stSlider > div > div > div { background: var(--accent-primary) !important; }
div[data-testid="stExpander"] { background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 12px; }
div[data-testid="stExpander"] > details > summary { font-family: 'Inter', sans-serif; font-weight: 600; color: var(--text-primary); }
.stAlert { border-radius: 10px; border-left-width: 3px; }
textarea { background: var(--bg-card) !important; color: var(--text-primary) !important; border: 1px solid var(--border-subtle) !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; }
hr { border-color: var(--border-subtle) !important; }
.stDataFrame { border-radius: 12px; overflow: hidden; }
.stDataFrame table { background: var(--bg-card) !important; }

/* ── Custom Components ── */
.optima-header {
    background: linear-gradient(135deg, var(--bg-deep) 0%, var(--bg-surface) 100%);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.optima-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(79,142,247,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.optima-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 36px;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(120deg, #4F8EF7 0%, #00D4C8 50%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    display: inline-block;
    margin: 0;
}
.optima-subtitle {
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 4px 0 0 2px;
}
.badge-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,200,150,0.1);
    border: 1px solid rgba(0,200,150,0.3);
    color: var(--accent-green);
    font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    padding: 4px 10px; border-radius: 20px;
    text-transform: uppercase;
}
.badge-live::before {
    content: '●';
    font-size: 8px;
    animation: pulse-dot 1.5s ease-in-out infinite;
}
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:0.3} }

.risk-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    position: relative;
    transition: border-color 0.2s;
}
.risk-card:hover { border-color: var(--border-glow); }
.risk-card.critical { border-left: 3px solid var(--accent-red); }
.risk-card.high     { border-left: 3px solid var(--accent-gold); }
.risk-card.medium   { border-left: 3px solid var(--accent-cyan); }
.risk-card.low      { border-left: 3px solid var(--accent-green); }

.risk-pill {
    display: inline-block;
    padding: 2px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pill-critical { background: rgba(255,77,106,0.15); color: var(--accent-red); }
.pill-high     { background: rgba(245,166,35,0.15); color: var(--accent-gold); }
.pill-medium   { background: rgba(0,212,200,0.15);  color: var(--accent-cyan); }
.pill-low      { background: rgba(0,200,150,0.15);  color: var(--accent-green); }

.ai-bubble {
    background: linear-gradient(135deg, rgba(79,142,247,0.08) 0%, rgba(139,92,246,0.05) 100%);
    border: 1px solid rgba(79,142,247,0.2);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 12px 0;
    position: relative;
}
.ai-bubble::before {
    content: '⬡';
    position: absolute; top: -10px; left: 20px;
    background: var(--bg-void);
    color: var(--accent-primary);
    font-size: 16px;
    padding: 0 6px;
}
.ai-label {
    font-size: 11px; font-weight: 600; letter-spacing: 0.1em;
    color: var(--accent-primary); text-transform: uppercase; margin-bottom: 10px;
}
.ai-text {
    font-size: 14px; line-height: 1.7;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

.util-bar-container { margin: 6px 0; }
.util-bar-label {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 4px;
    font-size: 13px; color: var(--text-secondary);
}
.util-bar-track {
    height: 6px; background: var(--bg-elevated);
    border-radius: 3px; overflow: hidden;
}
.util-bar-fill {
    height: 100%; border-radius: 3px;
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 11px; font-weight: 700;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--text-muted); margin: 20px 0 12px;
}

.scenario-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s;
}
.scenario-card:hover { border-color: var(--accent-primary); transform: translateY(-2px); }
.scenario-card.active { border-color: var(--accent-primary); background: rgba(79,142,247,0.06); }

.stat-chip {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px; color: var(--text-secondary);
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
#  DATA LAYER — Realistic Enterprise Scenario
# ═══════════════════════════════════════════════════════════════════════

@st.cache_data
def load_resource_data():
    """
    Scenario: APEX Financial Services — Fixed-Price Digital Transformation
    A $18M, 18-month program to modernize core banking infrastructure.
    Critical skill shortages + severe overallocation of senior architects.
    """

    # Master resource registry
    resources = pd.DataFrame([
        # id, name, role, seniority, location, team, skills, capacity%, allocated%, cost_rate, onsite
        ("R001","Arjun Mehta",       "Solution Architect", "Principal","Bangalore","Architecture", ["Cloud","API","Security","Azure"],100,145,180,"onsite"),
        ("R002","Priya Nair",         "Data Engineer",     "Senior",   "Hyderabad","Data & Analytics",["Spark","Python","Kafka","SQL"],100,130,140,"onsite"),
        ("R003","David Chen",         "DevOps Engineer",   "Senior",   "Singapore","Platform",  ["K8s","Terraform","CI/CD","AWS"],100,125,155,"remote"),
        ("R004","Fatima Al-Hassan",   "Security Analyst",  "Mid",      "Dubai",    "Security",  ["PenTest","SIEM","Compliance"],100,118,120,"remote"),
        ("R005","Marcus Thompson",    "BA / PM",           "Senior",   "London",   "Delivery",  ["Agile","JIRA","Stakeholder Mgmt"],100,112,130,"onsite"),
        ("R006","Yuki Tanaka",        "ML Engineer",       "Senior",   "Tokyo",    "Data & Analytics",["PyTorch","MLOps","Python"],100,108,160,"remote"),
        ("R007","Ravi Shankar",       "Backend Developer", "Mid",      "Bangalore","Engineering",["Java","Spring","Microservices","SQL"],100,95,95,"onsite"),
        ("R008","Elena Popescu",      "Frontend Developer","Mid",      "Bucharest","Engineering",["React","TypeScript","GraphQL"],100,88,90,"remote"),
        ("R009","James Okafor",       "Cloud Architect",   "Principal","Lagos",    "Architecture",["GCP","Multi-Cloud","FinOps"],100,82,175,"remote"),
        ("R010","Sofia Reyes",        "QA Engineer",       "Senior",   "Mexico City","QA",       ["Selenium","API Testing","Performance"],100,45,100,"remote"),
        ("R011","Ankit Patel",        "Backend Developer", "Junior",   "Bangalore","Engineering",["Java","Python","SQL"],100,40,60,"onsite"),
        ("R012","Chloe Dubois",       "UX Designer",       "Mid",      "Paris",    "Design",    ["Figma","Research","Design Systems"],100,38,95,"remote"),
        ("R013","Omar Farooq",        "Database Admin",    "Senior",   "Islamabad","Data & Analytics",["Oracle","PostgreSQL","MongoDB"],100,35,110,"remote"),
        ("R014","Ingrid Berg",        "Scrum Master",      "Mid",      "Oslo",     "Delivery",  ["Scrum","Kanban","Coaching"],100,30,105,"remote"),
        ("R015","Tariq Hassan",       "Network Engineer",  "Mid",      "Cairo",    "Platform",  ["Cisco","SD-WAN","Zero Trust"],100,28,88,"remote"),
        ("R016","Mei Ling",           "Data Scientist",    "Mid",      "Shanghai", "Data & Analytics",["R","Python","Statistics","Tableau"],100,25,115,"remote"),
        ("R017","Carlos Estrada",     "Solution Architect","Senior",   "Bogota",   "Architecture",["AWS","Serverless","Event-Driven"],100,22,145,"remote"),
        ("R018","Nadia Kovacs",       "Business Analyst",  "Junior",   "Budapest", "Delivery",  ["Requirements","BPMN","SQL"],100,18,55,"remote"),
    ], columns=["id","name","role","seniority","location","team","skills","capacity_pct","allocated_pct","cost_rate","work_mode"])

    # Sprint-by-sprint workload (12 sprints = 24 weeks)
    sprints = [f"S{i:02d}" for i in range(1,13)]
    workload_by_sprint = {
        "R001":[145,148,152,155,158,160,145,138,130,122,118,110],
        "R002":[118,122,128,132,135,130,125,120,118,115,112,108],
        "R003":[110,115,122,128,125,120,115,110,105,100,95, 90],
        "R004":[108,112,118,120,115,110,108,105,102,100,98, 95],
        "R005":[105,108,112,115,112,110,108,105,102,100,98, 95],
        "R006":[95, 100,105,108,110,108,105,102,100,98, 95, 92],
        "R007":[88, 90, 92, 95, 98, 100,98, 95, 92, 90, 88, 85],
        "R008":[80, 82, 85, 88, 90, 92, 90, 88, 85, 82, 80, 78],
        "R009":[75, 78, 80, 82, 85, 88, 85, 82, 80, 78, 75, 72],
        "R010":[42, 40, 38, 35, 32, 30, 35, 40, 45, 50, 55, 60],
        "R011":[38, 36, 35, 33, 30, 28, 30, 35, 40, 45, 50, 55],
        "R012":[35, 32, 30, 28, 25, 22, 25, 30, 35, 40, 45, 50],
        "R013":[32, 30, 28, 25, 22, 20, 22, 25, 30, 35, 40, 45],
        "R014":[28, 25, 22, 20, 18, 15, 18, 22, 28, 35, 42, 50],
        "R015":[25, 22, 20, 18, 16, 15, 18, 22, 28, 35, 42, 50],
        "R016":[22, 20, 18, 16, 14, 12, 15, 20, 25, 30, 38, 48],
        "R017":[20, 18, 16, 14, 12, 10, 12, 15, 20, 25, 30, 40],
        "R018":[16, 15, 14, 12, 10, 8,  10, 14, 18, 22, 28, 38],
    }

    # Monthly capacity vs demand (6 months)
    months = ["Jan","Feb","Mar","Apr","May","Jun"]
    capacity_demand = pd.DataFrame({
        "Month": months,
        "Available_Hours": [2800,2600,2900,2750,2850,2700],
        "Demanded_Hours":  [3350,3480,3620,3200,2950,2650],
        "Critical_Path_Hours": [1200,1350,1480,1300,1100,950],
    })

    # Skills supply/demand matrix
    skills_gap = pd.DataFrame([
        ("Cloud Architecture","Azure","Critical",2,0.5,"Principal SA"),
        ("Data Engineering","Kafka/Streaming","High",3,1.0,"Senior DE"),
        ("Security","Zero Trust","High",2,0.5,"Senior SA"),
        ("ML/AI","MLOps","Medium",2,1.5,"Mid ML Eng"),
        ("DevOps","GitOps","Medium",3,2.0,"Mid DevOps"),
        ("Frontend","Micro-frontends","Low",2,2.5,"Mid FE Dev"),
        ("QA","Performance Testing","Medium",2,0.5,"Senior QA"),
    ], columns=["domain","skill","gap_severity","needed","available","hire_profile"])

    # Milestone commitments
    milestones = pd.DataFrame([
        ("M1","Core API Gateway — Go-Live",      "2024-03-15","IN PROGRESS", 72, "critical",["R001","R003","R007"]),
        ("M2","Data Lake Migration Phase 1",     "2024-04-01","AT RISK",     45, "high",    ["R002","R006","R013"]),
        ("M3","Security Hardening Baseline",     "2024-04-20","ON TRACK",    88, "high",    ["R004","R009"]),
        ("M4","Customer Portal v2.0 Launch",     "2024-05-10","ON TRACK",    35, "medium",  ["R008","R012","R005"]),
        ("M5","Regulatory Reporting Module",     "2024-06-01","AT RISK",     28, "critical",["R001","R002","R013"]),
        ("M6","Performance Baseline Validation", "2024-06-20","PLANNING",    15, "medium",  ["R010","R003","R016"]),
        ("M7","Full Production Cutover",         "2024-08-01","PLANNING",    5,  "critical",["R001","R002","R003","R004"]),
    ], columns=["id","name","target_date","status","progress_pct","priority","key_resources"])

    return resources, workload_by_sprint, sprints, capacity_demand, skills_gap, milestones

# Load data once
resources_df, workload_data, sprints, cap_demand_df, skills_gap_df, milestones_df = load_resource_data()

# ═══════════════════════════════════════════════════════════════════════
#  AI AGENT — Multi-turn conversational intelligence
# ═══════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are OPTIMA AI, an elite Resource & Capacity Intelligence Agent for enterprise delivery programs.

You have deep expertise in:
- Resource planning and workforce optimization
- Fixed-price program risk management  
- Skill gap analysis and rebalancing strategies
- Utilization modeling and capacity planning
- Delivery milestone risk assessment

You're currently analyzing the APEX Financial Services Digital Transformation Program:
- Budget: $18M fixed-price, 18-month duration
- 18 resources across Architecture, Engineering, Data, Security, QA, Design, Delivery teams
- Critical issues: Principal architects at 145-160% allocation, 8 resources severely underutilized (<40%)
- Key risks: 3 milestones at-risk, skill shortages in Cloud Architecture and Kafka/Streaming

CURRENT RESOURCE STATUS (snapshot):
- OVERALLOCATED (>100%): Arjun Mehta 145%, Priya Nair 130%, David Chen 125%, Fatima Al-Hassan 118%, Marcus Thompson 112%, Yuki Tanaka 108%
- OPTIMAL (80-100%): Ravi Shankar 95%, Elena Popescu 88%, James Okafor 82%  
- UNDERUTILIZED (<50%): Sofia Reyes 45%, Ankit Patel 40%, Chloe Dubois 38%, Omar Farooq 35%, Ingrid Berg 30%, Tariq Hassan 28%, Mei Ling 25%, Carlos Estrada 22%, Nadia Kovacs 18%
- Team utilization gap: avg overallocated team = 123%, avg underutilized team = 31%

MILESTONES AT RISK:
1. M2: Data Lake Migration Phase 1 (Apr 1) — Priya Nair at 130%, single point of failure
2. M5: Regulatory Reporting Module (Jun 1) — Depends on Arjun (145%) AND Priya (130%)

RESPONSE STYLE:
- Be decisive and specific. Name actual resources by name.
- Use structured analysis: Risk → Root Cause → Recommendation → Impact
- Provide quantifiable outcomes (e.g., "redeploying X reduces risk from HIGH to MEDIUM")
- When asked for a plan, output it in clear sections with action owners and timelines
- Flag business impact in financial/delivery terms
- Be concise but thorough — you're advising C-suite stakeholders

Always format key recommendations in clear, actionable bullet points. Use markdown formatting."""

def get_ai_response(messages: list) -> str:
    """Stream response from Claude via Anthropic API."""
    try:
        client = Anthropic()
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            return stream.get_final_text()
    except Exception as e:
        return f"⚠️ AI Agent unavailable: {str(e)}\n\nPlease configure your ANTHROPIC_API_KEY environment variable to enable the AI agent."

# ═══════════════════════════════════════════════════════════════════════
#  CHART BUILDERS — Production Plotly charts
# ═══════════════════════════════════════════════════════════════════════

CHART_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(14,18,36,0.6)",
    font=dict(family="Inter, sans-serif", color="#8A9BBE", size=12),
    colorway=["#4F8EF7","#00D4C8","#F5A623","#FF4D6A","#8B5CF6","#00C896"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, linecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False, linecolor="rgba(255,255,255,0.08)"),
    margin=dict(l=10,r=10,t=30,b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(79,142,247,0.2)", borderwidth=1),
)

def allocation_gauge_chart(resources_df):
    """Heatmap-style allocation overview."""
    df = resources_df.sort_values("allocated_pct", ascending=True)

    def color_for_pct(pct):
        if pct > 120: return "#FF4D6A"
        elif pct > 100: return "#F5A623"
        elif pct >= 80: return "#00C896"
        else: return "#4F8EF7"

    colors = [color_for_pct(p) for p in df["allocated_pct"]]
    short_names = [n.split()[0] + " " + n.split()[1][0] + "." for n in df["name"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["allocated_pct"],
        y=short_names,
        orientation="h",
        marker_color=colors,
        marker_line_width=0,
        text=[f"{p}%" for p in df["allocated_pct"]],
        textposition="outside",
        textfont=dict(size=11, color="#8A9BBE"),
        hovertemplate="<b>%{y}</b><br>Allocation: %{x}%<extra></extra>",
    ))
    fig.add_vline(x=100, line_dash="dash", line_color="rgba(255,255,255,0.25)", line_width=1.5,
                  annotation_text="100% Capacity", annotation_font_size=10,
                  annotation_font_color="rgba(255,255,255,0.4)")
    fig.add_vline(x=120, line_dash="dot", line_color="rgba(255,77,106,0.4)", line_width=1)

    # ...existing code...
    theme_no_axes = {k: v for k, v in CHART_THEME.items() if k not in ["xaxis", "yaxis"]}
    fig.update_layout(
        **theme_no_axes, height=520,
        xaxis=dict(**CHART_THEME["xaxis"], title="Sprint"),
        yaxis=dict(**CHART_THEME["yaxis"], tickfont=dict(size=10))
    )
# ...existing code...
    fig.update_xaxes(range=[0,180], title="Allocation %")
    fig.update_yaxes(tickfont=dict(size=11))
    return fig


def workload_heatmap(workload_data, sprints, resources_df):
    """Sprint-by-sprint heatmap."""
    names = [r.split()[0]+" "+r.split()[1][0]+"." for r in resources_df["name"]]
    ids   = list(resources_df["id"])
    z = [[workload_data[rid][i] for i in range(len(sprints))] for rid in ids]

    fig = go.Figure(go.Heatmap(
        z=z, x=sprints, y=names,
        colorscale=[
            [0.0,  "#1A3B6B"],
            [0.25, "#4F8EF7"],
            [0.5,  "#00C896"],
            [0.75, "#F5A623"],
            [1.0,  "#FF4D6A"],
        ],
        zmid=100, zmin=0, zmax=165,
        text=[[f"{v}%" for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=9),
        hoverongaps=False,
        hovertemplate="<b>%{y}</b> | %{x}<br>Allocation: %{z}%<extra></extra>",
        colorbar=dict(
            title=dict(text="Alloc %", font=dict(size=11, color="#8A9BBE")),
            tickfont=dict(color="#8A9BBE", size=10),
            bgcolor="rgba(0,0,0,0)",
            len=0.8,
        ),
    ))
    theme_no_axes = {k: v for k, v in CHART_THEME.items() if k not in ["xaxis", "yaxis"]}
    fig.update_layout(
    **theme_no_axes, height=520,
    xaxis=dict(**CHART_THEME["xaxis"], title="Sprint"),
    yaxis=dict(**CHART_THEME["yaxis"], tickfont=dict(size=10))
)
    return fig


def capacity_demand_chart(cap_demand_df):
    """Capacity vs Demand waterfall-style."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cap_demand_df["Month"], y=cap_demand_df["Available_Hours"],
        mode="lines+markers",
        name="Available Capacity",
        line=dict(color="#00C896", width=2.5),
        marker=dict(size=7, symbol="circle"),
        fill="tozeroy", fillcolor="rgba(0,200,150,0.07)",
        hovertemplate="<b>Available</b>: %{y:,} hrs<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=cap_demand_df["Month"], y=cap_demand_df["Demanded_Hours"],
        mode="lines+markers",
        name="Demand (All Work)",
        line=dict(color="#FF4D6A", width=2.5, dash="solid"),
        marker=dict(size=7, symbol="diamond"),
        hovertemplate="<b>Demand</b>: %{y:,} hrs<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=cap_demand_df["Month"], y=cap_demand_df["Critical_Path_Hours"],
        mode="lines+markers",
        name="Critical Path Demand",
        line=dict(color="#F5A623", width=2, dash="dot"),
        marker=dict(size=6, symbol="triangle-up"),
        hovertemplate="<b>Critical Path</b>: %{y:,} hrs<extra></extra>",
    ))
    # Shade the gap
    fig.add_trace(go.Scatter(
        x=list(cap_demand_df["Month"]) + list(reversed(cap_demand_df["Month"])),
        y=list(cap_demand_df["Demanded_Hours"]) + list(reversed(cap_demand_df["Available_Hours"])),
        fill="toself", fillcolor="rgba(255,77,106,0.06)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
        name="Capacity Gap",
    ))
    # Remove legend from theme to avoid duplicate
    # Remove legend and yaxis from theme to avoid duplicate
    theme_no_legend_yaxis = {k: v for k, v in CHART_THEME.items() if k not in ["legend", "yaxis"]}
    fig.update_layout(
    **theme_no_legend_yaxis,
    height=340,
    yaxis=dict(**CHART_THEME["yaxis"], title="Hours"),
    legend=dict(**CHART_THEME["legend"], orientation="h", y=1.08)
)
    return fig

def skills_gap_radar(skills_gap_df):
    """Spider chart for skill supply vs demand."""
    severity_map = {"Critical":4,"High":3,"Medium":2,"Low":1}
    labels = [f"{r['domain']}\n({r['skill']})" for _,r in skills_gap_df.iterrows()]
    needed    = list(skills_gap_df["needed"])
    available = list(skills_gap_df["available"])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=needed + [needed[0]], theta=labels + [labels[0]],
        name="Required FTEs", fill="toself",
        fillcolor="rgba(255,77,106,0.12)", line=dict(color="#FF4D6A", width=2),
    ))
    fig.add_trace(go.Scatterpolar(
        r=available + [available[0]], theta=labels + [labels[0]],
        name="Available FTEs", fill="toself",
        fillcolor="rgba(79,142,247,0.12)", line=dict(color="#4F8EF7", width=2),
    ))

    theme_no_legend = {
    k: v for k, v in CHART_THEME.items()
    if k != "legend"
}

    fig.update_layout(
    **theme_no_legend,
    height=380,
    polar=dict(
        bgcolor="rgba(14,18,36,0.6)",
        radialaxis=dict(
            visible=True,
            range=[0, 4.5],
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(
                size=9,
                color="#4A5568"
            )
        ),
        angularaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(
                size=10,
                color="#8A9BBE"
            )
        ),
    ),
    legend=dict(
        **CHART_THEME["legend"],
        orientation="h",
        y=-0.12
    ),
)

    return fig


def team_utilization_donut(resources_df):
    """Donut chart by utilization bucket."""
    buckets = {"Overloaded (>120%)":0,"At Risk (101-120%)":0,"Optimal (80-100%)":0,"Underutilized (<80%)":0}
    for _,r in resources_df.iterrows():
        p = r["allocated_pct"]
        if p > 120:    buckets["Overloaded (>120%)"] += 1
        elif p > 100:  buckets["At Risk (101-120%)"] += 1
        elif p >= 80:  buckets["Optimal (80-100%)"]  += 1
        else:          buckets["Underutilized (<80%)"] += 1

    fig = go.Figure(go.Pie(
        labels=list(buckets.keys()),
        values=list(buckets.values()),
        hole=0.62,
        marker=dict(colors=["#FF4D6A","#F5A623","#00C896","#4F8EF7"],
                    line=dict(color="rgba(0,0,0,0)", width=0)),
        textfont=dict(size=11, color="#E8EDF8"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig.add_annotation(text=f"<b style='font-size:22px'>{len(resources_df)}</b><br>Resources",
                       x=0.5,y=0.5, font=dict(size=14,color="#8A9BBE"), showarrow=False)
    # Remove xaxis/yaxis keys for pie/donut charts
    pie_theme = {k: v for k, v in CHART_THEME.items() if k not in ["xaxis", "yaxis", "legend"]}
    fig.update_layout(**pie_theme, height=300, showlegend=True,
                  legend=dict(**CHART_THEME["legend"], orientation="v", x=1.02))
    return fig


def cost_efficiency_scatter(resources_df):
    """Cost rate vs utilization efficiency bubble chart."""
    fig = go.Figure()
    teams = resources_df["team"].unique()
    color_map = {t:c for t,c in zip(teams, ["#4F8EF7","#00D4C8","#F5A623","#FF4D6A","#8B5CF6","#00C896","#F97316","#EC4899"])}

    for team in teams:
        tdf = resources_df[resources_df["team"]==team]
        efficiency = tdf["allocated_pct"].apply(lambda x: 100 - abs(100 - x))
        fig.add_trace(go.Scatter(
            x=tdf["cost_rate"], y=tdf["allocated_pct"],
            mode="markers+text",
            name=team,
            text=[n.split()[0] for n in tdf["name"]],
            textposition="top center",
            textfont=dict(size=9),
            marker=dict(
                size=[e/5+8 for e in efficiency],
                color=color_map[team],
                opacity=0.85,
                line=dict(width=1, color="rgba(255,255,255,0.15)"),
            ),
            hovertemplate="<b>%{text}</b><br>Rate: $%{x}/day<br>Allocation: %{y}%<extra></extra>",
        ))

    fig.add_hrect(y0=80, y1=100, fillcolor="rgba(0,200,150,0.05)", line_width=0,
                  annotation_text="Optimal Zone", annotation_font_size=10,
                  annotation_font_color="rgba(0,200,150,0.5)")
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    theme_no_axes = {k: v for k, v in CHART_THEME.items() if k not in ["xaxis", "yaxis"]}
    fig.update_layout(
    **theme_no_axes, height=400,
    xaxis=dict(**CHART_THEME["xaxis"], title="Daily Cost Rate (USD)"),
    yaxis=dict(**CHART_THEME["yaxis"], title="Current Allocation %")
    )
    return fig


def rebalancing_waterfall(resources_df):
    """Before/After rebalancing comparison."""
    overloaded = resources_df[resources_df["allocated_pct"] > 100].head(6)
    underutil  = resources_df[resources_df["allocated_pct"] < 60].head(6)

    before_over = list(overloaded["allocated_pct"])
    after_over  = [min(p - 25, 100) for p in before_over]
    before_under = list(underutil["allocated_pct"])
    after_under  = [min(p + 40, 95) for p in before_under]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Overallocated — Rebalancing Impact",
                                        "Underutilized — Redeployment Uplift"])

    names_over  = [n.split()[0] for n in overloaded["name"]]
    names_under = [n.split()[0] for n in underutil["name"]]

    fig.add_trace(go.Bar(name="Current", x=names_over, y=before_over,
                         marker_color="#FF4D6A", marker_line_width=0), row=1, col=1)
    fig.add_trace(go.Bar(name="After Rebalance", x=names_over, y=after_over,
                         marker_color="#00C896", marker_line_width=0), row=1, col=1)
    fig.add_trace(go.Bar(name="Current", x=names_under, y=before_under,
                         marker_color="#4F8EF7", marker_line_width=0, showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(name="After Redeploy", x=names_under, y=after_under,
                         marker_color="#00D4C8", marker_line_width=0, showlegend=False), row=1, col=2)

    theme_no_yaxis_legend = {k: v for k, v in CHART_THEME.items() if k not in ["yaxis", "legend"]}
    fig.update_layout(
    **theme_no_yaxis_legend, height=360, barmode="group",
    legend=dict(**CHART_THEME["legend"], orientation="h", y=1.05),
    yaxis=dict(**CHART_THEME["yaxis"], title="Allocation %", range=[0,175]),
    yaxis2=dict(**CHART_THEME["yaxis"], title="Allocation %")
)
    for ax in ["xaxis","xaxis2"]:
        fig.update_layout(**{ax: dict(**CHART_THEME["xaxis"])})
    return fig

# ═══════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px'>
        <p class='optima-wordmark' style='font-size:24px; margin:0'>⬡ OPTIMA</p>
        <p style='color:var(--text-muted);font-size:10px;letter-spacing:.12em;text-transform:uppercase;margin:2px 0 0 2px'>
            Resource Intelligence
        </p>
    </div>
    <hr style='margin:12px 0; border-color:rgba(79,142,247,0.12)'>
    """, unsafe_allow_html=True)

    st.markdown("<p class='section-label'>Program</p>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(79,142,247,0.06);border:1px solid rgba(79,142,247,0.15);
                border-radius:10px;padding:14px 16px;margin-bottom:16px'>
        <p style='color:#E8EDF8;font-weight:600;font-size:14px;margin:0 0 4px'>APEX Digital Transformation</p>
        <p style='color:#8A9BBE;font-size:11px;margin:0'>Fixed-Price · $18M · 18 months</p>
        <div style='margin-top:10px;display:flex;gap:8px;flex-wrap:wrap'>
            <span class='badge-live'>Live</span>
            <span style='background:rgba(245,166,35,0.1);border:1px solid rgba(245,166,35,0.3);
                         color:#F5A623;font-size:10px;font-weight:600;padding:3px 8px;border-radius:12px;
                         text-transform:uppercase;letter-spacing:.06em'>Sprint 7</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p class='section-label'>Filters</p>", unsafe_allow_html=True)
    selected_teams = st.multiselect(
        "Teams", sorted(resources_df["team"].unique()),
        default=list(resources_df["team"].unique()),
    )
    util_filter = st.select_slider(
        "Allocation Range",
        options=[0,20,40,60,80,100,120,140,160],
        value=(0,160),
        format_func=lambda x: f"{x}%",
    )
    seniority_filter = st.multiselect(
        "Seniority", ["Junior","Mid","Senior","Principal"],
        default=["Junior","Mid","Senior","Principal"],
    )

    st.markdown("<p class='section-label'>Quick Actions</p>", unsafe_allow_html=True)
    if st.button("⚡ Run AI Risk Scan", use_container_width=True):
        st.session_state.run_risk_scan = True
    if st.button("📊 Export Resource Plan", use_container_width=True):
        st.session_state.export_plan = True
    if st.button("🔄 Simulate Rebalancing", use_container_width=True):
        st.session_state.show_simulation = True

    st.markdown("<hr style='border-color:rgba(79,142,247,0.12);margin:16px 0'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:var(--text-muted);text-align:center'>
        OPTIMA v2.0 · Hackathon Edition<br>
        <span style='color:rgba(79,142,247,0.5)'>Exercise 10: Capacity Optimization</span>
    </div>
    """, unsafe_allow_html=True)

# Apply sidebar filters
filtered_df = resources_df[
    (resources_df["team"].isin(selected_teams)) &
    (resources_df["allocated_pct"] >= util_filter[0]) &
    (resources_df["allocated_pct"] <= util_filter[1]) &
    (resources_df["seniority"].isin(seniority_filter))
]

# ═══════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════

# ── HEADER ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='optima-header'>
    <div style='display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px'>
        <div>
            <h1 class='optima-wordmark' style='font-size:32px'>⬡ OPTIMA</h1>
            <p class='optima-subtitle'>AI Resource & Capacity Intelligence Platform</p>
        </div>
        <div style='display:flex;gap:10px;align-items:center;flex-wrap:wrap'>
            <span class='badge-live'>Live Analysis</span>
            <span class='stat-chip'><i>📋</i> 18 Resources</span>
            <span class='stat-chip'><i>🎯</i> 7 Milestones</span>
            <span class='stat-chip'><i>⚠️</i> 3 At-Risk</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI STRIP ──────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
overloaded_n = len(resources_df[resources_df["allocated_pct"]>100])
underutil_n  = len(resources_df[resources_df["allocated_pct"]<50])
avg_alloc    = resources_df["allocated_pct"].mean()
at_risk_ms   = len(milestones_df[milestones_df["status"]=="AT RISK"])
util_gap_hrs = cap_demand_df["Demanded_Hours"].sum() - cap_demand_df["Available_Hours"].sum()

c1.metric("Avg Allocation",   f"{avg_alloc:.0f}%",   f"+{avg_alloc-100:.0f}% over")
c2.metric("Overallocated",    f"{overloaded_n}",      "resources at risk",  delta_color="inverse")
c3.metric("Underutilized",    f"{underutil_n}",       "< 50% utilized",     delta_color="inverse")
c4.metric("Milestones At Risk",f"{at_risk_ms}",       "need intervention",  delta_color="inverse")
c5.metric("Capacity Deficit", f"{util_gap_hrs:,} hrs","next 6 months",      delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📡  Command Center",
    "📊  Capacity Analytics",
    "🗺️  Resource Plan",
    "🧩  Skills Intelligence",
    "🤖  AI Agent",
])

# ────────────────────────────────────────────────────────────────────────
#  TAB 1 — COMMAND CENTER
# ────────────────────────────────────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns([3,2], gap="large")

    with col_l:
        st.markdown("<p class='section-label'>Allocation Overview — All Resources</p>", unsafe_allow_html=True)
        st.plotly_chart(allocation_gauge_chart(filtered_df), use_container_width=True, config={"displayModeBar":False})

    with col_r:
        st.markdown("<p class='section-label'>Distribution by Utilization Band</p>", unsafe_allow_html=True)
        st.plotly_chart(team_utilization_donut(filtered_df), use_container_width=True, config={"displayModeBar":False})

        st.markdown("<p class='section-label'>Active Risk Signals</p>", unsafe_allow_html=True)

        risks = [
            ("critical","CRITICAL","Arjun Mehta at 145%",
             "Principal SA is sole dependency for M1 & M5. Burnout risk within 3 sprints.",
             "Offload 30% to Carlos Estrada (22% alloc)"),
            ("high","HIGH","Data Lake M2 at risk",
             "Priya Nair (130%) is single point of failure for Apr 1 milestone.",
             "Pair with Omar Farooq (35% alloc, DB skills)"),
            ("high","HIGH","Skill gap: Kafka/Streaming",
             "3 FTEs needed, 1 available. Blocking Phase 1 data pipeline.",
             "Cross-train Mei Ling + contract 2 specialists"),
            ("medium","MEDIUM","8 resources < 40% util",
             "Cumulative $180K/month spend on underutilized talent.",
             "Redeploy to support overloaded Architecture team"),
        ]
        for severity, label, title, desc, action in risks:
            st.markdown(f"""
            <div class='risk-card {severity}'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px'>
                    <span style='color:#E8EDF8;font-weight:600;font-size:13px'>{title}</span>
                    <span class='risk-pill pill-{severity}'>{label}</span>
                </div>
                <p style='color:#8A9BBE;font-size:12px;margin:0 0 8px;line-height:1.5'>{desc}</p>
                <p style='color:#4F8EF7;font-size:11px;margin:0;font-weight:500'>→ {action}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p class='section-label'>Milestone Health Dashboard</p>", unsafe_allow_html=True)

    ms_cols = st.columns(len(milestones_df))
    status_colors = {"IN PROGRESS":"#4F8EF7","AT RISK":"#FF4D6A","ON TRACK":"#00C896","PLANNING":"#8A9BBE"}
    priority_colors = {"critical":"rgba(255,77,106,0.1)","high":"rgba(245,166,35,0.1)","medium":"rgba(79,142,247,0.08)"}

    for col,(_, ms) in zip(ms_cols, milestones_df.iterrows()):
        sc = status_colors.get(ms["status"],"#8A9BBE")
        pc = priority_colors.get(ms["priority"],"rgba(255,255,255,0.04)")
        with col:
            st.markdown(f"""
            <div style='background:{pc};border:1px solid {sc}22;border-top:3px solid {sc};
                        border-radius:10px;padding:14px;height:170px;'>
                <p style='font-size:10px;font-weight:700;letter-spacing:.1em;
                           text-transform:uppercase;color:{sc};margin:0 0 6px'>{ms["status"]}</p>
                <p style='font-size:12px;font-weight:600;color:#E8EDF8;margin:0 0 8px;
                           line-height:1.4'>{ms["name"]}</p>
                <p style='font-size:10px;color:#8A9BBE;margin:0 0 10px'>{ms["target_date"]}</p>
                <div style='background:rgba(255,255,255,0.06);border-radius:4px;height:4px;overflow:hidden'>
                    <div style='width:{ms["progress_pct"]}%;height:100%;background:{sc};border-radius:4px'></div>
                </div>
                <p style='font-size:10px;color:#8A9BBE;margin:6px 0 0;text-align:right'>{ms["progress_pct"]}%</p>
            </div>
            """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────
#  TAB 2 — CAPACITY ANALYTICS
# ────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("<p class='section-label'>Capacity vs Demand — 6-Month Outlook</p>", unsafe_allow_html=True)
    st.plotly_chart(capacity_demand_chart(cap_demand_df), use_container_width=True, config={"displayModeBar":False})

    col_a, col_b = st.columns([3,2], gap="large")
    with col_a:
        st.markdown("<p class='section-label'>Sprint Workload Heatmap — 12 Sprints</p>", unsafe_allow_html=True)
        st.plotly_chart(workload_heatmap(workload_data, sprints, resources_df),
                        use_container_width=True, config={"displayModeBar":False})

    with col_b:
        st.markdown("<p class='section-label'>Cost Rate vs Allocation Efficiency</p>", unsafe_allow_html=True)
        st.plotly_chart(cost_efficiency_scatter(filtered_df), use_container_width=True, config={"displayModeBar":False})

    st.markdown("<br><p class='section-label'>Rebalancing Simulation — Before vs After</p>", unsafe_allow_html=True)
    st.plotly_chart(rebalancing_waterfall(resources_df), use_container_width=True, config={"displayModeBar":False})

    st.markdown("""
    <div class='ai-bubble'>
        <p class='ai-label'>⬡ OPTIMA AI Insight</p>
        <p class='ai-text'>
        The capacity deficit peaks in <strong>February–March</strong> at +820 hours/month above available capacity.
        Applying a structured rebalancing plan — redistributing 30% load from the top 6 overallocated resources
        to the 8 underutilized resources — would recover approximately <strong>1,200+ hours</strong> of effective capacity
        without additional headcount. This alone addresses 65% of the 6-month deficit.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────
#  TAB 3 — RESOURCE PLAN
# ────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("<p class='section-label'>Comprehensive Resource Plan</p>", unsafe_allow_html=True)

    # Color-coded table
    def alloc_color(val):
        if val > 120:   return "background-color: rgba(255,77,106,0.2); color: #FF4D6A; font-weight:600"
        elif val > 100: return "background-color: rgba(245,166,35,0.2); color: #F5A623; font-weight:600"
        elif val >= 80: return "background-color: rgba(0,200,150,0.15); color: #00C896"
        else:           return "background-color: rgba(79,142,247,0.12); color: #4F8EF7"

    display_df = filtered_df.copy()
    display_df["Skills"] = display_df["skills"].apply(lambda x: ", ".join(x))
    display_df["Status"] = display_df["allocated_pct"].apply(
        lambda p: "🔴 OVERLOADED" if p>120 else ("🟡 AT RISK" if p>100 else ("🟢 OPTIMAL" if p>=80 else "🔵 UNDERUTIL"))
    )
    display_df["Daily Rate"] = display_df["cost_rate"].apply(lambda x: f"${x}")
    display_df["Monthly Cost"] = display_df["cost_rate"].apply(lambda x: f"${x*22:,.0f}")

    show_cols = ["name","role","seniority","team","location","Status","allocated_pct","Daily Rate","Monthly Cost","Skills"]
    rename_map = {"name":"Name","role":"Role","seniority":"Level","team":"Team","location":"Location",
                  "allocated_pct":"Alloc %"}
    table_df = display_df[show_cols].rename(columns=rename_map)

    st.dataframe(
        table_df.style.applymap(alloc_color, subset=["Alloc %"])
                      .format({"Alloc %": "{}%"}),
        use_container_width=True, height=500,
        hide_index=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        total_monthly = display_df["cost_rate"].sum() * 22
        st.metric("Total Monthly Spend", f"${total_monthly:,.0f}", "Fixed-price program")
    with col2:
        wasted_cost = display_df[display_df["allocated_pct"]<50]["cost_rate"].sum() * 22
        st.metric("Underutil Cost Leak", f"${wasted_cost:,.0f}/mo", "Recoverable capacity")

    st.markdown("<br><p class='section-label'>Recommended Rebalancing Actions</p>", unsafe_allow_html=True)

    actions = [
        ("IMMEDIATE","Offload 25-30% from Arjun Mehta to Carlos Estrada",
         "Move API Gateway documentation & cross-team coordination to Carlos (22% alloc, SA skills).",
         "Reduce Arjun: 145%→110%, Increase Carlos: 22%→65%", "Week 1-2"),
        ("IMMEDIATE","Pair Omar Farooq with Priya Nair on Data Lake",
         "Omar (DB Admin, 35% alloc) takes ownership of schema migration and DBA tasks from Priya.",
         "Reduce Priya: 130%→95%, Increase Omar: 35%→75%", "Week 1"),
        ("SHORT-TERM","Cross-train Mei Ling on Kafka Streaming",
         "Mei Ling (Data Scientist, 25% alloc) has Python/statistics foundation. 2-week Kafka intensive.",
         "Addresses critical skill gap, uplift Mei: 25%→70%", "Week 2-4"),
        ("SHORT-TERM","Activate Ingrid Berg as Delivery Coordinator for Architecture team",
         "Ingrid (Scrum Master, 30% alloc) absorbs status tracking from Marcus Thompson.",
         "Reduce Marcus: 112%→85%, Increase Ingrid: 30%→70%", "Week 2"),
        ("MEDIUM-TERM","Contract 2 Kafka/Streaming Specialists",
         "Critical skill gap of 2 FTEs cannot be closed by cross-training alone for M2 deadline.",
         "Resolves HIGH skill risk, cost ~$280K for 4-month engagement", "Week 3-6"),
        ("MEDIUM-TERM","Assign Ankit Patel + Nadia Kovacs to QA automation uplift",
         "Both at <40% allocation. Pair with Sofia Reyes to build automation test suite.",
         "Reduce QA backlog, increase Sofia: 45%→75%, Ankit: 40%→70%", "Week 4-6"),
    ]

    urgency_colors = {"IMMEDIATE":"#FF4D6A","SHORT-TERM":"#F5A623","MEDIUM-TERM":"#4F8EF7"}
    for urgency, title, detail, impact, timeline in actions:
        uc = urgency_colors.get(urgency,"#8A9BBE")
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);
                    border-left:3px solid {uc};border-radius:0 10px 10px 0;
                    padding:16px 20px;margin-bottom:10px'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>
                <span style='color:#E8EDF8;font-weight:600;font-size:13px'>{title}</span>
                <div style='display:flex;gap:8px;flex-shrink:0;margin-left:16px'>
                    <span style='background:{uc}22;color:{uc};font-size:10px;font-weight:700;
                                 padding:3px 8px;border-radius:10px;letter-spacing:.08em'>{urgency}</span>
                    <span style='background:rgba(255,255,255,0.05);color:#8A9BBE;font-size:10px;
                                 padding:3px 8px;border-radius:10px'>⏱ {timeline}</span>
                </div>
            </div>
            <p style='color:#8A9BBE;font-size:12px;margin:0 0 8px;line-height:1.5'>{detail}</p>
            <p style='color:{uc};font-size:11px;margin:0;font-weight:500'>Impact: {impact}</p>
        </div>
        """, unsafe_allow_html=True)

    # Export button
    if st.button("⬇ Download Resource Plan (Excel)", use_container_width=False):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            display_df.to_excel(writer, sheet_name="Resource Plan", index=False)
            skills_gap_df.to_excel(writer, sheet_name="Skills Gap", index=False)
            milestones_df.to_excel(writer, sheet_name="Milestones", index=False)
            cap_demand_df.to_excel(writer, sheet_name="Capacity Demand", index=False)
        st.download_button(
            "📥 Download APEX_Resource_Plan.xlsx",
            data=output.getvalue(),
            file_name=f"APEX_Resource_Plan_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ────────────────────────────────────────────────────────────────────────
#  TAB 4 — SKILLS INTELLIGENCE
# ────────────────────────────────────────────────────────────────────────
with tab4:
    col_left, col_right = st.columns([2,3], gap="large")

    with col_left:
        st.markdown("<p class='section-label'>Skill Supply vs Demand</p>", unsafe_allow_html=True)
        st.plotly_chart(skills_gap_radar(skills_gap_df), use_container_width=True, config={"displayModeBar":False})

        st.markdown("<p class='section-label'>Critical Skill Gaps</p>", unsafe_allow_html=True)
        for _,row in skills_gap_df.iterrows():
            gap = row["needed"] - row["available"]
            sev_color = {"Critical":"#FF4D6A","High":"#F5A623","Medium":"#4F8EF7","Low":"#8A9BBE"}[row["gap_severity"]]
            st.markdown(f"""
            <div class='util-bar-container'>
                <div class='util-bar-label'>
                    <span>{row["domain"]} — {row["skill"]}</span>
                    <span style='color:{sev_color};font-weight:600;font-size:11px'>{row["gap_severity"]} GAP</span>
                </div>
                <div class='util-bar-track'>
                    <div class='util-bar-fill' style='width:{row["available"]/row["needed"]*100:.0f}%;background:{sev_color}'></div>
                </div>
                <div style='display:flex;justify-content:space-between;margin-top:3px;font-size:10px;color:#4A5568'>
                    <span>Have: {row["available"]} FTE</span>
                    <span>Need: {row["needed"]} FTE  (gap: {gap:.1f})</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("<p class='section-label'>Resource Skills Matrix</p>", unsafe_allow_html=True)

        all_skills = sorted(set(s for skills in resources_df["skills"] for s in skills))
        z_matrix = []
        for _,r in resources_df.iterrows():
            row_z = []
            for skill in all_skills:
                if skill in r["skills"]:
                    row_z.append(1 if r["allocated_pct"] < 80 else (2 if r["allocated_pct"] <= 100 else 3))
                else:
                    row_z.append(0)
            z_matrix.append(row_z)

        names_short = [n.split()[0]+" "+n.split()[1][0]+"." for n in resources_df["name"]]

        skill_fig = go.Figure(go.Heatmap(
            z=z_matrix, x=all_skills, y=names_short,
            colorscale=[
                [0.0, "rgba(20,25,40,0.8)"],
                [0.33,"#1A3B6B"],
                [0.66,"#00C896"],
                [1.0, "#FF4D6A"],
            ],
            zmin=0, zmax=3, showscale=True,
            colorbar=dict(
                tickvals=[0,1,2,3],
                ticktext=["No Skill","Avail","Optimal","Overloaded"],
                tickfont=dict(size=9, color="#8A9BBE"),
                len=0.7,
            ),
            hovertemplate="<b>%{y}</b><br>Skill: %{x}<br>Status: %{z}<extra></extra>",
        ))
        theme_no_axes = {
    k: v for k, v in CHART_THEME.items()
    if k not in ["xaxis", "yaxis"]
}

        skill_fig.update_layout(
    **theme_no_axes,
    height=550,
    xaxis=dict(
        **CHART_THEME["xaxis"],
        tickangle=-45,
        tickfont=dict(size=9)
    ),
    yaxis=dict(
        **CHART_THEME["yaxis"],
        tickfont=dict(size=10)
    )
)
        st.plotly_chart(skill_fig, use_container_width=True, config={"displayModeBar":False})

        st.markdown("""
        <div class='ai-bubble'>
            <p class='ai-label'>⬡ Skills Intelligence Summary</p>
            <p class='ai-text'>
            <strong>2 critical gaps</strong> threaten delivery: Cloud Architecture (Azure/Principal level)
            and Kafka/Streaming (3 FTEs needed, 0.5 available). Both block the highest-priority milestones.
            The matrix reveals <strong>6 resources with relevant adjacent skills</strong> that can be
            cross-trained within 2–4 weeks, partially mitigating 1 of the 2 critical gaps.
            Recommend immediate contract hiring for Kafka specialists to protect M2.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><p class='section-label'>Skills Gap Resolution Plan</p>", unsafe_allow_html=True)
    st.dataframe(
        skills_gap_df.style.applymap(
            lambda v: "color:#FF4D6A;font-weight:600" if v=="Critical" else
                      ("color:#F5A623;font-weight:600" if v=="High" else ""),
            subset=["gap_severity"]
        ),
        use_container_width=True, hide_index=True, height=300,
    )


# ────────────────────────────────────────────────────────────────────────
#  TAB 5 — AI AGENT (Multi-turn conversational)
# ────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(79,142,247,0.06) 0%,rgba(139,92,246,0.04) 100%);
                border:1px solid rgba(79,142,247,0.18);border-radius:14px;padding:20px 24px;margin-bottom:20px'>
        <div style='display:flex;align-items:center;gap:14px'>
            <div style='width:44px;height:44px;background:linear-gradient(135deg,#4F8EF7,#8B5CF6);
                        border-radius:12px;display:flex;align-items:center;justify-content:center;
                        font-size:22px;flex-shrink:0'>⬡</div>
            <div>
                <p style='color:#E8EDF8;font-weight:700;font-size:15px;margin:0 0 2px;
                           font-family:Syne,sans-serif'>OPTIMA AI Agent</p>
                <p style='color:#8A9BBE;font-size:12px;margin:0'>
                    Conversational resource intelligence · Powered by Claude · Multi-turn memory
                </p>
            </div>
            <span class='badge-live' style='margin-left:auto'>Online</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": """👋 I'm **OPTIMA AI**, your Resource & Capacity Intelligence Agent for the **APEX Digital Transformation Program**.

I have full context on all 18 resources, 7 milestones, capacity gaps, and skill shortages.

Here's what I can help you with right now:

- 🔍 **Risk Analysis** — Which resources and milestones need immediate attention?
- ⚖️ **Rebalancing Recommendations** — Who should be redeployed where, and how?
- 📊 **Capacity Planning** — How do we close the Feb-Mar capacity deficit?
- 🧩 **Skill Gap Resolution** — Hire, train, or contract? Options for critical gaps.
- 📋 **Executive Briefing** — Generate a leadership-ready summary with decisions needed.

What would you like to explore first?"""
        })

    # Suggested prompts
    st.markdown("<p class='section-label'>Quick Prompts</p>", unsafe_allow_html=True)
    p_cols = st.columns(4)
    prompts = [
        ("🚨 Risk Report",      "Give me a full risk assessment of all resources and milestones. Identify top 3 critical actions."),
        ("⚖️ Rebalance Plan",   "Create a detailed rebalancing plan to bring all resources between 80-100% allocation without impacting milestones."),
        ("💼 Executive Brief",  "Write a 1-page executive briefing on the resource situation with decisions required from leadership."),
        ("💡 Quick Wins",       "What are the 3 fastest things we can do this week to reduce overallocation risk with zero cost?"),
    ]
    for col,(label,prompt) in zip(p_cols, prompts):
        with col:
            if st.button(label, use_container_width=True, key=f"prompt_{label}"):
                st.session_state.selected_prompt = prompt

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])

    # Handle quick prompt selection
    if "selected_prompt" in st.session_state:
        user_input = st.session_state.selected_prompt
        del st.session_state.selected_prompt
    else:
        user_input = None

    # Chat input
    user_typed = st.chat_input("Ask about resource risks, rebalancing, capacity planning, skills gaps...")
    if user_typed:
        user_input = user_typed

if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input   
    })

    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Build message list
    api_messages = st.session_state.messages[:]

    # Assistant response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("OPTIMA AI thinking..."):
            response = get_ai_response(api_messages)

        st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
    st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Clear conversation
    st.markdown("<br>", unsafe_allow_html=True)
    col_clr, _ = st.columns([1,4])
    with col_clr:
        if st.button("🗑 Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;padding:16px 0'>
    <p style='font-family:Syne,sans-serif;font-size:11px;font-weight:700;letter-spacing:.2em;
               text-transform:uppercase;color:rgba(79,142,247,0.4);margin:0 0 4px'>
        ⬡ OPTIMA · Resource & Capacity Intelligence Platform
    </p>
    <p style='font-size:11px;color:rgba(255,255,255,0.15);margin:0'>
        Exercise 10: Resource & Capacity Optimization · Enterprise Hackathon Edition · Built with Streamlit + Claude AI
    </p>
</div>
""", unsafe_allow_html=True)

