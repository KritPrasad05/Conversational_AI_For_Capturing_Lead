from langgraph.graph import StateGraph, END
from .state import AgentState
from .planner import agent_step
from ..rag.vector_store import create_vector_store
from ..rag.retriever import get_retriever


def get_initial_state() -> AgentState:
    return AgentState(
        history=[],
        user_name=None,
        email=None,
        platform=None,
        selected_plan=None,
        stage=None,
        lead_ready=False,
    )


def build_graph():
    vectorstore = create_vector_store()
    retriever = get_retriever(vectorstore)

    def run_agent(state: AgentState) -> AgentState:
        updated_state, response = agent_step(state, retriever)
        updated_state["history"].append({"role": "assistant", "content": response})
        return updated_state

    graph = StateGraph(AgentState)
    graph.add_node("agent", run_agent)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)

    return graph.compile()