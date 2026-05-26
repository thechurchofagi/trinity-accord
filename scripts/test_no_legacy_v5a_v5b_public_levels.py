#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_RE = re.compile(r"\bV5[ab]\b")

ALLOWED_TEXT_PATH_PARTS = {
    "RED-TEAM",
    "corrections-index",
    "archive_legacy",
    "legacy",
    "CHANGELOG",
}

LEVEL_KEYS = {
    "used_for_levels",
    "protocol_levels",
    "verification_levels",
    "levels",
    "current_levels",
    "required_levels",
}

def allowed_path(path: Path) -> bool:
    s = str(path)
    return any(part in s for part in ALLOWED_TEXT_PATH_PARTS)

def walk_json(obj, path, key_path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            next_path = f"{key_path}.{k}" if key_path else k
            if k in LEVEL_KEYS:
                flat = json.dumps(v, ensure_ascii=False)
                assert not LEGACY_RE.search(flat), (
                    f"Legacy V5a/V5b found in current level key {next_path} in {path}"
                )
            walk_json(v, path, next_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_json(v, path, f"{key_path}[{i}]")
    elif isinstance(obj, str):
        if LEGACY_RE.search(obj) and "legacy" not in key_path.lower() and "deprecated" not in key_path.lower():
            raise AssertionError(f"Legacy V5a/V5b string not marked legacy at {path}:{key_path}")

def main():
    for path in list((ROOT / "api").glob("*.json")) + [ROOT / ".well-known/trinity-accord.json"]:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        walk_json(data, path.relative_to(ROOT))

    public_text_files = [
        ROOT / "verify.md",
        ROOT / "agent-verify.md",
        ROOT / "agent-verify-simple.md",
        ROOT / "verification-materials.md",
        ROOT / "README.md",
        ROOT / "llms.txt",
        ROOT / "llms-full.txt",
    ]
    for path in public_text_files:
        if not path.exists() or allowed_path(path):
            continue
        text = path.read_text(encoding="utf-8")
        if LEGACY_RE.search(text):
            assert "not current protocol levels" in text or "legacy" in text.lower(), (
                f"{path.relative_to(ROOT)} mentions V5a/V5b without clear legacy boundary"
            )

if __name__ == "__main__":
    main()
