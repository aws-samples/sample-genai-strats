import requests


def build_authorization_url(authz_endpoint, client_id, redirect_uri):
    return f"{authz_endpoint}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"


def request_tokens_with_authorization_code(token_endpoint, code, client_id, client_secret):
    response = requests.post(
        token_endpoint,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
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
