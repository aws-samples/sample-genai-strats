from __future__ import annotations

import base64
import json
import sys
import urllib.parse
import urllib.request
from utils import TMP_DIR, read_value

def get_token() -> dict:
    client_id = read_value("cognito_client_id.txt")
    client_secret = read_value("cognito_client_secret.txt")
    scopes = read_value("cognito_scopes.txt")
    token_endpoint = read_value("cognito_token_endpoint.txt")

    form = {"grant_type": "client_credentials"}
    form["scope"] = scopes
    data = urllib.parse.urlencode(form).encode()

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        token_endpoint,
        data=data,
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        sys.exit(f"error: token request failed ({e.code}): {body}")


if __name__ == "__main__":
    print(f"Retrieving cognito access token...")
    token = get_token()

    print(json.dumps(token, indent=2))

    token_file = TMP_DIR / "cognito_access_token.txt"
    token_file.write_text(token["access_token"])

