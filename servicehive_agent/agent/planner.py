"""
Agent brain — clean separation of concerns:

  Intent detection  → intent.py  (LLM with history)
  Info extraction   → extractor.py (LLM with history + regex for email)
  Knowledge answers → RAG + LLM
  Flow control      → explicit state machine (no LLM guessing stages)
  DB operations     → utils/db.py
"""

from agent.llm import get_llm
from agent.intent import detect_intent
from agent.extractor import extract_user_info
from utils.db import save_user, get_all_users, get_users_by_plan
from tools.lead_capture import mock_lead_capture

llm = get_llm()

RAG_PROMPT = """You are a helpful sales assistant for AutoStream, an AI-powered video editing SaaS.

Answer the user's question using ONLY the context provided. Be concise and friendly.
If the context doesn't have the answer, say you don't have that information.

Context from knowledge base:
{context}

Conversation history:
{history}

User question: {user_input}

Answer:"""

GREET_PROMPT = """You are a friendly sales assistant for AutoStream, an AI-powered video editing SaaS.
Greet the user warmly in 1-2 sentences. Mention you can help with plans, pricing, and sign-ups.
User said: "{user_input}"
"""


def _history_str(history: list) -> str:
    lines = []
    for turn in history[-8:]:
        role = "User" if turn["role"] == "user" else "Agent"
        lines.append(f"{role}: {turn['content']}")
    return "\n".join(lines)


def _rag_answer(user_input: str, history: list, retriever) -> str:
    try:
        docs = retriever.invoke(user_input)
        if not docs:
            return "I don't have specific information on that. Feel free to ask about our plans or policies!"
        context = "\n\n".join(doc.page_content for doc in docs)
        prompt = RAG_PROMPT.format(
            context=context,
            history=_history_str(history),
            user_input=user_input
        )
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"[RAG ERROR] {e}")
        return "I'm having trouble fetching that right now. Please try again."


def _greet(user_input: str) -> str:
    try:
        return llm.invoke(GREET_PROMPT.format(user_input=user_input)).content.strip()
    except Exception:
        return "Hi there! Welcome to AutoStream. I can help you with our plans, pricing, and getting you signed up."


def _format_users(users: list) -> str:
    if not users:
        return "No users found."
    return "\n".join(
        f"• {u['name']} ({u['email']}) — {u['platform']} — {u['plan']}"
        for u in users
    )


def _complete_onboarding(state: dict) -> tuple[dict, str]:
    state["stage"] = "done"
    state["lead_ready"] = True
    save_user(state)
    mock_lead_capture(state["user_name"], state["email"], state["platform"])
    plan = state.get("selected_plan") or "AutoStream"
    return state, (
        f"You're all set, {state['user_name']}! 🎉\n"
        f"Registered for **{plan}** on **{state['platform']}**.\n"
        f"Confirmation will be sent to {state['email']}.\n"
        f"Is there anything else I can help you with?"
    )


# ---------------------------------------------------------------------------
# Onboarding state machine — sequential, no LLM guessing
# ---------------------------------------------------------------------------

def _run_onboarding(state: dict, user_input: str, retriever) -> tuple[dict, str | None]:
    """
    Drives the collecting_name → collecting_email → collecting_platform → done flow.
    Returns (state, response) or (state, None) to fall through to normal handling.
    """
    stage = state.get("stage")

    # Always try to extract from current message
    state = extract_user_info(state, user_input)

    if stage == "collecting_name":
        if state.get("user_name"):
            state["stage"] = "collecting_email"
            return state, f"Nice to meet you, {state['user_name']}! What's your email address?"
        return state, "I didn't catch your name — could you tell me what to call you?"

    if stage == "collecting_email":
        if state.get("email"):
            state["stage"] = "collecting_platform"
            return state, "Got it! Which platform are you creating content on? (e.g. YouTube, Instagram, TikTok)"
        return state, "Could you share your email address so I can register you?"

    if stage == "collecting_platform":
        if state.get("platform"):
            return _complete_onboarding(state)
        return state, "Which platform are you creating content on? (e.g. YouTube, Instagram, TikTok)"

    if stage == "done":
        # Check if user wants to add another platform/plan
        lower = user_input.lower()
        add_keywords = ["another", "also", "add", "different", "as well",
                        "youtube", "instagram", "tiktok", "facebook", "twitter",
                        "basic plan", "pro plan"]
        if any(kw in lower for kw in add_keywords):
            # Keep name + email, reset platform + plan for new subscription
            state["platform"] = None
            state["selected_plan"] = None
            state["stage"] = "collecting_platform"
            state["lead_ready"] = False
            # Re-extract — they may have mentioned platform in same message
            state = extract_user_info(state, user_input)
            if state.get("platform"):
                if not state.get("selected_plan"):
                    # Try to infer plan from message
                    if "pro" in lower:
                        state["selected_plan"] = "Pro Plan"
                    elif "basic" in lower:
                        state["selected_plan"] = "Basic Plan"
                return _complete_onboarding(state)
            return state, "Which platform would you like to add? (YouTube, Instagram, TikTok, etc.)"
        # Not an add-request — fall through to normal Q&A
        return state, None

    return state, None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def agent_step(state: dict, retriever) -> tuple[dict, str]:
    """
    Process one user turn. Returns (updated_state, response_text).
    """
    user_input = state["history"][-1]["content"]
    lower = user_input.lower().strip()
    history = state.get("history", [])

    # ------------------------------------------------------------------
    # 0. Admin DB queries — keyword shortcut, no LLM needed
    # ------------------------------------------------------------------
    admin_triggers = ["tell me all", "show all", "list all", "list users", "show users",
                      "users with", "who has"]
    if any(t in lower for t in admin_triggers):
        if "pro" in lower:
            return state, f"Users on Pro Plan:\n{_format_users(get_users_by_plan('Pro Plan'))}"
        elif "basic" in lower:
            return state, f"Users on Basic Plan:\n{_format_users(get_users_by_plan('Basic Plan'))}"
        return state, f"All registered users:\n{_format_users(get_all_users())}"

    # ------------------------------------------------------------------
    # 1. If in active onboarding, drive the state machine
    # ------------------------------------------------------------------
    onboarding_stages = {"collecting_name", "collecting_email", "collecting_platform", "done"}
    if state.get("stage") in onboarding_stages:
        state, response = _run_onboarding(state, user_input, retriever)
        if response is not None:
            return state, response
        # None = fall through to normal handling (e.g. Q&A after sign-up)

    # ------------------------------------------------------------------
    # 2. Detect intent (LLM with history for context)
    # ------------------------------------------------------------------
    intent = detect_intent(user_input, history)
    print(f"[INTENT] {intent}")  # Debug — remove before demo

    # ------------------------------------------------------------------
    # 3. Greeting
    # ------------------------------------------------------------------
    if intent == "greeting":
        return state, _greet(user_input)

    # ------------------------------------------------------------------
    # 4. High intent → extract what we can, start onboarding
    # ------------------------------------------------------------------
    if intent == "high_intent":
        # Extract plan/platform from this message + history context
        state = extract_user_info(state, user_input)

        # Infer plan from history if not yet set
        if not state.get("selected_plan"):
            hist_text = _history_str(history).lower()
            if "pro plan" in hist_text:
                state["selected_plan"] = "Pro Plan"
            elif "basic plan" in hist_text:
                state["selected_plan"] = "Basic Plan"

        plan_str = f" for the {state['selected_plan']}" if state.get("selected_plan") else ""
        platform_str = f" on {state['platform']}" if state.get("platform") else ""

        if not state.get("user_name"):
            state["stage"] = "collecting_name"
            return state, f"Great{plan_str}{platform_str}! Let's get you signed up. What's your name?"

        if not state.get("email"):
            state["stage"] = "collecting_email"
            return state, f"Awesome{plan_str}{platform_str}! What's your email address, {state['user_name']}?"

        if not state.get("platform"):
            state["stage"] = "collecting_platform"
            return state, "Which platform are you creating content on? (e.g. YouTube, Instagram, TikTok)"

        # All info already available
        state, msg = _complete_onboarding(state)
        return state, msg

    # ------------------------------------------------------------------
    # 5. Product query or general → RAG
    # ------------------------------------------------------------------
    return state, _rag_answer(user_input, history, retriever)