"""
In-memory user database.
Key: "{email}_{platform}" — so same user can have different plans on different platforms.
"""

USER_DB = {}


def save_user(state: dict) -> dict:
    email = (state.get("email") or "").lower().strip()
    platform = (state.get("platform") or "").lower().strip()

    if not email or not platform:
        return {}

    key = f"{email}_{platform}"
    record = {
        "name": state.get("user_name", ""),
        "email": email,
        "platform": platform.capitalize(),
        "plan": state.get("selected_plan", ""),
    }
    USER_DB[key] = record
    return record


def get_user(email: str, platform: str = None) -> list:
    email = email.lower().strip()
    if platform:
        key = f"{email}_{platform.lower().strip()}"
        record = USER_DB.get(key)
        return [record] if record else []
    return [v for k, v in USER_DB.items() if k.startswith(email + "_")]


def get_all_users() -> list:
    return list(USER_DB.values())


def get_users_by_plan(plan_name: str) -> list:
    plan_lower = plan_name.lower()
    return [v for v in USER_DB.values() if plan_lower in (v.get("plan") or "").lower()]