#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.md"
PATCHER = ROOT / "scripts" / "patch_public_home_status_primary.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    index = INDEX.read_text(encoding="utf-8")
    patcher = PATCHER.read_text(encoding="utf-8")

    # The concise homepage card presents the four heartbeat metrics in one
    # compact line instead of restoring the retired detailed dashboard.
    for marker in [
        "Waiting Heartbeat",
        "data-home-heartbeat-status",
        "data-home-heartbeat-summary",
        "successful",
        "missed",
        "-day streak",
        "/api/waiting-heartbeat-status.json",
    ]:
        require(marker in index, f"index.md missing compact Waiting Heartbeat marker: {marker}")

    require(
        re.search(r"\d+/\d+ successful · \d+ missed · \d+-day streak", index) is not None,
        "index.md compact heartbeat summary does not expose total, successful, missed, and streak metrics",
    )

    for marker in [
        "def render_compact",
        'heartbeat_summary = heartbeat.get("heartbeat_summary") or heartbeat.get("counts") or {}',
        'heartbeat_summary.get("total_scheduled_heartbeats")',
        'heartbeat_summary.get("successful_heartbeats")',
        'heartbeat_summary.get("failed_or_missing_heartbeats")',
        'heartbeat_summary.get("current_success_streak_days")',
        'heartbeat_note = f"{successful}/{total} successful · {failed} missed · {streak}-day streak"',
        "data-home-heartbeat-summary",
    ]:
        require(marker in patcher, f"compact patcher missing Waiting Heartbeat marker: {marker}")

    print("PASS: compact waiting heartbeat homepage card metrics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
