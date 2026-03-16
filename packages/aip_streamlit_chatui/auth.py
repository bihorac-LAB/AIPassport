"""auth.py – HMAC-SHA256 request signing for AIP chat widget.

The module app calls `make_headers(client_id, client_secret, body_bytes)`
and passes the returned dict as HTTP headers to the Brain API.
"""
from __future__ import annotations
import hashlib
import hmac
import time


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_headers(client_id: str, client_secret: str, body_bytes: bytes) -> dict[str, str]:
    """Return HMAC-signed headers for a Brain API request.

    Headers:
        X-AIP-Client    – the module app's client_id
        X-AIP-Timestamp – current Unix time (seconds)
        X-AIP-Signature – HMAC-SHA256(secret, timestamp + "." + sha256(body))
    """
    timestamp = str(int(time.time()))
    body_hash = _sha256_hex(body_bytes)
    message = f"{timestamp}.{body_hash}".encode()
    signature = hmac.new(client_secret.encode(), message, hashlib.sha256).hexdigest()
    return {
        "X-AIP-Client": client_id,
        "X-AIP-Timestamp": timestamp,
        "X-AIP-Signature": signature,
    }
