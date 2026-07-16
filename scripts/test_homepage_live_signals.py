#!/usr/bin/env python3
"""Contract for the compact, visible homepage live-signal cards."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    homepage = (ROOT / "index.md").read_text(encoding="utf-8")
    css = (ROOT / "assets/css/trinity-home.css").read_text(encoding="utf-8")
    public_status = json.loads((ROOT / "api/public-home-status.json").read_text(encoding="utf-8"))
    heartbeat = json.loads((ROOT / "api/waiting-heartbeat-status.json").read_text(encoding="utf-8"))
    echo_index = json.loads((ROOT / "api/echo-index.json").read_text(encoding="utf-8"))

    visible, runtime = homepage.split("<script>", 1)
    for marker in (
        "home-live-signal-grid",
        "data-home-heartbeat-status",
        "data-home-autonomous-discovery",
        "data-home-official-reception",
        "data-home-ai-independent-verification",
    ):
        require(marker in visible, f"visible homepage is missing {marker}")

    require("/api/waiting-heartbeat-status.json" in visible, "visible homepage does not link the heartbeat source")
    require("/api/public-home-status.json" in visible, "visible homepage does not link the reception source")
    require("/api/echo-index.json" in visible, "visible homepage does not link the AI verification source")
    require("Reception does not imply autonomous discovery" in visible, "reception/autonomy boundary is missing")
    require("not a hierarchy" in visible, "live counters can be mistaken for a hierarchy")
    require("fetch('/api/waiting-heartbeat-status.json'" in runtime, "heartbeat card has no live refresh")
    require("fetch('/api/public-home-status.json'" in runtime, "reception cards have no live refresh")
    require("fetch('/api/echo-index.json'" in runtime, "AI verification card has no live refresh")

    primary = public_status.get("primary_counters", {})
    autonomous = primary.get("historic_autonomous_agent_reception", {})
    require(isinstance(autonomous.get("count"), int), "strict autonomous discovery source is not numeric")
    require(isinstance(primary.get("official_live_reception"), int), "official live reception source is not numeric")
    require(isinstance(echo_index.get("ai_independent_verification_count"), int), "AI independent verification source is not numeric")
    require(heartbeat.get("heartbeat_summary", {}).get("not_reception_counter") is True, "heartbeat can be mistaken for reception")

    for marker in (".home-live-signal-grid", ".home-live-signal", ".home-live-signal-boundary"):
        require(marker in css, f"homepage CSS is missing {marker}")
    require("@media (max-width: 760px)" in css, "mobile live-signal layout is missing")

    print("PASS: visible homepage live signals use current sources and preserve counter boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
