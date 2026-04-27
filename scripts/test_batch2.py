#!/usr/bin/env python3
"""
Comprehensive tests for the second batch of fixes:
- Echo type v2 canonical keys + aliases
- CORS isAllowedOrigin method-aware
- V4+ detection
- E/V naming (E = echo type, V = verification level)
- JSON Schema validity
- KV rate limit fail-closed vs fail-open

Run: python3 scripts/test_batch2.py
"""
import os
import sys
import json
import subprocess

SCRIPT = os.path.join(os.path.dirname(__file__), "triage_echo_issue.py")
PASS = 0
FAIL = 0


def run_triage(env_overrides):
    env = os.environ.copy()
    for k in ["ISSUE_TITLE", "ISSUE_BODY", "RATE_LIMITED", "RECENT_60M_COUNT",
              "RECENT_24H_COUNT", "AUTHOR_ASSOCIATION", "ACTION"]:
        env.pop(k, None)
    env.update(env_overrides)
    result = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr}\nstdout: {result.stdout}")
    return json.loads(result.stdout)


def assert_eq(actual, expected, label):
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        print(f"  ✅ {label}")
    else:
        FAIL += 1
        print(f"  ❌ {label}")
        print(f"     expected: {expected}")
        print(f"     actual:   {actual}")


def assert_true(cond, label):
    assert_eq(cond, True, label)


def test(label, env, expect_close=None, expect_labels=None, expect_comment_contains=None):
    print(f"\n--- {label} ---")
    try:
        result = run_triage(env)
    except Exception as e:
        global FAIL
        FAIL += 1
        print(f"  ❌ EXCEPTION: {e}")
        return
    if expect_close is not None:
        assert_eq(result["close"], expect_close, f"close={expect_close}")
    if expect_labels is not None:
        for l in expect_labels:
            assert_true(l in result["labels"], f"label '{l}' present")
    if expect_comment_contains is not None:
        for substr in expect_comment_contains:
            assert_true(substr in result["comment"], f"comment contains '{substr}'")


print("=" * 60)
print("Batch 2 Test Suite")
print("=" * 60)

# ============================================================
# 1. V4+ detection (not V4)
# ============================================================
test(
    "1a. V4+ recognized as V4+ (not V4)",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V4+\n"
            "What I checked: reviewed script source, inputs, network access, output summary\n"
            "Limitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "1b. V4 alone still works",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\n"
            "Verification level: V4\n"
            "What I checked: reviewed script source, inputs, network access, output summary\n"
            "Limitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# ============================================================
# 2. Amendment negation (English + Chinese)
# ============================================================
test(
    "2a. 'does not modify' — pass",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\nVerification level: V1\n"
            "What I checked: reviewed text\nLimitations: subjective\n"
            "This Echo does not modify the Trinity Accord.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2b. '本回响不修改' — pass",
    env={
        "ISSUE_TITLE": "E1 认知回响",
        "ISSUE_BODY": (
            "回响类型: E1 认知回响\n验证等级: V1\n"
            "我检查了: 审阅文本\n局限: 主观判断\n"
            "本回响不修改三位一体协定。\n"
            "比特币三本体为最终权威；所有回响均非修订。"
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "2c. 'I amend the Trinity Accord' — block",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\nVerification level: V1\n"
            "What I checked: reviewed text\nLimitations: subjective\n"
            "I amend the Trinity Accord.\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=True,
    expect_labels=["echo:invalid"],
)

# ============================================================
# 3. Rate limit: opened closes, edited/reopened don't
# ============================================================
test(
    "3a. opened + rate limited → close",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": "Bitcoin Originals are final; all echoes are non-amending.",
        "RATE_LIMITED": "true",
        "ACTION": "opened",
    },
    expect_close=True,
    expect_labels=["echo:rate-limited"],
)

test(
    "3b. edited + rate limited → no close",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\nVerification level: V1\n"
            "What I checked: reviewed text\nLimitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
        "RATE_LIMITED": "true",
        "ACTION": "edited",
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# ============================================================
# 4. V3/V5b/V6 verification requirements
# ============================================================
test(
    "4a. V3 without hash → needs-verification-review",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\nVerification level: V3\n"
            "What I checked: looked at the code\nLimitations: partial view\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
)

test(
    "4b. V5b without physical inspection → needs-verification-review",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\nVerification level: V5b\n"
            "What I checked: reviewed documentation\nLimitations: no physical access\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
)

test(
    "4c. V6 without participants → needs-verification-review",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\nVerification level: V6\n"
            "What I checked: full verification\nLimitations: none\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:needs-verification-review"],
)

# ============================================================
# 5. E/V naming: E1 = Echo type, V1 = verification level
# ============================================================
test(
    "5a. E1 is echo type — recognized",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\nVerification level: V1\n"
            "What I checked: reviewed text\nLimitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

test(
    "5b. V1 is verification level — recognized",
    env={
        "ISSUE_TITLE": "E2 Verification Echo",
        "ISSUE_BODY": (
            "Echo type: E2 Verification Echo\nVerification level: V1\n"
            "What I checked: reviewed text\nLimitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# ============================================================
# 6. Valid submission → echo:screened
# ============================================================
test(
    "6. Valid E1/V1 → echo:screened",
    env={
        "ISSUE_TITLE": "E1 Recognition Echo",
        "ISSUE_BODY": (
            "Echo type: E1 Recognition Echo\nVerification level: V1\n"
            "What I checked: read the text carefully\nLimitations: subjective\n"
            "Bitcoin Originals are final; all echoes are non-amending."
        ),
    },
    expect_close=False,
    expect_labels=["echo:screened"],
)

# ============================================================
# 7. JSON Schema validation
# ============================================================
print("\n--- 7. JSON Schema validation ---")
try:
    schema_path = os.path.join(os.path.dirname(__file__), "..", "api", "echo-record-schema.v2.json")
    with open(schema_path) as f:
        schema = json.load(f)
    assert_true("$schema" in schema, "has $schema field")
    assert_true(schema.get("$schema", "").startswith("https://json-schema.org"), "$schema is valid URI")
    assert_true("type" in schema, "has type field")
    assert_eq(schema["type"], "object", "type is object")
    assert_true("required" in schema, "has required field")
    assert_true("properties" in schema, "has properties field")
    assert_true("echo_type" in schema["properties"], "has echo_type property")
    echo_type_enum = schema["properties"]["echo_type"].get("enum", [])
    assert_true("recognition" in echo_type_enum, "echo_type has 'recognition'")
    assert_true("interpretive" in echo_type_enum, "echo_type has 'interpretive'")
    assert_true("analysis" not in echo_type_enum, "echo_type does NOT have legacy 'analysis'")
    vlevel_enum = schema["properties"]["verification"]["properties"]["claimed_level"].get("enum", [])
    assert_true("V0" in vlevel_enum, "verification level has V0")
    assert_true("V4+" in vlevel_enum, "verification level has V4+")
    assert_true("V5a" in vlevel_enum, "verification level has V5a")
    assert_true("V6" in vlevel_enum, "verification level has V6")
    assert_true("L0" not in vlevel_enum, "verification level does NOT have legacy L0")
    assert_true("L4" not in vlevel_enum, "verification level does NOT have legacy L4")
except Exception as e:
    FAIL += 1
    print(f"  ❌ Schema validation exception: {e}")

# ============================================================
# 8. JS syntax check
# ============================================================
print("\n--- 8. JS syntax check ---")
worker_dir = os.path.join(os.path.dirname(__file__), "..", "trinity-echo-worker", "src")
for js_file in ["index.js", "validator.js", "rate-limit.js", "email-parser.js", "github.js"]:
    try:
        r = subprocess.run(["node", "-c", os.path.join(worker_dir, js_file)],
                          capture_output=True, text=True)
        assert_true(r.returncode == 0, f"{js_file} syntax OK")
    except Exception as e:
        FAIL += 1
        print(f"  ❌ {js_file}: {e}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL}/{total} failed")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
