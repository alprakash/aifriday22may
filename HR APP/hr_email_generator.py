import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime
import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Suite",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=IBM+Plex+Serif:wght@400;600&display=swap');
* { font-family: 'Poppins', sans-serif; }
.main-title {
    font-family: 'IBM Plex Serif', serif;
    font-size: 2.2em; font-weight: 700;
    color: #1a3a52; margin-bottom: 0.2em; letter-spacing: -0.5px;
}
.subtitle { font-size: 1em; color: #5a6c7d; margin-bottom: 1.5em; }
.scenario-card {
    background: linear-gradient(135deg, #f8f9ff 0%, #f0f4f8 100%);
    border: 1px solid #d4dce6; border-radius: 12px;
    padding: 1.2em; margin-bottom: 1em;
}
.scenario-title { font-weight: 600; color: #1a3a52; font-size: 1em; margin-bottom: 0.3em; }
.employee-card {
    background: #ffffff; border-left: 4px solid #2e5f8a;
    border-radius: 8px; padding: 1.2em; margin: 0.8em 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.employee-name { font-size: 1.1em; font-weight: 600; color: #1a3a52; margin-bottom: 0.4em; }
.employee-detail { color: #5a6c7d; font-size: 0.9em; margin: 0.25em 0; }
.email-preview {
    background: #ffffff; border: 1px solid #cdd8e3;
    border-radius: 12px; padding: 1.8em; margin-top: 1em;
    font-family: 'IBM Plex Serif', serif; line-height: 1.75;
    box-shadow: 0 4px 16px rgba(26,58,82,0.07);
}
.email-preview-header {
    border-bottom: 2px solid #2e5f8a;
    padding-bottom: 0.8em; margin-bottom: 1.2em;
}
.email-preview-subject { font-size: 1.05em; font-weight: 700; color: #1a3a52; margin-bottom: 0.3em; }
.email-preview-meta { color: #5a6c7d; font-size: 0.88em; }
.email-preview-body {
    color: #2d3748; font-size: 0.96em;
    white-space: pre-wrap; word-break: break-word;
}
.tone-badge {
    display: inline-block; background: #2e5f8a; color: white;
    padding: 0.3em 0.7em; border-radius: 4px;
    font-size: 0.82em; font-weight: 500; margin-right: 0.4em;
}
.agent-msg-user {
    background: #2e5f8a; color: white;
    border-radius: 16px 16px 4px 16px;
    padding: 0.8em 1.1em; margin: 0.5em 0 0.5em auto;
    max-width: 75%; font-size: 0.93em;
}
.agent-msg-ai {
    background: #f0f4f8; color: #1a3a52;
    border-radius: 16px 16px 16px 4px;
    padding: 0.8em 1.1em; margin: 0.5em auto 0.5em 0;
    max-width: 85%; font-size: 0.93em; line-height: 1.6;
    border-left: 3px solid #2e5f8a;
}
.agent-suggestion-box {
    background: #eef6ff; border: 1px solid #b3d0f0;
    border-radius: 10px; padding: 1em 1.2em; margin-top: 0.6em;
    font-size: 0.9em; color: #1a3a52;
}
.section-header {
    font-size: 1.1em; font-weight: 600; color: #1a3a52;
    margin: 1.2em 0 0.5em 0; border-bottom: 1px solid #e0e6ed; padding-bottom: 0.3em;
}
</style>
""", unsafe_allow_html=True)
key = os.getenv("KEY")
endpoint = os.getenv("ENDPOINT")
# ── OpenAI client ─────────────────────────────────────────────────────────────
client = OpenAI(api_key=key, base_url=endpoint, http_client=httpx.Client(verify=False))

# ── Load employee data ────────────────────────────────────────────────────────
@st.cache_data
def load_employee_data():
    df = pd.read_csv('C:\\Users\\GenAICHNSIRUSR55\\Documents\\HR\\HR APP\\Employee 1000x.csv')
    return df

employees_df = load_employee_data()

# ── HR Scenarios ──────────────────────────────────────────────────────────────
HR_SCENARIOS = {
    "joining_date_clarification": {
        "name": "🎯 Joining Date Clarification",
        "description": "New employee with pending background verification needs date clarity",
        "tone": "Supportive & Transparent",
    },
    "leave_policy_query": {
        "name": "🏖️ Leave Policy / Balance Query",
        "description": "Employee inquires about leave policy or discrepancy in balance",
        "tone": "Clarifying & Helpful",
    },
    "work_arrangement_policy": {
        "name": "🏢 Work Arrangement Policy",
        "description": "Clarification on WFH / hybrid / office work policy",
        "tone": "Clear & Flexible",
    },
    "grievance_acknowledgement": {
        "name": "⚖️ Grievance Acknowledgement",
        "description": "Formal acknowledgement of employee grievance with careful wording",
        "tone": "Empathetic & Formal",
    },
    "confirmation_letter_delay": {
        "name": "📄 Confirmation Letter Delay",
        "description": "Explanation for delayed employment confirmation letter issuance",
        "tone": "Apologetic & Reassuring",
    },
    "relocation_reimbursement": {
        "name": "🚚 Relocation Reimbursement",
        "description": "Clarification on relocation reimbursement eligibility",
        "tone": "Informative & Supportive",
    },
    "parental_leave": {
        "name": "👶 Parental / Caregiver Leave",
        "description": "Process and documentation for maternity/paternity/caregiver leave",
        "tone": "Warm & Informative",
    },
    "exit_formalities": {
        "name": "👋 Exit Formalities",
        "description": "Guidance for resigning employee on exit process and documentation",
        "tone": "Professional & Supportive",
    },
    "payroll_concern": {
        "name": "💰 Payroll / Salary Concern",
        "description": "Address payroll deduction query or salary correction need",
        "tone": "Efficient & Reassuring",
    },
    "onboarding_escalation": {
        "name": "🚀 Onboarding Escalation",
        "description": "Manager escalation regarding delayed onboarding support for new joiner",
        "tone": "Accountable & Action-Oriented",
    },
}

scenario_options = list(HR_SCENARIOS.keys())
scenario_names   = [HR_SCENARIOS[k]["name"] for k in scenario_options]


def clean_scenario_name(name):
    for emoji in ["🎯 ", "🏖️ ", "🏢 ", "⚖️ ", "📄 ", "🚚 ", "👶 ", "👋 ", "💰 ", "🚀 "]:
        name = name.replace(emoji, "")
    return name.strip()


def call_gpt(messages, max_tokens=1200):
    resp = client.chat.completions.create(
        model="azure/genailab-maas-gpt-4o-mini",
        max_tokens=max_tokens,
        messages=messages,
    )
    return resp.choices[0].message.content.strip()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📧 HR Suite — Email Generator & Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Craft professional HR responses · Chat with your AI HR Agent</div>', unsafe_allow_html=True)

tab_email, tab_agent = st.tabs(["✉️  Email Generator", "🤖  HR Agent"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — EMAIL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_email:

    with st.sidebar:
        st.markdown("## ⚙️ Email Generator Config")

        st.markdown("### HR Scenario")
        selected_scenario_idx = st.selectbox(
            "Choose scenario:",
            range(len(scenario_options)),
            format_func=lambda i: scenario_names[i],
            key="scenario_select"
        )
        selected_scenario = scenario_options[selected_scenario_idx]
        scenario_info     = HR_SCENARIOS[selected_scenario]

        st.markdown("### Employee")
        employee_names = employees_df['First Name'] + ' ' + employees_df['Last Name']
        selected_employee_idx = st.selectbox(
            "Choose employee:",
            range(len(employees_df)),
            format_func=lambda i: f"{employee_names.iloc[i]} ({employees_df.iloc[i]['Job Title'][:28]}...)",
            key="employee_select"
        )
        selected_employee = employees_df.iloc[selected_employee_idx]

        st.markdown("### Context / Issue")
        email_context = st.text_area(
            "Brief description:",
            placeholder="E.g., Employee concerned about joining date delay...",
            height=90, key="context_input"
        )

        st.markdown("### Tone")
        tone_option = st.radio(
            "Select tone:",
            ["Empathetic", "Formal", "Supportive", "Action-Oriented"],
            key="tone_select"
        )

    col1, col2 = st.columns([1, 1.3], gap="medium")

    with col1:
        st.markdown('<div class="section-header">👤 Employee Details</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="employee-card">
            <div class="employee-name">{selected_employee['First Name']} {selected_employee['Last Name']}</div>
            <div class="employee-detail"><b>Title:</b> {selected_employee['Job Title']}</div>
            <div class="employee-detail"><b>Email:</b> {selected_employee['Email']}</div>
            <div class="employee-detail"><b>Phone:</b> {selected_employee['Phone']}</div>
            <div class="employee-detail"><b>DOB:</b> {selected_employee['Date of birth']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">📋 Scenario</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="scenario-card">
            <div class="scenario-title">{scenario_info['name']}</div>
            <p style="margin:0.4em 0 0.6em 0; color:#5a6c7d; font-size:0.92em;">{scenario_info['description']}</p>
            <span class="tone-badge">{scenario_info['tone']}</span>
        </div>
        """, unsafe_allow_html=True)

        if email_context:
            st.markdown('<div class="section-header">📌 Context</div>', unsafe_allow_html=True)
            st.info(email_context)

    with col2:
        st.markdown('<div class="section-header">✉️ Email Preview</div>', unsafe_allow_html=True)

        gen_btn = st.button("🤖 Generate Email Response", key="generate_btn", use_container_width=True)

        if "generated_email"   not in st.session_state:
            st.session_state.generated_email   = None
        if "generated_subject" not in st.session_state:
            st.session_state.generated_subject = None
        if "generated_to"      not in st.session_state:
            st.session_state.generated_to      = None

        if gen_btn:
            with st.spinner("Crafting your professional HR response..."):
                try:
                    prompt = f"""You are an experienced HR professional drafting a response to an employee inquiry.

Employee Information:
- Name: {selected_employee['First Name']} {selected_employee['Last Name']}
- Job Title: {selected_employee['Job Title']}
- Email: {selected_employee['Email']}

HR Scenario: {scenario_info['name']}
Scenario Description: {scenario_info['description']}
Default Tone: {scenario_info['tone']}
Tone Preference: {tone_option}

Employee Issue/Context:
{email_context if email_context else "General inquiry related to the scenario."}

Draft a professional, empathetic HR email that:
1. Acknowledges the issue clearly
2. Clarifies next steps without overcommitting
3. Provides helpful information or timeline if applicable
4. Avoids promises requiring additional verification
5. Is concise yet thorough (200-300 words)

Structure: proper greeting, 2-3 body paragraphs, clear next steps, professional closing.
Format: Plain text only — no markdown, no asterisks, no bullet symbols."""

                    email_text = call_gpt([{"role": "user", "content": prompt}])
                    st.session_state.generated_email   = email_text
                    st.session_state.generated_subject = f"Re: {clean_scenario_name(scenario_info['name'])}"
                    st.session_state.generated_to      = selected_employee['Email']

                except Exception as e:
                    st.error(f"Error generating email: {str(e)}")

        if st.session_state.generated_email:
            body_html = st.session_state.generated_email.replace("\n", "<br>")
            st.markdown(f"""
            <div class="email-preview">
                <div class="email-preview-header">
                    <div class="email-preview-subject">📨 {st.session_state.generated_subject}</div>
                    <div class="email-preview-meta"><b>To:</b> {st.session_state.generated_to}</div>
                    <div class="email-preview-meta"><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}</div>
                </div>
                <div class="email-preview-body">{body_html}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**✏️ Edit before sending:**")
            edited_email = st.text_area(
                label="Edit email",
                value=st.session_state.generated_email,
                height=260,
                label_visibility="collapsed",
                key="editable_email"
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🔄 Regenerate", key="regen_btn", use_container_width=True):
                    st.session_state.generated_email = None
                    st.rerun()
            with c2:
                st.download_button(
                    label="⬇️ Download .txt",
                    data=f"Subject: {st.session_state.generated_subject}\nTo: {st.session_state.generated_to}\nDate: {datetime.now().strftime('%B %d, %Y')}\n\n{edited_email}",
                    file_name=f"HR_Email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with c3:
                if st.button("💾 Save to disk", key="save_btn", use_container_width=True):
                    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
                    out = f"HR_Email_{ts}.txt"
                    with open(out, "w") as f:
                        f.write(f"Subject: {st.session_state.generated_subject}\n")
                        f.write(f"To: {st.session_state.generated_to}\n")
                        f.write(f"Date: {datetime.now().strftime('%B %d, %Y')}\n\n")
                        f.write(edited_email)
                    st.success(f"Saved as {out}")

            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Word Count", len(st.session_state.generated_email.split()))
            m2.metric("Tone", tone_option)
            m3.metric("Scenario", clean_scenario_name(scenario_names[selected_scenario_idx]).split()[0])
        else:
            st.info("Click **Generate Email Response** to preview your email here.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — HR AGENT
# ══════════════════════════════════════════════════════════════════════════════
with tab_agent:
    st.markdown('<div class="section-header">🤖 HR Agent — Your AI-Powered HR Assistant</div>', unsafe_allow_html=True)
    st.caption("Ask HR policy questions · Get email suggestions · Run end-to-end workflows for any employee")

    if "agent_messages"    not in st.session_state:
        st.session_state.agent_messages    = []
    if "agent_suggestion"  not in st.session_state:
        st.session_state.agent_suggestion  = None
    if "agent_analysis"    not in st.session_state:
        st.session_state.agent_analysis    = None

    agent_col1, agent_col2 = st.columns([1.1, 1], gap="large")

    # ── LEFT: Chat ────────────────────────────────────────────────────────────
    with agent_col1:
        st.markdown("#### 💬 Chat with HR Agent")

        chat_container = st.container(height=420)
        with chat_container:
            if not st.session_state.agent_messages:
                st.markdown("""
                <div class="agent-msg-ai">
                    👋 Hi! I am your HR Agent.<br><br>
                    You can ask me things like:<br>
                    &bull; <i>"What is the parental leave policy?"</i><br>
                    &bull; <i>"Draft an exit email for John Smith"</i><br>
                    &bull; <i>"Analyse the best scenario for this situation..."</i><br><br>
                    How can I help you today?
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.agent_messages:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="agent-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        content_html = msg["content"].replace("\n", "<br>")
                        st.markdown(f'<div class="agent-msg-ai">{content_html}</div>', unsafe_allow_html=True)

        user_input = st.chat_input("Ask about HR policies, employees, or request an email draft...")

        if user_input:
            st.session_state.agent_messages.append({"role": "user", "content": user_input})

            employee_summary = employees_df[['First Name', 'Last Name', 'Job Title', 'Email']].head(20).to_string(index=False)

            system_prompt = f"""You are an expert HR Agent assistant with deep knowledge of:
- HR policies: leave, payroll, onboarding, exit, grievances, relocation, parental leave, WFH/hybrid
- Professional email drafting for all HR scenarios
- Employee data analysis and end-to-end workflow recommendations

Available HR Scenarios:
{json.dumps({k: v['name'] for k, v in HR_SCENARIOS.items()}, indent=2)}

Sample employee data (first 20 rows):
{employee_summary}

Capabilities:
1. Answer HR policy questions with clear, concise explanations
2. Suggest the most appropriate HR scenario for a described situation and explain why
3. Draft full professional HR emails when asked (plain text, 200-300 words)
4. Analyse an employee situation end-to-end and recommend next steps

Keep responses focused, actionable, and professional."""

            history_for_api = [{"role": "system", "content": system_prompt}] + \
                              st.session_state.agent_messages

            with st.spinner("HR Agent thinking..."):
                try:
                    reply = call_gpt(history_for_api, max_tokens=1400)
                    st.session_state.agent_messages.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.session_state.agent_messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

            st.rerun()

        if st.button("🗑️ Clear conversation", key="clear_chat"):
            st.session_state.agent_messages   = []
            st.session_state.agent_suggestion = None
            st.session_state.agent_analysis   = None
            st.rerun()

    # ── RIGHT: Auto-Suggest Workflow ──────────────────────────────────────────
    with agent_col2:
        st.markdown("#### 🔍 Auto-Suggest Email via Agent")

        ag_emp_names = employees_df['First Name'] + ' ' + employees_df['Last Name']
        ag_emp_idx   = st.selectbox(
            "Select employee for agent analysis:",
            range(len(employees_df)),
            format_func=lambda i: f"{ag_emp_names.iloc[i]} — {employees_df.iloc[i]['Job Title'][:28]}",
            key="agent_emp_select"
        )
        ag_employee  = employees_df.iloc[ag_emp_idx]

        ag_situation = st.text_area(
            "Describe the situation:",
            placeholder="E.g., Employee raised concern about delayed salary credit for last month...",
            height=90, key="agent_situation"
        )

        ag_run = st.button("🚀 Run Full Agent Workflow", key="agent_run", use_container_width=True)

        if ag_run and ag_situation:
            with st.spinner("Agent analysing employee and situation..."):
                try:
                    analysis_prompt = f"""You are an HR Agent. Analyse the situation and return ONLY a valid JSON object:
{{
  "scenario_key": "<one of the available scenario keys>",
  "scenario_name": "<human readable name>",
  "urgency": "Low or Medium or High",
  "tone": "<recommended tone>",
  "analysis": "<2-3 sentence analysis>",
  "next_steps": ["step1", "step2", "step3"]
}}

Employee: {ag_employee['First Name']} {ag_employee['Last Name']}, {ag_employee['Job Title']}
Situation: {ag_situation}

Available scenario keys: {list(HR_SCENARIOS.keys())}

Return ONLY the JSON object. No markdown, no extra text."""

                    raw = call_gpt([{"role": "user", "content": analysis_prompt}], max_tokens=600)
                    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                    analysis_data = json.loads(raw)
                    st.session_state.agent_analysis = analysis_data

                    chosen_scenario = HR_SCENARIOS.get(
                        analysis_data.get("scenario_key", "payroll_concern"),
                        list(HR_SCENARIOS.values())[0]
                    )

                    email_prompt = f"""Draft a professional HR email response.

Employee: {ag_employee['First Name']} {ag_employee['Last Name']}, {ag_employee['Job Title']}
Email: {ag_employee['Email']}
Scenario: {chosen_scenario['name']}
Situation: {ag_situation}
Recommended Tone: {analysis_data.get('tone', chosen_scenario['tone'])}

Rules: plain text only, no markdown, 200-300 words, proper greeting and closing."""

                    email_draft = call_gpt([{"role": "user", "content": email_prompt}], max_tokens=800)
                    st.session_state.agent_suggestion = {
                        "email":   email_draft,
                        "subject": f"Re: {clean_scenario_name(chosen_scenario['name'])}",
                        "to":      ag_employee['Email'],
                    }

                except Exception as e:
                    st.error(f"Agent error: {str(e)}")
            st.rerun()

        # Analysis results card
        if st.session_state.agent_analysis:
            a = st.session_state.agent_analysis
            urgency_icon = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}.get(a.get("urgency", ""), "⚪")
            next_steps_html = "".join(f"&bull; {s}<br>" for s in a.get("next_steps", []))
            st.markdown(f"""
            <div class="agent-suggestion-box">
                <b>📊 Agent Analysis</b><br><br>
                <b>Scenario:</b> {a.get('scenario_name', '—')}<br>
                <b>Urgency:</b> {urgency_icon} {a.get('urgency', '—')}<br>
                <b>Recommended Tone:</b> {a.get('tone', '—')}<br><br>
                <b>Analysis:</b><br>{a.get('analysis', '—')}<br><br>
                <b>Next Steps:</b><br>{next_steps_html}
            </div>
            """, unsafe_allow_html=True)

        # Suggested email preview
        if st.session_state.agent_suggestion:
            sug = st.session_state.agent_suggestion
            st.markdown("#### 📨 Agent-Suggested Email")
            body_html = sug["email"].replace("\n", "<br>")
            st.markdown(f"""
            <div class="email-preview">
                <div class="email-preview-header">
                    <div class="email-preview-subject">📨 {sug['subject']}</div>
                    <div class="email-preview-meta"><b>To:</b> {sug['to']}</div>
                    <div class="email-preview-meta"><b>Date:</b> {datetime.now().strftime('%B %d, %Y')}</div>
                </div>
                <div class="email-preview-body">{body_html}</div>
            </div>
            """, unsafe_allow_html=True)

            edited_sug = st.text_area(
                "Edit suggested email:",
                value=sug["email"],
                height=200,
                key="agent_email_edit",
                label_visibility="collapsed"
            )

            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    "⬇️ Download",
                    data=f"Subject: {sug['subject']}\nTo: {sug['to']}\n\n{edited_sug}",
                    file_name=f"Agent_Email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with dl2:
                if st.button("📤 Use in Email Tab", use_container_width=True, key="use_in_tab"):
                    st.session_state.generated_email   = edited_sug
                    st.session_state.generated_subject = sug["subject"]
                    st.session_state.generated_to      = sug["to"]
                    st.success("Loaded into Email Generator tab!")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#5a6c7d; font-size:0.85em; margin-top:1em;'>
    💡 Always review AI-generated emails before sending &nbsp;·&nbsp; Consult Legal/HR for sensitive grievances
</div>
""", unsafe_allow_html=True)
