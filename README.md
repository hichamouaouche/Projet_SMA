# Language Learning AI - Multi-Agent System

## Description

An intelligent multi-agent ecosystem for interactive language learning. The system simulates real-world conversational situations, corrects grammar, checks cultural appropriateness, and formats responses — all orchestrated autonomously via LangGraph.

## Features

### 1. Agent Workflow & Orchestration (LangGraph)
- **5 specialized agents** working in parallel and sequential pipelines
- **Hybrid orchestration**: character + teacher run in parallel, then merge into mentality, then styler
- State management via `StateGraph` with typed `WorkflowState`

### 2. RAG (Retrieval-Augmented Generation)
- PDF-based knowledge base loaded from `files/Grammer.pdf`
- FAISS vector store with HuggingFace embeddings (`all-MiniLM-L6-v2`)
- Chunking via `RecursiveCharacterTextSplitter`
- Retriever tool available for agents to access grammar rules dynamically

### 3. Human-in-the-Loop (HITL)
- Interactive save checkpoint after each response (`save_check` node)
- User decides whether to persist corrections to disk
- Streamlit UI save button for manual content preservation

### 4. Prompt Evaluation (A/B Testing)
- `prompt_evaluation.py` compares 3 prompt versions on 10 test sentences
- Metrics: correction rate, word count compliance, average response length
- Results exported to JSON with automatic best-version recommendation

### 5. Web UI (Streamlit)
- Real-time chat interface
- Language selection (French, Spanish, German, Italian, Arabic)
- New situation generation, chat history, save functionality
- Clean markdown-formatted responses

## Architecture

```
START
  ├── character (ReAct agent + web search)
  └── teacher (grammar correction)
        ↓
    mentality (cultural check)
        ↓
    styler (markdown formatting)
        ↓
    save_check (human-in-the-loop)
        ↓
    save_agent (optional) → END
```

### Agents

| Agent | Role | Tools |
|---|---|---|
| `situational` | Generates real-life conversation scenarios | Tavily web search |
| `character` | Responds as a human with emotions | Tavily web search |
| `teacher` | Corrects grammar errors | (RAG retriever) |
| `mentality` | Checks cultural appropriateness | Tavily web search |
| `styler` | Formats output in clean markdown | Tavily web search |
| `save_agent` | Persists corrections to disk | None |

## Tech Stack

- **LangGraph** — Agent orchestration and workflow
- **LangChain** — Agent creation, tools, chains
- **Ollama** — Local LLM inference
- **Tavily API** — Web search tool
- **FAISS** — Vector store for RAG
- **ChromaDB** — Alternative vector store
- **HuggingFace Embeddings** — Text embeddings (`all-MiniLM-L6-v2`)
- **Streamlit** — Web UI
- **PyPDFLoader** — PDF document loading
- **LangSmith** — Tracing and evaluation

## Installation

```bash
# Clone or copy the project
cd PythonProject6

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
echo "modelName=your-ollama-model" > .env
echo "tavilyApiKey=your-tavily-key" >> .env
echo "Ollama_api_key=your-ollama-key" >> .env
echo "LANGSMITH_API_KEY=your-langsmith-key" >> .env

```

## Usage

### CLI Mode
```bash
python withoutUi.py
```

### Web UI (Streamlit)
```bash
streamlit run Ui.py
```

### Prompt Evaluation
```bash
python prompt_evaluation.py
```

### LangGraph Studio
```bash
langgraph dev
```
Then open `http://localhost:2024` in your browser.

## Project Structure

```
PythonProject6/
 ├── Ui.py                       # Streamlit web UI + separate graph
 ├── withoutUi.py                # CLI entry point
 ├── agents.py                   # Agent definitions, tools, prompts, RAG setup
 ├── workflows.py                # LangGraph workflow graph
 ├── prompt_evaluation.py        # A/B/C prompt testing
 ├── prompt_evaluation_results.json  # Evaluation results
 ├── langgraph.json              # LangGraph Studio configuration
 ├── requirements.txt            # Python dependencies (pinned versions)
 ├── .env                        # Environment variables
 ├── files/
 │   ├── Grammer.pdf             # Grammar knowledge base (RAG source)
 │   └── saved_corrections_*.txt # Persisted user corrections
 └── README.md
```

## Requirements

- Python 3.10+
- Ollama running locally or remotely
- Tavily API key
- All dependencies listed in `requirements.txt`
