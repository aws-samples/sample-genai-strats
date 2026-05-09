import gradio as gr


def build():
    with gr.Column(visible=True) as screen:
        gr.HTML("""
            <style>
                #connecting-box {
                    max-width: 480px;
                    margin: 15vh auto 0;
                    padding: 2.5rem 3rem;
                    border: 1px solid var(--border-color-primary);
                    border-radius: 12px;
                    background: var(--background-fill-primary);
                    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
                    text-align: center;
                }
            </style>
        """)
        with gr.Column(elem_id="connecting-box"):
            gr.Markdown("# Welcome to HR Agent")
            gr.Markdown("---")
            gr.Markdown("Connecting to the agent...")
    return screen
