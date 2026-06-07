#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}")

def restore_snapshot(bundle_path: Path, out_dir: Path) -> None:
    bundle = read_json(bundle_path)
    if bundle.get("bundle_type") != "record_chain_data_snapshot":
        raise SystemExit("restore drill currently requires snapshot bundle")

    for rec in bundle.get("records", []):
        rid = rec["record_id"]
        write_json(out_dir / "record-chain/records" / f"{rid}.json", rec["record_payload"])

    ledger = out_dir / "record-chain/hash-chain/main.chain.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(bundle["main_chain_jsonl"], encoding="utf-8")

    write_json(out_dir / "api/record-chain-head.json", bundle["api_head"])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle-file", required=True)
    ap.add_argument("--out-dir", default="/tmp/trinity-record-chain-restore-drill")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    shutil.copytree(ROOT / "scripts", out_dir / "scripts")
    restore_snapshot(ROOT / args.bundle_file, out_dir)

    if args.verify:
        run([
            sys.executable,
            "scripts/verify_record_chain_integrity.py",
            "--ledger", "record-chain/hash-chain/main.chain.jsonl",
            "--head", "api/record-chain-head.json",
            "--chain-id", "trinity-record-chain-main",
            "--verify-payload-files",
            "--base-dir", ".",
        ], out_dir)

    print(json.dumps({
        "result": "pass",
        "out_dir": str(out_dir),
        "bundle_file": args.bundle_file,
        "verify": args.verify,
    }, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
