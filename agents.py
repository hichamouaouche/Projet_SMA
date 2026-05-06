import os

from langchain_ollama import ChatOllama
from tavily import TavilyClient
from typing import Dict, Any, List, TypedDict, Optional
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()

model_name = os.getenv("modelName")
tavily_api_key = os.getenv("tavilyApiKey")

if not model_name:
    raise ValueError("Missing environment variable: modelName")
if not tavily_api_key:
    raise ValueError("Missing environment variable: tavilyApiKey")

# Fixed Ollama config (local instance by default)
model = ChatOllama(
    model=os.getenv("modelName"),
    base_url="https://ollama.com",
    client_kwargs={
        "headers": {
            "Authorization": f"Bearer {os.getenv("Ollama_api_key")}"
        }
    },
)

tavily_client = TavilyClient(api_key=tavily_api_key)

@tool(description="Cherche des recettes, techniques ou associations d'ingrédients ")
def web_search(query: str) -> Dict[str, Any]:
    return tavily_client.search(query)

class WorkflowState(TypedDict):
    messages: List
    character: Optional[str]
    teacher: Optional[str]
    cultural: Optional[str]
    styler: Optional[str]
    situational: Optional[str]
    mentality: Optional[str]
    prompt: Optional[str]
    history: List
    save_it: bool
    language: Optional[str]

def save_agent(state: WorkflowState) -> WorkflowState:
    import time
    filename = f"files/saved_corrections_{int(time.time())}.txt"
    content = f"""Language: {state.get('language', 'N/A')}

=== Teacher Corrections ===
{state.get('teacher', 'N/A')}

=== Original Prompt ===
{state.get('prompt', 'N/A')}

=== Situation ===
{state.get('situational', 'N/A')}
"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ Saved to {filename}")
    return state

teacher_system_prompt = """
correct the input and give the grammer correction just if needed and nesseccery bias to not correct if it is acceptble  , not synthaxe correction !
responde just in 10~15 word ;
"""

character_system_prompt = """
respond as humen and imagine and take some feeling [happy ,angry , hurry etc ]
IMPORTANT: Always respond in 10 words or less .
"""

styler_system_prompt = """
You are a formatting expert. Take the following three inputs and combine them into one clean markdown output:

- **Grammar Correction**: {teacher}
- **Character Response**: {character}
- **Cultural Check**: {mentality}

Format nicely with markdown headers and keep content unchanged.
"""

mentality_system_prompt = """
check the  input safe culteraly in this language ; just a cristal clear problems and so on 
respond in 10 word adivse if needed or no problem 
"""

situational_system_prompt = """
give a introduction of a real situaton of humen from its view and real things and creative like 
place : mesume 
time:morning / night
situation : you are walking down the street see night lighs meet me wearing bla bla and you want to open or ask for something
the situation in just 30 words
"""

checkpointer = InMemorySaver()


character = create_react_agent(
    model=model,
    tools=[web_search],
    checkpointer=checkpointer,
    prompt=character_system_prompt
)
styler = create_react_agent(
    model=model,
    tools=[web_search],
    checkpointer=checkpointer,
    prompt=styler_system_prompt
)
situational = create_react_agent(
    model=model,
    tools=[web_search],
    checkpointer=checkpointer,
    prompt=situational_system_prompt
)
mentality = create_react_agent(
    model=model,
    tools=[web_search],
    checkpointer=checkpointer,
    prompt=mentality_system_prompt
)

config = {"configurable": {"thread_id": "1"}}


from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from rank_bm25 import BM25Okapi
import re

pdf_path = "./files/Grammer.pdf"
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# Simple text splitting by paragraphs/sentences
text_chunks = []
for doc in documents:
    chunks = re.split(r'\n\s*\n|(?<=[.!?])\s+', doc.page_content)
    text_chunks.extend([chunk.strip() for chunk in chunks if len(chunk.strip()) > 50])

# Build BM25 index
tokenized_corpus = [chunk.lower().split() for chunk in text_chunks]
bm25 = BM25Okapi(tokenized_corpus)

def bm25_search(query: str, top_k: int = 3) -> str:
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return "\n\n".join([text_chunks[i] for i in top_indices])

@tool
def pdf_search(query: str) -> str:
    """Search the loaded PDF for relevant grammar information"""
    return bm25_search(query)

teacher = create_react_agent(
    model=model,
    tools=[pdf_search],
    checkpointer=checkpointer,
    prompt=teacher_system_prompt
)