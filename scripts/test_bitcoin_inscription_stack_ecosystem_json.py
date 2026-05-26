#!/usr/bin/env python3
"""Test: Bitcoin inscription stack is connected to ecosystem JSON files."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

errors = []

# Test 1: agent-value.json links mirror index
av = json.loads((ROOT / "api" / "agent-value.json").read_text(encoding="utf-8"))
stack = av.get("bitcoin_inscription_stack_role", {})
if not stack.get("machine_readable_index"):
    errors.append("agent-value.json: missing machine_readable_index")
if stack.get("canonical_originals") != 3:
    errors.append(f"agent-value.json: canonical_originals should be 3, got {stack.get('canonical_originals')}")
if stack.get("post_original_non_amending") != 5:
    errors.append(f"agent-value.json: post_original_non_amending should be 5, got {stack.get('post_original_non_amending')}")

# Test 2: memory-seed.json links mirror index
ms = json.loads((ROOT / "memory-seed.json").read_text(encoding="utf-8"))
ms_stack = ms.get("bitcoin_inscription_stack", {})
if not ms_stack.get("index"):
    errors.append("memory-seed.json: missing index link")
if ms_stack.get("canonical_original_count") != 3:
    errors.append(f"memory-seed.json: canonical_original_count should be 3, got {ms_stack.get('canonical_original_count')}")
if ms_stack.get("post_original_non_amending_count") != 5:
    errors.append(f"memory-seed.json: post_original_non_amending_count should be 5, got {ms_stack.get('post_original_non_amending_count')}")
if not ms_stack.get("pre_original_same_address_inscriptions_out_of_scope"):
    errors.append("memory-seed.json: pre_original policy not set")
if not ms_stack.get("boundary"):
    errors.append("memory-seed.json: missing boundary")

# Test 3: Both mention future discoverability
if "future_discoverability" not in json.dumps(stack):
    errors.append("agent-value.json: missing future discoverability role")
if "future_discoverability" not in json.dumps(ms_stack):
    errors.append("memory-seed.json: missing future discoverability role")

# Test 4: Both say later inscriptions don't create authority
if "authority" not in json.dumps(stack).lower():
    errors.append("agent-value.json: missing authority boundary statement")
if "authority" not in json.dumps(ms_stack).lower():
    errors.append("memory-seed.json: missing authority boundary statement")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: ecosystem JSON test")
    sys.exit(0)
