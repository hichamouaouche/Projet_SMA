import os
import re
import time
from typing import Dict, Any, List, Optional, TypedDict

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from rank_bm25 import BM25Okapi
from tavily import TavilyClient

load_dotenv()

# ── Environment ────────────────────────────────────────────────────────────────

model_name     = os.getenv("modelName")
tavily_api_key = os.getenv("tavilyApiKey")
ollama_api_key = os.getenv("Ollama_api_key")

if not model_name:
    raise ValueError("Missing environment variable: modelName")
if not tavily_api_key:
    raise ValueError("Missing environment variable: tavilyApiKey")

# ── LLM & Search client ────────────────────────────────────────────────────────

model = ChatOllama(
    model=model_name,
    base_url="https://ollama.com",
    client_kwargs={"headers": {"Authorization": f"Bearer {ollama_api_key}"}},
)

tavily_client = TavilyClient(api_key=tavily_api_key)

# ── State ──────────────────────────────────────────────────────────────────────

class WorkflowState(TypedDict):
    messages:    List
    character:   Optional[str]
    teacher:     Optional[str]
    cultural:    Optional[str]
    styler:      Optional[str]
    situational: Optional[str]
    mentality:   Optional[str]
    prompt:      Optional[str]
    history:     List
    save_it:     bool
    language:    Optional[str]
    level:       Optional[str]
    domain:      Optional[str]

# ── Tools ──────────────────────────────────────────────────────────────────────

@tool(description="Search the web for language, cultural, or conversation information.")
def web_search(query: str) -> Dict[str, Any]:
    return tavily_client.search(query)


# ── RAG (BM25 over Grammar PDF) ────────────────────────────────────────────────

_pdf_path   = "./files/Grammer.pdf"
_documents  = PyPDFLoader(_pdf_path).load()

_chunks: List[str] = []
for _doc in _documents:
    for _chunk in re.split(r'\n\s*\n|(?<=[.!?])\s+', _doc.page_content):
        if len(_chunk.strip()) > 50:
            _chunks.append(_chunk.strip())

_bm25 = BM25Okapi([c.lower().split() for c in _chunks])


def _bm25_search(query: str, top_k: int = 3) -> str:
    scores = _bm25.get_scores(query.lower().split())
    top    = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return "\n\n".join([_chunks[i] for i in top])


@tool
def pdf_search(query: str) -> str:
    """Search the grammar knowledge base (PDF) for relevant grammar rules."""
    return _bm25_search(query)


# ── Level-based system prompts ─────────────────────────────────────────────────

_PROMPTS = {
    "beginner": {
        "teacher": (
            "You are a patient grammar teacher for beginners. "
            "Correct only the single most important error. Use very simple language. "
            "Respond in 10-15 words maximum."
        ),
        "character": (
            "Respond simply as a friendly, slow-speaking human. "
            "Use basic vocabulary only. 10 words max."
        ),
        "situational": (
            "Generate a very simple everyday conversation scenario for a beginner language learner. "
            "Under 25 words."
        ),
        "mentality": (
            "Note only a major cultural issue if present. Respond in under 10 words."
        ),
    },
    "intermediate": {
        "teacher": (
            "You are a grammar teacher. Correct the user's input only if there is a clear grammatical error. "
            "Do not correct style or phrasing unless the grammar is incorrect. "
            "Respond in 10 to 15 words maximum."
        ),
        "character": (
            "Respond naturally as a human being. Express a realistic emotion "
            "(happy, annoyed, in a hurry, surprised, etc.). "
            "Always respond in 10 words or fewer."
        ),
        "situational": (
            "Generate a realistic, immersive conversation scenario written from the user's point of view. "
            "Include: a specific location, a time of day, and a clear reason to start a conversation. "
            "Keep it under 35 words."
        ),
        "mentality": (
            "Check whether the user's input is culturally appropriate for the target language and culture. "
            "Flag only clear and significant cultural issues. "
            "Respond in 10 words or fewer."
        ),
    },
    "advanced": {
        "teacher": (
            "You are an advanced grammar coach. Identify subtle grammatical errors, unnatural phrasing, "
            "or register problems. Cite the specific rule that was violated. "
            "Respond in 15-20 words."
        ),
        "character": (
            "Respond as a native speaker with natural idioms and cultural references. "
            "Express a nuanced emotion with subtext. 15 words max."
        ),
        "situational": (
            "Generate a complex, culturally rich conversation scenario with clear social stakes. "
            "Include context, time pressure, and a subtle communication challenge. Under 40 words."
        ),
        "mentality": (
            "Analyse cultural appropriateness in depth. Highlight subtle issues of register, "
            "tone, or cultural expectation. Respond in 10-15 words."
        ),
    },
}

_STYLER_PROMPT = (
    "You are a formatting expert. Combine the following inputs into one clean markdown response.\n\n"
    "- **Grammar Correction**: {teacher}\n"
    "- **Character Response**: {character}\n"
    "- **Cultural Note**: {mentality}\n\n"
    "Use markdown headers. Keep all content unchanged."
)

# ── Agent factory (cached per level) ──────────────────────────────────────────

_cache: Dict[str, Dict] = {}


def get_agents(level: str = "intermediate") -> Dict:
    if level not in _cache:
        p = _PROMPTS.get(level, _PROMPTS["intermediate"])
        _cache[level] = {
            "character":   create_react_agent(model=model, tools=[web_search],  checkpointer=InMemorySaver(), prompt=p["character"]),
            "teacher":     create_react_agent(model=model, tools=[pdf_search],  checkpointer=InMemorySaver(), prompt=p["teacher"]),
            "mentality":   create_react_agent(model=model, tools=[web_search],  checkpointer=InMemorySaver(), prompt=p["mentality"]),
            "styler":      create_react_agent(model=model, tools=[web_search],  checkpointer=InMemorySaver(), prompt=_STYLER_PROMPT),
            "situational": create_react_agent(model=model, tools=[web_search],  checkpointer=InMemorySaver(), prompt=p["situational"]),
        }
    return _cache[level]


# ── Fast situation (direct LLM call, no ReAct overhead) ───────────────────────

def generate_situation_fast(language: str, level: str, domain_ctx: str = "") -> str:
    p       = _PROMPTS.get(level, _PROMPTS["intermediate"])
    content = f"Generate a realistic conversation scenario in {language}."
    if domain_ctx:
        content += f" {domain_ctx}"
    result = model.invoke([
        {"role": "system", "content": p["situational"]},
        {"role": "user",   "content": content},
    ])
    return result.content


# ── Default agents (backward-compat with workflows.py) ─────────────────────────

config       = {"configurable": {"thread_id": "1"}}
_defaults    = get_agents("intermediate")
character    = _defaults["character"]
teacher      = _defaults["teacher"]
mentality    = _defaults["mentality"]
styler       = _defaults["styler"]
situational  = _defaults["situational"]


# ── Save agent ─────────────────────────────────────────────────────────────────

def save_agent(state: WorkflowState) -> WorkflowState:
    os.makedirs("files", exist_ok=True)
    filename = f"files/saved_corrections_{int(time.time())}.txt"
    content  = (
        f"Language : {state.get('language', 'N/A')}\n"
        f"Level    : {state.get('level', 'N/A')}\n\n"
        f"=== Situation ===\n{state.get('situational', 'N/A')}\n\n"
        f"=== User Input ===\n{state.get('prompt', 'N/A')}\n\n"
        f"=== Grammar Correction ===\n{state.get('teacher', 'N/A')}\n\n"
        f"=== Full Response ===\n{state.get('styler', 'N/A')}\n"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return state
