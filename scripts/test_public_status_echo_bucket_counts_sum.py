#!/usr/bin/env python3
"""Public status Echo archive count must equal sum of canonical by_echo_type buckets."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
status = json.loads((ROOT / "api/public-home-status.json").read_text(encoding="utf-8"))

echo_archives = status["reception"]["agent_declared_echo_archives"]
count = echo_archives["count"]
bucket_sum = sum(echo_archives["by_echo_type"].values())

if count != bucket_sum:
    print("FAIL: agent_declared_echo_archives.count does not equal sum(by_echo_type)")
    print("count:", count)
    print("bucket_sum:", bucket_sum)
    print("by_echo_type:", echo_archives["by_echo_type"])
    sys.exit(1)

print("PASS: agent_declared_echo_archives count equals by_echo_type sum")
