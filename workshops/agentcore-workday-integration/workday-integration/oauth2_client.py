import base64
import hashlib
import os
import requests


def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")

def derive_code_challenge(code_verifier):
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

def build_authorization_url(authz_endpoint, client_id, redirect_uri, code_challenge):
    return (
        f"{authz_endpoint}?client_id={client_id}&redirect_uri={redirect_uri}"
        f"&response_type=code&code_challenge={code_challenge}&code_challenge_method=S256"
    )


def request_tokens_with_authorization_code(token_endpoint, code, client_id, client_secret, code_verifier):
    response = requests.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "code_verifier": code_verifier,
        },
    )
    response.raise_for_status()
    return response.json()


def request_tokens_with_refresh_token(token_endpoint, refresh_token, client_id, client_secret):
    response = requests.post(
        token_endpoint,
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    response.raise_for_status()
    return response.json()
