from logging_config import configure_logging
configure_logging()

import dotenv
import uvicorn
import gradio as gr
from fastapi import FastAPI, Request, HTTPException
import logging
import screen_connecting
import screen_chat
import screen_login
import callback_router

dotenv.load_dotenv()

l = logging.getLogger("aws.dashboard")

fastapi_app = FastAPI()
fastapi_app.include_router(callback_router.router)

FOCUS_JS = """
() => {
    const attach = () => {
        const ta = document.querySelector('[data-testid="textbox"] textarea');
        if (!ta) return;
        new MutationObserver(() => {
            if (!ta.disabled) ta.focus();
        }).observe(ta, { attributes: true, attributeFilter: ['disabled'] });
    };
    const poll = setInterval(() => {
        if (document.querySelector('[data-testid="textbox"] textarea')) {
            attach();
            clearInterval(poll);
        }
    }, 200);
}
"""

with gr.Blocks(js=FOCUS_JS) as gradio_app:
    gr.HTML("<style>* { font-size: 1.2rem !important; }</style>")

    connecting_screen = screen_connecting.build()
    chat_screen = screen_chat.build()
    login_screen, auth_url_box = screen_login.build()

    def on_load(request: gr.Request):
        # callback_url = f"{request.url.scheme}://{request.url.netloc}/app/callback"
        # auth_url = chat_manager.init_agent(callback_url=callback_url) 
        # if auth_url is None:
            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), ""
        # else:
            # return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), auth_url

    gradio_app.load(on_load, outputs=[connecting_screen, chat_screen, login_screen, auth_url_box])

gr.mount_gradio_app(fastapi_app, gradio_app, path="/app")

if __name__ == "__main__":
    uvicorn.run("dashboard:fastapi_app", 
                host="0.0.0.0", 
                port=8081, 
                reload=True, 
                timeout_graceful_shutdown=1)



