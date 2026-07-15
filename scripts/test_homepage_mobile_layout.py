#!/usr/bin/env python3
"""Regression contract for the homepage-only mobile layout."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    homepage = (ROOT / "index.md").read_text(encoding="utf-8")
    css = (ROOT / "assets/css/trinity-home.css").read_text(encoding="utf-8")

    require("trinity-home.css?v=11" in homepage, "homepage does not request the mobile-layout stylesheet revision")

    mobile_marker = "@media (max-width: 760px) {"
    narrow_marker = "@media (max-width: 340px) {"
    require(css.count(mobile_marker) == 1, "760px homepage breakpoint is missing or duplicated")
    require(css.count(narrow_marker) == 1, "narrow-phone fallback is missing or duplicated")

    desktop, mobile_and_narrow = css.split(mobile_marker, 1)
    mobile, narrow = mobile_and_narrow.split(narrow_marker, 1)

    # Desktop remains a four-column signal grid; all compacting rules stay mobile-only.
    require("grid-template-columns: repeat(4, 1fr);" in desktop, "desktop live-signal grid changed")
    for mobile_only in (
        "padding: 1.25rem 1rem 3rem !important;",
        "main section.home-proof-strip",
        "grid-template-columns: repeat(2, minmax(0, 1fr));",
        ".home-action-primary",
        ".home-live-signal {",
        "min-height: 150px;",
        "min-height: 2.7em;",
        "justify-content: center;",
        "text-wrap: balance;",
    ):
        require(mobile_only in mobile, f"mobile layout is missing {mobile_only}")

    require("main section.home-proof-strip" not in desktop, "mobile section reset leaked into desktop CSS")
    require("grid-template-columns: 1fr;" in narrow, "narrow-phone single-column fallback is missing")
    require("min-height: 125px;" in narrow, "narrow-phone cards are not compacted")

    print("PASS: homepage mobile layout is compact and desktop rules remain unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
