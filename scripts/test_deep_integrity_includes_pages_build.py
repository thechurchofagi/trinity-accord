#!/usr/bin/env python3
"""deep-integrity.yml must include pages-build so GitHub Pages/Jekyll smoke runs."""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".github" / "workflows" / "deep-integrity.yml"

data = yaml.safe_load(path.read_text(encoding="utf-8"))
matrix = (
    data.get("jobs", {})
    .get("grouped-integrity", {})
    .get("strategy", {})
    .get("matrix", {})
)
groups = matrix.get("group", [])

if "pages-build" not in groups:
    print("FAIL: deep-integrity.yml matrix missing pages-build")
    sys.exit(1)

print("PASS: deep-integrity.yml includes pages-build")
