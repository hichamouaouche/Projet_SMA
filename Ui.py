import streamlit as st
from agents import situational, WorkflowState, config, teacher, character, mentality, styler, save_agent
from langgraph.graph import StateGraph, START, END
from typing import Dict, Any
from datetime import datetime

# ===== PAGE CONFIGURATION =====
st.set_page_config(
    page_title="Language Learning AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS FOR PROFESSIONAL STYLING =====
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --text-dark: #1a202c;
        --text-light: #ffffff;
        --bg-light: #f5f7fa;
        --bg-white: #ffffff;
        --border-color: #e5e7eb;
    }
    
    /* Light Mode */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
        min-height: 100vh;
    }
    
    [data-testid="stMainBlockContainer"] {
        background: transparent;
        padding: 0 !important;
    }
    
    [data-testid="stVerticalBlockBelowGap"] {
        gap: 0 !important;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
        }
        
        .main {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2d2d44 0%, #1f1f2e 100%) !important;
        }
        
        .sidebar-title {
            color: #e5e7eb !important;
        }
        
        .situation-box {
            background: rgba(102, 126, 234, 0.15) !important;
            border: 1.5px solid rgba(102, 126, 234, 0.5) !important;
            color: #e5e7eb !important;
        }
        
        .assistant-bubble {
            background: #2d2d44 !important;
            color: #e5e7eb !important;
            border: 1px solid rgba(102, 126, 234, 0.3) !important;
        }
        
        .stChatInput input {
            background: #2d2d44 !important;
            color: #e5e7eb !important;
            border: 1.5px solid rgba(102, 126, 234, 0.3) !important;
        }
        
        .stChatInput input::placeholder {
            color: #9ca3af !important;
        }
        
        [data-testid="stSelectbox"] {
            color: #e5e7eb;
        }
        
        [data-testid="stSelectbox"] > div > div {
            background: #2d2d44 !important;
            border: 1.5px solid rgba(102, 126, 234, 0.3) !important;
            color: #e5e7eb !important;
        }
        
        [data-testid="stCaption"] {
            color: #cbd5e1 !important;
        }
        
        label {
            color: #cbd5e1 !important;
        }
        
        p, span {
            color: #e5e7eb !important;
        }
    }
    
    /* Light Mode Specific */
    @media (prefers-color-scheme: light) {
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #ffffff 0%, #f8f9fb 100%);
            box-shadow: 2px 0 15px rgba(0,0,0,0.08);
        }
        
        .sidebar-title {
            color: #1a202c;
        }
        
        .situation-box {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            color: #1a202c;
            border: 1.5px solid #667eea30;
        }
        
        .assistant-bubble {
            background: white;
            color: #1a202c;
            border: 1px solid #e5e7eb;
        }
        
        .stChatInput input {
            background: white !important;
            color: #1a202c !important;
            border: 1.5px solid #e5e7eb !important;
        }
        
        [data-testid="stSelectbox"] > div > div {
            background: white !important;
            border: 1.5px solid #e5e7eb !important;
            color: #1a202c !important;
        }
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        box-shadow: 2px 0 15px rgba(0,0,0,0.08);
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBelowGap"] {
        background: transparent;
    }
    
    .sidebar-title {
        font-size: 0.85em;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 24px;
        margin-bottom: 12px;
        opacity: 0.9;
    }
    
    /* Header */
    .header-container {
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .header-title {
        font-size: 2.2em;
        font-weight: 800;
        color: white;
        margin: 0;
        position: relative;
        z-index: 1;
        letter-spacing: -0.5px;
    }
    
    /* Situation Box */
    .situation-box {
        padding: 20px 24px;
        border-radius: 14px;
        margin: 24px auto;
        line-height: 1.7;
        max-width: 900px;
        font-size: 0.95em;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.08);
    }
    
    .situation-icon {
        display: inline-block;
        margin-right: 8px;
        font-size: 1.2em;
    }
    
    /* Chat Container */
    .chat-wrapper {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        background: transparent;
    }
    
    /* Messages */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin: 12px 0;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 70%;
        word-wrap: break-word;
        line-height: 1.5;
        font-size: 0.95em;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
        position: relative;
    }
    
    .user-bubble::after {
        content: '';
        position: absolute;
        bottom: -2px;
        right: 0;
        width: 20px;
        height: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        opacity: 0.3;
    }
    
    .assistant-message {
        display: flex;
        justify-content: flex-start;
        margin: 12px 0;
        animation: slideIn 0.3s ease-out;
    }
    
    .assistant-bubble {
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 70%;
        word-wrap: break-word;
        line-height: 1.6;
        font-size: 0.95em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        position: relative;
    }
    
    .assistant-bubble::before {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        opacity: 0.3;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 0.9em;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        letter-spacing: 0.3px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    /* Selectbox */
    .stSelectbox {
        margin-bottom: 16px;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
        border: 1.5px solid var(--border-color);
    }
    
    /* Input Area */
    .stChatInput {
        border-radius: 12px !important;
        border: 1.5px solid var(--border-color) !important;
    }
    
    .stChatInput input {
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 0.95em;
    }
    
    .stChatInput input::placeholder {
        color: #9ca3af !important;
    }
    
    /* Divider */
    hr {
        border: none;
        border-top: 1px solid rgba(0,0,0,0.05);
        margin: 20px 0;
    }
    
    /* Success/Info Messages */
    [data-testid="stSuccess"] {
        background: linear-gradient(135deg, rgba(34,197,94,0.1) 0%, rgba(34,197,94,0.05) 100%);
        border-left: 3px solid #22c55e;
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    [data-testid="stInfo"] {
        background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(59,130,246,0.05) 100%);
        border-left: 3px solid #3b82f6;
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Spinner */
    .stSpinner {
        text-align: center;
        padding: 20px;
    }
    
    /* Main Content */
    .main-content {
        background: transparent;
        padding: 20px;
    }
    
    /* Text visibility in both modes */
    [data-testid="stCaption"] {
        font-weight: 500;
        line-height: 1.6;
    }
    
    label {
        font-weight: 500;
    }
    
    /* Theme selector buttons - Light mode */
    @media (prefers-color-scheme: light) {
        button[kind="secondary"] {
            background-color: #d1d5db !important;
            color: #000000 !important;
            border: 1.5px solid #9ca3af !important;
            font-weight: 600 !important;
        }
        
        button[kind="secondary"]:hover {
            background-color: #9ca3af !important;
            color: #ffffff !important;
            border: 1.5px solid #6b7280 !important;
        }
        
        [data-testid="stToolbarActions"] button {
            color: #1a202c !important;
        }
    }
    
    /* Theme selector buttons - Dark mode */
    @media (prefers-color-scheme: dark) {
        button[kind="secondary"] {
            background-color: #4b5563 !important;
            color: #e5e7eb !important;
            border: 1.5px solid #6b7280 !important;
            font-weight: 600 !important;
        }
        
        button[kind="secondary"]:hover {
            background-color: #6b7280 !important;
            color: #ffffff !important;
            border: 1.5px solid #9ca3af !important;
        }
        
        [data-testid="stToolbarActions"] button {
            color: #e5e7eb !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===== STREAMLIT-SPECIFIC WORKFLOW GRAPH =====
def build_streamlit_graph():
    builder = StateGraph(WorkflowState)

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
        styler_state = {
            "messages": [{
                "role": "user",
                "content": f"Format this into clean markdown:\n\n**Grammar Correction**: {state.get('teacher', '')}\n\n**Character Response**: {state.get('character', '')}\n\n**Cultural Check**: {state.get('mentality', '')}"
            }],
            **{k: v for k, v in state.items() if k != "messages"}
        }
        result = styler.invoke(styler_state, config)
        return {"styler": result["messages"][-1].content}

    builder.add_node("character", run_character)
    builder.add_node("teacher", run_teacher)
    builder.add_node("mentality", run_mentality)
    builder.add_node("styler", run_styler)

    builder.add_edge(START, "character")
    builder.add_edge(START, "teacher")
    builder.add_edge("character", "mentality")
    builder.add_edge("teacher", "mentality")
    builder.add_edge("mentality", "styler")
    builder.add_edge("styler", END)

    return builder.compile()

streamlit_graph = build_streamlit_graph()

# ===== SESSION STATE INITIALIZATION =====
if 'state' not in st.session_state:
    st.session_state.state = {
        "messages": [], "character": None, "teacher": None, "cultural": None,
        "styler": None, "situational": None, "mentality": None, "prompt": None,
        "history": [], "save_it": False, "language": "French"
    }
    state = {
        "messages": [{"role": "user", "content": "Generate a real situation in French for conversation practice."}],
        **{k: v for k, v in st.session_state.state.items() if k != "messages"}
    }
    result = situational.invoke(state, config)
    st.session_state.state["situational"] = result["messages"][-1].content

# ===== HELPER FUNCTIONS =====
def generate_new_situation(language):
    st.session_state.state.update({
        "language": language,
        "history": [],
        "messages": [{"role": "user", "content": f"Generate a new situation in {language}."}]
    })
    result = situational.invoke(st.session_state.state, config)
    st.session_state.state["situational"] = result["messages"][-1].content

def clear_chat():
    st.session_state.state["history"] = []
    if "last_response" in st.session_state:
        del st.session_state.last_response

# ===== UI =====
# Header with branding
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🌍 Language Learning AI</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar with professional styling
with st.sidebar:
    st.markdown('<p class="sidebar-title">⚙️ Settings</p>', unsafe_allow_html=True)
    
    language = st.selectbox(
        "Language",
        ["French", "Spanish", "German", "Italian", "Arabic"],
        index=["French", "Spanish", "German", "Italian", "Arabic"].index(st.session_state.state["language"]),
        key="lang_select"
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Situation", use_container_width=True):
            generate_new_situation(language)
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_chat()
            st.rerun()
    
    st.markdown("---")
    st.markdown('<p class="sidebar-title">📝 Instructions</p>', unsafe_allow_html=True)
    st.caption("""
    • Type **new** to generate a new scenario
    • Type **quit** to clear conversation
    • Your responses are corrected by AI agents
    """)

# Handle language change
if st.session_state.state["language"] != language:
    generate_new_situation(language)
    st.rerun()

# Main content wrapper
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Situation display
st.markdown(f"""
<div class="situation-box">
    <span class="situation-icon">📌</span><strong>Situation:</strong><br><br>
    {st.session_state.state['situational']}
</div>
""", unsafe_allow_html=True)

# Chat history - improved rendering
if st.session_state.state["history"]:
    for msg in st.session_state.state["history"]:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="user-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="assistant-bubble">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)

# User input
st.markdown("---")

user_input = st.chat_input("Type your message...", key="user_input")

if user_input:
    if user_input.lower() == "quit":
        clear_chat()
        st.rerun()
    elif user_input.lower() == "new":
        generate_new_situation(language)
        st.rerun()
    else:
        # Show user message immediately
        st.markdown(f"""
        <div class="user-message">
            <div class="user-bubble">{user_input}</div>
        </div>
        """, unsafe_allow_html=True)
        
        workflow_state = {
            "messages": [{"role": "user", "content": f"Situation: {st.session_state.state['situational']}\n\nUser: {user_input}"}],
            "character": None, "teacher": None, "cultural": None, "styler": None,
            "situational": st.session_state.state["situational"],
            "mentality": None, "prompt": user_input,
            "history": st.session_state.state["history"] + [{"role": "user", "content": user_input}],
            "save_it": False,
            "language": st.session_state.state["language"]
        }

        with st.spinner("⏳ Processing your message..."):
            result = streamlit_graph.invoke(workflow_state)
            for key in result:
                if key in st.session_state.state:
                    st.session_state.state[key] = result[key]

        if "styler" in result and result["styler"]:
            st.session_state.state["history"].append({
                "role": "assistant",
                "content": result["styler"]
            })

            st.session_state.last_response = result["styler"]
            st.rerun()

# Save button section
if "last_response" in st.session_state:
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save Response", use_container_width=True):
            save_agent(st.session_state.state)
            st.success("✅ Response saved successfully!")
            if "last_response" in st.session_state:
                del st.session_state.last_response
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

