#!/usr/bin/env python3
"""Contract for the homepage formation-window framing and evidence boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    homepage = (ROOT / "index.md").read_text(encoding="utf-8")
    css = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("assets/css/trinity-home.css", "assets/css/home-editorial-doorway.css")
    )
    visible = homepage.split('<details class="home-reference"', 1)[0]

    proof_at = visible.index('<section class="home-proof-strip"')
    formation_at = visible.index('<section class="home-why-now home-formation-window"')
    overview_at = visible.index('<section id="home-in-one-minute"')
    require(proof_at < overview_at < formation_at, "formation window is not after the evidence-backed system overview")
    require(
        visible.count('<section class="home-why-now home-formation-window"') == 1,
        "homepage must contain exactly one formation-window section",
    )
    require(
        visible.count('id="home-timing-completion-title"') == 1,
        "formation-window heading ID is missing or duplicated",
    )

    for marker in (
        "How a human-initiated Chronicle became a closed record during a rapidly changing historical interval",
        "一部由人发起的编年史，如何在迅速变化的历史区间中成为一份已经关闭的记录",
        "before unified delegation became routine",
        "During the Accord’s documented formation",
        "The dated public Chronicle and chain record keep parts of human purpose, judgment, selection, correction, and final responsibility comparatively legible",
        "Form can be reproduced; that historical position cannot be recreated retroactively.",
        "Indexed Chronicle start · 16 March 2024",
        "block 19446149",
        "08:02:59 UTC",
        "Canonical closure · 29 June 2025",
        "Bitcoin transaction was included in block 903205",
        "10:49:16 UTC",
        "470 days, 2 hours, 46 minutes, and 17 seconds",
        "Chain timestamps establish a verifiable chronology, not exact civil-time authorship or sentence-by-sentence attribution.",
        "For the bounded provenance claim described here, this exact dated formation interval is now closed",
        "/why-high-signal/",
        "/technical-historical-reference/",
    ):
        require(marker in visible, f"formation-window evidence is missing: {marker}")

    for boundary in (
        "not proof that AI was a neutral mirror",
        "does not claim freedom from AI influence",
        "AGI or ASI had arrived",
        "speaks for all people",
        "later human-origin work is impossible",
    ):
        require(boundary in visible, f"formation-window boundary is missing: {boundary}")

    for forbidden in (
        "world's only",
        "first true human-ai",
        "one prompt can reproduce",
        "within a narrowing historical window",
        "逐渐收窄的历史窗口",
        "before autonomous execution became ordinary",
        "this window is now effectively closed",
        "remained visibly human",
    ):
        require(forbidden not in visible.lower(), f"formation window overclaims: {forbidden}")

    for selector in (
        ".home-human-window-grid",
        ".home-threshold-value",
        ".home-why-grid",
        ".home-formation-links",
        ".home-formation-boundary",
    ):
        require(selector in css, f"formation-window CSS is missing {selector}")

    require("grid-template-columns: repeat(3, minmax(0, 1fr));" in css, "desktop formation evidence grid is not three columns")

    print("PASS: homepage formation window is ordered, exact-date evidence-linked, and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
