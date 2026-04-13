from typing import TypedDict, Optional, List


class AgentState(TypedDict):
    # Full conversation history as list of {"role": "user"/"assistant", "content": "..."}
    history: List[dict]

    # Current onboarding data
    user_name: Optional[str]
    email: Optional[str]
    platform: Optional[str]
    selected_plan: Optional[str]

    # Flow control
    # None | "collecting_name" | "collecting_email" | "collecting_platform" | "done"
    stage: Optional[str]
    lead_ready: bool