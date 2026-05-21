import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import api_client  # Our network layer connection script
import json

# Set up page configurations with a wide canvas footprint
st.set_page_config(
    page_title="Enterprise SOP Engine",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Application Top Header Banners
st.title("📋 Enterprise HR Process & SOP Engineering Console")
st.caption("AI-Powered Productivity Booster for HR Operations Systems | TCS Internal")
st.markdown("---")

# Session state initialization to hold data patterns safely through user interactions
if 'sop_payload' not in st.session_state:
    st.session_state['sop_payload'] = None
if 'user_edits' not in st.session_state:
    st.session_state['user_edits'] = {}

# ==========================================
# SIDEBAR CONTROL PANEL: INTAKE SCHEMAS
# ==========================================
st.sidebar.header("🎯 Target Process Definitions")

themes = [
    "Employee onboarding support process",
    "Joining documentation and background verification follow-up process",
    "Employee query handling and escalation process",
    "Leave exception approval process",
    "Employee grievance intake and acknowledgement process",
    "Payroll correction request handling process",
    "Exit formalities and clearance tracking process",
    "Probation confirmation and manager feedback process",
    "Internal job movement and release-date coordination process",
    "HRMS employee data correction process"
]

selected_theme = st.sidebar.selectbox("Select Core HR Process Theme:", themes)

st.sidebar.markdown("### 🔍 Evaluation Checklist Compliance")
st.sidebar.info(
    """
    **Required Audit Components Enforced:**
    * 👥 2 Employee-Facing Touchpoints
    * 👔 2 Manager-Facing Touchpoints
    * 🛡️ 2 HR Internal Control Points
    * ⚖️ 1 Compliance / Audit Check
    * 🚨 1 SLA Breach Scenario Route
    * 🔒 1 PII Data Confidentiality Rule
    * 🤝 1 Downstream Team Handoff Flow
    """
)

# Core Execution Action Trigger
if st.sidebar.button("⚙️ Compile Production-Ready SOP", type="primary"):
    with st.spinner("Processing deep architectural validation logic through core services..."):
        # Make the request to our isolated API client layer
        result = api_client.contact_generation_engine(selected_theme)
        
        if result.get("status") == "success":
            st.session_state['sop_payload'] = result.get("data")
            # Clear previous workspace edits when a fresh document is built
            st.session_state['user_edits'] = result.get("data").copy()
            st.sidebar.success(f"SOP Compiled! DB Record ID: #{st.session_state['sop_payload'].get('db_record_id', 0)}")
        else:
            st.sidebar.error(result.get("message", "Network Connection Error."))

# ==========================================
# MAIN DASHBOARD OUTPUT WORKSPACE
# ==========================================
if st.session_state['sop_payload']:
    sop = st.session_state['sop_payload']
    
    # Track core changes inside tabs matching your deliverables package
    tab1, tab2, tab3 = st.tabs([
        "📄 1. Structured SOP Document Editor", 
        "📊 2. Process Flow Swimlanes", 
        "📦 3. Compile Export Packages"
    ])
    
    # --- TAB 1: STRUCTURED CONTENT WORKSPACE & WORKFLOW ---
    with tab1:
        st.subheader("Edit & Refine SOP Structure Fields")
        st.caption("Review or overwrite generated blocks to custom fit your specific team workflow parameters.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state['user_edits']['title'] = st.text_input("Process Title:", value=sop.get("title"))
            st.session_state['user_edits']['objective'] = st.text_area("Process Objective:", value=sop.get("objective"), height=100)
            st.session_state['user_edits']['scope'] = st.text_area("Scope and Applicability:", value=sop.get("scope"), height=100)
            st.session_state['user_edits']['trigger_condition'] = st.text_input("Trigger / Start Condition:", value=sop.get("trigger_condition"))
            
        with col2:
            st.markdown("### 🛡️ Operational Guardrails & Controls")
            
            # Map out compliance fields cleanly for clear workspace tracking
            control_data = sop.get("controls", {})
            st.markdown(f"**HR Internal Control 1:** {control_data.get('control_point_1')}")
            st.markdown(f"**HR Internal Control 2:** {control_data.get('control_point_2')}")
            st.warning(f"⚖️ **Compliance/Audit Consideration:** {control_data.get('audit_consideration')}")
            
            st.markdown("### 🚨 Exception Configurations")
            exception_data = sop.get("exceptions", {})
            st.error(f"**Normal Deviation Path:** {exception_data.get('normal_exception_flow')}")
            st.error(f"⚠️ **SLA Breach Mitigation Vector:** {exception_data.get('sla_breach_scenario')}")
            
            st.markdown("### 🔒 Data Confidentiality Parameters")
            privacy_data = sop.get("privacy_considerations", {})
            st.code(f"PII Protocol: {privacy_data.get('confidentiality_protocol')}\nAccess Scheme: {privacy_data.get('access_control')}", language="text")

    # --- TAB 2: VISUAL SWIMLANES & MILESTONES ---
    with tab2:
        st.subheader("Visual Process Pipeline Architecture")
        st.caption("Chronological trace of touchpoints satisfying both internal and employee/manager interfaces.")
        
        # Chronologically map individual process execution step segments
        for step in sop.get("steps", []):
            with st.container(border=True):
                c_actor, c_desc = st.columns([1, 3])
                with c_actor:
                    # Highlight actors with bold callouts
                    st.markdown(f"👤 **{step.get('actor')}**")
                    st.caption(f"*{step.get('phase')}*")
                with c_desc:
                    st.write(step.get("description"))

    # --- TAB 3: ASSET EXPORT INTERFACE ---
    with tab3:
        st.subheader("Compile and Extract Finished Artifact Packages")
        st.write("Extract your completed configurations into a standard web-safe format that")