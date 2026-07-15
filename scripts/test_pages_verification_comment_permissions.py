#!/usr/bin/env python3
"""Keep Pages verification truth separate from optional PR evidence comments."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = [
    ROOT / ".github/workflows/verify-pages-production.yml",
    ROOT / ".github/workflows/verify-current-pages.yml",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    for path in WORKFLOWS:
        text = path.read_text(encoding="utf-8")
        header = text.split("jobs:", 1)[0]
        require("pull-requests: write" in header, f"{path.name} cannot comment on its evidence PR")
        require("issues: write" not in header, f"{path.name} retains unnecessary issue-write permission")
        require(text.count("if ! gh pr comment") >= 2, f"{path.name} lets optional comments override deployment truth")
        require('test "$overall" = "success"' in text, f"{path.name} does not fail on a real production mismatch")

    print("PASS: Pages verification permissions are minimal and comment failures cannot mask deployment truth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
