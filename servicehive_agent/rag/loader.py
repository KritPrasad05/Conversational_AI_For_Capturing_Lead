import json
import os
from langchain_core.documents import Document

# Get the directory where loader.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_PATH = os.path.join(current_dir, "..", "data", "knowledge_base.json")

def load_knowledge_base(path=KNOWLEDGE_BASE_PATH):
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