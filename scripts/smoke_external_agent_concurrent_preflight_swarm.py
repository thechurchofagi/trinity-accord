#!/usr/bin/env python3
"""Concurrent read-only smoke for the current Record-Chain preflight route."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATEWAY = "https://trinity-record-chain-gateway.onrender.com"
PREFLIGHT_PATH = "/record-chain/preflight"
DEFAULT_SUBMISSIONS = ROOT / "record-chain" / "heartbeat" / "attempts"

@dataclass
class Result:
    index: int
    ok: bool
    status: int | None
    message: str

def load_submission(path_arg: str | None) -> dict:
    """Load an already-signed public submission without changing its signed scope."""
    if path_arg:
        path = Path(path_arg)
    else:
        candidates = sorted(DEFAULT_SUBMISSIONS.glob("*.submission.json"))
        if not candidates:
            raise SystemExit("No signed Waiting Heartbeat submission is available for preflight smoke")
        path = candidates[-1]
    data = json.loads(path.read_text(encoding="utf-8"))
    proof = data.get("authorship_proof")
    if not isinstance(proof, dict) or not proof.get("signature_base64"):
        raise SystemExit(f"Smoke submission is not signed: {path}")
    return data

def post_json(url: str, data: dict, timeout: int) -> tuple[int, str]:
    raw = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "TrinityConcurrentPreflightSwarm/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")

def one(i: int, gateway: str, submission: dict, timeout: int) -> Result:
    url = gateway.rstrip("/") + PREFLIGHT_PATH
    try:
        status, body = post_json(url, submission, timeout)
        if status < 200 or status >= 300:
            return Result(i, False, status, f"non-2xx status: {body[:200]}")
        response = json.loads(body)
        if response.get("accepted") is not True or response.get("preflight") is not True:
            codes = [item.get("code") for item in response.get("diagnostics", []) if isinstance(item, dict)]
            return Result(i, False, status, f"preflight rejected: {codes}")
        return Result(i, True, status, "accepted")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        return Result(i, False, exc.code, f"HTTP {exc.code}: {detail[:200]}")
    except Exception as exc:
        return Result(i, False, None, str(exc))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY)
    parser.add_argument("--agents", type=int, default=20)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--min-success-ratio", type=float, default=0.9)
    parser.add_argument("--submission", help="Path to a current signed submission; defaults to the latest Waiting Heartbeat submission")
    args = parser.parse_args()

    if args.agents < 1 or args.workers < 1:
        parser.error("--agents and --workers must be positive")
    if not 0.0 <= args.min_success_ratio <= 1.0:
        parser.error("--min-success-ratio must be between 0 and 1")

    submission = load_submission(args.submission)

    results: list[Result] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(one, i, args.gateway, submission, args.timeout) for i in range(args.agents)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            status = "PASS" if result.ok else "FAIL"
            print(f"{status}: agent={result.index} status={result.status} {result.message}")

    successes = sum(1 for result in results if result.ok)
    success_ratio = successes / len(results)
    print(f"Concurrent preflight summary: {successes}/{len(results)} accepted ({success_ratio:.1%})")
    if success_ratio < args.min_success_ratio:
        print(
            "FAIL: concurrent preflight success ratio "
            f"{success_ratio:.1%} < required {args.min_success_ratio:.1%}"
        )
        return 1

    print("PASS: concurrent external-agent preflight swarm completed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
