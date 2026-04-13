from .llm import get_llm

llm = get_llm()

INTENT_PROMPT = """You are an intent classifier for AutoStream, a video editing SaaS.

Given the conversation history and the latest user message, classify the intent into EXACTLY one of:
- greeting        : casual hello, hi, how are you
- product_query   : asking about plans, features, pricing, policies, refunds, support
- high_intent     : user wants to BUY, SIGN UP, GET, or PURCHASE a plan (e.g. "how do I get this", "sign me up", "I want to go with pro", "let's do it", "get me the basic plan")
- general_query   : anything else

IMPORTANT:
- "I want a plan" alone is product_query (still browsing)
- "how do I get this plan" or "I want to go with this" after discussing a plan = high_intent
- "let's go", "sign me up", "get me the basic plan" = high_intent
- Use the conversation history to understand context (e.g. "this plan" refers to what was discussed)

Conversation history (last few turns):
{history}

Latest user message: "{user_input}"

Reply with ONLY the intent label, nothing else."""


def detect_intent(user_input: str, history: list) -> str:
    # Fast rule-based shortcuts for unambiguous cases
    lower = user_input.lower().strip()

    if lower in {"hi", "hello", "hey", "good morning", "good evening", "howdy", "hiya"}:
        return "greeting"

    # Build history string for LLM
    history_str = ""
    for turn in history[-8:]:  # Last 8 turns for context
        role = "User" if turn["role"] == "user" else "Agent"
        history_str += f"{role}: {turn['content']}\n"

    prompt = INTENT_PROMPT.format(history=history_str, user_input=user_input)

    try:
        result = llm.invoke(prompt).content.strip().lower()
        for label in ["greeting", "product_query", "high_intent", "general_query"]:
            if label in result:
                return label
        return "general_query"
    except Exception as e:
        print(f"[INTENT ERROR] {e}")
        return "general_query"