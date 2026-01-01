from src.graph import build_graph
from src.state import AgentState

def run_app():
    graph = build_graph()

    print("Personal AI Assistant")

    while True:
        user_input = input("You: ")
        if user_input.lower().strip() in {"exit", "quit", "bye", "goodbye"}:
            print("Goodbye!")
            break
        
        state = AgentState(messages=[{"role": "user", "content": user_input}])
        result = graph.invoke(state, {'recursion_limit': 50})
        for msg in reversed(result["messages"]):
            if msg.get("role") == "assistant":
                print("Assistant: " + msg["content"])
                break


if __name__ == "__main__":
    run_app()
