import dotenv
dotenv.load_dotenv()

from logging_config import configure_logging
configure_logging()

import uvicorn
import gradio as gr
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import screen_connecting
import screen_chat
import screen_login
import callback_router
import chat_manager


l = logging.getLogger("aws.dashboard")

fastapi_app = FastAPI()

class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

fastapi_app.add_middleware(ForceHTTPSMiddleware)
fastapi_app.include_router(callback_router.router)

@fastapi_app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


with gr.Blocks() as gradio_app:
    gr.HTML("<style>* { font-size: 1.2rem !important; }</style>")

    connecting_screen = screen_connecting.build()
    chat_screen = screen_chat.build()
    login_screen, auth_url_box = screen_login.build()

    def on_load(request: gr.Request):
        host = request.headers.get("host", "")
        scheme = "http" if host.split(":")[0] in {"localhost", "127.0.0.1", "0.0.0.0"} else "https"
        callback_url = f"{scheme}://{request.url.netloc}/app/callback"
        auth_url = chat_manager.init_agent(callback_url=callback_url)
        if auth_url is None:
            return (
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=False),
                "",
            )
        else:
            return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), auth_url

    gradio_app.load(
        on_load, 
        outputs=[connecting_screen, chat_screen, login_screen, auth_url_box],
    )

gr.mount_gradio_app(fastapi_app, gradio_app, path="/app")

if __name__ == "__main__":
    uvicorn.run(
        "dashboard:fastapi_app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        timeout_graceful_shutdown=1,
        proxy_headers=True, 
        forwarded_allow_ips="*"
    )
