from agents import situational, WorkflowState, config
from workflows import graph

def main():
    print("=== Language Learning AI ===\n")
    language = input("Select language to learn: ").strip() or "French"

    # Generate and print situation first
    state: WorkflowState = {
        "messages": [{"role": "user", "content": f"Generate a real situation in {language} for conversation practice."}],
        "character": None, "teacher": None, "cultural": None, "styler": None,
        "situational": None, "mentality": None, "prompt": None, "history": [],
        "save_it": False, "language": language
    }
    result = situational.invoke(state, config)
    situation = result["messages"][-1].content
    print(f"\n=== Situation ({language}) ===\n{situation}\n")

    while True:
            user_input = input(f"Your response ({language}) (or 'quit'/'new'): ").strip()
            if user_input.lower() == "quit":
                break
            if user_input.lower() == "new":
                result = situational.invoke({
                    "messages": [{"role": "user", "content": f"Generate a new situation in {language}."}],
                    "character": None, "teacher": None, "cultural": None, "styler": None,
                    "situational": None, "mentality": None, "prompt": None, "history": [],
                    "save_it": False, "language": language
                }, config)
                situation = result["messages"][-1].content
                print(f"\n=== New Situation ===\n{situation}\n")
                continue

            workflow_state = {
                "messages": [{"role": "user", "content": f"Situation: {situation}\n\nUser: {user_input}"}],
                "character": None, "teacher": None, "cultural": None, "styler": None,
                "situational": situation, "mentality": None, "prompt": user_input,
                "history": state["history"] + [{"role": "user", "content": user_input}],
                "save_it": False, "language": language
            }

            result = graph.invoke(workflow_state)

if __name__ == "__main__":
    main()
