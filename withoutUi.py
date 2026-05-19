from agents import situational, WorkflowState, config
from workflows import graph


def main():
    print("=" * 50)
    print("   Language Learning AI — CLI Mode")
    print("=" * 50)

    language = input("\nLanguage to practise (default: French): ").strip() or "French"

    def generate_situation(lang: str) -> str:
        state: WorkflowState = {
            "messages": [{"role": "user", "content": f"Generate a real conversation situation in {lang}."}],
            "character": None, "teacher": None, "cultural": None, "styler": None,
            "situational": None, "mentality": None, "prompt": None,
            "history": [], "save_it": False, "language": lang,
        }
        result = situational.invoke(state, config)
        return result["messages"][-1].content

    situation = generate_situation(language)
    print(f"\n--- Situation ({language}) ---\n{situation}\n")

    while True:
        user_input = input(f"Your response in {language} (or 'new' / 'quit'): ").strip()

        if user_input.lower() == "quit":
            print("\nGoodbye.")
            break

        if user_input.lower() == "new":
            situation = generate_situation(language)
            print(f"\n--- New Situation ---\n{situation}\n")
            continue

        if not user_input:
            continue

        workflow_state: WorkflowState = {
            "messages": [{"role": "user", "content": f"Situation: {situation}\n\nUser: {user_input}"}],
            "character": None, "teacher": None, "cultural": None, "styler": None,
            "situational": situation, "mentality": None, "prompt": user_input,
            "history": [{"role": "user", "content": user_input}],
            "save_it": False, "language": language,
        }

        graph.invoke(workflow_state)


if __name__ == "__main__":
    main()
