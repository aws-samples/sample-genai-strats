import boto3
from botocore.exceptions import ClientError
import os
import asyncio
from bedrock_agentcore.services.identity import IdentityClient, UserIdIdentifier

DEFAULT_TEST_USER_ID="defaulttestuser"
WORKLOAD_IDENTITY_NAME = os.getenv("WORKLOAD_IDENTITY_NAME")
CREDENTIAL_PROVIDER_NAME = os.getenv("CREDENTIAL_PROVIDER_NAME")
print(f"WORKLOAD_IDENTITY_NAME={WORKLOAD_IDENTITY_NAME}")
print(f"CREDENTIAL_PROVIDER_NAME={CREDENTIAL_PROVIDER_NAME}")
print(f"DEFAULT_TEST_USER_ID={DEFAULT_TEST_USER_ID}")

region = boto3.session.Session().region_name
identity_client = IdentityClient(region)
AGENT_MODE = os.environ.get("AGENT_MODE")

ENV_VAR_ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", None)

async def initialize(payload):
    print("> initialize")
    callback_url = payload.get("callback_url")
    user_id = payload.get("user_id", DEFAULT_TEST_USER_ID)
    print(f"| callback_url={callback_url}")
    print(f"| user_id={user_id}")

    if ENV_VAR_ACCESS_TOKEN:
        print("| Found ACCESS_TOKEN env var, skipping auth sequence")
        return {"status":"ok", "agent_mode": AGENT_MODE}

    loop = asyncio.get_event_loop()
    auth_url_future = loop.create_future()
    token_future = loop.create_future()

    def capture_auth_url(url):
        print(f"> capture_auth_url url={url}")
        if not auth_url_future.done():
            auth_url_future.set_result(url)

    async def run_and_capture_token():
        try:
            token = await get_access_token(
                on_auth_url_cb=capture_auth_url,
                callback_url=callback_url,
                user_id=user_id)
        except Exception as e:
            print(f"| get_access_token error: {type(e).__name__}: {e}")
            if not token_future.done():
                token_future.set_exception(e)
            return

        if not token_future.done():
            token_future.set_result(token)

    asyncio.create_task(run_and_capture_token())

    done, _ = await asyncio.wait(
        [auth_url_future, token_future],
        return_when=asyncio.FIRST_COMPLETED
    )

    if auth_url_future in done:
        print(f"| auth required, returning auth_url to client")
        return {"auth_url": auth_url_future.result()}

    if token_future in done and token_future.exception():
        e = token_future.exception()
        print(f"| token_future error: {type(e).__name__}: {e}")
        return {"error": str(e)}

    # token = token_future.result()
    return {"status":"ok", "agent_mode": AGENT_MODE}

async def get_access_token(on_auth_url_cb, callback_url, user_id):
    print("> get_access_token")
    print(f"| callback_url={callback_url}")
    print(f"| user_id={user_id}")
    print(f"| getting workload access token")

    if ENV_VAR_ACCESS_TOKEN:
        print("| Found ACCESS_TOKEN env var, skipping auth sequence")
        return ENV_VAR_ACCESS_TOKEN

    response = identity_client.get_workload_access_token(workload_name=WORKLOAD_IDENTITY_NAME, user_id=user_id)
    workload_access_token = response.get("workloadAccessToken")
    print(f"| workload_access_token={workload_access_token[:10]}...REDACTED...")

    print(f"| getting resource access token")
    access_token = await identity_client.get_token(
        provider_name=CREDENTIAL_PROVIDER_NAME,
        scopes=[],
        auth_flow="USER_FEDERATION",
        agent_identity_token=workload_access_token,
        callback_url=callback_url,
        on_auth_url=on_auth_url_cb,
        force_authentication=False
    )

    print(f"| resource_access_token={access_token[:10]}...REDACTED...")
    # print(response)
    return access_token

async def complete_auth(payload):
    print(f"> complete_auth")
    session_id = payload.get("session_id")
    user_id = payload.get("user_id", DEFAULT_TEST_USER_ID)
    print(f"| session_id={session_id}")
    print(f"| user_id={user_id}")

    try:
        identity_client.complete_resource_token_auth(
            session_uri=session_id,
            user_identifier=UserIdIdentifier(user_id=user_id)
        )
    except ClientError as e:
        meta = e.response.get("ResponseMetadata", {})
        print(f"| complete_resource_token_auth failed")
        print(f"| code={e.response['Error']['Code']}")
        print(f"| message={e.response['Error']['Message']}")
        print(f"| http_status={meta.get('HTTPStatusCode')}")
        print(f"| request_id={meta.get('RequestId')}")
        print(f"| retry_attempts={meta.get('RetryAttempts')}")
        raise
    
    print(f"| auth sequence completed")
    return {"status":"ok"}
