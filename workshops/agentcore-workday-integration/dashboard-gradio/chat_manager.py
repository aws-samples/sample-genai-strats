import logging
import gradio as gr
from ac_client import invoke_agent

l = logging.getLogger("aws.chat_manager")

def init_agent(callback_url: str) -> str:
    l.info(f"> init_agent")
    l.info(f"| callback_url={callback_url} ")
    payload = {"cmd": "initialize", "callback_url": callback_url}
    response = invoke_agent(payload)
    l.info(f"> init_agent response={response}")
    if response.get("status") == "ok":
        return None
    else:
        return response.get("auth_url")

def handle_message(message, history, request: gr.Request):
    l.info(f"handle_message")
    l.info(f"| message={message} ")
    payload = {"cmd":"prompt", "prompt":message}
    response = invoke_agent(payload)
    l.info(f"> handle_message response={response}")
    if response.get("status") == "ok":
        return response.get("response");
    else:
        return "Error communicating to the agent. Try again in a moment."
