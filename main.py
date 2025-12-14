import streamlit as st
import requests
import uuid

# -----------------------------
# CONFIG & CONSTANTS
# -----------------------------
BASE_URL = "http://13.61.194.44/api/chatbot"
USER_ID = 35

st.set_page_config(
    page_title="Holiya Medical AI Agent",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# STYLES (Theme)
# -----------------------------
st.markdown("""
<style>
/* Main Chat Bubbles */
.user-msg {
    background-color: #DCF8C6;
    padding: 10px 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    width: fit-content;
}
.ai-msg {
    background-color: #E8E8E8;
    padding: 10px 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    width: fit-content;
}

/* Sidebar Session List */
.sidebar-session {
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 6px;
    cursor: pointer;
}
.sidebar-session:hover {
    background-color: #e5e5e5;
}
.active-session {
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------------

def get_sessions():
    """Fetch sessions for the user."""
    try:
        url = f"{BASE_URL}/get-sessions?user_id={USER_ID}"
        response = requests.get(url)
        return response.json().get("data", [])
    except:
        return []


def get_messages(chat_session_id):
    """Fetch full conversation history for a session."""
    try:
        url = f"{BASE_URL}/get-messages?chat_session_id={chat_session_id}"
        resp = requests.get(url).json()
        return resp.get("data", [])
    except:
        return []


def send_message(session_id, user_message):
    """Send message to AI and return its response."""
    payload = {
        "user_id": USER_ID,
        "session_id": session_id,
        "user_message": user_message
    }

    url = f"{BASE_URL}/ai-agent"
    r = requests.post(url, json=payload)

    try:
        return r.json()["data"]["ai_response"]
    except:
        return "⚠️ Error contacting AI agent."


# ---------------------------------------------------------
# INITIALIZE SESSION STATE
# ---------------------------------------------------------
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "current_chat_session_record" not in st.session_state:
    st.session_state.current_chat_session_record = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("💬 Holiya Medical AI Agent")
st.sidebar.subheader("Sessions")

sessions = get_sessions()

# --- NEW SESSION BUTTON ---
if st.sidebar.button("➕ Start New Session"):
    new_session_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_session_id
    st.session_state.current_chat_session_record = None  # no DB session id yet
    st.session_state.messages = []
    st.rerun()

# --- SHOW SESSION LIST ---
for s in sessions:
    db_session_id = s["chat_session_id"]
    session_id_val = s["session_id"]

    button_label = f"Session {db_session_id} — {session_id_val[:10]}..."

    if st.sidebar.button(button_label, key=db_session_id):
        st.session_state.current_session_id = session_id_val
        st.session_state.current_chat_session_record = db_session_id
        st.session_state.messages = get_messages(db_session_id)
        st.rerun()


# ---------------------------------------------------------
# MAIN CHAT UI
# ---------------------------------------------------------

st.title("🩺 Holiya Medical AI Agent")

if not st.session_state.current_session_id:
    st.info("Start by creating or selecting a session from the left.")
    st.stop()


# -------------------------
# DISPLAY MESSAGES
# -------------------------
st.subheader(f"Session: `{st.session_state.current_session_id}`")

for msg in st.session_state.messages:
    user_msg = msg["user_message"]
    ai_msg = msg.get("ai_response", "")

    st.markdown(f"<div class='user-msg'><strong>You:</strong> {user_msg}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai-msg'><strong>AI:</strong> {ai_msg}</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# MESSAGE INPUT (using st.text_input for Enter to trigger)
# -------------------------
user_input = st.text_input("Write your message:")

if user_input.strip():
    # Send the message when Enter is pressed
    ai_response = send_message(st.session_state.current_session_id, user_input)

    # Append user message and AI response to the chat history
    st.session_state.messages.append({
        "user_message": user_input,
        "ai_response": ai_response
    })
    st.rerun()
