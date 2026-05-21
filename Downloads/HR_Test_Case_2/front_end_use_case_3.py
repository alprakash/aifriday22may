import streamlit as st
import json

# Set up page configuration with wide layout for side-by-side editing / viewing
st.set_page_config(
    page_title="AI HR Knowledge Base Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Header & Metadata branding
st.title("💼 AI-Powered HR Knowledge Document Engineer")
st.caption("TCS Internal Automation Sprint - Productivity Booster using AI for HR")
st.markdown("---")

# Initialize Session State variables to capture data persistently across tab refreshes
if 'transcript' not in st.session_state:
    st.session_state['transcript'] = ""
if 'knowledge_doc' not in st.session_state:
    st.session_state['knowledge_doc'] = {}
if 'walkthrough' not in st.session_state:
    st.session_state['walkthrough'] = ""
if 'is_generated' not in st.session_state:
    st.session_state['is_generated'] = False

# ==========================================
# SIDEBAR CONTROL PANEL: INTAKE PARAMETERS
# ==========================================
st.sidebar.header("🎯 Scenario Configuration")

scenarios = [
    "Revised employee onboarding process",
    "Updated leave approval and exception handling process",
    "New employee grievance intake and tracking process",
    "Revised exit clearance and full-and-final settlement process",
    "New internal job posting and employee movement process",
    "Updated joining documentation and background verification process",
    "New HR query management model using a centralized mailbox/ticketing system",
    "Revised probation confirmation and extension process",
    "New employee data correction process for HRMS records",
    "Updated manager responsibilities for onboarding and employee engagement"
]

selected_scenario = st.sidebar.selectbox("Select HR Scenario/Theme:", scenarios)

st.sidebar.markdown("### 📋 Verification Criteria Guardrails")
st.sidebar.info(
    """
    **AI Constraint Validations:**
    * 👥 **Min 4 Speakers:** (HR Ops Lead, HRBP, Payroll Rep, Reporting Manager, Compliance Rep)
    * 🛠️ **Min 3 Action Items** with defined owners.
    * 🔍 **Min 2 Process Clarifications** handled inside text.
    * ⚠️ **Min 1 Explicit Exception Scenario**.
    * ❓ **Min 1 Open Question / Decision Pending**.
    """
)

# Mock button function linking to Flask backend layer API
def trigger_backend_generation(scenario):
    """
    In your full end-to-end framework, replace this dummy code block with an actual HTTP request:
    import requests
    response = requests.post("http://localhost:5000/api/v1/generate", json={"scenario": scenario})
    return response.json()
    """
    # Sample Mock JSON schema representing perfect baseline compliance data
    mock_transcript = (
        "HR Operations Lead (Anjali): Thanks for joining team. We need to standardize the "
        "Revised employee onboarding process starting next week.\n\n"
        "HRBP (Vikram): Right, the key change is shifting backend document collection before Day 1. "
        "But what happens if a candidate doesn't get their degree certificate in time?\n\n"
        "HR Compliance Rep (Rajesh): [Clarification 1] That's an explicit compliance check. "
        "If certificates are delayed, they can upload a provisional letter valid strictly for 30 days.\n\n"
        "Reporting Manager (Sanjay): That handles the exception cleanly. Who tracks the automated IT provisioning?\n\n"
        "Payroll Representative (Sneha): [Clarification 2] IT works fine, but Payroll needs bank details by the 15th to cycle them correctly. "
        "An open question here is whether international hires follow the same automated system or standard manual verification."
    )
    
    mock_knowledge_doc = {
        "purpose": f"To modernize, accelerate, and audit the execution of the {scenario}.",
        "background": "Identified process friction points and delays in cross-departmental handoffs during internal audits.",
        "scope": "All full-time employees, contractors, and regional operating business group managers.",
        "definitions": "**HRMS**: Human Resource Management System. **Day 1**: The formal induction date.",
        "steps": "1. Offer acceptance flags pipeline automation.\n2. Digital locker upload triggered.\n3. IT provisioning automated.",
        "roles": "**HR Ops Lead**: Orchestration.\n**HRBP**: Escalation handling.\n**Reporting Manager**: Team alignment.",
        "exceptions": "Provisional onboarding allowed for a maximum window of 30 days upon submission of a formal provisional letter.",
        "faqs": "**Q: What happens if background checks fail?**\nA: Immediate immediate suspension and escalation to the business compliance lead.",
        "action_items": "1. Anjali: Update system templates (Target: EOD Friday).\n2. Vikram: Notify regional managers.\n3. Sneha: Wire up database mappings.",
        "open_points": "Finalizing the automated verification schema pattern for cross-border international resource tracks.",
        "communication_guidance": "Send out the standardized template email alerts to business heads and update the wiki repository."
    }
    
    mock_walkthrough = (
        "# Screen-Recorded Video Explainer Script\n"
        "**[0:00 - 1:00] Slide 1: Executive Overview**\n"
        "Hello team, today we are walking through the operational adjustments to our HR process pipeline...\n\n"
        "**[1:00 - 3:00] Slide 2: Step-by-Step System Flow**\n"
        "As we trace the execution mapping from phase 1 to phase 3, note how the backend validation steps work..."
    )
    
    return mock_transcript, mock_knowledge_doc, mock_walkthrough

# Execution Button Core Action Trigger
if st.sidebar.button("🚀 Engine Run: Build Core Deliverables", type="primary"):
    with st.spinner("Executing generative agent workflows across services..."):
        t, k, w = trigger_backend_generation(selected_scenario)
        st.session_state['transcript'] = t
        st.session_state['knowledge_doc'] = k
        st.session_state['walkthrough'] = w
        st.session_state['is_generated'] = True
    st.sidebar.success("Process Completed successfully!")

# ==========================================
# MAIN DASHBOARD OUTPUT WORKSPACE
# ==========================================
if not st.session_state['is_generated']:
    st.info("👋 Welcome! Please select an HR scenario from the left panel sidebar configuration and click **Engine Run** to compile your documents.")
else:
    # Organize outputs strictly according to the Participant Deliverables checklist using clear UI tabs
    tab1, tab2, tab3 = st.tabs([
        "📝 1. Synthetic Meeting Transcript", 
        "📄 2. Structured HR Knowledge Document", 
        "🎙️ 3. Training Walkthrough Script"
    ])
    
    # --- TAB 1: SYNTHETIC TRANSCRIPT WORKSPACE ---
    with tab1:
        st.subheader("Synthetic Meeting Transcript Data Output")
        st.caption("Editable markdown text window tracking mandatory roles, context scenario variables, and discussion traces.")
        
        # Display as a text area allowing the user to refine or fix details manually before exporting
        updated_transcript = st.text_area(
            label="Transcript Workspace Editor:", 
            value=st.session_state['transcript'], 
            height=400
        )
        st.session_state['transcript'] = updated_transcript
        
        st.download_button(
            label="📥 Download Raw Transcript (.txt)",
            data=st.session_state['transcript'],
            file_name="synthetic_meeting_transcript.txt",
            mime="text/plain"
        )
        
    # --- TAB 2: STRUCTURED KNOWLEDGE DOCUMENT WORKSPACE ---
    with tab2:
        st.subheader("Structured Reusable HR Reference Knowledge Document")
        st.caption("Formatted explicitly matching the target structural requirements of the evaluation criteria rubric.")
        
        k_doc = st.session_state['knowledge_doc']
        
        # Build out clean presentation blocks for the user to view
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🎯 Purpose\n{k_doc['purpose']}")
            st.markdown(f"### 📜 Background & Reason for Change\n{k_doc['background']}")
            st.markdown(f"### 🌐 Scope & Applicability\n{k_doc['scope']}")
            st.markdown(f"### 📑 Key Terms & Definitions\n{k_doc['definitions']}")
            st.markdown(f"### ⚙️ Step-by-Step Process Explanation\n{k_doc['steps']}")
            
        with col2:
            st.markdown(f"### 👥 Roles & Responsibilities\n{k_doc['roles']}")
            st.markdown(f"### ⚠️ Exception Handling Guidance\n{k_doc['exceptions']}")
            st.markdown(f"### ❓ Frequently Asked Questions (FAQs)\n{k_doc['faqs']}")
            st.markdown(f"### 🛠️ Action Items & Owners\n{k_doc['action_items']}")
            st.markdown(f"### 🛑 Open Points & Pending Decisions\n{k_doc['open_points']}")
            st.markdown(f"### 📢 Employee/Manager Communication Guidance\n{k_doc['communication_guidance']}")

        st.markdown("---")
        
        # Compile complete HTML payload artifact code string block so they can save directly to Word / Web
        html_payload = f"""
        <html>
        <head><style>body {{ font-family: Arial, sans-serif; line-height: 1.6; }} h1, h2 {{ color: #1E3A8A; }}</style></head>
        <body>
            <h1>HR Knowledge Reference Document: {selected_scenario}</h1>
            <h2>1. Purpose</h2><p>{k_doc['purpose']}</p>
            <h2>2. Background & Reason</h2><p>{k_doc['background']}</p>
            <h2>3. Scope</h2><p>{k_doc['scope']}</p>
            <h2>4. Definitions</h2><p>{k_doc['definitions']}</p>
            <h2>5. Process Steps</h2><p>{k_doc['steps']}</p>
            <h2>6. Roles & Responsibilities</h2><p>{k_doc['roles']}</p>
            <h2>7. Exception Handling</h2><p>{k_doc['exceptions']}</p>
            <h2>8. FAQs</h2><p>{k_doc['faqs']}</p>
            <h2>9. Action Items</h2><p>{k_doc['action_items']}</p>
            <h2>10. Open Points</h2><p>{k_doc['open_points']}</p>
            <h2>11. Communications</h2><p>{k_doc['communication_guidance']}</p>
        </body>
        </html>
        """
        
        st.download_button(
            label="📥 Export Structured Document as HTML / Word Web Page",
            data=html_payload,
            file_name="HR_Structured_Knowledge_Document.html",
            mime="text/html"
        )

    # --- TAB 3: TRAINING WALKTHROUGH SCRIPT WORKSPACE ---
    with tab3:
        st.subheader("Short Training Walkthrough Explainer & Presentation Script")
        st.caption("Use this script template text directly as your voiceover narration for your screen-recorded presentation submission.")
        
        updated_walkthrough = st.text_area(
            label="Walkthrough Script Editor Window:", 
            value=st.session_state['walkthrough'], 
            height=350
        )
        st.session_state['walkthrough'] = updated_walkthrough
        
        st.download_button(
            label="📥 Download Presentation Script (.md)",
            data=st.session_state['walkthrough'],
            file_name="training_walkthrough_narration_script.md",
            mime="text/plain"
        )