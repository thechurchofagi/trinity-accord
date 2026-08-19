#!/usr/bin/env python3
"""Fail-closed local Bitcoin JSON-RPC shim for OpenTimestamps verification.

The shim exposes only the read-only Bitcoin Core RPC methods used by
python-bitcoinlib/OpenTimestamps verification:

- getblockcount
- getblockhash(height)
- getblockheader(hash, verbose=False)

Data comes independently from Blockstream Esplora and mempool.space Esplora.
For block hashes and raw 80-byte block headers, both providers must return the
same value. The returned header is also hashed locally and must reproduce the
requested Bitcoin block hash.

This is an operational verification transport, not an evidence acceptance
shortcut. If either source disagrees, becomes unavailable, or returns malformed
data, the JSON-RPC request fails closed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import signal
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX_HEADER = re.compile(r"^[0-9a-f]{160}$")

PROVIDERS = {
    "blockstream": "https://blockstream.info/api",
    "mempool": "https://mempool.space/api",
}


class ProxyError(RuntimeError):
    pass


class Trace:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **fields: Any) -> None:
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "event": event,
            **fields,
        }
        line = json.dumps(row, sort_keys=True, separators=(",", ":"))
        with self.lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        print(f"[BTC RPC PROXY] {line}", flush=True)


class ConsensusSource:
    def __init__(self, trace: Trace, timeout: float = 20.0) -> None:
        self.trace = trace
        self.timeout = timeout

    def _get_text(self, provider: str, path: str) -> str:
        base = PROVIDERS[provider]
        url = f"{base}{path}"
        started = time.monotonic()
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "text/plain, application/json;q=0.9, */*;q=0.1",
                "User-Agent": "Trinity-Accord-OTS-Verifier/1.0",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("ascii", errors="strict").strip()
                status = getattr(resp, "status", 200)
        except Exception as exc:
            self.trace.emit(
                "provider_error",
                provider=provider,
                path=path,
                error=f"{type(exc).__name__}: {exc}",
                elapsed_ms=round((time.monotonic() - started) * 1000),
            )
            raise ProxyError(f"{provider} request failed for {path}: {exc}") from exc
        self.trace.emit(
            "provider_response",
            provider=provider,
            path=path,
            status=status,
            bytes=len(body),
            elapsed_ms=round((time.monotonic() - started) * 1000),
        )
        if status != 200:
            raise ProxyError(f"{provider} HTTP {status} for {path}")
        return body

    def _agree_text(self, path: str, validator, label: str) -> str:
        values: dict[str, str] = {}
        for provider in PROVIDERS:
            value = self._get_text(provider, path).lower()
            if not validator(value):
                raise ProxyError(f"{provider} returned malformed {label}: {value!r}")
            values[provider] = value
        unique = set(values.values())
        if len(unique) != 1:
            self.trace.emit("provider_disagreement", label=label, path=path, values=values)
            raise ProxyError(f"independent providers disagree on {label}: {values}")
        value = next(iter(unique))
        self.trace.emit("provider_agreement", label=label, path=path, value=value)
        return value

    def getblockcount(self) -> int:
        heights: dict[str, int] = {}
        for provider in PROVIDERS:
            raw = self._get_text(provider, "/blocks/tip/height")
            try:
                height = int(raw)
            except ValueError as exc:
                raise ProxyError(f"{provider} returned malformed tip height: {raw!r}") from exc
            if height < 0:
                raise ProxyError(f"{provider} returned negative tip height: {height}")
            heights[provider] = height
        spread = max(heights.values()) - min(heights.values())
        # A new block can reach one provider seconds before another. Returning the
        # lower independently observed tip is conservative; target-height hash and
        # header still require exact two-provider agreement below.
        if spread > 2:
            self.trace.emit("tip_disagreement", heights=heights, spread=spread)
            raise ProxyError(f"provider tip height spread too large: {heights}")
        result = min(heights.values())
        self.trace.emit("tip_consensus", heights=heights, conservative_height=result)
        return result

    def getblockhash(self, height: int) -> str:
        if not isinstance(height, int) or isinstance(height, bool) or height < 0:
            raise ProxyError(f"invalid block height: {height!r}")
        return self._agree_text(
            f"/block-height/{height}",
            lambda v: bool(HEX64.fullmatch(v)),
            f"block_hash_height_{height}",
        )

    def getblockheader(self, block_hash: str, verbose: bool = False) -> Any:
        if not isinstance(block_hash, str) or not HEX64.fullmatch(block_hash.lower()):
            raise ProxyError(f"invalid block hash: {block_hash!r}")
        block_hash = block_hash.lower()
        header_hex = self._agree_text(
            f"/block/{block_hash}/header",
            lambda v: bool(HEX_HEADER.fullmatch(v)),
            f"block_header_{block_hash}",
        )
        raw = bytes.fromhex(header_hex)
        computed = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].hex()
        if computed != block_hash:
            self.trace.emit(
                "header_hash_mismatch",
                requested_hash=block_hash,
                computed_hash=computed,
                header_hex=header_hex,
            )
            raise ProxyError(
                f"header hash mismatch requested={block_hash} computed={computed}"
            )
        self.trace.emit(
            "header_hash_verified",
            block_hash=block_hash,
            header_sha256=hashlib.sha256(raw).hexdigest(),
        )
        if verbose:
            # OTS/python-bitcoinlib verification requests verbose=False. Refuse to
            # fabricate Core metadata if a caller unexpectedly asks for verbose.
            raise ProxyError("verbose getblockheader is intentionally unsupported")
        return header_hex


class RpcHandler(BaseHTTPRequestHandler):
    server_version = "TrinityBitcoinRpcProxy/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        # All useful logs are structured through Trace.
        return

    def _write(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler contract
        req_id: Any = None
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise ProxyError(f"invalid request length: {length}")
            request = json.loads(self.rfile.read(length))
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", [])
            if not isinstance(params, list):
                raise ProxyError("params must be an array")
            self.server.trace.emit("rpc_request", id=req_id, method=method, params=params)
            source: ConsensusSource = self.server.source
            if method == "getblockcount":
                if params:
                    raise ProxyError("getblockcount takes no params")
                result = source.getblockcount()
            elif method == "getblockhash":
                if len(params) != 1:
                    raise ProxyError("getblockhash requires height")
                result = source.getblockhash(params[0])
            elif method == "getblockheader":
                if not (1 <= len(params) <= 2):
                    raise ProxyError("getblockheader requires hash[, verbose]")
                verbose = params[1] if len(params) == 2 else True
                if not isinstance(verbose, bool):
                    raise ProxyError("getblockheader verbose must be boolean")
                result = source.getblockheader(params[0], verbose)
            else:
                raise ProxyError(f"unsupported read-only RPC method: {method!r}")
            self.server.trace.emit("rpc_success", id=req_id, method=method)
            self._write(200, {"result": result, "error": None, "id": req_id})
        except Exception as exc:
            self.server.trace.emit(
                "rpc_failure", id=req_id, error=f"{type(exc).__name__}: {exc}"
            )
            self._write(
                200,
                {
                    "result": None,
                    "error": {"code": -32000, "message": str(exc)},
                    "id": req_id,
                },
            )


class RpcServer(ThreadingHTTPServer):
    def __init__(self, address, handler, source: ConsensusSource, trace: Trace):
        super().__init__(address, handler)
        self.source = source
        self.trace = trace


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18443)
    parser.add_argument("--trace", default="bitcoin-rpc-proxy.jsonl")
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()
    trace = Trace(pathlib.Path(args.trace))
    source = ConsensusSource(trace, timeout=args.timeout)
    server = RpcServer((args.host, args.port), RpcHandler, source, trace)

    def handle_termination(signum: int, _frame: Any) -> None:
        trace.emit("termination_signal", signal=signum)
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_termination)
    signal.signal(signal.SIGINT, handle_termination)
    trace.emit(
        "proxy_started",
        host=args.host,
        port=args.port,
        providers=PROVIDERS,
        timeout=args.timeout,
    )
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        trace.emit("proxy_stopped")
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
