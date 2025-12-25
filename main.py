import streamlit as st
import requests
import uuid

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://13.61.194.44/api/chatbot"
USER_ID = 35

st.set_page_config(
    page_title="Holiya Medical AI Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# STYLES
# -----------------------------
st.markdown("""
<style>
.user-msg {
    background-color: #DCF8C6;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    max-width: 70%;
}
.ai-msg {
    background-color: #F1F1F1;
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 12px;
    max-width: 70%;
}
.chat-container {
    display: flex;
    flex-direction: column;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# API FUNCTIONS
# -----------------------------
def get_sessions():
    try:
        url = f"{BASE_URL}/get-sessions?user_id={USER_ID}"
        return requests.get(url).json().get("data", [])
    except Exception:
        return []


def get_messages(chat_session_id):
    try:
        url = f"{BASE_URL}/get-messages?chat_session_id={chat_session_id}"
        return requests.get(url).json().get("data", [])
    except Exception:
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
    except Exception:
        return "⚠️ Unable to reach AI service."

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "current_chat_db_id" not in st.session_state:
    st.session_state.current_chat_db_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("💬 Holiya Medical AI")
st.sidebar.subheader("Chat Sessions")

# Start New Session
if st.sidebar.button("➕ Start New Session"):
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.current_chat_db_id = None
    st.session_state.messages = []
    st.rerun()

# Existing Sessions
sessions = get_sessions()

for s in sessions:
    db_id = s["chat_session_id"]
    session_uuid = s["session_id"]

    label = f"Session {db_id} — {session_uuid[:8]}"

    if st.sidebar.button(label, key=db_id):
        st.session_state.current_session_id = session_uuid
        st.session_state.current_chat_db_id = db_id
        st.session_state.messages = get_messages(db_id)
        st.rerun()

# -----------------------------
# MAIN CHAT
# -----------------------------
st.title("🩺 Holiya Medical AI Agent")

if not st.session_state.current_session_id:
    st.info("Create or select a chat session from the sidebar.")
    st.stop()

st.caption(f"Session ID: `{st.session_state.current_session_id}`")

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Display Messages
for msg in st.session_state.messages:
    st.markdown(
        f"<div class='user-msg'><b>You:</b> {msg['user_message']}</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div class='ai-msg'><b>Holiya AI:</b> {msg.get('ai_response', '')}</div>",
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# -----------------------------
# MESSAGE INPUT (SAFE)
# -----------------------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Write your message")
    send_btn = st.form_submit_button("Send")

if send_btn and user_input.strip():
    # Optional: show spinner for better UX
    with st.spinner("Holiya Agent is thinking..."):
        ai_response = send_message(
            st.session_state.current_session_id,
            user_input
        )

    st.session_state.messages.append({
        "user_message": user_input,
        "ai_response": ai_response
    })

    st.rerun()
