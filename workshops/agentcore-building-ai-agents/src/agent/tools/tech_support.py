import os
import boto3
from strands.tools import tool
from strands_tools import retrieve
from logger import get_logger

l = get_logger("tech_support")


TECH_SUPPORT_KB_ID = os.environ.get("TECH_SUPPORT_KB_ID")
l.info(f"ℹ️ TECH_SUPPORT_KB_ID={TECH_SUPPORT_KB_ID}")

@tool
def get_technical_support(issue_description: str) -> str:
    try:
        region = boto3.Session().region_name

        tool_use = {
            "toolUseId": "tech_support_query",
            "input": {
                "text": issue_description,
                "knowledgeBaseId": TECH_SUPPORT_KB_ID,
                "region": region,
                "numberOfResults": 3,
                "score": 0.4,
            },
        }

        result = retrieve.retrieve(tool_use)

        if result["status"] == "success":
            return result["content"][0]["text"]
        else:
            return f"Unable to access technical support documentation. Error: {result['content'][0]['text']}"

    except Exception as e:
        l.error(f"Detailed error in get_technical_support: {str(e)}")
        return f"Unable to access technical support documentation. Error: {str(e)}"

l.info("✅ get_technical_support tool ready")
