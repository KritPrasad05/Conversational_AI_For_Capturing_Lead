import json
from langchain_core.documents import Document


def load_knowledge_base(path="data/knowledge_base.json"):
    with open(path, "r") as f:
        data = json.load(f)

    documents = []

    # -------------------
    # Plans
    # -------------------
    for plan in data.get("plans", []):
        content = f"""
        Plan Name: {plan['name']}
        Price: {plan['price']}
        Description: {plan.get('description', '')}
        Features: {', '.join(plan['features'])}
        """

        documents.append(
            Document(
                page_content=content.strip(),
                metadata={
                    "type": "plan",
                    "plan_name": plan["name"]
                }
            )
        )

    # -------------------
    # Policies
    # -------------------
    for policy in data.get("policies", []):
        content = f"""
        Policy Type: {policy['type']}
        Details: {policy['details']}
        """

        documents.append(
            Document(
                page_content=content.strip(),
                metadata={
                    "type": "policy",
                    "policy_type": policy["type"]
                }
            )
        )

    # -------------------
    # General Info
    # -------------------
    for info in data.get("general_info", []):
        documents.append(
            Document(
                page_content=info,
                metadata={"type": "general"}
            )
        )

    return documents