#!/usr/bin/env python3
"""Contract for the homepage formation-window framing and evidence boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    homepage = (ROOT / "index.md").read_text(encoding="utf-8")
    css = (ROOT / "assets/css/trinity-home.css").read_text(encoding="utf-8")
    visible = homepage.split('<details class="home-reference"', 1)[0]

    proof_at = visible.index('<section class="home-proof-strip"')
    formation_at = visible.index('<section class="home-why-now home-formation-window"')
    overview_at = visible.index('<section id="home-in-one-minute"')
    require(proof_at < formation_at < overview_at, "formation window is not between evidence and system overview")

    for marker in (
        "Created across the 2024–2025 shift from conversational AI",
        "The form can be reproduced. The formation conditions cannot.",
        "From March 2024 through June 2025",
        "final August 2025 record preserved the website",
        "original model states, human labor pattern, or dated sequence",
        "/chronicle/",
        "/archive_legacy_index_2025_09/",
    ):
        require(marker in visible, f"formation-window evidence is missing: {marker}")

    for boundary in (
        "not proof of external events",
        "AI consciousness",
        "autonomous authorship",
        "historical uniqueness",
        "philosophical truth",
    ):
        require(boundary in visible, f"formation-window boundary is missing: {boundary}")

    for forbidden in ("world's only", "first true human-ai", "one prompt can reproduce"):
        require(forbidden not in visible.lower(), f"formation window overclaims: {forbidden}")

    for selector in (".home-era-note", ".home-formation-links", ".home-formation-boundary"):
        require(selector in css, f"formation-window CSS is missing {selector}")

    print("PASS: homepage formation window is early, evidence-linked, and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
