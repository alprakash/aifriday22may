import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime
import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# ── PAGE CONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Enterprise SOP Engine",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ENHANCED ENTERPRISE CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
* { font-family: 'Inter', sans-serif; }

.main-title {
    font-size: 2.2em; font-weight: 700;
    color: #0f172a; margin-bottom: 0.1em; letter-spacing: -0.5px;
}
.subtitle { font-size: 1.05em; color: #475569; margin-bottom: 2em; }

.sop-container {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 2.5em; margin-top: 1em;
    box-shadow: 0 4px 20px rgba(15,23,42,0.04);
}
.sop-header-block {
    border-bottom: 2px solid #0f172a; padding-bottom: 1.5em; margin-bottom: 2em;
}
.sop-title { font-size: 1.8em; font-weight: 700; color: #0f172a; }
.sop-meta { font-size: 0.9em; color: #64748b; margin-top: 0.5em; display: flex; gap: 20px; }

.sop-section { margin-bottom: 2em; padding-bottom: 1.5em; border-bottom: 1px solid #f1f5f9; }
.sop-section-title { font-size: 1.25em; font-weight: 600; color: #1e3a8a; margin-bottom: 0.8em; }
.sop-body { color: #334155; font-size: 0.98em; line-height: 1.7; white-space: pre-wrap; }

.matrix-table { width: 100%; border-collapse: collapse; margin: 1em 0; }
.matrix-table th, .matrix-table td { border: 1px solid #cbd5e1; padding: 10px; text-align: left; font-size: 0.92em; }
.matrix-table th { background-color: #f8fafc; font-weight: 600; color: #0f172a; }

.badge { display: inline-block; padding: 0.25em 0.6em; border-radius: 4px; font-size: 0.8em; font-weight: 500; }
.badge-info { background: #e0f2fe; color: #0369a1; }
.badge-warning { background: #fef3c7; color: #b45309; }

.template-box {
    background: #f8fafc; border-left: 4px solid #3b82f6;
    padding: 1.2em; border-radius: 0 8px 8px 0; font-family: monospace; font-size: 0.9em; margin-top: 0.8em;
}
</style>
""", unsafe_allow_html=True)

key = os.getenv("KEY")
endpoint = os.getenv("ENDPOINT")
client = OpenAI(api_key=key, base_url=endpoint, http_client=httpx.Client(verify=False))

# ── SOP CONSTANTS & THEMES ────────────────────────────────────────────────────
SOP_THEMES = {
    "onboarding_support": {
        "name": "🚀 Employee Onboarding Support Process",
        "description": "End-to-end framework managing Day 1 logistics, workspace allocations, and IT handoffs.",
        "handoff": "IT & Admin Ops"
    },
    "bgv_followup": {
        "name": "🔍 Joining Documentation & BGV Process",
        "description": "Rigorous processing of candidate documentation, verification checks, and conditional approvals.",
        "handoff": "Background Verification Team"
    },
    "query_escalation": {
        "name": "☎️ Employee Query Handling & Escalation",
        "description": "Shared services ticketing processing loop mapped across internal tiers and SLA checkpoints.",
        "handoff": "HR Ops Tier 2 / Employee Support"
    },
    "leave_exception": {
        "name": "🏖️ Leave Exception Approval Process",
        "description": "Governance routing pipeline for non-standard leave types and special programmatic exceptions.",
        "handoff": "Payroll Compliance"
    },
    "grievance_intake": {
        "name": "⚖️ Employee Grievance Intake & Acknowledgement",
        "description": "Secure, legally defensive intake logging framework safeguarding confidentiality and strict protocols.",
        "handoff": "Legal & Employee Relations"
    },
    "payroll_correction": {
        "name": "💰 Payroll Correction Request Handling",
        "description": "Remediation loop for mid-cycle changes, variance accounting, and transaction adjustments.",
        "handoff": "Core Payroll & Finance"
    },
    "exit_clearance": {
        "name": "👋 Exit Formalities & Clearance Tracking",
        "description": "Offboarding operational chain tracking asset collections, separation terms, and final settlement computations.",
        "handoff": "IT, Asset Management & Payroll"
    },
    "probation_confirmation": {
        "name": "📄 Probation Confirmation & Feedback Loop",
        "description": "Performance tracking evaluation flow securing manager sign-offs and structural role transitions.",
        "handoff": "HR Business Partners"
    }
}

theme_options = list(SOP_THEMES.keys())
theme_names = [SOP_THEMES[k]["name"] for k in theme_options]

def call_gpt(messages, max_tokens=2500):
    resp = client.chat.completions.create(
        model="azure/genailab-maas-gpt-4o-mini",
        max_tokens=max_tokens,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=messages,
    )
    return resp.choices[0].message.content.strip()

# ── CORE HEADER ───────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📋 Enterprise SOP Architect</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Generate production-grade, compliance-mapped HR Standard Operating Procedures with Flow Diagrams</div>', unsafe_allow_html=True)

# ── SIDEBAR SELECTIONS ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ SOP Parameter Matrix")
    
    selected_theme_idx = st.selectbox(
        "Select Core HR Domain / Theme:",
        range(len(theme_options)),
        format_func=lambda i: theme_names[i]
    )
    current_key = theme_options[selected_theme_idx]
    current_theme = SOP_THEMES[current_key]
    
    st.markdown("---")
    st.markdown("### 💼 Operational Scope")
    scope_target = st.multiselect(
        "Target Applicability:",
        ["All Global Entities", "Corporate HQ Only", "Contractual Staff", "Remote Workforce"],
        default=["All Global Entities"]
    )
    
    sla_target = st.slider("Target Service Level Agreement (SLA hours):", 12, 72, 24, step=12)
    
    st.markdown("### 🔒 Data Security Tier")
    security_tier = st.radio("Classification Level:", ["Confidential / Restrictive", "Internal HR Access Only"])

# ── MAIN WORKSPACE LAYOUT ─────────────────────────────────────────────────────
col_config, col_display = st.columns([1, 2], gap="large")

with col_config:
    st.markdown("### 📝 Context & Requirements Mapping")
    st.caption("Inject domain variance rules below to configure structural checkpoints.")
    
    custom_context = st.text_area(
        "Custom Operational Constraints / Inclusions:",
        placeholder="E.g., Require dual-approvals for variations exceeding 15%; specify escalation to HR Director upon continuous SLA breaches...",
        height=140
    )
    
    st.markdown("""
    <div style='background-color:#f1f5f9; padding:12px; border-radius:8px; font-size:0.85em; color:#475569;'>
    <b>⚡ Enterprise Guardrail Compliance Checklist Included:</b><br>
    • 2x Employee & 2x Manager Touchpoints<br>
    • 2x Internal HR Controls & 1x Compliance Audit Check<br>
    • 1x Critical SLA Breach Scenario Exception<br>
    • 1x Handoff Chain to downstream business teams
    </div>
    """, unsafe_allow_html=True)
    
    generate_sop = st.button("🚀 Build Production SOP Document", use_container_width=True, type="primary")

# ── SOP STRUCTURAL GENERATION AND RENDERING LOOP ──────────────────────────────
with col_display:
    if generate_sop:
        with st.spinner("Generating Standard Operating Procedure JSON Schema..."):
            try:
                system_instruction = """You are an Enterprise HR Solutions Architect and Legal Compliance Officer. 
                Generate a highly detailed, professional Standard Operating Procedure (SOP) based on the inputs provided.
                Your response must be structured precisely as a JSON object matching the requested schema fields.
                Ensure all parameters around touchpoints, checkpoints, handoffs, and risks are meticulously fully written out without placeholders."""
                
                prompt = f"""Generate a highly detailed Standard Operating Procedure (SOP) for: {current_theme['name']}
                Description Context: {current_theme['description']}
                Handoff Destination Team: {current_theme['handoff']}
                Target Applicability Scope: {', '.join(scope_target)}
                SLA Boundary Conditions: {sla_target} Hours
                Data Confidentiality Tier: {security_tier}
                Additional Context: {custom_context if custom_context else "Standard enterprise baseline."}

                Strict Structural Constraints to Include in Text:
                - 2 Employee-facing touchpoints, 2 Manager-facing touchpoints, 2 HR Internal Controls.
                - 1 Regulatory Compliance/Audit consideration, 1 Data Confidentiality baseline, 1 Handoff rule.
                - Operational process loops containing Normal flow, Exception flow, and Escalation flow.

                Return exactly a JSON object structured with the following keys:
                {{
                   "title": "String",
                   "objective": "String",
                   "scope": "String",
                   "inputs_outputs": {{ "inputs": ["str"], "outputs": ["str"] }},
                   "stakeholders": [{{ "role": "str", "responsibility": "str" }}],
                   "step_by_step_normal_flow": ["Step number: text detail"],
                   "controls_checkpoints": {{ "hr_internal_controls": ["str"], "compliance_audit": "str" }},
                   "exceptions_and_slas": {{ "exception_flow": "str", "sla_breach_scenario": "str" }},
                   "escalation_matrix": [{{ "level": "L1/L2/L3", "trigger": "str", "owner": "str" }}],
                   "communication_templates": {{ "employee_touchpoint": "str", "manager_touchpoint": "str" }},
                   "data_privacy": "String",
                   "risks_mitigations": [{{ "risk": "str", "mitigation": "str" }}],
                   "graphviz_dot": "String representation of a valid simple flowchart matching Dot language syntax using clean boxes and simple arrows. Keep node names alphabetic, short, and use clean text labels."
                }}
                Ensure the JSON is completely clean without markdown block symbols.
                """
                
                raw_response = call_gpt([{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}])
                sop_data = json.loads(raw_response)
                
                # Render Section Header Block
                st.markdown(f"""
                <div class="sop-container">
                    <div class="sop-header-block">
                        <div class="sop-title">{sop_data.get('title', current_theme['name'])}</div>
                        <div class="sop-meta">
                            <span><b>SLA Limit:</b> {sla_target} Hrs</span>
                            <span><b>Classification:</b> <span class="badge badge-warning">{security_tier}</span></span>
                            <span><b>Primary Handoff:</b> {current_theme['handoff']}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Render Structural Sections Dynamically
                def render_section(title, content):
                    st.markdown(f'<div class="sop-section"><div class="sop-section-title">{title}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="sop-body">{content}</div></div>', unsafe_allow_html=True)
                
                render_section("1. Objective & Purpose", sop_data.get("objective", ""))
                render_section("2. Scope & Applicability Boundaries", sop_data.get("scope", ""))
                
                # Inputs / Outputs Box
                st.markdown('<div class="sop-section-title">3. Process Boundary Matrix</div>', unsafe_allow_html=True)
                io = sop_data.get("inputs_outputs", {"inputs": [], "outputs": []})
                ioc1, ioc2 = st.columns(2)
                with ioc1:
                    st.markdown("**Process Entrant Inputs:**")
                    for i in io.get("inputs", []): st.markdown(f"- {i}")
                with ioc2:
                    st.markdown("**Process Deliverable Outputs:**")
                    for o in io.get("outputs", []): st.markdown(f"- {o}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Stakeholder Table Matrix
                st.markdown('<div class="sop-section-title">4. Roles & Responsibilities Matrix</div>', unsafe_allow_html=True)
                sh_table = "<table class='matrix-table'><tr><th>Functional Role</th><th>Core Process Responsibility</th></tr>"
                for sh in sop_data.get("stakeholders", []):
                    sh_table += f"<tr><td><b>{sh.get('role')}</b></td><td>{sh.get('responsibility')}</td></tr>"
                sh_table += "</table>"
                st.markdown(sh_table, unsafe_allow_html=True)
                
                # Step-by-Step Flowchart Visualization Layer
                st.markdown('<div class="sop-section-title">5. Dynamic Architecture Flowchart Diagram</div>', unsafe_allow_html=True)
                dot_code = sop_data.get("graphviz_dot", "")
                if dot_code and "digraph" in dot_code:
                    try:
                        st.graphviz_chart(dot_code, use_container_width=True)
                    except Exception:
                        st.caption("Visual chart rendering bypassed due to layout dimensions. Processing fallback details.")
                
                # Step by step text execution listing
                st.markdown("**Detailed Core Operational Steps:**")
                for step in sop_data.get("step_by_step_normal_flow", []):
                    st.markdown(f"{step}")
                
                # Internal Controls Checkpoints Block
                st.markdown('<div class="sop-section-title">6. Control Checkpoints & Compliance Auditing</div>', unsafe_allow_html=True)
                cc = sop_data.get("controls_checkpoints", {"hr_internal_controls": [], "compliance_audit": ""})
                st.markdown("**HR Internal Control Verification Points:**")
                for ctrl in cc.get("hr_internal_controls", []):
                    st.markdown(f"🔒 <span style='font-size:0.95em;'>{ctrl}</span>", unsafe_allow_html=True)
                st.markdown(f"⚖️ **Regulatory Compliance / Audit Baseline:** \n{cc.get('compliance_audit')}")
                
                # SLA and Exception Infrastructure
                ex_sla = sop_data.get("exceptions_and_slas", {})
                render_section("7. Exception Management Flow Execution", ex_sla.get("exception_flow", ""))
                render_section("8. Critical SLA Breach Remediation Protocols", ex_sla.get("sla_breach_scenario", ""))
                
                # Escalation Matrix Structure
                st.markdown('<div class="sop-section-title">9. Operational Escalation Path Protocol</div>', unsafe_allow_html=True)
                esc_table = "<table class='matrix-table'><tr><th>Escalation Level</th><th>Process Trigger Point</th><th>Operational Accountable Owner</th></tr>"
                for esc in sop_data.get("escalation_matrix", []):
                    esc_table += f"<tr><td><span class='badge badge-info'>{esc.get('level')}</span></td><td>{esc.get('trigger')}</td><td>{esc.get('owner')}</td></tr>"
                esc_table += "</table>"
                st.markdown(esc_table, unsafe_allow_html=True)
                
                # Communication Templates Block
                st.markdown('<div class="sop-section-title">10. Standardized Touchpoint Templates</div>', unsafe_allow_html=True)
                comm = sop_data.get("communication_templates", {})
                st.markdown("**Employee-Facing System Communication Notification:**")
                st.markdown(f"<div class='template-box'>{comm.get('employee_touchpoint')}</div>", unsafe_allow_html=True)
                st.markdown("**Manager-Facing Action Protocol Notification:**")
                st.markdown(f"<div class='template-box'>{comm.get('manager_touchpoint')}</div>", unsafe_allow_html=True)
                
                # Security & Privacy Layer
                render_section("11. Data Privacy & Confidentiality Foundations", sop_data.get("data_privacy", ""))
                
                # Risk Analysis Layout
                st.markdown('<div class="sop-section-title">12. Operational Risk & System Mitigation Strategy Matrix</div>', unsafe_allow_html=True)
                risk_table = "<table class='matrix-table'><tr><th>Identified Process Risk</th><th>Enterprise Mitigation Control Strategy</th></tr>"
                for rm in sop_data.get("risks_mitigations", []):
                    risk_table += f"<tr><td>❌ {rm.get('risk')}</td><td>✅ {rm.get('mitigation')}</td></tr>"
                risk_table += "</table>"
                st.markdown(risk_table, unsafe_allow_html=True)
                
                # Document Control Layer Info Footer
                st.markdown("""
                <div style="margin-top:3em; border-top:1px dashed #cbd5e1; padding-top:1em; font-size:0.82em; color:#94a3b8;">
                    <b>Document Version:</b> v1.0.0 (Enterprise Standard Base) &nbsp;•&nbsp; 
                    <b>Review Interval Cycle:</b> Bi-Annually &nbsp;•&nbsp; 
                    <b>Architect Systems Sign-off:</b> Authorized Automated Systems Control
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True) # End Container
                
                # Downloadable Action System
                st.markdown("### 💾 Export Configuration Suite")
                sop_string = json.dumps(sop_data, indent=4)
                st.download_button(
                    label="⬇️ Download Full SOP Schema (.json)",
                    data=sop_string,
                    file_name=f"Enterprise_HR_SOP_{current_key}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Operational Framework Compilation Fault: {str(e)}")
    else:
        st.info("Configure variables and metrics via parameters side panel, then execute the compiler to build the production SOP document.")