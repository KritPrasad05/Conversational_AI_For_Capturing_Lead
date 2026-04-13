"""
FastAPI backend for AutoStream AI Agent.
Run with: uvicorn api.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid

from servicehive_agent.agent.graph import build_graph, get_initial_state
from servicehive_agent.utils.db import get_all_users, get_users_by_plan

app = FastAPI(title="AutoStream Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id → state
graph = build_graph()
sessions: dict = {}


# ── Models ──────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    stage: Optional[str]
    user_name: Optional[str]
    email: Optional[str]
    platform: Optional[str]
    selected_plan: Optional[str]
    lead_ready: bool


# ── Routes ───────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Get or create session
    session_id = req.session_id or str(uuid.uuid4())
    state = sessions.get(session_id) or get_initial_state()

    # Append user message to history
    state["history"].append({"role": "user", "content": req.message})

    # Run agent
    state = graph.invoke(state)

    # Persist updated state
    sessions[session_id] = state

    # Extract agent reply (last history item)
    reply = state["history"][-1]["content"]

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        stage=state.get("stage"),
        user_name=state.get("user_name"),
        email=state.get("email"),
        platform=state.get("platform"),
        selected_plan=state.get("selected_plan"),
        lead_ready=state.get("lead_ready", False),
    )


@app.post("/reset/{session_id}")
def reset_session(session_id: str):
    sessions[session_id] = get_initial_state()
    return {"status": "reset", "session_id": session_id}


@app.get("/leads")
def get_leads(plan: Optional[str] = None):
    if plan:
        users = get_users_by_plan(plan)
    else:
        users = get_all_users()
    return {"count": len(users), "leads": users}


@app.get("/health")
def health():
    return {"status": "ok"}
