#!/usr/bin/env python3
"""Pretty-print the /health/ready payload for `./run.sh status`.

A separate file rather than an inline `python3 -c` so the quoting stays readable.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    print(f"      readiness: {data.get('status', 'unknown')}")
    for check in data.get("checks", []):
        mark = "ok  " if check.get("ok") else "FAIL"
        detail = check.get("detail") or ""
        print(f"        [{mark}] {check.get('name')}{': ' + detail if detail else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
