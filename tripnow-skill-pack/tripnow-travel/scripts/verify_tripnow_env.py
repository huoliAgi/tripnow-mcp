#!/usr/bin/env python3
"""检查 TripNow API Key 是否已通过环境变量配置。"""

import os
import sys


def main() -> int:
    key = (os.getenv("tripnow_api_key") or os.getenv("TRIPNOW_API_KEY") or "").strip()
    if key:
        print("OK: tripnow_api_key or TRIPNOW_API_KEY is set.")
        return 0
    print(
        "MISSING: set tripnow_api_key or TRIPNOW_API_KEY in the environment.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
