#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
required = [ROOT / "api/authority.json", ROOT / "api/evidence-manifest.json", ROOT / "api/verification-levels.json"]
ok = True
print("Trinity Accord local verification (minimal)")
for p in required:
    if p.exists():
        print(f"[PASS] exists: {p.relative_to(ROOT)}")
        try:
            json.loads(p.read_text(encoding="utf-8"))
            print(f"[PASS] json valid: {p.relative_to(ROOT)}")
        except Exception as e:
            ok = False
            print(f"[FAIL] json invalid: {p.relative_to(ROOT)} -> {e}")
    else:
        ok = False
        print(f"[FAIL] missing: {p.relative_to(ROOT)}")
manifest = json.loads((ROOT / "api/evidence-manifest.json").read_text(encoding="utf-8"))
if "public_covenant_archive" in manifest and "sha256" in manifest["public_covenant_archive"]:
    print("[INFO] manifest includes covenant archive sha256")
print("[WARN] manual external verification required for full blockchain checks")
print("RESULT:", "PASS" if ok else "FAIL")
