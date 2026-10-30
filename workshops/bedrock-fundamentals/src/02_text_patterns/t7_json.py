"""
Lab T-7: Extracting JSON data from text.

Structured outputs make the model's answer follow a JSON schema. The app sends the schema in
outputConfig, and the model's text response is JSON that matches it, ready to parse.

Run from src/: uv run 02_text_patterns/t7_json.py
"""
import json
import os
import textwrap

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

SAMPLE_EMAIL = """Dear Acme Investments,

I am writing to bring to your attention a situation that I believe to be
unethical on the part of one of your account managers, Roger Longbottom.

I recently met with Roger to discuss my investment portfolio and was deeply
concerned to hear that he suggested I invest in a certain stock. When I asked
him why he thought this was a good investment, he stated that the stock was
currently undervalued and was likely to increase in value in the near future.

However, upon further research, I have discovered that the stock in question has
a questionable reputation. It has been the subject of multiple lawsuits and has
been found to have engaged in questionable business practices.

I believe Roger was aware of these facts, but failed to disclose them to me. As
a result, I feel I was misled into making an unwise investment decision.

I therefore urge you to investigate whether Roger has acted unethically and take
appropriate action if necessary.

Yours sincerely,
Carson Bradford"""


# --- Amazon Bedrock

# The JSON schema you want back
EMAIL_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "A brief one-line or two-line summary of the email.",
        },
        "escalate_complaint": {
            "type": "boolean",
            "description": "Indicates if this email is serious enough to be immediately escalated for further review.",
        },
        "level_of_concern": {
            "type": "integer",
            "description": "Rate the level of concern for the above content on a scale from 1 to 10.",
        },
        "overall_sentiment": {
            "type": "string",
            "description": "The sender's overall sentiment.",
            "enum": ["Positive", "Neutral", "Negative"],
        },
        "supporting_business_unit": {
            "type": "string",
            "description": "The internal business unit that this email should be routed to.",
            "enum": ["Sales", "Operations", "Customer Service", "Fund Management"],
        },
        "customer_names": {
            "type": "array",
            "description": "An array of customer names mentioned in the email.",
            "items": {"type": "string"},
        },
        "sentiment_towards_employees": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "employee_name": {
                        "type": "string",
                        "description": "The employee's name.",
                    },
                    "sentiment": {
                        "type": "string",
                        "description": "The sender's sentiment towards the employee.",
                        "enum": ["Positive", "Neutral", "Negative"],
                    },
                },
                "required": ["employee_name", "sentiment"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "summary",
        "escalate_complaint",
        "overall_sentiment",
        "supporting_business_unit",
        "level_of_concern",
        "customer_names",
        "sentiment_towards_employees",
    ],
    "additionalProperties": False,
}


def get_json_response(input_content):
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    message = {
        "role": "user",
        "content": [
            {"text": f"<content>{input_content}</content>"},
            {"text": "Please summarize the email within the <content> tags."},
        ],
    }

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=[message],
        inferenceConfig={"maxTokens": 2000},
        outputConfig={
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "name": "email_summary",
                        "description": "A summary of a customer email.",
                        "schema": json.dumps(EMAIL_SUMMARY_SCHEMA),  # the schema is sent as a JSON string
                    }
                },
            }
        },
    )

    # The response text is JSON that follows the schema
    return json.loads(response["output"]["message"]["content"][0]["text"])


# --- Command line

# To try your own text, replace SAMPLE_EMAIL at the top of this file
print("Email:\n")
print(textwrap.indent(SAMPLE_EMAIL, "  ") + "\n")

print("Sending the email and the JSON schema to the model...\n")
response_content = get_json_response(input_content=SAMPLE_EMAIL)
print(json.dumps(response_content, indent=2, ensure_ascii=False))
