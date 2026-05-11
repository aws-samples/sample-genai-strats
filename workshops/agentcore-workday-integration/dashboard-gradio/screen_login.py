import gradio as gr


def build():
    with gr.Column(visible=False) as screen:
        gr.HTML("""
            <style>
                #login-box {
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
        with gr.Column(elem_id="login-box"):
            gr.Markdown("# Welcome to HR Agent")
            gr.Markdown("---")
            gr.Markdown("Authentication required")
            auth_url_box = gr.Textbox(value="", visible=False)
            login_btn = gr.Button("Login with Workday", variant="primary")
            login_btn.click(fn=None, inputs=[auth_url_box], js="(url) => { window.location.href = url; }")
    return screen, auth_url_box
