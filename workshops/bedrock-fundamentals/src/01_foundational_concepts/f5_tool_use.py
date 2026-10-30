"""
Lab F-5: Tool use (function calling).

You describe your tools to the model. When the model needs one, it stops with stopReason "tool_use"
and returns a toolUse content block with the tool name and input. Your code runs the tool and sends
the result back in a toolResult content block. The model never runs code itself.

Run from src/: uv run 01_foundational_concepts/f5_tool_use.py
"""
import json
import math
import os

import boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = "us.anthropic.claude-sonnet-4-6"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

# The system prompt makes the model use the tool instead of doing the math itself
system = [{"text": "You must only do math by using a tool."}]

# Describe the tool: its name, what it does, and a JSON schema for its input. This is only a
# definition for the model, not an implementation: the code that runs the tool is in section 2.
tool_list = [
    {
        "toolSpec": {
            "name": "cosine",
            "description": "Calculate the cosine of x.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "number",
                            "description": "The number to pass to the function.",
                        }
                    },
                    "required": ["x"],
                }
            },
        }
    }
]

message_list = [{
    "role": "user",
    "content": [{"text": "What is the cosine of 7?"}],
}]

# 1. Model response: the model asks for the tool
print("1. Model response\n")
print("Sending prompt and tool description to the model...\n")
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    inferenceConfig={"maxTokens": 2000, "temperature": 0},
    toolConfig={"tools": tool_list},
    system=system,
)
response_message = response["output"]["message"]
print("Stop reason: " + response["stopReason"] + "\n")
print(json.dumps(response_message, indent=4))
message_list.append(response_message)

input("\nPress Enter to continue...")

# 2. Tool result: run the tool for each toolUse block and collect the results
tool_results = []
for content_block in response_message["content"]:
    if "toolUse" in content_block:
        tool_use = content_block["toolUse"]
        if tool_use["name"] == "cosine":
            tool_result_value = math.cos(tool_use["input"]["x"])
            tool_results.append({
                "toolResult": {
                    "toolUseId": tool_use["toolUseId"],
                    "content": [{"json": {"result": tool_result_value}}],
                }
            })

#    Send the tool results back to the model as a user message
message_list.append({"role": "user", "content": tool_results})
print("\n2. Tool result for the model\n")
print(json.dumps(message_list[-1], indent=4))

input("\nPress Enter to continue...")

# 3. Final answer: the model uses the tool result to write its answer
print("\n3. Final answer\n")
print("Sending the tool result to the model...\n")
response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    inferenceConfig={"maxTokens": 2000, "temperature": 0},
    toolConfig={"tools": tool_list},
    system=system,
)
print(response["output"]["message"]["content"][0]["text"])

# 4. Tool failure: send the same tool request again, but this time the tool result is an error.
#    The model decides what to do with it. To run this scenario, uncomment the code below.

# input("\nPress Enter to continue to the tool failure scenario...")

# error_message_list = message_list[:-1]
# error_message_list.append({
#     "role": "user",
#     "content": [{
#         "toolResult": {
#             "toolUseId": tool_results[0]["toolResult"]["toolUseId"],
#             "content": [{"text": "Error: the cosine tool is unavailable right now."}],
#             "status": "error",
#         }
#     }],
# })

# print("\n4. Answer after a tool error\n")
# print("Sending a tool error to the model...\n")
# response = bedrock.converse(
#     modelId=MODEL_ID,
#     messages=error_message_list,
#     inferenceConfig={"maxTokens": 2000, "temperature": 0},
#     toolConfig={"tools": tool_list},
#     system=system,
# )
# print(response["output"]["message"]["content"][0]["text"])
