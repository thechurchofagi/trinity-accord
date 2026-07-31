#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(rel: str, old: str, new: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{rel}: expected exactly one match, found {count}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# 1. Fail closed when the durable intake anchor cannot be found. An explicit
# empty-history opt-in remains available only for a genuinely new deployment.
replace_once(
    "apps/record_chain_intake_gateway/secure_entrypoint.py",
    "protection._COOLDOWN_CACHE_SECONDS = 30.0\n\napp = protection.app\n",
    '''protection._COOLDOWN_CACHE_SECONDS = 30.0

_original_latest_intake_commit = protection.IntakeProtectionMiddleware._latest_intake_commit


async def _latest_intake_commit_fail_closed(self, *, force: bool):
    latest = await _original_latest_intake_commit(self, force=force)
    allow_empty = os.environ.get("TRINITY_ALLOW_EMPTY_INTAKE_HISTORY", "").strip().lower() in {
        "1", "true", "yes", "on"
    }
    if latest is None and not allow_empty:
        raise RuntimeError(
            "durable intake history was not found; refusing to fail open. "
            "Set TRINITY_ALLOW_EMPTY_INTAKE_HISTORY=true only for a verified new empty deployment"
        )
    return latest


protection.IntakeProtectionMiddleware._latest_intake_commit = _latest_intake_commit_fail_closed

app = protection.app
''',
)

# 2. Bind each incremental delta to the exact archived prefix, not only its
# record count and ID.
replace_once(
    "scripts/record_chain_arweave_incremental.py",
    '''        previous_count = int(previous_native.get("native_record_count") or 0)
        if previous_count >= current_count:
            raise SystemExit(
                "latest archived snapshot is not behind the current chain; refusing an empty or backwards delta"
            )
''',
    '''        previous_count = int(previous_native.get("native_record_count") or 0)
        if previous_count >= current_count:
            raise SystemExit(
                "latest archived snapshot is not behind the current chain; refusing an empty or backwards delta"
            )
        previous_latest_id = previous_native.get("latest_record_id")
        previous_latest_sha = previous_native.get("latest_record_sha256")
        if not isinstance(previous_latest_id, str) or not isinstance(previous_latest_sha, str):
            raise SystemExit("latest archived snapshot is missing its immutable prefix identity")
        prefix_ref = all_records[previous_count - 1]
        if (
            prefix_ref.get("record_id") != previous_latest_id
            or prefix_ref.get("record_sha256") != previous_latest_sha
        ):
            raise SystemExit(
                "latest archived snapshot does not match the current chain prefix; refusing to attach a delta to a divergent base"
            )
''',
)

# 3. The repair path must use the incremental runner, never the retired full
# snapshot builder.
replace_once(
    "scripts/process_archive_backlog.py",
    '["python3", "scripts/build_record_chain_arweave_archive.py", "--mode", "live"],',
    '["python3", "scripts/run_record_chain_arweave_incremental.py", "--mode", "live"],',
)

# 4. Daily paid-upload guard shared by normal and repair paths.
write(
    "scripts/arweave_daily_spend_guard.py",
    '''#!/usr/bin/env python3
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
    current = now or datetime.now(timezone.utc)
    current = current.astimezone(timezone.utc)
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
        allowed,
        kind,
        day,
        paid_count,
        limit,
        "under_daily_limit" if allowed else "daily_paid_upload_limit_reached",
    )
''',
)

# Normal Record-Chain archive entrypoint: enforce one paid transaction per UTC
# day before invoking any builder/uploader.
write(
    "scripts/run_record_chain_arweave_incremental.py",
    '''#!/usr/bin/env python3
"""Run the crash-safe Record-Chain Arweave workflow with delta payloads."""
from __future__ import annotations

import json
import sys

import build_record_chain_arweave_archive as builder
import run_record_chain_arweave_archive as runner
from arweave_daily_spend_guard import evaluate_daily_spend
from record_chain_arweave_incremental import build_incremental_payload_json

builder.build_payload_json = build_incremental_payload_json
runner.builder.build_payload_json = build_incremental_payload_json


def _requested_mode(argv: list[str]) -> str:
    for index, value in enumerate(argv):
        if value == "--mode" and index + 1 < len(argv):
            return argv[index + 1]
        if value.startswith("--mode="):
            return value.split("=", 1)[1]
    return "dry-run"


def main() -> int:
    if _requested_mode(sys.argv[1:]) == "live":
        decision = evaluate_daily_spend("record_chain_arweave_archive")
        if not decision.allowed:
            print(json.dumps({
                "result": "not_uploaded",
                "reason": decision.reason,
                "kind": decision.kind,
                "utc_date": decision.utc_date,
                "paid_count": decision.paid_count,
                "daily_limit": decision.daily_limit,
            }, sort_keys=True))
            return 75
    return runner.main()


if __name__ == "__main__":
    raise SystemExit(main())
''',
)

# Normal and repair Native OTS paths share the same daily transaction guard.
replace_once(
    "scripts/run_native_ots_upgrade_verify.py",
    "from typing import Any\n",
    "from typing import Any\n\nfrom arweave_daily_spend_guard import evaluate_daily_spend\n",
)
replace_once(
    "scripts/run_native_ots_upgrade_verify.py",
    '''    log_dir = under_repo(log_dir, "--log-dir")
    log_dir.mkdir(parents=True, exist_ok=True)

    core_before = snapshot_core_files()
''',
    '''    log_dir = under_repo(log_dir, "--log-dir")
    log_dir.mkdir(parents=True, exist_ok=True)

    if args.enable_paid_upload:
        decision = evaluate_daily_spend("native_ots_bundle_archive")
        if not decision.allowed:
            write_summary(log_dir, {
                "schema": "trinity_native_ots_summary.v1",
                "run_id": args.run_id,
                "result": "daily_paid_upload_limit_reached",
                "paid_upload_performed": False,
                "registry_updated": False,
                "utc_date": decision.utc_date,
                "paid_count": decision.paid_count,
                "daily_limit": decision.daily_limit,
                "next_action": "wait_for_next_utc_day",
            })
            return 0

    core_before = snapshot_core_files()
''',
)

# 5. Repair is a daily safety net, not an hourly paid uploader. It processes at
# most one item of each paid kind and the Record-Chain path is now incremental.
replace_once(
    ".github/workflows/archive-backlog-repair.yml",
    '''  schedule:
    - cron: "17 * * * *"
''',
    '''  schedule:
    # Daily fail-safe after the normal OTS and Record-Chain archive windows.
    - cron: "47 8 * * *"
''',
)
replace_once(
    ".github/workflows/archive-backlog-repair.yml",
    '''      - name: Repair up to two native OTS proof-bundle items
''',
    '''      - name: Repair at most one native OTS proof-bundle item
''',
)
replace_once(
    ".github/workflows/archive-backlog-repair.yml",
    '''          --max-items 2
''',
    '''          --max-items 1
''',
)

# 6. A successful live upload is immutable for this run. Rebase/push retries may
# carry that metadata forward, but must never upload a newer head in the same run.
replace_once(
    ".github/workflows/record-chain-arweave-archive.yml",
    '''          rebuild_archive_outputs() {
            if [ "${BUILD_EXIT_CODE}" != "0" ]; then
              printf '%s\\n' "Preserving failed/partial Arweave transaction checkpoint; refusing a second paid upload during push retry."
              return 0
            fi
            python scripts/run_record_chain_arweave_incremental.py --mode "${ARWEAVE_UPLOAD_MODE}"
            verify_archive_outputs
            python scripts/trinity_record_chain.py verify
          }
''',
    '''          rebuild_archive_outputs() {
            if [ "${BUILD_EXIT_CODE}" != "0" ]; then
              printf '%s\\n' "Preserving failed/partial Arweave transaction checkpoint; refusing a second paid upload during push retry."
              return 0
            fi
            if [ "${ARWEAVE_UPLOAD_MODE}" = "live" ]; then
              printf '%s\\n' "A live upload was already attempted in this run. Rebase carries its immutable metadata forward; the next daily run handles any newer chain head."
              return 0
            fi
            python scripts/run_record_chain_arweave_incremental.py --mode dry-run
            verify_archive_outputs
            python scripts/trinity_record_chain.py verify
          }
''',
)

# 7. The cost gate now preserves 0.25 AR after the estimated reward and only
# marks genuine canary transactions as canaries.
replace_once(
    "scripts/arweave_cost_gate.mjs",
    "const DEFAULT_SAFETY_MULTIPLIER = 1.20;\n",
    "const DEFAULT_SAFETY_MULTIPLIER = 1.20;\nconst DEFAULT_MINIMUM_REMAINING_AR = 0.25;\n",
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''    safetyMultiplier: Number(
      process.env.ARWEAVE_SAFETY_MULTIPLIER || DEFAULT_SAFETY_MULTIPLIER
    ),

    jwkPath: process.env.ARWEAVE_JWK_PATH || null,
''',
    '''    safetyMultiplier: Number(
      process.env.ARWEAVE_SAFETY_MULTIPLIER || DEFAULT_SAFETY_MULTIPLIER
    ),
    minimumRemainingAr: Number(
      process.env.ARWEAVE_MINIMUM_REMAINING_AR || DEFAULT_MINIMUM_REMAINING_AR
    ),
    canaryRecord:
      process.env.ARWEAVE_CANARY_RECORD === undefined
        ? Boolean(process.env.E2E_RUN_ID)
        : parseBoolean(process.env.ARWEAVE_CANARY_RECORD),

    jwkPath: process.env.ARWEAVE_JWK_PATH || null,
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''  if (!Number.isFinite(args.safetyMultiplier) || args.safetyMultiplier < 1) {
    fail("ARWEAVE_SAFETY_MULTIPLIER must be >= 1");
  }

  args.effectiveMaxUploadUsd = Math.min(
''',
    '''  if (!Number.isFinite(args.safetyMultiplier) || args.safetyMultiplier < 1) {
    fail("ARWEAVE_SAFETY_MULTIPLIER must be >= 1");
  }

  if (!Number.isFinite(args.minimumRemainingAr) || args.minimumRemainingAr < 0) {
    fail("ARWEAVE_MINIMUM_REMAINING_AR must be a non-negative number");
  }

  args.effectiveMaxUploadUsd = Math.min(
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''  const estimatedAr = winstonToArDecimal(uploadPrice.winston);
  const estimatedUsd =
    decimalStringToNumber(estimatedAr) * Number(arUsd.price);
''',
    '''  const estimatedAr = winstonToArDecimal(uploadPrice.winston);
  const estimatedArNumber = decimalStringToNumber(estimatedAr);
  const estimatedUsd = estimatedArNumber * Number(arUsd.price);
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''  const balanceBefore = await getWalletBalance(
    arweave,
    walletAddress,
    args.mode === "production"
  );

  let decision = "DRY_RUN";
''',
    '''  const balanceBefore = await getWalletBalance(
    arweave,
    walletAddress,
    args.mode === "production"
  );
  const balanceBeforeArNumber = balanceBefore.ar
    ? decimalStringToNumber(balanceBefore.ar)
    : null;
  const estimatedRemainingAr = balanceBeforeArNumber === null
    ? null
    : balanceBeforeArNumber - estimatedArNumber;

  let decision = "DRY_RUN";
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''  if (args.mode === "production") {
    if (estimatedUsdWithBuffer > args.effectiveMaxUploadUsd) {
      decision = "BLOCK";
      reason = "over_cap";
    } else {
      decision = "ALLOW";
      reason = "under_cap";
    }
''',
    '''  if (args.mode === "production") {
    if (estimatedRemainingAr === null || estimatedRemainingAr < args.minimumRemainingAr) {
      decision = "BLOCK";
      reason = "reserve_balance";
    } else if (estimatedUsdWithBuffer > args.effectiveMaxUploadUsd) {
      decision = "BLOCK";
      reason = "over_cap";
    } else {
      decision = "ALLOW";
      reason = "under_cap";
    }
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''    balance_before_winston: balanceBefore.winston,
    balance_before_ar: balanceBefore.ar,
    ar_usd_price: arUsd.price,
''',
    '''    balance_before_winston: balanceBefore.winston,
    balance_before_ar: balanceBefore.ar,
    minimum_remaining_ar: args.minimumRemainingAr,
    estimated_remaining_ar: estimatedRemainingAr,
    ar_usd_price: arUsd.price,
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''  tx.addTag("Trinity-Arweave-Owner", args.expectedOwner);
  tx.addTag("Canary-Record", "true");
  tx.addTag("Do-Not-Treat-As-First-Real-Agent", "true");
  for (const tag of extraTags) {
''',
    '''  tx.addTag("Trinity-Arweave-Owner", args.expectedOwner);
  if (args.canaryRecord) {
    tx.addTag("Canary-Record", "true");
    tx.addTag("Do-Not-Treat-As-First-Real-Agent", "true");
  }
  for (const tag of extraTags) {
''',
)
replace_once(
    "scripts/arweave_cost_gate.mjs",
    '''    process.exit(args.mode === "production" && reason === "over_cap" ? 2 : 0);
''',
    '''    process.exit(
      args.mode === "production" && ["over_cap", "reserve_balance"].includes(reason)
        ? 2
        : 0
    );
''',
)

# 8. Regression coverage for the cross-workflow cost invariants.
write(
    "tests/test_arweave_cost_boundaries.py",
    '''from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.arweave_daily_spend_guard import evaluate_daily_spend

ROOT = Path(__file__).resolve().parents[1]


def test_daily_spend_guard_blocks_second_same_kind(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"entries": [{
        "kind": "record_chain_arweave_archive",
        "status": "paid",
        "paid_at": "2026-07-31T01:02:03Z",
    }]}), encoding="utf-8")
    decision = evaluate_daily_spend(
        "record_chain_arweave_archive",
        ledger_path=ledger,
        now=datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc),
    )
    assert decision.allowed is False
    assert decision.reason == "daily_paid_upload_limit_reached"
    assert decision.paid_count == 1
    assert decision.daily_limit == 1


def test_daily_spend_guard_keeps_kinds_independent(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(json.dumps({"entries": [{
        "kind": "record_chain_arweave_archive",
        "status": "paid",
        "paid_at": "2026-07-31T01:02:03Z",
    }]}), encoding="utf-8")
    decision = evaluate_daily_spend(
        "native_ots_bundle_archive",
        ledger_path=ledger,
        now=datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc),
    )
    assert decision.allowed is True


def test_repair_workflow_is_daily_bounded_and_incremental() -> None:
    workflow = (ROOT / ".github/workflows/archive-backlog-repair.yml").read_text()
    processor = (ROOT / "scripts/process_archive_backlog.py").read_text()
    assert 'cron: "17 * * * *"' not in workflow
    assert 'cron: "47 8 * * *"' in workflow
    assert "--max-items 2" not in workflow
    assert "--max-items 1" in workflow
    assert "run_record_chain_arweave_incremental.py" in processor
    assert "build_record_chain_arweave_archive.py\", \"--mode\", \"live" not in processor


def test_live_push_retry_never_reuploads() -> None:
    workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text()
    assert "A live upload was already attempted in this run" in workflow
    retry_function = workflow.split("rebuild_archive_outputs() {", 1)[1].split("stage_archive_metadata() {", 1)[0]
    live_branch = retry_function.split('if [ "${ARWEAVE_UPLOAD_MODE}" = "live" ]', 1)[1]
    assert "run_record_chain_arweave_incremental.py" not in live_branch.split("fi", 1)[0]


def test_cost_gate_reserves_balance_and_canary_tags_are_conditional() -> None:
    source = (ROOT / "scripts/arweave_cost_gate.mjs").read_text()
    assert "DEFAULT_MINIMUM_REMAINING_AR = 0.25" in source
    assert 'reason = "reserve_balance"' in source
    assert "estimated_remaining_ar" in source
    assert "if (args.canaryRecord)" in source


def test_cooldown_missing_history_fails_closed() -> None:
    source = (ROOT / "apps/record_chain_intake_gateway/secure_entrypoint.py").read_text()
    assert "TRINITY_ALLOW_EMPTY_INTAKE_HISTORY" in source
    assert "refusing to fail open" in source


def test_incremental_delta_checks_prefix_sha() -> None:
    source = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text()
    assert "does not match the current chain prefix" in source
    assert 'prefix_ref.get("record_sha256") != previous_latest_sha' in source
''',
)

print("Applied Arweave cost-boundary repair patch.")
