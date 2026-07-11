#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def strip_volatile(value: Any, keys: set[str]) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_volatile(item, keys)
            for key, item in value.items()
            if key not in keys
        }
    if isinstance(value, list):
        return [strip_volatile(item, keys) for item in value]
    return value


def head_text(rel: str) -> str | None:
    result = subprocess.run(
        ['git', 'show', f'HEAD:{rel}'],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def restore_if_volatile_only(path: Path, keys: set[str]) -> bool:
    if not path.is_file():
        return False
    rel = path.resolve().relative_to(ROOT).as_posix()
    previous_text = head_text(rel)
    if previous_text is None:
        return False
    current_text = path.read_text(encoding='utf-8')
    if current_text == previous_text:
        return False
    try:
        previous = json.loads(previous_text)
        current = json.loads(current_text)
    except json.JSONDecodeError:
        return False
    if strip_volatile(previous, keys) != strip_volatile(current, keys):
        return False
    path.write_text(previous_text, encoding='utf-8')
    print(f'RESTORED_VOLATILE_ONLY {rel}')
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', action='append', default=[])
    parser.add_argument('--glob', dest='globs', action='append', default=[])
    parser.add_argument('--volatile-key', action='append', required=True)
    args = parser.parse_args()

    candidates: set[Path] = {ROOT / value for value in args.path}
    for pattern in args.globs:
        candidates.update(Path(value) for value in glob.glob(str(ROOT / pattern)))

    restored = 0
    keys = set(args.volatile_key)
    for path in sorted(candidates):
        restored += int(restore_if_volatile_only(path, keys))
    print(f'volatile-only files restored: {restored}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
