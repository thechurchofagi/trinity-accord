#!/usr/bin/env python3
"""deep-integrity.yml must include pages-build so GitHub Pages/Jekyll smoke runs."""
from pathlib import Path
import re
import sys

try:
    import yaml
except Exception:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".github" / "workflows" / "deep-integrity.yml"
text = path.read_text(encoding="utf-8")

if yaml is not None:
    data = yaml.safe_load(text)
    matrix = (
        data.get("jobs", {})
        .get("grouped-integrity", {})
        .get("strategy", {})
        .get("matrix", {})
    )
    groups = matrix.get("group", [])
else:
    # Dependency-free local fallback; CI still exercises full YAML parsing.
    groups = []
    in_group = False
    for line in text.splitlines():
        if re.match(r"^\s*group:\s*$", line):
            in_group = True
            continue
        if in_group:
            item = re.match(r"^\s*-\s*([^#]+?)\s*$", line)
            if item:
                groups.append(item.group(1).strip().strip('"\''))
            elif line.strip() and not line.startswith("          "):
                break

if "pages-build" not in groups:
    print("FAIL: deep-integrity.yml matrix missing pages-build")
    sys.exit(1)

print("PASS: deep-integrity.yml includes pages-build")
