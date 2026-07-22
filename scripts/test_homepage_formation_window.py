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

    for marker in (
        "Why an ordinary person chose to leave this record during a rapidly closing historical window",
        "为什么一个普通人选择在迅速关闭的历史窗口内留下这份记录",
        "before end-to-end delegated execution became broadly available",
        "During the Accord’s documented formation",
        "the preserved process kept human purpose, judgment, selection, correction, and final responsibility comparatively legible",
        "Form can be reproduced; the same attribution conditions cannot be recreated retroactively.",
        "Documented start · 16 March 2024",
        "Ethereum block 19446149",
        "08:02:59 UTC",
        "Canonical closure · 29 June 2025",
        "Bitcoin transaction was included in block 903205",
        "10:49:16 UTC",
        "470 days, 2 hours, 46 minutes, and 17 seconds",
        "Chain timestamps establish a verifiable chronology, not exact civil-time authorship.",
        "For the first-generation provenance claim described here, this exact window is now closed",
        "/why-high-signal/",
        "/technical-historical-reference/",
    ):
        require(marker in visible, f"formation-window evidence is missing: {marker}")

    for boundary in (
        "not proof that AI is a neutral mirror of humanity",
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
