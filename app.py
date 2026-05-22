import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from openai import OpenAI
import httpx
from dotenv import load_dotenv
load_dotenv()

# Read OpenAI key and endpoint from environment
key = os.getenv("KEY")
endpoint = os.getenv("ENDPOINT")
# ── OpenAI client ─────────────────────────────────────────────────────────────
client = OpenAI(api_key=key, base_url=endpoint, http_client=httpx.Client(verify=False))

def call_gpt(messages, max_tokens=1200):
    resp = client.chat.completions.create(
        model="azure/genailab-maas-gpt-4o-mini",
        max_tokens=max_tokens,
        messages=messages,
    )
    return resp

# 1. Page & Layout Configuration
st.set_page_config(
    page_title="Delivery Health Diagnostic & Executive Brief",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for a polished executive look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #4B5563;
        margin-bottom: 1.8rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
    }
    .delivery-agent-header {
        font-size: 2.1rem;
        color: #0054A3;
        font-weight: 700;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    .delivery-agent-sub {
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 1.2rem;
    }
    .delivery-agent-box {
        background: linear-gradient(90deg, #0054A310 0%, #FDB82610 100%);
        border: 2px solid #0054A3;
        border-radius: 12px;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .delivery-agent-response {
        background: #fff;
        border-left: 6px solid #FDB826;
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 1.2rem;
        font-size: 1.08rem;
    }
</style>
""", unsafe_allow_html=True)

DEFAULT_FILE = "delivery_health_diagnostic_portfolio_data.csv"

# 2. Sidebar Navigation, Key & File Upload Configuration
st.sidebar.title("🔐 Portfolio Controls & Config")
st.sidebar.markdown("---")

# File Uploader with fallback to default path
uploaded_file = st.sidebar.file_uploader("Upload Delivery Portfolio Data (CSV)", type=["csv"])

@st.cache_data
def load_portfolio_data(file_source):
    try:
        return pd.read_csv(file_source)
    except Exception as e:
        st.sidebar.error(f"Error loading portfolio data: {e}")
        return None

# Determine data source
if uploaded_file is not None:
    df = load_portfolio_data(uploaded_file)
elif os.path.exists(DEFAULT_FILE):
    df = load_portfolio_data(DEFAULT_FILE)
else:
    df = None

# 3. Application Main Flow
if df is not None:
    # Portfolio Track Filter
    st.sidebar.subheader("🎯 Portfolio Track Filter")
    unique_tracks = ["All Tracks"] + sorted(list(df["Portfolio_Track"].dropna().unique()))
    selected_track = st.sidebar.selectbox("Filter by Portfolio Pillar:", unique_tracks)
    
    # Filter the working DataFrame
    filtered_df = df if selected_track == "All Tracks" else df[df["Portfolio_Track"] == selected_track]
    
    # Main Dashboard Branding Headers
    st.markdown('<div class="main-header">📋 Delivery Health Diagnostic & Executive Brief</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enterprise Delivery Cockpit for Large-Scale IT Programs & Managed Services Portfolios</div>', unsafe_allow_html=True)
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Portfolio Dashboard & Trends", 
        "🤖 AI Executive Diagnostic Brief", 
        "🗂️ Account Explorer & Core Records",
        "🤝 Delivery Agent"
    ])
    
    # ==========================================
    # --- TAB 1: PORTFOLIO DASHBOARD & TRENDS ---
    # ==========================================
    with tab1:
        st.subheader("📌 Key Performance Indicators (KPI) Summary")
        
        # Calculate high-level aggregate metrics
        total_projects = len(filtered_df)
        total_escalations = filtered_df['Critical_Escalations'].sum()
        avg_csat = filtered_df['CSAT_Score'].mean()
        avg_sla = filtered_df['SLA_Performance_Pct'].mean()
        total_defects = filtered_df['Defect_Backlog_Count'].sum()
        avg_attrition = filtered_df['Resource_Attrition_Pct'].mean()
        
        # Grid of KPI Cards
        kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
        kpi_col1.metric("Active Projects", total_projects)
        kpi_col2.metric(
            "Critical Escalations", 
            total_escalations, 
            delta=int(total_escalations), 
            delta_color="inverse" if total_escalations > 0 else "normal"
        )
        kpi_col3.metric("Avg CSAT Score", f"{avg_csat:.2f} / 5.0")
        kpi_col4.metric("Avg SLA Performance", f"{avg_sla:.1f}%")
        kpi_col5.metric("Total Defect Backlog", f"{total_defects:,}")
        kpi_col6.metric("Avg Attrition Rate", f"{avg_attrition:.1f}%")
        
        st.markdown("---")
        
        # Visual Health Distribution Charts
        st.subheader("🔴🟡🟢 Delivery Posture & Risk Profiling")
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("#### RAG Status Pillars")
            # Reshape RAG columns to draw a clean side-by-side bar count
            rag_melted = filtered_df[['Schedule_Status', 'Quality_Status', 'Budget_Status']].melt(
                var_name='Delivery_Dimension', value_name='RAG_Status'
            )
            rag_counts = rag_melted.groupby(['Delivery_Dimension', 'RAG_Status']).size().reset_index(name='Count')
            
            # Map standardized delivery colors
            color_theme_map = {'Green': '#10B981', 'Amber': '#F59E0B', 'Red': '#EF4444'}
            
            fig_rag = px.bar(
                rag_counts, 
                x='Delivery_Dimension', 
                y='Count', 
                color='RAG_Status',
                color_discrete_map=color_theme_map,
                barmode='group',
                text_auto=True,
                title="RAG Breakdown Across Health Dimensions"
            )
            fig_rag.update_layout(xaxis_title="Pillar", yaxis_title="Number of Accounts", legend_title="Status")
            st.plotly_chart(fig_rag, use_container_width=True)
            
        with g2:
            st.markdown("#### Multi-Dimensional Risk Heatmap")
            heatmap_df = filtered_df.copy()
            # Scaling size dynamically for clear bubble mapping visibility
            heatmap_df['Bubble_Visual_Size'] = heatmap_df['Critical_Escalations'] * 5 + 12
            
            fig_heat = px.scatter(
                heatmap_df,
                x='Resource_Attrition_Pct',
                y='Defect_Backlog_Count',
                size='Bubble_Visual_Size',
                color='CSAT_Score',
                color_continuous_scale='RdYlGn',  # Green implies strong CSAT, Red represents critical risk
                hover_name='Project_Name',
                hover_data=['Project_ID', 'Portfolio_Track', 'Critical_Escalations', 'Schedule_Status'],
                labels={
                    'Resource_Attrition_Pct': 'Resource Attrition Rate (%)',
                    'Defect_Backlog_Count': 'Defect Backlog Count',
                    'CSAT_Score': 'Customer Satisfaction (CSAT)'
                },
                title="Risk Analysis: Attrition vs. Defect Backlog (Bubble Size = Escalations)"
            )
            st.plotly_chart(fig_heat, use_container_width=True)
            
        st.markdown("---")
        
        # Statistical Correlations & Operational Timelines Watchlist
        st.subheader("🔗 Cross-KPI Correlation Matrix & Immediate Release Timeline Risk")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### Operational Metric Relationships")
            numeric_fields = ['SLA_Performance_Pct', 'CSAT_Score', 'Resource_Attrition_Pct', 'Defect_Backlog_Count', 'Critical_Escalations']
            correlation_df = filtered_df[numeric_fields].corr()
            
            fig_corr = px.imshow(
                correlation_df,
                text_auto=".2f",
                color_continuous_scale='RdBu_r',
                zmin=-1, zmax=1,
                title="Statistical Matrix Across Portfolio Metrics"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            st.caption("💡 *Insight Guide: Values approaching +1.0 or -1.0 demonstrate tight structural linkages (e.g., high resource attrition closely correlating with defect accumulation or dropping customer scores).*")
            
        with c2:
            st.markdown("#### High-Risk Release Timelines Watchlist")
            # Isolate projects with critical flags
            timeline_watchlist = filtered_df[
                (filtered_df['Schedule_Status'] == 'Red') | 
                (filtered_df['Quality_Status'] == 'Red') | 
                (filtered_df['Critical_Escalations'] > 0)
            ].sort_values(by='Critical_Escalations', ascending=False)
            
            if not timeline_watchlist.empty:
                st.dataframe(
                    timeline_watchlist[['Project_ID', 'Project_Name', 'Schedule_Status', 'Quality_Status', 'Critical_Escalations', 'SLA_Performance_Pct']],
                    column_config={
                        "Project_ID": "ID",
                        "Project_Name": "Account/Project Name",
                        "Schedule_Status": "Schedule RAG",
                        "Quality_Status": "Quality RAG",
                        "Critical_Escalations": "Active Escalations",
                        "SLA_Performance_Pct": "SLA Adherence"
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.success("✅ Complete Stability: No active projects are flagged for schedule delays or escalations.")

    # ==========================================
    # --- TAB 2: AI EXECUTIVE DIAGNOSTIC BRIEF ---
    # ==========================================
    with tab2:
        st.subheader("🤖 GenAI Portfolio Health Diagnostic Engine")
        st.markdown("This model scans qualitative delivery narratives alongside quantitative thresholds to build standard steering-ready briefs.")
        
        if not key or not endpoint:
            st.warning("🔑 System Alert: OpenAI KEY and ENDPOINT must be set in your environment to run the portfolio auto-diagnostic report.")
        else:
            if st.button("🚀 Run AI Analysis & Generate Briefing"):
                with st.spinner("Analyzing text concerns, calculating correlation patterns, and formalizing leadership suggestions..."):
                    try:
                        # Prepare data summaries for contextual prompt injection
                        aggregate_metrics = {
                            "Track_Scope": selected_track,
                            "Total_Projects_Evaluated": len(filtered_df),
                            "Cumulative_Escalations": int(total_escalations),
                            "Mean_Portfolio_CSAT": round(float(avg_csat), 2),
                            "Mean_Portfolio_SLA_Pct": round(float(avg_sla), 2),
                            "Total_Defect_Backlog": int(total_defects),
                            "Mean_Resource_Attrition_Pct": round(float(avg_attrition), 2)
                        }
                        
                        markdown_data_grid = filtered_df.to_markdown(index=False)
                        
                        prompt_template = f"""
You are an expert IT Delivery Director and Portfolio Management Consultant. Analyze this large-scale IT delivery portfolio/managed services dataset and draft a professional, executive-level Briefing Document.

### PORTFOLIO AGGREGATE SUMMARY:
{aggregate_metrics}

### DETAILED ACCOUNT DATA RECORDS:
{markdown_data_grid}

Please construct a comprehensive and highly polished executive diagnostic report written using professional Markdown, strictly adhering to the following structure:

1. 📊 EXECUTIVE BRIEF & PORTFOLIO HEALTH SUMMARY
   - Provide a high-level overview of the track/portfolio's health posture. Call out standout operational achievements and mention critical structural pain points.

2. 🚨 CLEAR PRIORITIZATION OF RISKS (HIGH / MEDIUM / LOW)
   - Order and categorize the accounts needing immediate executive intervention. Clearly state the drivers (such as poor RAG statuses, high defect volume, or customer friction) for each classification.

3. 🔍 CROSS-KPI CORRELATIONS & STRUCTURED INSIGHTS
   - Highlight the analytical correlations present in the data (for example, connect how team attrition or severe engineering bottlenecks directly impact delivery quality and CSAT outcomes in specific accounts like Beta Mobile App or Omicron Microservices).

4. 🎯 ACTIONABLE LEADERSHIP DECISIONS & REMEDIATION STEPS
   - Deliver concrete, actionable, and practical recommendations for governance boards (e.g., resource backfill interventions, codebase stabilization sprints, client communication resets).
"""
                        messages = [
                            {
                                "role": "system", 
                                "content": "You are a professional Enterprise Delivery Director. Your output must be highly structured, rigorous, and directly helpful for executive steering committees."
                            },
                            {"role": "user", "content": prompt_template}
                        ]
                        response = call_gpt(messages)
                        st.success("✨ Executive Briefing successfully compiled!")
                        st.markdown("---")
                        st.markdown(response.choices[0].message.content)
                    except Exception as err:
                        st.error(f"Failed to communicate with AI diagnostic model: {err}")

    # ==========================================
    # --- TAB 3: ACCOUNT EXPLORER & CORE DATA ---
    # ==========================================
    with tab3:
        st.subheader("📋 Master Portfolio Data Grid")
        st.markdown("Interactive view containing all tabular operational metrics and primary delivery annotations.")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🔍 Single Account Deep-Dive Inspector")
        
        # Let leaders zero-in on a specific account
        available_projects = sorted(list(filtered_df['Project_Name'].unique()))
        selected_project = st.selectbox("Select a Project Account to Inspect:", available_projects)
        
        if selected_project:
            proj_data = filtered_df[filtered_df['Project_Name'] == selected_project].iloc[0]
            
            col_layout_left, col_layout_right = st.columns([1, 2])
            
            with col_layout_left:
                st.markdown(f"### {proj_data['Project_Name']} (`{proj_data['Project_ID']}`)")
                st.markdown(f"**Portfolio Track:** {proj_data['Portfolio_Track']}")
                st.markdown(f"**Schedule Pillar Status:** `{proj_data['Schedule_Status']}`")
                st.markdown(f"**Quality Pillar Status:** `{proj_data['Quality_Status']}`")
                st.markdown(f"**Budget Pillar Status:** `{proj_data['Budget_Status']}`")
                
            with col_layout_right:
                st.markdown("#### Project Operational Snapshot")
                m_row1, m_row2, m_row3 = st.columns(3)
                m_row1.metric("SLA Adherence Rate", f"{proj_data['SLA_Performance_Pct']}%")
                m_row2.metric("CSAT Score Rating", f"{proj_data['CSAT_Score']} / 5")
                m_row3.metric("Critical Escalations", int(proj_data['Critical_Escalations']))
                
                m_row4, m_row5, _ = st.columns(3)
                m_row4.metric("Resource Attrition", f"{proj_data['Resource_Attrition_Pct']}%")
                m_row5.metric("Defect Backlog Count", int(proj_data['Defect_Backlog_Count']))
                
                st.markdown("#### ⚠️ Primary Leadership & Delivery Concern")
                if "None" in str(proj_data['Primary_Leadership_Concern']):
                    st.success(proj_data['Primary_Leadership_Concern'])
                else:
                    st.warning(proj_data['Primary_Leadership_Concern'])

    # ==========================================
    # --- TAB 4: DELIVERY AGENT (EXEC LEADERSHIP QUERY BOT) ---
    # ==========================================
    with tab4:
        st.markdown('<div class="delivery-agent-header">🤝 Delivery Agent: Executive Leadership Query Bot</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="delivery-agent-sub">Ask any question about the delivery portfolio, project risks, KPIs, or request a summary for a specific account. The Delivery Agent will respond with clear, actionable, and data-driven answers for executive decision-making.</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="delivery-agent-box">', unsafe_allow_html=True)
        user_query = st.text_input("🔍 Type your executive query here (e.g., 'Show all projects with Red schedule status', 'Summarize risks for Beta Mobile App', 'Which accounts have the highest attrition?')", key="exec_query")
        submit_btn = st.button("Ask Delivery Agent", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submit_btn and user_query:
            with st.spinner("Delivery Agent is analyzing your query and portfolio data..."):
                try:
                    # Prepare a context for the agent
                    agent_context = f"""
You are Delivery Agent, an executive assistant for IT portfolio leadership. You have access to the following delivery portfolio data (in markdown table format). 
Always answer with clear, concise, and actionable insights. Use bullet points or tables if helpful. 
Highlight critical risks in **bold** and use the following color codes for emphasis:
- Primary: #0054A3
- Accent: #FDB826

DATA TABLE:
{filtered_df.to_markdown(index=False)}

EXECUTIVE QUERY:
{user_query}
"""
                    agent_messages = [
                        {"role": "system", "content": "You are Delivery Agent, a concise, data-driven executive assistant for IT delivery leadership. Use the provided data only."},
                        {"role": "user", "content": agent_context}
                    ]
                    agent_response = call_gpt(agent_messages, max_tokens=900)
                    st.markdown(
                        f'<div class="delivery-agent-response">{agent_response.choices[0].message.content}</div>',
                        unsafe_allow_html=True
                    )
                except Exception as err:
                    st.error(f"Delivery Agent failed: {err}")

else:
    st.error("❌ Data Pipeline Broken: 'delivery_health_diagnostic_portfolio_data.csv' was not found in the root workspace directory. Please upload a valid CSV file through the sidebar filter menu.")