import os
import requests
from pathlib import Path

import oauth2_client


def acquire_tokens(client_name, client_id, client_secret, authz_endpoint, token_endpoint, redirect_uri):
    refresh_token_path = Path(f"./../tmp/{client_name}_refresh_token.txt")
    access_token_path = Path(f"./../tmp/{client_name}_access_token.txt")

    print("-" * 20)
    if refresh_token_path.exists():
        print("Refresh token found. Attempting token refresh...")
        try:
            tokens = oauth2_client.request_tokens_with_refresh_token(
                token_endpoint,
                refresh_token_path.read_text(),
                client_id,
                client_secret,
            )
            print("| Token refresh succeeded")
        except requests.HTTPError as e:
            print(f"| Token refresh failed ({e}). Falling back to authorization_code flow...")
            tokens = _authorization_code_flow(token_endpoint, authz_endpoint, redirect_uri, client_id, client_secret)
    else:
        print("No refresh token found. Starting authorization_code flow...")
        tokens = _authorization_code_flow(token_endpoint, authz_endpoint, redirect_uri, client_id, client_secret)

    _save_tokens(tokens, access_token_path, refresh_token_path)
    return tokens.get('access_token')


def _authorization_code_flow(token_endpoint, authz_endpoint, redirect_uri, client_id, client_secret):
    print("-" * 20)
    authorization_url = oauth2_client.build_authorization_url(authz_endpoint, client_id, redirect_uri)
    print("Open the following URL in your browser. Login and provide consent. Paste Authorization Code back into the Terminal.")
    print("")
    print(authorization_url)

    authorization_code = input("\nPaste Authorization Code: ")
    print(f"\nReceived authorization Code: {authorization_code}")

    print("-" * 20)
    print("Retrieving access/refresh tokens via authorization_code grant")

    return oauth2_client.request_tokens_with_authorization_code(
        token_endpoint, authorization_code, client_id, client_secret,
    )


def _save_tokens(tokens, access_token_path, refresh_token_path):
    os.makedirs("./../tmp", exist_ok=True)
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    access_token_path.write_text(access_token)
    refresh_token_path.write_text(refresh_token)
    print(f"| access_token={access_token[:10]}...REDACTED...")
    print(f"| refresh_token={refresh_token[:10]}...REDACTED...")
    print("| Tokens saved to ./tmp/")
