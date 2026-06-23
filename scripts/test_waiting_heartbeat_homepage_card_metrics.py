#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.md"
PATCHER = ROOT / "scripts" / "patch_public_home_status_primary.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    index = INDEX.read_text(encoding="utf-8")
    patcher = PATCHER.read_text(encoding="utf-8")

    for marker in [
        "Waiting Heartbeat",
        "Total scheduled heartbeats",
        "Successful heartbeats",
        "Failed / missed heartbeats",
        "Current success streak",
        "累计心跳",
        "最近连续成功",
    ]:
        require(marker in index, f"index.md missing Waiting Heartbeat metric marker: {marker}")

    # JS live fetch must also preserve the same metrics.
    for marker in [
        "var summary = d.heartbeat_summary || {{}}",
        "total_scheduled_heartbeats",
        "successful_heartbeats",
        "failed_or_missing_heartbeats",
        "current_success_streak_days",
        "Failed / missed heartbeats",
        "Current success streak",
        "\u7d2f\u8ba1\u5fc3\u8df3",
    ]:
        require(marker in patcher, f"patcher live JS missing Waiting Heartbeat marker: {marker}")

    print("PASS: waiting heartbeat homepage card metrics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
