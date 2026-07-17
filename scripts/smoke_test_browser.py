"""Smoke-test a local web app in headless Chrome using the DevTools protocol.

This intentionally uses only the standard library so it can verify the WASM
export without adding Playwright or Selenium to the project.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import socket
import struct
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class DevTools:
    def __init__(self, url: str) -> None:
        parsed = urllib.parse.urlparse(url)
        key = base64.b64encode(os.urandom(16)).decode()
        self.socket = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
        request = (
            f"GET {parsed.path} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{parsed.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.socket.sendall(request.encode())
        response = self.socket.recv(4096)
        if b" 101 " not in response:
            raise RuntimeError(f"WebSocket upgrade failed: {response!r}")
        self.next_id = 0

    def call(self, method: str, params: dict[str, object] | None = None) -> dict:
        self.next_id += 1
        message_id = self.next_id
        payload = json.dumps(
            {"id": message_id, "method": method, "params": params or {}}
        ).encode()
        self.socket.sendall(client_frame(payload))
        while True:
            message = json.loads(self.read_message())
            if message.get("id") == message_id:
                return message

    def read_message(self) -> str:
        parts: list[bytes] = []
        while True:
            first, second = read_exact(self.socket, 2)
            opcode = first & 0x0F
            finished = bool(first & 0x80)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack("!H", read_exact(self.socket, 2))[0]
            elif length == 127:
                length = struct.unpack("!Q", read_exact(self.socket, 8))[0]
            masked = bool(second & 0x80)
            mask = read_exact(self.socket, 4) if masked else b""
            payload = read_exact(self.socket, length)
            if masked:
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
            if opcode == 8:
                raise RuntimeError("Chrome closed the DevTools socket")
            if opcode in (0, 1):
                parts.append(payload)
            if finished and parts:
                return b"".join(parts).decode()


def read_exact(connection: socket.socket, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise RuntimeError("Unexpected end of DevTools socket")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def client_frame(payload: bytes) -> bytes:
    first = 0x81
    length = len(payload)
    if length < 126:
        header = bytes([first, 0x80 | length])
    elif length < 65536:
        header = bytes([first, 0x80 | 126]) + struct.pack("!H", length)
    else:
        header = bytes([first, 0x80 | 127]) + struct.pack("!Q", length)
    mask = os.urandom(4)
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    return header + mask + masked


def open_target(port: int, url: str) -> dict:
    endpoint = f"http://127.0.0.1:{port}/json/new?{urllib.parse.quote(url, safe=':/')}"
    request = urllib.request.Request(endpoint, method="PUT")
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--expect", required=True)
    parser.add_argument("--screenshot")
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()

    port = 9223
    with tempfile.TemporaryDirectory(prefix="aipassport-chrome-") as profile:
        chrome = subprocess.Popen(
            [
                CHROME,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                f"--remote-debugging-port={port}",
                f"--user-data-dir={profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + args.timeout
            while True:
                try:
                    target = open_target(port, args.url)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Chrome DevTools did not start")
                    time.sleep(0.2)

            devtools = DevTools(target["webSocketDebuggerUrl"])
            devtools.call("Runtime.enable")
            while True:
                result = devtools.call(
                    "Runtime.evaluate",
                    {"expression": "document.body.innerText", "returnByValue": True},
                )
                text = (
                    result.get("result", {})
                    .get("result", {})
                    .get("value", "")
                )
                if args.expect in text:
                    break
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"Did not find {args.expect!r}; page text ended with {text[-500:]!r}"
                    )
                time.sleep(0.5)

            if args.screenshot:
                result = devtools.call(
                    "Page.captureScreenshot",
                    {"format": "png", "captureBeyondViewport": False},
                )
                image = base64.b64decode(result["result"]["data"])
                with open(args.screenshot, "wb") as output:
                    output.write(image)

            print(f"PASS: found {args.expect!r} at {args.url}")
        finally:
            chrome.terminate()
            chrome.wait(timeout=10)


if __name__ == "__main__":
    main()
