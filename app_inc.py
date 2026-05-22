import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import httpx
from dotenv import load_dotenv

# --- Load environment variables for OpenAI ---
load_dotenv()
key = os.getenv("KEY")
endpoint = os.getenv("ENDPOINT")
client = OpenAI(api_key=key, base_url=endpoint, http_client=httpx.Client(verify=False))

def call_gpt(messages, max_tokens=800):
    resp = client.chat.completions.create(
        model="azure/genailab-maas-gpt-4o-mini",
        max_tokens=max_tokens,
        messages=messages,
    )
    return resp

# --- Streamlit UI ---
st.set_page_config(
    page_title="Automated Incident Resolution Cockpit",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.incident-header {
    font-size: 2.2rem;
    color: #0054A3;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.incident-sub {
    font-size: 1.1rem;
    color: #333;
    margin-bottom: 1.2rem;
}
.incident-agent-box {
    background: linear-gradient(90deg, #0054A310 0%, #FDB82610 100%);
    border: 2px solid #0054A3;
    border-radius: 12px;
    padding: 1.5rem 1.5rem 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}
.incident-agent-response {
    background: #fff;
    border-left: 6px solid #FDB826;
    border-radius: 8px;
    padding: 1.2rem;
    margin-top: 1.2rem;
    font-size: 1.08rem;
}
.aiops-agent-header {
    font-size: 1.6rem;
    color: #FDB826;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.aiops-agent-box {
    background: linear-gradient(90deg, #FDB82610 0%, #0054A310 100%);
    border: 2px solid #FDB826;
    border-radius: 12px;
    padding: 1.2rem 1.2rem 1rem 1.2rem;
    margin-bottom: 1.2rem;
}
.aiops-agent-response {
    background: #fff;
    border-left: 6px solid #0054A3;
    border-radius: 8px;
    padding: 1.1rem;
    margin-top: 1.1rem;
    font-size: 1.05rem;
}
.human-approval-box {
    background: #fffbe6;
    border: 2px solid #FDB826;
    border-radius: 10px;
    padding: 1.2rem;
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
}
.action-btn {
    background-color: #FDB826;
    color: #0054A3;
    border: none;
    border-radius: 6px;
    padding: 0.3rem 1.2rem;
    font-weight: bold;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="incident-header">🛠️ Automated Incident Resolution Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="incident-sub">AI agents monitor logs, detect anomalies, and trigger self-healing workflows.<br><b>Benefits:</b> Reduced downtime, faster resolution, and engineers freed to focus on complex issues.</div>', unsafe_allow_html=True)

# --- Data Loading ---
DEFAULT_FILE = "C:\\Users\\GenAICHNSIRUSR63\\Downloads\\aifriday22may-main\\aifriday22may-main\\Delivery_Exec_Report\\Incident_data.csv"
uploaded_file = st.sidebar.file_uploader("Upload Incident Data (CSV)", type=["csv"])
@st.cache_data
def load_incident_data(file_source):
    try:
        return pd.read_csv(file_source)
    except Exception as e:
        st.sidebar.error(f"Error loading incident data: {e}")
        return None

if uploaded_file is not None:
    df = load_incident_data(uploaded_file)
elif os.path.exists(DEFAULT_FILE):
    df = load_incident_data(DEFAULT_FILE)
else:
    df = None

if df is not None:
    # --- KPI Summary ---
    st.subheader("📊 Incident Resolution KPIs")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Incidents", len(df))
    col2.metric("Avg. Resolution Time (min)", f"{df['Resolution_Time_Minutes'].mean():.1f}")
    col3.metric("Resolved", df[df['Status'] == "Resolved"].shape[0])
    col4.metric("Escalations", df[df['Escalation_Required'] == "Yes"].shape[0])
    col5.metric("Unique Services", df['Service'].nunique())

    st.markdown("---")
    # --- Incident Table with Action Column ---
    st.subheader("🗂️ All Incidents (Click Action to Resolve)")
    st.info("Click 'Action' for any incident to trigger the AI workflow. The AI will analyze and suggest resolution steps. Human must approve to proceed.")

    # Add session state for actions and approvals
    if "incident_action" not in st.session_state:
        st.session_state.incident_action = {}
    if "incident_approval" not in st.session_state:
        st.session_state.incident_approval = {}

    # Show all incidents in a table with action buttons
    def incident_action_button(incident_id):
        btn_key = f"action_{incident_id}"
        return st.button("Action", key=btn_key)

    # Build a table with action buttons
    for idx, row in df.iterrows():
        cols = st.columns([1, 1.5, 1.5, 1.5, 1, 1, 1, 1, 1, 1, 1])
        cols[0].write(row['Incident_ID'])
        cols[1].write(row['Timestamp'])
        cols[2].write(row['Service'])
        cols[3].write(row['Anomaly_Type'])
        cols[4].write(row['Detected_By'])
        cols[5].write(row['Status'])
        cols[6].write(row['Root_Cause'])
        cols[7].write(row['Escalation_Required'])
        cols[8].write(row['Resolution_Action'])
        cols[9].write(row['Resolution_Time_Minutes'])
        # Action button
        if cols[10].button("Action", key=f"action_{row['Incident_ID']}"):
            st.session_state.incident_action[row['Incident_ID']] = True
            st.session_state.incident_approval[row['Incident_ID']] = False

        # If action triggered, show AI analysis and approval
        if st.session_state.incident_action.get(row['Incident_ID'], False):
            with st.spinner("AI Assistant is analyzing the incident and preparing resolution steps..."):
                try:
                    ai_prompt = f"""
You are an AI assistant for IT operations. Given the following incident details, propose a step-by-step resolution workflow.
Clearly explain each step, and highlight any actions that require human approval before execution.
Wait for explicit human approval before proceeding with any automated action.

Incident Details:
Incident ID: {row['Incident_ID']}
Timestamp: {row['Timestamp']}
Service: {row['Service']}
Anomaly Type: {row['Anomaly_Type']}
Detected By: {row['Detected_By']}
Root Cause: {row['Root_Cause']}
Escalation Required: {row['Escalation_Required']}
Engineer Notes: {row['Engineer_Notes']}
Current Status: {row['Status']}
Resolution Action: {row['Resolution_Action']}
Resolution Time (min): {row['Resolution_Time_Minutes']}
"""
                    ai_messages = [
                        {"role": "system", "content": "You are an AI assistant for IT incident resolution. Always require human approval before executing any action."},
                        {"role": "user", "content": ai_prompt}
                    ]
                    ai_response = call_gpt(ai_messages)
                    st.markdown(
                        f'<div class="incident-agent-response">{ai_response.choices[0].message.content}</div>',
                        unsafe_allow_html=True
                    )
                    approval_key = f"approve_{row['Incident_ID']}"
                    if st.button("✅ Approve & Execute Resolution", key=approval_key):
                        st.session_state.incident_approval[row['Incident_ID']] = True
                        st.session_state.incident_action[row['Incident_ID']] = False

                    if st.session_state.incident_approval.get(row['Incident_ID'], False):
                        st.success(f"Incident {row['Incident_ID']} resolution approved and executed! (Simulated)")
                except Exception as err:
                    st.error(f"AI Assistant failed: {err}")

    st.markdown("---")
    # --- Automated Insights & Query Agent ---
    st.markdown('<div class="incident-header">🤖 Incident Resolution Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="incident-agent-box">', unsafe_allow_html=True)
    user_query = st.text_input(
        "Ask about incidents, root causes, or request a summary (e.g., 'Show all memory issues', 'Summarize fastest resolutions', 'What are common root causes?')",
        key="incident_query"
    )
    submit_btn = st.button("Ask Incident Agent", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if submit_btn and user_query:
        with st.spinner("Incident Agent is analyzing your query and incident data..."):
            try:
                context = f"""
You are an AI-powered IT operations assistant. You have access to the following incident log (in markdown table format).
Always answer with clear, concise, and actionable insights. Use bullet points or tables if helpful.
Highlight automation/self-healing actions and benefits where relevant.

INCIDENT LOG:
{df.to_markdown(index=False)}

QUERY:
{user_query}
"""
                messages = [
                    {"role": "system", "content": "You are an expert IT operations assistant. Use only the provided data."},
                    {"role": "user", "content": context}
                ]
                response = call_gpt(messages)
                st.markdown(
                    f'<div class="incident-agent-response">{response.choices[0].message.content}</div>',
                    unsafe_allow_html=True
                )
            except Exception as err:
                st.error(f"Incident Agent failed: {err}")

    # --- Visuals ---
    st.markdown("---")
    st.subheader("📈 Resolution Time by Service")
    chart_df = df.groupby("Service")["Resolution_Time_Minutes"].mean().reset_index()
    st.bar_chart(chart_df, x="Service", y="Resolution_Time_Minutes", color="#FDB826")

    st.subheader("🟠 Top Anomaly Types")
    anomaly_counts = df["Anomaly_Type"].value_counts().reset_index()
    anomaly_counts.columns = ["Anomaly_Type", "Count"]
    st.bar_chart(anomaly_counts, x="Anomaly_Type", y="Count", color="#0054A3")

    # --- AI Ops Agent ---
    st.markdown("---")
    st.markdown('<div class="aiops-agent-header">🤖 AI Ops Agent: Proactive Operations Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="aiops-agent-box">', unsafe_allow_html=True)
    aiops_query = st.text_input(
        "Ask the AI Ops Agent for recommendations, trends, or automation opportunities (e.g., 'Suggest improvements for self-healing', 'What patterns do you see?', 'How can we reduce escalations?')",
        key="aiops_query"
    )
    aiops_btn = st.button("Ask AI Ops Agent", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if aiops_btn and aiops_query:
        with st.spinner("AI Ops Agent is analyzing your request and incident data..."):
            try:
                aiops_context = f"""
You are an AI Ops expert. Analyze the following incident log (markdown table) and provide proactive recommendations, automation opportunities, and trend insights for IT operations leadership.
Focus on self-healing, reducing escalations, and improving incident response.

INCIDENT LOG:
{df.to_markdown(index=False)}

QUERY:
{aiops_query}
"""
                aiops_messages = [
                    {"role": "system", "content": "You are an AI Ops expert for IT operations. Use only the provided data."},
                    {"role": "user", "content": aiops_context}
                ]
                aiops_response = call_gpt(aiops_messages)
                st.markdown(
                    f'<div class="aiops-agent-response">{aiops_response.choices[0].message.content}</div>',
                    unsafe_allow_html=True
                )
            except Exception as err:
                st.error(f"AI Ops Agent failed: {err}")

else:
    st.error("❌ No incident data found. Please upload a valid Incident_data.csv file.")