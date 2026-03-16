"""api_client.py – HTTP client that calls the Brain API."""
import json
import uuid
from typing import Optional

import httpx

from .auth import make_headers


class BrainClient:
    def __init__(self, base_url: str, client_id: str, client_secret: str, timeout: float = 40.0):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout

    def chat(
        self,
        app_id: str,
        messages: list,
        context: Optional[dict] = None,
        conversation_id: Optional[str] = None,
        screen_image: Optional[str] = None,
    ) -> dict:
        """POST /v1/chat and return the parsed JSON response dict.

        Parameters
        ----------
        screen_image:
            Optional base64-encoded PNG of the current chart/screen.
            Passed as ``context.screen_image`` to the Brain API so Gemini
            can see the visual directly.
        """
        ctx = dict(context or {})
        if screen_image:
            ctx["screen_image"] = screen_image

        payload = {
            "app_id": app_id,
            "conversation_id": conversation_id or str(uuid.uuid4()),
            "context": ctx,
            "messages": messages,
        }
        body_bytes = json.dumps(payload).encode()
        headers = make_headers(self.client_id, self.client_secret, body_bytes)
        headers["Content-Type"] = "application/json"

        with httpx.Client(timeout=self.timeout) as http:
            resp = http.post(f"{self.base_url}/v1/chat", content=body_bytes, headers=headers)
            resp.raise_for_status()
            return resp.json()
