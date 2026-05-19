from langgraph.graph import StateGraph, START, END
from agents import teacher, character, styler, mentality, save_agent, WorkflowState, config
from typing import Dict, Any


# ── Node Functions ─────────────────────────────────────────────────────────────

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
            "content": (
                "Format this into clean markdown:\n\n"
                f"**Grammar Correction**: {state.get('teacher', '')}\n\n"
                f"**Character Response**: {state.get('character', '')}\n\n"
                f"**Cultural Note**: {state.get('mentality', '')}"
            ),
        }],
        **{k: v for k, v in state.items() if k != "messages"},
    }
    result = styler.invoke(styler_state, config)
    output = result["messages"][-1].content
    print(f"\n{output}\n")
    return {"styler": output}


def save_check(state: WorkflowState) -> Dict[str, Any]:
    """Human-in-the-loop checkpoint: ask the user whether to persist the response."""
    print(f"\n--- Response ---\n{state.get('styler', '')}\n")
    answer = input("Save this response? (yes/no): ").strip().lower()
    return {"save_it": answer in {"yes", "y", "true", "1"}}


def should_save(state: WorkflowState) -> str:
    return "save_agent" if state.get("save_it", False) else END


# ── Graph ──────────────────────────────────────────────────────────────────────

builder = StateGraph(WorkflowState)

builder.add_node("character", run_character)
builder.add_node("teacher", run_teacher)
builder.add_node("mentality", run_mentality)
builder.add_node("styler", run_styler)
builder.add_node("save_check", save_check)
builder.add_node("save_agent", save_agent)

# character and teacher run in parallel from START
builder.add_edge(START, "character")
builder.add_edge(START, "teacher")

# both merge into mentality, then styler
builder.add_edge("character", "mentality")
builder.add_edge("teacher", "mentality")
builder.add_edge("mentality", "styler")

# HITL checkpoint, then conditional save
builder.add_edge("styler", "save_check")
builder.add_conditional_edges("save_check", should_save)

graph = builder.compile()
