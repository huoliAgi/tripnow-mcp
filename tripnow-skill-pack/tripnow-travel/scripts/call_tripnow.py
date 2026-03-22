#!/usr/bin/env python3
"""
TripNow 旅行助手 — Chat Completions HTTP 调用脚本。

用于在终端或自动化流程中向 TripNow 发起对话请求（票务查询、列车/航班动态、出行政策问答等）。

依赖：httpx（见本包根目录 requirements.txt）
鉴权：环境变量 tripnow_api_key 或 TRIPNOW_API_KEY
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any, List

import httpx

TRIPNOW_API_URL = "https://tripnowengine.133.cn/tripnow/v1/chat/completions"
MODEL = "tripnow-travel-pro"


def get_api_key() -> str:
    return (os.getenv("tripnow_api_key") or os.getenv("TRIPNOW_API_KEY") or "").strip()


def normalize_messages(raw: Any) -> List[dict]:
    if not isinstance(raw, list):
        raise ValueError("messages must be a JSON array")
    out: List[dict] = []
    for item in raw:
        if isinstance(item, dict):
            out.append(
                {
                    "role": item.get("role", "user"),
                    "content": item.get("content", ""),
                }
            )
        else:
            out.append({"role": "user", "content": str(item)})
    return out


async def run(messages: List[dict], timeout: float) -> str:
    key = get_api_key()
    if not key:
        raise RuntimeError("Set tripnow_api_key or TRIPNOW_API_KEY")

    payload = {"model": MODEL, "messages": messages, "stream": False}
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TRIPNOW_API_URL, headers=headers, json=payload, timeout=timeout
        )
        if not response.is_success:
            detail = response.text[:2000] if response.text else response.reason_phrase
            raise RuntimeError(f"HTTP {response.status_code}: {detail}")
        return response.text


async def main() -> int:
    parser = argparse.ArgumentParser(
        description="Call TripNow travel assistant (chat completions API)."
    )
    parser.add_argument(
        "-m",
        "--message",
        help="Single user message (natural language query)",
    )
    parser.add_argument(
        "-j",
        "--messages-json",
        metavar="JSON",
        help='Messages as JSON array, e.g. \'[{"role":"user","content":"..."}]\'',
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="PATH",
        help="JSON file containing a messages array",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="HTTP timeout in seconds (default: 60)",
    )
    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, encoding="utf-8") as fh:
                messages = normalize_messages(json.load(fh))
        elif args.messages_json:
            messages = normalize_messages(json.loads(args.messages_json))
        elif args.message:
            messages = [{"role": "user", "content": args.message}]
        else:
            parser.print_help()
            print(
                "\nExample:\n  export tripnow_api_key=YOUR_KEY\n"
                "  python call_tripnow.py -m '帮我查询明天北京到上海的火车票'\n",
                file=sys.stderr,
            )
            return 2

        text = await run(messages, timeout=args.timeout)
        print(text)
        return 0
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
