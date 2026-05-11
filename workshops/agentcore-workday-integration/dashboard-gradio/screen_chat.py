import gradio as gr
import chat_manager

user_avatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
bot_avatar = "https://cdn-icons-png.flaticon.com/512/4712/4712042.png"

placeholder_text = '''
Waiting for user input...
--------------------------------
You can ask me questions like:
- What's my PTO balance?
- Which department am I a part of?
- What's my employment start date?



'''

examples_text = [
    "How can you help me?",
    "What's my PTO balance?",
    "Which department am I a part of?",
    "What's my employment start date?"
]
def build():
    with gr.Column(visible=False) as screen:

        gr.ChatInterface(
            fn=chat_manager.handle_message,
            title="Welcome to AwesomeCorp HR agent (running on Amazon Bedrock AgentCore + Workday)",
            examples=examples_text,
            autofocus=True,
            fill_height=True,
            fill_width=True,
            save_history=False,
            chatbot=gr.Chatbot(
                label="Ask a question about your benefits, time off, or HR policies.",
                placeholder=placeholder_text,
                avatar_images=(user_avatar, bot_avatar),
                height="70vh",
                autoscroll=True
            ),
            textbox=gr.Textbox(placeholder="Type your message...", autofocus=True, interactive=True)
        )
    return screen
