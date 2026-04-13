"""
AutoStream AI Agent — Streamlit Frontend
Run with: streamlit run streamlit_app.py
(from the ServiceHive root folder, NOT from inside frontend/)
"""

import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoStream AI Agent",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}
.stApp { background-color: #0a0a0f; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111128 0%, #0d0d1f 100%);
    border-right: 1px solid rgba(120, 80, 255, 0.2);
}
[data-testid="stSidebar"] * { color: #c8c4e0 !important; }

.agent-header {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
    letter-spacing: -0.02em;
}
.agent-subtitle {
    font-size: 0.85rem;
    color: #6b6880;
    margin-bottom: 1.5rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.chat-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
}
.msg-user {
    display: flex;
    justify-content: flex-end;
    animation: fadeUp 0.3s ease;
}
.msg-agent {
    display: flex;
    justify-content: flex-start;
    animation: fadeUp 0.3s ease;
}
.bubble-user {
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #fff;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 70%;
    font-size: 0.93rem;
    line-height: 1.5;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.3);
}
.bubble-agent {
    background: #1a1a2e;
    border: 1px solid rgba(120, 80, 255, 0.2);
    color: #ddd8f5;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-size: 0.93rem;
    line-height: 1.6;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}
.bubble-agent strong { color: #a78bfa; }

.avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    margin: 0 8px;
    flex-shrink: 0;
    align-self: flex-end;
}
.avatar-agent { background: linear-gradient(135deg, #7c3aed, #4f46e5); color: white; }
.avatar-user  { background: linear-gradient(135deg, #0ea5e9, #6366f1); color: white; }

.status-card {
    background: #111128;
    border: 1px solid rgba(120, 80, 255, 0.25);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.status-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: #6b6880; margin-bottom: 0.75rem;
}
.status-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.3rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.83rem;
}
.status-row:last-child { border-bottom: none; }
.status-label { color: #6b6880; }
.status-value { color: #a78bfa; font-weight: 500; }
.status-value.empty { color: #3d3a52; font-style: italic; }

.lead-badge {
    background: linear-gradient(135deg, #065f46, #047857);
    border: 1px solid #10b981;
    border-radius: 8px; padding: 0.5rem 0.75rem;
    font-size: 0.8rem; color: #6ee7b7;
    text-align: center; margin-top: 0.5rem; font-weight: 500;
}
.not-lead-badge {
    background: rgba(55, 48, 80, 0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 0.5rem 0.75rem;
    font-size: 0.8rem; color: #4b4870;
    text-align: center; margin-top: 0.5rem;
}
.stage-pill {
    display: inline-block;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(124, 58, 237, 0.35);
    color: #a78bfa; border-radius: 99px;
    padding: 0.2rem 0.65rem;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase;
}

.stTextInput > div > div > input {
    background: #111128 !important;
    border: 1px solid rgba(120, 80, 255, 0.3) !important;
    border-radius: 12px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.25) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s !important; letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.4) !important;
}

.lead-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.lead-table th {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #6b6880; padding: 0.6rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.07); text-align: left;
}
.lead-table td {
    padding: 0.65rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #c4c0da;
}
.lead-table tr:last-child td { border-bottom: none; }
.plan-tag {
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(124, 58, 237, 0.3);
    color: #a78bfa; border-radius: 6px;
    padding: 0.15rem 0.5rem;
    font-size: 0.75rem; font-weight: 600;
}
hr { border-color: rgba(120, 80, 255, 0.12) !important; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "stage": None, "user_name": None, "email": None,
        "platform": None, "selected_plan": None, "lead_ready": False,
    }

# ── KEY FIX: counter used to reset the text input widget between sends ────────
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# Flag set to True only in the same run where Send was clicked
if "pending_send" not in st.session_state:
    st.session_state.pending_send = False

if "pending_message" not in st.session_state:
    st.session_state.pending_message = ""


# ── Helpers ───────────────────────────────────────────────────────────────────
def send_message(user_input: str) -> dict:
    try:
        resp = requests.post(
            f"{API_URL}/chat",
            json={"session_id": st.session_state.session_id, "message": user_input},
            timeout=30,
        )
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "reply": "⚠️ Cannot connect to backend. Make sure FastAPI is running:\n`uvicorn api.main:app --reload --port 8000`",
            "error": True,
        }
    except Exception as e:
        return {"reply": f"⚠️ Error: {str(e)}", "error": True}


def fetch_leads(plan: str = None) -> dict:
    try:
        url = f"{API_URL}/leads"
        if plan:
            url += f"?plan={plan}"
        return requests.get(url, timeout=10).json()
    except Exception:
        return {"leads": [], "count": 0}


def do_reset():
    try:
        requests.post(f"{API_URL}/reset/{st.session_state.session_id}", timeout=5)
    except Exception:
        pass
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.agent_state = {
        "stage": None, "user_name": None, "email": None,
        "platform": None, "selected_plan": None, "lead_ready": False,
    }
    st.session_state.input_key += 1
    st.session_state.pending_send = False
    st.session_state.pending_message = ""


def val_html(v):
    if v:
        return f'<span class="status-value">{v}</span>'
    return '<span class="status-value empty">—</span>'


def render_agent_content(content: str) -> str:
    """Convert **bold** markdown and newlines to HTML."""
    import re
    content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
    return content.replace("\n", "<br>")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎬 AutoStream")
    st.markdown("---")

    s = st.session_state.agent_state
    stage_display = s.get("stage") or "browsing"

    st.markdown(f"""
    <div class="status-card">
        <div class="status-title">Session Status</div>
        <div class="status-row">
            <span class="status-label">Stage</span>
            <span class="stage-pill">{stage_display}</span>
        </div>
        <div class="status-row">
            <span class="status-label">Name</span>
            {val_html(s.get('user_name'))}
        </div>
        <div class="status-row">
            <span class="status-label">Email</span>
            {val_html(s.get('email'))}
        </div>
        <div class="status-row">
            <span class="status-label">Platform</span>
            {val_html(s.get('platform'))}
        </div>
        <div class="status-row">
            <span class="status-label">Plan</span>
            {val_html(s.get('selected_plan'))}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if s.get("lead_ready"):
        st.markdown('<div class="lead-badge">✅ Lead Captured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="not-lead-badge">○ Lead not yet captured</div>', unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🔄 New Conversation", use_container_width=True):
        do_reset()
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📋 Lead Database")

    plan_filter = st.selectbox("Filter by plan", ["All", "Basic Plan", "Pro Plan"])
    if st.button("Refresh Leads", use_container_width=True):
        st.session_state.leads_data = fetch_leads(
            None if plan_filter == "All" else plan_filter
        )

    leads_data = st.session_state.get("leads_data", fetch_leads())
    leads = leads_data.get("leads", [])
    count = leads_data.get("count", 0)

    st.markdown(f"<small style='color:#6b6880'>Total: {count} lead(s)</small>", unsafe_allow_html=True)

    if leads:
        rows = "".join(f"""
        <tr>
            <td>{lead.get('name','—')}</td>
            <td style="color:#60a5fa;font-size:0.78rem">{lead.get('email','—')}</td>
            <td>{lead.get('platform','—')}</td>
            <td><span class="plan-tag">{lead.get('plan','—')}</span></td>
        </tr>""" for lead in leads)
        st.markdown(f"""
        <div style="overflow-x:auto;margin-top:0.5rem">
        <table class="lead-table">
            <thead><tr><th>Name</th><th>Email</th><th>Platform</th><th>Plan</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color:#3d3a52'>No leads yet.</small>", unsafe_allow_html=True)


# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<div class="agent-header">AutoStream Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="agent-subtitle">AI-Powered Sales Assistant</div>', unsafe_allow_html=True)

# ── Process pending send from PREVIOUS rerun ──────────────────────────────────
# This is the key pattern: we store the message in session_state,
# increment input_key (which clears the widget), rerun once to clear UI,
# then in the NEXT rerun we actually call the API.
if st.session_state.pending_send and st.session_state.pending_message:
    msg = st.session_state.pending_message
    st.session_state.pending_send = False
    st.session_state.pending_message = ""

    st.session_state.messages.append({"role": "user", "content": msg})

    with st.spinner("Thinking..."):
        result = send_message(msg)

    reply = result.get("reply", "Something went wrong.")
    st.session_state.messages.append({"role": "agent", "content": reply})

    if not result.get("error"):
        st.session_state.agent_state = {
            "stage": result.get("stage"),
            "user_name": result.get("user_name"),
            "email": result.get("email"),
            "platform": result.get("platform"),
            "selected_plan": result.get("selected_plan"),
            "lead_ready": result.get("lead_ready", False),
        }
        if result.get("lead_ready"):
            st.session_state.leads_data = fetch_leads()

    st.rerun()

# ── Render chat history ───────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="msg-agent" style="display:flex;margin-bottom:1rem">
        <div class="avatar avatar-agent">🎬</div>
        <div class="bubble-agent">
            👋 Hi! I'm the <strong>AutoStream AI Agent</strong>.<br>
            I can help you explore our video editing plans, answer pricing questions, and get you signed up.<br><br>
            Try: <em>"Tell me about your plans"</em> or <em>"What's the refund policy?"</em>
        </div>
    </div>
    """, unsafe_allow_html=True)

chat_html = '<div class="chat-container">'
for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f"""
        <div class="msg-user">
            <div class="bubble-user">{msg["content"]}</div>
            <div class="avatar avatar-user">You</div>
        </div>"""
    else:
        chat_html += f"""
        <div class="msg-agent">
            <div class="avatar avatar-agent">🎬</div>
            <div class="bubble-agent">{render_agent_content(msg["content"])}</div>
        </div>"""
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

st.markdown("---")

# ── Input row ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])

with col1:
    # input_key increments after every send → Streamlit treats it as a NEW
    # widget and renders it empty. This is the standard Streamlit pattern
    # for clearing a text_input after submission.
    user_input = st.text_input(
        "message",
        placeholder="Ask about plans, pricing, or say 'sign me up'...",
        label_visibility="collapsed",
        key=f"chat_input_{st.session_state.input_key}",
    )

with col2:
    send_clicked = st.button("Send →", use_container_width=True)

# ── Trigger: only on explicit Send click or Enter (not on reruns) ─────────────
if send_clicked and user_input.strip():
    # Store message + set flag, then increment key to clear the input
    st.session_state.pending_message = user_input.strip()
    st.session_state.pending_send = True
    st.session_state.input_key += 1   # ← clears the text box on next render
    st.rerun()