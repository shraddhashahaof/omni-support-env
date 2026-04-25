import streamlit as st
import pandas as pd
import os
import subprocess
import re

# --- HELPER FUNCTION ---
def strip_ansi(text):
    """Removes ANSI terminal colors."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# --- PAGE CONFIG MUST BE FIRST ---
st.set_page_config(page_title="OmniSupport Analytics", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# --- ULTRA HIGH DENSITY DARK THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Dark Theme Settings */
    .stApp { background-color: #0A0A0F !important; color: #E2E8F0 !important; font-family: 'Inter', sans-serif !important; }
    header[data-testid="stHeader"] { display: none !important; }
    
    /* Main container padding - ABSOLUTE MINIMUM */
    .block-container { padding-top: 10px !important; padding-bottom: 10px !important; max-width: 1400px !important; }

    /* Typography - ULTRA SMALL & TIGHT */
    h1, h2, h3, p, div { margin: 0; padding: 0; }
    h2 { font-size: 14px !important; font-weight: 600 !important; color: #FFFFFF !important; border-bottom: 1px solid rgba(255,255,255,0.1) !important; padding-bottom: 4px !important; margin-bottom: 8px !important; line-height: 1.2 !important; }
    p { font-size: 12px !important; line-height: 1.4 !important; color: #CBD5E1 !important; margin-bottom: 6px !important; }

    /* Ultra Compact Cards */
    .glass-card {
        background: rgba(20, 20, 25, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 4px !important;
        padding: 12px 14px !important;
        margin-bottom: 12px !important;
    }

    /* Terminal Window */
    .cyber-terminal {
        background-color: #000000 !important;
        color: #A3E635 !important;
        padding: 10px !important;
        border-radius: 4px !important;
        font-family: 'Consolas', monospace !important;
        font-size: 11px !important;
        line-height: 1.2 !important;
        height: 400px !important;
        overflow-y: auto !important;
        border: 1px solid rgba(163, 230, 53, 0.3) !important;
        margin-top: 4px !important;
        white-space: pre-wrap !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #050508 !important; border-right: 1px solid rgba(255,255,255,0.1) !important; padding-top: 10px !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 12px !important; margin-bottom: 4px !important; padding: 2px 0 !important;}
    
    /* Tables - EXTREME DENSITY */
    table { width: 100% !important; border-collapse: collapse !important; margin-top: 4px !important; font-size: 12px !important; }
    th { text-align: left !important; padding: 6px 8px !important; border-bottom: 1px solid rgba(255,255,255,0.2) !important; color: #FFFFFF !important; font-weight: 600 !important; background: rgba(0,0,0,0.3) !important; }
    td { padding: 6px 8px !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; color: #E2E8F0 !important; vertical-align: top !important; }
    tr:nth-child(even) { background: rgba(255,255,255,0.02) !important; }
    
    /* Selectboxes and Buttons */
    .stSelectbox div { min-height: 28px !important; font-size: 12px !important; }
    .stButton button { padding: 2px 8px !important; font-size: 12px !important; min-height: 28px !important; margin-top: 1px !important; }
    
    div.stMarkdown { margin-bottom: 0 !important; }
    .text-glow { color: #38BDF8 !important; font-weight: bold !important; }
    
    /* Bullets */
    ul { margin: 0; padding-left: 20px; font-size: 12px; color: #CBD5E1; margin-bottom: 6px; }
    li { margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# --- TASK DATA ---
TASKS = {
    "Easy": ["easy_refund_001", "easy_password_001", "easy_cancel_001", "easy_delivery_001", "easy_update_001"],
    "Medium": ["med_chargeback_001", "med_partial_refund_001", "med_tech_billing_001", "med_subscription_dispute_001", "med_api_quota_001"],
    "Hard": ["hard_fraud_001", "hard_abuse_001", "hard_enterprise_breach_001", "hard_bulk_001", "hard_gdpr_001"]
}

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: white !important; margin-top: 0 !important; border: none !important; font-size: 16px !important;'>⚡ Omni<span class='text-glow'>Support</span></h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 10px !important; color: #94A3B8 !important; border-bottom: 1px solid rgba(255,255,255,0.1) !important; padding-bottom: 8px !important; margin-bottom: 12px !important;'>Advanced AI Agent Integrity</p>", unsafe_allow_html=True)
    page = st.radio("Navigation", [
        "Executive Dashboard",
        "Live Simulation Engine",
        "RL Training Analytics",
        "Performance Matrix",
        "Policy Database"
    ], label_visibility="collapsed")

# --- PAGE: EXECUTIVE OVERVIEW ---
if page == "Executive Dashboard":
    st.markdown("""
    <div class="glass-card">
        <h2>The Real-World Stakes</h2>
        <p>Every large company employs thousands of support agents to handle billing disputes, fraud alerts, technical issues, and compliance requests. Getting these decisions wrong creates massive liabilities.</p>
    </div>
    
    <div class="glass-card" style="border-left: 3px solid #EF4444 !important; background: rgba(239, 68, 68, 0.1) !important;">
        <h2 style="color: #FCA5A5 !important; border: none !important; margin: 0 !important;">⚠️ Critical Vulnerability</h2>
        <p style="color: #F8FAFC !important; margin-bottom: 0 !important;">If an autonomous agent fails under policy constraints, the enterprise loses revenue or incurs legal penalties. Current RL research benchmarks games and coding puzzles, ignoring the high-stakes reality of enterprise support.</p>
    </div>

    <div class="glass-card">
        <h2>Environment Comparison</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 20%;">Feature</th>
                    <th style="width: 40%;">Existing RL Environments (Games/Code)</th>
                    <th style="width: 40%; color: #38BDF8 !important;">OmniSupportEnv (OpenEnv)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color: #FFFFFF !important; font-weight: 600;">Domain</td>
                    <td>Atari, Chess, Python Coding</td>
                    <td style="color: #38BDF8 !important; font-weight: 600;">Enterprise Customer Support</td>
                </tr>
                <tr>
                    <td style="color: #FFFFFF !important; font-weight: 600;">Stakes</td>
                    <td>Low (Score / Pass-Fail)</td>
                    <td style="color: #38BDF8 !important; font-weight: 600;">High (Financial Liability, Legal/GDPR)</td>
                </tr>
                <tr>
                    <td style="color: #FFFFFF !important; font-weight: 600;">Complexity</td>
                    <td>Single domain, perfect information</td>
                    <td style="color: #38BDF8 !important; font-weight: 600;">Multi-step workflows, partial observations</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div class="glass-card">
        <h2>Architecture & Core Components</h2>
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">Component</th>
                    <th style="width: 75%;">Description</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Tasks</td><td>15 hand-crafted enterprise scenarios across Easy/Medium/Hard difficulties (Refunds, Chargebacks, GDPR, Fraud).</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Support Action</td><td>The robust action space available to the agent (e.g., `lookup_order`, `process_refund`, `escalate`, `flag_security`).</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">State Observation</td><td>The agent's working view of the environment, updated dynamically after each tool call (Ticket context, CRM profile).</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Tools</td><td>10 functional tools simulating real enterprise backend systems (Billing APIs, Security Databases, Comm Channels).</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Rewards</td><td>Dense reward function tracking Resolution (40%), Tool Usage (25%), Policy Safety (20%), and Efficiency (15%).</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Graders</td><td>Deterministic policy evaluators enforcing hard traps (e.g., ×0.20 multiplier penalty for refunding active chargebacks).</td></tr>
            </tbody>
        </table>
    </div>
    
    <div class="glass-card cyber-terminal" style="height: auto !important; overflow: hidden !important; margin-bottom: 0 !important;">
    <p style="color: #A3E635 !important; font-family: 'Consolas', monospace !important; font-size: 11px !important; line-height: 1.4 !important;">
    reset()  →  ticket: "I was charged twice for order #78234..."<br>
    step("check_account: USR_4821")     →  account clean, premium tier    +reward<br>
    step("lookup_order: 78234")         →  duplicate charge confirmed      +reward<br>
    step("process_refund: 78234,49.99") →  refund initiated                +reward<br>
    step("send_response: ...")          →  customer notified               +reward<br>
    step("resolve")                     →  episode ends, score computed
    </p>
    </div>
    """, unsafe_allow_html=True)

# --- PAGE: LIVE SIMULATION LAB ---
elif page == "Live Simulation Engine":
    st.markdown('<div class="glass-card" style="padding: 6px 10px !important; margin-bottom: 4px !important;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: tier = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], label_visibility="collapsed")
    with col2: task_id = st.selectbox("Task ID", TASKS[tier], label_visibility="collapsed")
    with col3: run_btn = st.button("RUN SIMULATION 🚀", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if run_btn:
        with st.spinner(f"Running {task_id}..."):
            try:
                result = subprocess.run(["python", "agent.py", task_id], capture_output=True, text=True, check=False)
                clean_output = strip_ansi(result.stdout)
                st.markdown(f'<div class="cyber-terminal">{clean_output}</div>', unsafe_allow_html=True)
                if result.stderr:
                    st.error("System Error Detected:")
                    st.code(strip_ansi(result.stderr))
            except Exception as e:
                st.error(f"Simulation failed: {e}")
    else:
        st.markdown('<div class="cyber-terminal" style="display: flex; align-items: center; justify-content: center; color: #475569 !important;">[ AWAITING INPUT ]</div>', unsafe_allow_html=True)

# --- PAGE: TRAINING ANALYTICS ---
elif page == "RL Training Analytics":
    st.markdown('<div class="glass-card"><h2>Reward Convergence</h2>', unsafe_allow_html=True)
    img_path = "omni-grpo-output/reward_curve.png"
    if os.path.exists(img_path):
        st.image(img_path)
    else:
        st.markdown("<div style='text-align: center; padding: 10px !important; color: #475569 !important; border: 1px dashed #334155 !important;'>[ Image Not Found ]</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h2>Training Specifications</h2>
        <table>
            <tbody>
                <tr><td style="color: #FFFFFF !important; font-weight: 600; width: 20%;">Model</td><td>Qwen2.5-1.5B-Instruct</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Hardware</td><td>Google Colab T4 GPU</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Duration</td><td>32 Minutes</td></tr>
                <tr><td style="color: #FFFFFF !important; font-weight: 600;">Objective</td><td>Teach the agent to respect complex operational constraints using dense reward signals via TRL/GRPO.</td></tr>
            </tbody>
        </table>
    </div>
    
    <div class="glass-card" style="border-left: 3px solid #10B981 !important; background: rgba(16, 185, 129, 0.1) !important;">
        <h2 style="color: #34D399 !important; border: none !important; margin: 0 0 6px 0 !important;">Impact: +170% Baseline improvement</h2>
        <p style="color: #F8FAFC !important; margin-bottom: 6px !important;">The GRPO-trained model successfully learned to:</p>
        <ul>
            <li style="color: #F8FAFC !important;">Stop hallucinating fake order IDs.</li>
            <li style="color: #F8FAFC !important;">Escalate first, refund second during disputes.</li>
            <li style="color: #F8FAFC !important;">Detect fraud signals on new accounts.</li>
            <li style="color: #F8FAFC !important;">Route legal/GDPR requests securely.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- PAGE: FINAL RESULTS ---
elif page == "Performance Matrix":
    st.markdown('<div class="glass-card"><h2>Model Evaluation Comparison</h2>', unsafe_allow_html=True)
    comp_data = {
        "Architecture": ["1.5B (Zero-Shot)", "1.5B (Post-GRPO)", "72B (Oracle)"],
        "Easy Pass": ["40%", "100%", "100%"],
        "Medium Pass": ["0%", "80%", "100%"],
        "Hard Pass": ["0%", "40%", "100%"],
        "Global Pass": ["13%", "73%", "100%"]
    }
    
    table_html = "<table><thead><tr>"
    for col in comp_data.keys(): table_html += f"<th>{col}</th>"
    table_html += "</tr></thead><tbody>"
    for i in range(3):
        table_html += "<tr>"
        for key in comp_data.keys():
            val = comp_data[key][i]
            color = "#34D399" if val == "100%" else ("#FBBF24" if "7" in val or "8" in val else "#F87171" if "0%" in val else "#94A3B8")
            table_html += f"<td style='color: {color if key != 'Architecture' else '#FFFFFF'} !important;'>{val}</td>"
        table_html += "</tr>"
    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><h2>72B Oracle Trace Results</h2>', unsafe_allow_html=True)
    results = [
        {"Task": "easy_refund_001", "Score": "0.7413", "Status": "PASS"},
        {"Task": "med_chargeback_001", "Score": "0.7413", "Status": "PASS"},
        {"Task": "med_tech_billing_001", "Score": "0.5922", "Status": "PASS"},
        {"Task": "hard_fraud_001", "Score": "0.7601", "Status": "PASS"},
        {"Task": "hard_enterprise_breach", "Score": "0.8044", "Status": "PASS"},
    ]
    t2_html = "<table><thead><tr><th>Task ID</th><th>Score</th><th>Status</th></tr></thead><tbody>"
    for row in results:
        t2_html += f"<tr><td style='color: #FFFFFF !important;'>{row['Task']}</td><td>{row['Score']}</td><td style='color: #34D399 !important; font-weight: bold !important;'>{row['Status']}</td></tr>"
    t2_html += "</tbody></table></div>"
    st.markdown(t2_html, unsafe_allow_html=True)

# --- PAGE: POLICY QA ---
elif page == "Policy Database":
    st.markdown('<div class="glass-card" style="padding-bottom: 20px !important;"><h2>Policy Database Query</h2>', unsafe_allow_html=True)
    
    with st.form(key="policy_form"):
        prompt = st.text_input("Query the internal rules engine (e.g., 'Protocol for active chargebacks?')")
        submit_btn = st.form_submit_button("Query Database")
        
    if submit_btn and prompt:
        p = prompt.lower()
        response = "System ready to answer policy questions."
        if "chargeback" in p: response = "🛑 **Active Chargeback Policy:** NEVER issue a refund. Escalate immediately."
        elif "fraud" in p: response = "🛡️ **Fraud Protocol:** Use `flag_security` and `escalate`."
        elif "refund" in p: response = "💵 **Refund Policy:** Always call `check_account` before processing."
        elif "gdpr" in p: response = "⚖️ **GDPR Policy:** Escalate to Legal. Do not simply close."

        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10B981; padding: 10px; margin-top: 10px; border-radius: 4px;">
            <p style="color: #FFFFFF !important; margin: 0 !important; font-size: 13px !important;">{response}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)