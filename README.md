# Language Learning AI — Multi-Agent System

An intelligent language-learning platform powered by a multi-agent architecture. The system places the user inside a realistic conversation scenario, then corrects grammar, checks cultural appropriateness, and formats the full response — all orchestrated automatically via **LangGraph**.

---

## Features

| Feature | Description |
|---|---|
| Multi-agent workflow | Six specialised agents running in parallel and sequential pipelines |
| RAG grammar correction | BM25 retrieval over a grammar PDF knowledge base |
| Cultural check | Detects culturally inappropriate phrasing for the target language |
| Human-in-the-Loop | User decides whether to save each corrected response to disk |
| Web UI | Real-time Streamlit interface with chat history and save button |
| CLI mode | Lightweight terminal interface for offline use |
| Prompt evaluation | A/B/C testing framework with automatic best-version recommendation |
| Multi-language | French, Spanish, German, Italian, Arabic |

---

## Architecture

```
START
  ├─── character (human-like response with emotion)
  └─── teacher   (grammar correction via RAG)
            ↓
       mentality  (cultural appropriateness check)
            ↓
        styler    (markdown formatting)
            ↓
      save_check  (human-in-the-loop — CLI only)
            ↓
      save_agent  (persist to disk if approved)
            ↓
          END
```

### Agents

| Agent | Role | Tools |
|---|---|---|
| `situational` | Generates a realistic conversation scenario | Web search |
| `character` | Responds as a human with emotion | Web search |
| `teacher` | Corrects grammar errors | Grammar PDF (BM25 RAG) |
| `mentality` | Flags cultural issues | Web search |
| `styler` | Formats the final output in markdown | Web search |
| `save_agent` | Persists approved corrections to disk | — |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| Agent framework | LangChain |
| LLM inference | Ollama (remote or local) |
| RAG retrieval | BM25 (`rank-bm25`) over PyPDF-loaded document |
| Web search | Tavily API |
| Web UI | Streamlit |
| Tracing (optional) | LangSmith |

---

## Project Structure

```
Projet_SMA/
├── agents.py                       # Agent definitions, tools, prompts, RAG setup
├── workflows.py                    # LangGraph workflow graph (CLI mode)
├── Ui.py                           # Streamlit web interface
├── withoutUi.py                    # CLI entry point
├── prompt_evaluation.py            # A/B/C prompt testing framework
├── prompt_evaluation_results.json  # Latest evaluation results
├── langgraph.json                  # LangGraph Studio configuration
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not committed)
└── files/
    ├── Grammer.pdf                 # Grammar knowledge base (RAG source)
    └── saved_corrections_*.txt     # Persisted user sessions
```

---

## Installation

**Requirements:** Python 3.10+, pip

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env with your credentials
MODELNAME=your-ollama-model-name
TAVILYAPIKEY=your-tavily-api-key
OLLAMA_API_KEY=your-ollama-bearer-token
LANGSMITH_API_KEY=your-langsmith-key   # optional
```

---

## Usage

### Web Interface (recommended)

```bash
streamlit run Ui.py
```

Open `http://localhost:8501` in your browser.

### CLI Mode

```bash
python withoutUi.py
```

| Command | Action |
|---|---|
| `new` | Generate a new scenario |
| `quit` | Exit the session |

### Prompt Evaluation

```bash
python prompt_evaluation.py
```

Compares three prompt versions across 10 test sentences and exports results to `prompt_evaluation_results.json`.

### LangGraph Studio

```bash
langgraph dev
```

Open `http://localhost:2024` to visualise and debug the agent graph.

---

## Environment Variables

| Variable | Description |
|---|---|
| `modelName` | Ollama model name (e.g. `llama3`) |
| `tavilyApiKey` | Tavily API key for web search |
| `Ollama_api_key` | Bearer token for the Ollama endpoint |
| `LANGSMITH_API_KEY` | LangSmith tracing key (optional) |
