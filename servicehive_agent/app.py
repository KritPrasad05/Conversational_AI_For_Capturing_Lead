from agent.graph import build_graph, get_initial_state

graph = build_graph()


def run():
    print("AutoStream Agent Ready")
    print("Type 'exit' to quit.\n")
    state = get_initial_state()

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", "bye"}:
            print("Agent: Thanks for chatting! Have a great day. 👋")
            break

        # Add user message to history BEFORE invoking graph
        state["history"].append({"role": "user", "content": user_input})

        state = graph.invoke(state)

        # Agent reply is the last item in history (added by graph)
        agent_reply = state["history"][-1]["content"]
        print(f"Agent: {agent_reply}\n")


if __name__ == "__main__":
    run()