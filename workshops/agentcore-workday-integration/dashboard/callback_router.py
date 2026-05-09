import logging
from urllib.parse import unquote
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from ac_client import invoke_agent

l = logging.getLogger("aws.callback")

router = APIRouter()


@router.get("/app/callback")
async def callback(request: Request):
    session_id = unquote(request.query_params.get("session_id", ""))
    l.info(f"> callback session_id={session_id}")

    payload = {"cmd": "completeAuth", "session_id": session_id}
    response = invoke_agent(payload)
    l.info(f"> init_agent response={response}")
    return RedirectResponse(url="/app")
