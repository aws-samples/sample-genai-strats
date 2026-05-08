import httpx

class LocalTransport:
    def __init__(self, url: str = "http://localhost:8080/invocations"):
        self.url = url

    def _post(self, cmd: dict) -> dict:
        response = httpx.post(self.url, json=cmd, timeout=60.0)
        response.raise_for_status()
        return response.json()

    def initialize(self) -> str | None:
        result = self._post({"cmd": "initialize"})
        return result.get("auth_url")

    def complete_auth(self, session_id: str) -> None:
        self._post({"cmd": "completeAuth", "session_id": session_id})

    def send_prompt(self, prompt: str) -> str:
        result = self._post({"cmd": "prompt", "prompt": prompt})
        return result.get("response", result.get("error", "No response"))
