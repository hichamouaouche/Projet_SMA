import streamlit as st
from agents import (
    situational, WorkflowState, config,
    teacher, character, mentality, styler, save_agent,
)
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Language Learning AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ═══════════════════════════════════════════════
   RESET & BASE
═══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
section.main { font-family: 'Inter', sans-serif !important; }

/* ═══════════════════════════════════════════════
   APP BACKGROUND  — deep dark base
═══════════════════════════════════════════════ */
html, body,
[data-testid="stAppViewContainer"] {
    background: #0b0d1a !important;
    min-height: 100vh;
}

[data-testid="stMainBlockContainer"] {
    background: transparent !important;
    padding-top: 0 !important;
}

/* ═══════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12102b 0%, #0d0c1e 100%) !important;
    border-right: 1px solid rgba(120, 80, 220, 0.25) !important;
}

[data-testid="stSidebar"] * { color: #e2e0ff !important; }

[data-testid="stSidebar"] label { color: #a89fd8 !important; font-size: 0.82em !important; }

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(120, 80, 220, 0.4) !important;
    color: #e2e0ff !important;
    border-radius: 10px !important;
}

/* ═══════════════════════════════════════════════
   HEADER
═══════════════════════════════════════════════ */
.app-header {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 55%, #a21caf 100%);
    padding: 42px 32px 36px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-radius: 0 0 24px 24px;
    margin-bottom: 30px;
    box-shadow: 0 8px 40px rgba(124, 58, 237, 0.45);
}

.app-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 20% 50%, rgba(255,255,255,0.12) 0%, transparent 55%),
        radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 45%);
    pointer-events: none;
}

.app-header::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
}

.header-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.25);
    color: rgba(255,255,255,0.9);
    font-size: 0.72em;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 14px;
}

.header-title {
    font-size: 2.4em;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.8px;
    line-height: 1.15;
    position: relative;
    z-index: 1;
}

.header-title span {
    background: linear-gradient(90deg, #c4b5fd, #e0e7ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.header-sub {
    margin-top: 8px;
    color: rgba(255,255,255,0.65);
    font-size: 0.92em;
    font-weight: 400;
    position: relative;
    z-index: 1;
}

/* ═══════════════════════════════════════════════
   SCENARIO CARD
═══════════════════════════════════════════════ */
.scenario-card {
    background: linear-gradient(135deg,
        rgba(37, 99, 235, 0.18) 0%,
        rgba(124, 58, 237, 0.14) 100%);
    border: 1px solid rgba(124, 58, 237, 0.35);
    border-left: 4px solid #7c3aed;
    border-radius: 16px;
    padding: 20px 26px;
    margin: 0 auto 28px;
    max-width: 900px;
    backdrop-filter: blur(8px);
    position: relative;
    overflow: hidden;
}

.scenario-card::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(124,58,237,0.15), transparent 70%);
    pointer-events: none;
}

.scenario-label {
    font-size: 0.72em;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.scenario-text {
    color: #ddd6fe;
    font-size: 0.96em;
    line-height: 1.75;
    font-weight: 400;
}

/* ═══════════════════════════════════════════════
   CHAT AREA
═══════════════════════════════════════════════ */
.chat-area {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

/* USER bubble */
.msg-row { display: flex; margin: 8px 0; align-items: flex-end; gap: 10px; }
.msg-row.user  { justify-content: flex-end; }
.msg-row.bot   { justify-content: flex-start; }

.avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1em;
    flex-shrink: 0;
}
.avatar.bot  { background: linear-gradient(135deg,#2563eb,#7c3aed); }
.avatar.user { background: linear-gradient(135deg,#7c3aed,#a21caf); }

.bubble {
    max-width: 66%;
    padding: 13px 18px;
    line-height: 1.65;
    font-size: 0.93em;
    word-wrap: break-word;
    position: relative;
}

.bubble.user {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    color: #ffffff;
    border-radius: 20px 20px 6px 20px;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
}

.bubble.bot {
    background: rgba(255,255,255,0.07);
    color: #e2e0ff;
    border: 1px solid rgba(120, 80, 220, 0.22);
    border-radius: 20px 20px 20px 6px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* ═══════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-size: 0.87em !important;
    font-weight: 600 !important;
    width: 100%;
    letter-spacing: 0.2px;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.55) !important;
    filter: brightness(1.08);
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ═══════════════════════════════════════════════
   CHAT INPUT
═══════════════════════════════════════════════ */
.stChatInput > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(120, 80, 220, 0.35) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(10px);
}

.stChatInput textarea,
.stChatInput input {
    background: transparent !important;
    color: #e2e0ff !important;
    font-size: 0.93em !important;
    caret-color: #a78bfa !important;
}

.stChatInput textarea::placeholder,
.stChatInput input::placeholder {
    color: rgba(167, 139, 250, 0.5) !important;
}

/* ═══════════════════════════════════════════════
   SIDEBAR SECTION LABELS
═══════════════════════════════════════════════ */
.sb-label {
    font-size: 0.72em;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6d5fc7;
    margin: 20px 0 8px;
}

/* ═══════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════ */
.gradient-divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(124, 58, 237, 0.5) 30%,
        rgba(37, 99, 235, 0.5) 70%,
        transparent 100%);
    margin: 20px auto;
    max-width: 900px;
}

/* ═══════════════════════════════════════════════
   SPINNER
═══════════════════════════════════════════════ */
.stSpinner > div { border-top-color: #7c3aed !important; }

/* ═══════════════════════════════════════════════
   NOTIFICATIONS
═══════════════════════════════════════════════ */
[data-testid="stSuccess"] {
    background: rgba(34, 197, 94, 0.1) !important;
    border-left: 3px solid #22c55e !important;
    border-radius: 10px !important;
    color: #bbf7d0 !important;
}

[data-testid="stInfo"] {
    background: rgba(99, 102, 241, 0.1) !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 10px !important;
    color: #c7d2fe !important;
}

/* ═══════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #2563eb, #7c3aed);
    border-radius: 3px;
}

/* ═══════════════════════════════════════════════
   MARKDOWN INSIDE BOT BUBBLE
═══════════════════════════════════════════════ */
.bubble.bot h1, .bubble.bot h2, .bubble.bot h3 {
    color: #c4b5fd !important;
    font-size: 1em !important;
    margin: 8px 0 4px !important;
}
.bubble.bot strong { color: #e0d7ff !important; }
.bubble.bot code {
    background: rgba(255,255,255,0.1);
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.88em;
    color: #c4b5fd;
}

/* ═══════════════════════════════════════════════
   HR override
═══════════════════════════════════════════════ */
hr { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── Streamlit-only Graph ───────────────────────────────────────────────────────
def build_graph():
    def run_character(state: WorkflowState) -> Dict[str, Any]:
        result = character.invoke(state, config)
        return {"character": result["messages"][-1].content}

    def run_teacher(state: WorkflowState) -> Dict[str, Any]:
        result = teacher.invoke(state, config)
        return {"teacher": result["messages"][-1].content}

    def run_mentality(state: WorkflowState) -> Dict[str, Any]:
        result = mentality.invoke(state, config)
        return {"mentality": result["messages"][-1].content}

    def run_styler(state: WorkflowState) -> Dict[str, Any]:
        content = (
            "Format this into clean markdown:\n\n"
            f"**Grammar Correction**: {state.get('teacher', '')}\n\n"
            f"**Character Response**: {state.get('character', '')}\n\n"
            f"**Cultural Note**: {state.get('mentality', '')}"
        )
        styler_state = {
            "messages": [{"role": "user", "content": content}],
            **{k: v for k, v in state.items() if k != "messages"},
        }
        result = styler.invoke(styler_state, config)
        return {"styler": result["messages"][-1].content}

    b = StateGraph(WorkflowState)
    b.add_node("character", run_character)
    b.add_node("teacher",   run_teacher)
    b.add_node("mentality", run_mentality)
    b.add_node("styler",    run_styler)
    b.add_edge(START, "character")
    b.add_edge(START, "teacher")
    b.add_edge("character", "mentality")
    b.add_edge("teacher",   "mentality")
    b.add_edge("mentality", "styler")
    b.add_edge("styler", END)
    return b.compile()


_graph = build_graph()

LANGUAGES = ["French", "Spanish", "German", "Italian", "Arabic"]


# ── Session helpers ────────────────────────────────────────────────────────────
def _blank(language: str = "French") -> WorkflowState:
    return {
        "messages": [], "character": None, "teacher": None, "cultural": None,
        "styler": None, "situational": None, "mentality": None, "prompt": None,
        "history": [], "save_it": False, "language": language,
    }


def _new_situation(language: str) -> str:
    s = _blank(language)
    s["messages"] = [{"role": "user", "content": f"Generate a real conversation situation in {language}."}]
    return situational.invoke(s, config)["messages"][-1].content


if "app" not in st.session_state:
    st.session_state.app = _blank()
    st.session_state.app["situational"] = _new_situation("French")

app = st.session_state.app


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:18px 4px 4px;text-align:center;">
        <div style="font-size:2em;margin-bottom:6px;">🌐</div>
        <div style="font-size:1em;font-weight:700;color:#c4b5fd;letter-spacing:-0.3px;">
            Language AI
        </div>
        <div style="font-size:0.75em;color:#6d5fc7;margin-top:2px;">Multi-Agent System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Language</div>', unsafe_allow_html=True)
    language = st.selectbox(
        "Language",
        LANGUAGES,
        index=LANGUAGES.index(app["language"]),
        label_visibility="collapsed",
    )

    st.markdown('<div class="sb-label">Actions</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        new_btn = st.button("✦ New", use_container_width=True)
    with col2:
        clear_btn = st.button("⊘ Clear", use_container_width=True)

    if new_btn:
        with st.spinner("Generating…"):
            app.update({
                "language": language,
                "history": [],
                "situational": _new_situation(language),
            })
        st.session_state.pop("last_response", None)
        st.rerun()

    if clear_btn:
        app["history"] = []
        st.session_state.pop("last_response", None)
        st.rerun()

    st.markdown('<div class="sb-label">Commands</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.82em;color:#6d5fc7;line-height:1.9;">
        <b style="color:#a78bfa;">new</b> — fresh scenario<br>
        <b style="color:#a78bfa;">quit</b> — clear chat<br>
        <b style="color:#a78bfa;">save</b> button — save session
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-label">Status</div>', unsafe_allow_html=True)
    turns = len([m for m in app["history"] if m["role"] == "user"])
    st.markdown(f"""
    <div style="font-size:0.82em;color:#6d5fc7;line-height:1.9;">
        Language: <b style="color:#a78bfa;">{app['language']}</b><br>
        Turns: <b style="color:#a78bfa;">{turns}</b>
    </div>
    """, unsafe_allow_html=True)

# Handle language switch
if app["language"] != language:
    with st.spinner("Switching language…"):
        app.update({
            "language": language,
            "history": [],
            "situational": _new_situation(language),
        })
    st.session_state.pop("last_response", None)
    st.rerun()


# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="header-badge">AI · Multi-Agent · LangGraph</div>
    <h1 class="header-title">Language Learning <span>AI</span></h1>
    <p class="header-sub">Practice real conversations — corrected by intelligent agents</p>
</div>
""", unsafe_allow_html=True)


# ── SCENARIO CARD ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="scenario-card">
    <div class="scenario-label">
        <span>📍</span> Active Scenario — {app['language']}
    </div>
    <div class="scenario-text">{app['situational']}</div>
</div>
""", unsafe_allow_html=True)


# ── CHAT HISTORY ───────────────────────────────────────────────────────────────
st.markdown('<div class="chat-area">', unsafe_allow_html=True)

for msg in app["history"]:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-row user">
            <div class="bubble user">{msg['content']}</div>
            <div class="avatar user">👤</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row bot">
            <div class="avatar bot">🤖</div>
            <div class="bubble bot">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)


# ── CHAT INPUT ─────────────────────────────────────────────────────────────────
user_input = st.chat_input(f"Write in {app['language']}…", key="chat_input")

if user_input:
    text = user_input.strip()

    if text.lower() == "quit":
        app["history"] = []
        st.session_state.pop("last_response", None)
        st.rerun()

    elif text.lower() == "new":
        with st.spinner("Generating new scenario…"):
            app.update({
                "history": [],
                "situational": _new_situation(app["language"]),
            })
        st.session_state.pop("last_response", None)
        st.rerun()

    else:
        # Show user message immediately
        st.markdown(f"""
        <div class="msg-row user" style="max-width:900px;margin:8px auto;">
            <div class="bubble user">{text}</div>
            <div class="avatar user">👤</div>
        </div>
        """, unsafe_allow_html=True)

        workflow_state: WorkflowState = {
            "messages": [{"role": "user", "content": f"Situation: {app['situational']}\n\nUser: {text}"}],
            "character": None, "teacher": None, "cultural": None, "styler": None,
            "situational": app["situational"], "mentality": None, "prompt": text,
            "history": app["history"] + [{"role": "user", "content": text}],
            "save_it": False, "language": app["language"],
        }

        with st.spinner("Agents processing…"):
            result = _graph.invoke(workflow_state)

        for key in result:
            if key in app:
                app[key] = result[key]

        if result.get("styler"):
            app["history"].append({"role": "assistant", "content": result["styler"]})
            st.session_state.last_response = result["styler"]
            st.rerun()


# ── SAVE BUTTON ────────────────────────────────────────────────────────────────
if "last_response" in st.session_state:
    col1, _, _ = st.columns([1, 1, 2])
    with col1:
        if st.button("💾  Save Response", use_container_width=True):
            save_agent(app)
            st.success("Session saved.")
            st.session_state.pop("last_response", None)
            st.rerun()
