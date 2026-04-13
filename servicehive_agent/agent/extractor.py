import re
from agent.llm import get_llm

llm = get_llm()

EXTRACT_PROMPT = """You are a data extractor for AutoStream, a video editing SaaS.

Given the conversation history and the latest user message, extract the following:
1. name      - The user's name IF they provided it as a direct answer to "what is your name?"
2. plan      - The plan the user wants: "Basic Plan", "Pro Plan", or null
3. platform  - The platform: "YouTube", "Instagram", "TikTok", "Twitter", "Facebook", or null

IMPORTANT rules for name:
- ONLY extract name if the user is clearly giving their name (e.g. replying to "what's your name?")
- Do NOT extract name from phrases like "I am interested", "I am a creator", "I am showing high intent"
- "I am Krit" or "Krit Prasad" as a reply to a name question = extract "Krit Prasad"
- If no clear name is given, return null

IMPORTANT rules for plan:
- Use conversation history to infer plan if user says "this plan", "that one", "the one above"
- Only return "Basic Plan" or "Pro Plan"

Conversation history (last few turns):
{history}

Latest message: "{user_input}"

Reply with ONLY valid JSON, no extra text:
{{"name": "...", "plan": "...", "platform": "..."}}
Use null (not "null" string) for missing values."""


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_info_llm(user_input: str, history: list) -> dict:
    """Use LLM to extract name, plan, platform from message + context."""
    history_str = ""
    for turn in history[-8:]:
        role = "User" if turn["role"] == "user" else "Agent"
        history_str += f"{role}: {turn['content']}\n"

    prompt = EXTRACT_PROMPT.format(history=history_str, user_input=user_input)

    try:
        import json
        raw = llm.invoke(prompt).content.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?|```", "", raw).strip()
        data = json.loads(raw)
        return {
            "name": data.get("name") or None,
            "plan": data.get("plan") or None,
            "platform": data.get("platform") or None,
        }
    except Exception as e:
        print(f"[EXTRACT ERROR] {e}")
        return {"name": None, "plan": None, "platform": None}


def extract_user_info(state: dict, user_input: str) -> dict:
    """
    Extract all available info from user_input + conversation history.
    Updates state in-place. Returns updated state.
    """
    history = state.get("history", [])

    # Email: always use regex (100% reliable)
    if not state.get("email"):
        email = extract_email(user_input)
        if email:
            state["email"] = email

    # Name, plan, platform: use LLM with conversation context
    extracted = extract_info_llm(user_input, history)

    if not state.get("user_name") and extracted.get("name"):
        state["user_name"] = extracted["name"]

    if not state.get("selected_plan") and extracted.get("plan"):
        state["selected_plan"] = extracted["plan"]

    if not state.get("platform") and extracted.get("platform"):
        state["platform"] = extracted["platform"]

    return state    