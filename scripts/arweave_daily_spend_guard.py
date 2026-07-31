#!/usr/bin/env python3
"""Fail-closed daily transaction budgets for Trinity Arweave uploads."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "record-chain" / "arweave-wallet-ledger.json"

_DEFAULT_LIMITS = {
    "record_chain_arweave_archive": 1,
    "native_ots_bundle_archive": 1,
}
_ENV_LIMITS = {
    "record_chain_arweave_archive": "ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT",
    "native_ots_bundle_archive": "ARWEAVE_DAILY_NATIVE_OTS_UPLOAD_LIMIT",
}


@dataclass(frozen=True)
class SpendDecision:
    allowed: bool
    kind: str
    utc_date: str
    paid_count: int
    daily_limit: int
    reason: str


def _daily_limit(kind: str) -> int:
    if kind not in _DEFAULT_LIMITS:
        return 0
    raw = os.environ.get(_ENV_LIMITS[kind], str(_DEFAULT_LIMITS[kind]))
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"invalid daily Arweave limit for {kind}: {raw!r}") from exc
    if value < 0 or value > 4:
        raise RuntimeError(f"unsafe daily Arweave limit for {kind}: {value}")
    return value


def evaluate_daily_spend(
    kind: str,
    *,
    ledger_path: Path = DEFAULT_LEDGER,
    now: datetime | None = None,
) -> SpendDecision:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    day = current.date().isoformat()
    limit = _daily_limit(kind)
    if limit < 1:
        return SpendDecision(False, kind, day, 0, limit, "kind_not_authorized")
    try:
        ledger: dict[str, Any] = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"cannot verify paid-upload ledger {ledger_path}: {exc}") from exc
    entries = ledger.get("entries")
    if not isinstance(entries, list):
        raise RuntimeError("Arweave wallet ledger entries are unavailable")
    paid_count = sum(
        1
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("status") == "paid"
        and entry.get("kind") == kind
        and isinstance(entry.get("paid_at"), str)
        and entry["paid_at"][:10] == day
    )
    allowed = paid_count < limit
    return SpendDecision(
        allowed=allowed,
        kind=kind,
        utc_date=day,
        paid_count=paid_count,
        daily_limit=limit,
        reason="under_daily_limit" if allowed else "daily_paid_upload_limit_reached",
    )
