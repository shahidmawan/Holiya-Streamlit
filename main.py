import streamlit as st
import requests
import uuid
import re

# -----------------------------
# PASSWORD PROTECTION
# -----------------------------
PASSWORD = "holiyaAI572"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Access Required")
    password_input = st.text_input("Enter password", type="password")
    if password_input == PASSWORD:
        st.session_state.authenticated = True
        st.success("Access granted ✅")
        st.rerun()
    elif password_input:
        st.error("Incorrect password ❌")
    st.stop()

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "https://holiya-be.holiya.co.uk/api/chatbot"
USER_ID = 35

st.set_page_config(
    page_title="Holiya Medical AI Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# HOLIYA THEME (TEXT COLOR FOCUSED)
# -----------------------------
st.markdown("""
<style>

/* ---------- APP BACKGROUND ---------- */
.main, .stApp {
    background-color: #F7F3EF;     /* warm beige */
    color: #5F5A54;                /* default body text */
    font-family: 'Inter', sans-serif;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background-color: #EFE9E4;
    color: #3E3A37;
}

/* ---------- USER MESSAGE ---------- */
.user-message {
    background-color: #E7EFEA;
    padding: 16px 20px;
    border-radius: 18px;
    margin: 14px 0;
    border-left: 5px solid #8A9A5B;
    color: #D1AB88;
}

/* ---------- AI MESSAGE ---------- */
.ai-message {
    background-color: #FFFFFF;
    padding: 22px;
    border-radius: 18px;
    margin: 14px 0;
    border-left: 5px solid #8A9A5B;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    color: #AE7C49;
}

/* ---------- TEXT HIERARCHY ---------- */
.ai-message h1 {
    color: #3B3A36;                /* strong heading */
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 14px;
}

.ai-message h2 {
    color: #4A4A45;
    font-weight: 700;
}

.ai-message h3 {
    color: #4A4A45;
    font-weight: 600;
}

.ai-message p {
    color: #5F5A54;                /* soft paragraph */
    font-size: 16px;
    line-height: 1.75;
}

.ai-message ul,
.ai-message ol {
    padding-left: 20px;
}

.ai-message li {
    color: #5F5A54;
    line-height: 1.7;
}

/* Emphasis */
.ai-message strong {
    color: #2F2E2B;
}

/* ---------- OPTIONAL BLOCKS ---------- */
.block-info {
    background-color: #EEF3F6;
    border-left: 4px solid #A3B6C4;
    color: #5F5A54;
}

.block-success {
    background-color: #E4EFE6;
    border-left: 4px solid #8A9A5B;
    color: #5F5A54;
}

.block-warning {
    background-color: #F8EEE6;
    border-left: 4px solid #C8A27A;
    color: #5F5A54;
}

.block-danger {
    background-color: #F6E6E6;
    border-left: 4px solid #C28B8B;
    color: #5F5A54;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# MARKDOWN → HTML (UNCHANGED)
# -----------------------------
def is_html(text):
    return bool(re.search(r'<[^>]+>', text))

def markdown_to_html(text):
    if not text:
        return ""

    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Bold & italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # Line breaks
    return text.replace("\n", "<br>")

def render_message(text):
    return text if is_html(text) else markdown_to_html(text)

# -----------------------------
# API FUNCTIONS
# -----------------------------
def get_sessions():
    try:
        return requests.get(
            f"{BASE_URL}/get-sessions?user_id={USER_ID}"
        ).json().get("data", [])
    except:
        return []

def get_messages(chat_session_id):
    try:
        return requests.get(
            f"{BASE_URL}/get-messages?chat_session_id={chat_session_id}"
        ).json().get("data", [])
    except:
        return []

def send_message(session_id, user_message):
    payload = {
        "user_id": USER_ID,
        "session_id": session_id,
        "user_message": user_message
    }
    try:
        r = requests.post(f"{BASE_URL}/ai-agent", json=payload)
        return r.json()["data"]["ai_response"]
    except:
        return "⚠️ Unable to reach AI service."

# -----------------------------
# SESSION STATE
# -----------------------------
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("💬 Holiya Medical AI")

if st.sidebar.button("➕ Start New Session"):
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

for s in get_sessions():
    if st.sidebar.button(f"Session {s['chat_session_id']}"):
        st.session_state.current_session_id = s["session_id"]
        st.session_state.messages = get_messages(s["chat_session_id"])
        st.rerun()

# -----------------------------
# MAIN CHAT
# -----------------------------
st.title("🩺 Holiya Medical AI Agent")

if not st.session_state.current_session_id:
    st.info("Create or select a chat session.")
    st.stop()

st.caption(f"Session ID: `{st.session_state.current_session_id}`")
st.divider()

for msg in st.session_state.messages:
    st.markdown(
        f"<div class='user-message'><strong>You:</strong> {msg['user_message']}</div>",
        unsafe_allow_html=True
    )

    ai_html = render_message(msg["ai_response"])
    st.markdown(
        f"<div class='ai-message'><strong>Holiya AI:</strong><br>{ai_html}</div>",
        unsafe_allow_html=True
    )

st.divider()

# -----------------------------
# INPUT
# -----------------------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message")
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    with st.spinner("Holiya is thinking..."):
        ai_response = send_message(
            st.session_state.current_session_id,
            user_input
        )
        st.session_state.messages.append({
            "user_message": user_input,
            "ai_response": ai_response
        })
        st.rerun()