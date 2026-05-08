import boto3
import os
import asyncio
from bedrock_agentcore.services.identity import IdentityClient, UserIdIdentifier

USER_ID="user3"
WORKLOAD_IDENTITY_NAME = os.getenv("WORKLOAD_IDENTITY_NAME")
CREDENTIAL_PROVIDER_NAME = os.getenv("CREDENTIAL_PROVIDER_NAME")
print(f"WORKLOAD_IDENTITY_NAME={WORKLOAD_IDENTITY_NAME}")
print(f"CREDENTIAL_PROVIDER_NAME={CREDENTIAL_PROVIDER_NAME}")
print(f"USER_ID={USER_ID}")

region = boto3.session.Session().region_name
identity_client = IdentityClient(region)

async def initialize(payload):
    print("> initialize")

    loop = asyncio.get_event_loop()
    auth_url_future = loop.create_future()
    token_future = loop.create_future()

    def capture_auth_url(url):
        print(f"> capture_auth_url url={url}")
        if not auth_url_future.done():
            auth_url_future.set_result(url)

    async def run_and_capture_token():
        token = await get_access_token(on_auth_url_cb=capture_auth_url)
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

    # token = token_future.result()
    return {"status":"ok"}


async def get_access_token(on_auth_url_cb):
    print("> get_access_token")
    print(f"| getting workload access token")
    response = identity_client.get_workload_access_token(workload_name=WORKLOAD_IDENTITY_NAME, user_id=USER_ID)
    workload_access_token = response.get("workloadAccessToken")
    print(f"| workload_access_token={workload_access_token[:10]}...REDACTED...")

    print(f"| getting resource access token")
    access_token = await identity_client.get_token(
        provider_name=CREDENTIAL_PROVIDER_NAME,
        scopes=["profile"],
        auth_flow="USER_FEDERATION",
        agent_identity_token=workload_access_token,
        callback_url="https://9svcav6rs3.execute-api.us-east-1.amazonaws.com",
        on_auth_url=on_auth_url_cb,
        force_authentication=False
    )

    print(f"| resource_access_token={access_token[:10]}...REDACTED...")
    # print(response)
    return access_token

async def complete_auth(session_id):
    print(f"> complete_auth session_id={session_id}")
    identity_client.complete_resource_token_auth(
        session_uri=session_id,
        user_identifier=UserIdIdentifier(user_id=USER_ID)
    )
    print(f"| session completed")
    return {"status":"ok"}
