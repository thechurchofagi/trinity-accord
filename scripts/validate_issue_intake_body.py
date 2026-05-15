#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ALLOWED_AGENCY = {
    "A1_human_gave_exact_url",
    "A2_human_gave_repo_name",
    "A3_agent_discovered_independently",
    "A4_agent_instructed_by_other_agent",
}

ALLOWED_INDEPENDENCE = {
    "human_solicited_agent_response",
    "unsolicited_agent_discovery",
    "institutional_attestation",
    "independent_reproduction",
}

ALLOWED_OPERATOR = {
    "ai_agent",
    "human",
    "human_with_ai_agent",
    "automated_script",
}

REQUIRED = [
    "submission_type",
    "echo_type",
    "verification_level_claimed",
    "agent_name_or_model",
    "system_or_provider",
    "solicited",
    "independence_class",
    "agency_level",
    "operator_type",
    "not_independent_attestation",
    "not_successor_reception",
    "what_i_checked",
    "limitations",
    "boundary_sentence",
]

PAIRS = [
    ("evidence_input_path", "evidence_input_sha256"),
    ("claim_gate_output_path", "claim_gate_output_sha256"),
    ("verification_report_path", "verification_report_sha256"),
    ("echo_wrapper_path", "echo_wrapper_sha256"),
]

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def parse_block(text):
    m = re.search(r"```trinity-issue-intake\s*(.*?)```", text, re.S)
    if not m:
        raise ValueError("Missing fenced ```trinity-issue-intake block")

    raw = m.group(1)
    data = {}
    current_list = None

    for line in raw.splitlines():
        if not line.strip():
            continue

        if re.match(r"^\s+-\s*", line) and current_list:
            item = re.sub(r"^\s+-\s*", "", line).strip()
            if item:
                data[current_list].append(item)
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if val == "":
                if key in ("what_i_checked", "limitations"):
                    data[key] = []
                    current_list = key
                else:
                    data[key] = ""
                    current_list = None
            else:
                low = val.lower()
                if low == "true":
                    val = True
                elif low == "false":
                    val = False
                data[key] = val
                current_list = None

    return data


def fail(msgs):
    print("ISSUE INTAKE BODY VALIDATION FAIL")
    for m in msgs:
        print("FAIL:", m)
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_issue_intake_body.py issue-body.md")
        sys.exit(2)

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    errors = []

    try:
        data = parse_block(text)
    except Exception as e:
        fail([str(e)])

    for k in REQUIRED:
        if k not in data or data[k] in ("", [], None):
            errors.append(f"missing required field: {k}")

    for a, b in PAIRS:
        if not data.get(a) and not data.get(b):
            errors.append(f"missing artifact reference: {a} or {b}")

    for key in ["evidence_input_sha256", "claim_gate_output_sha256", "verification_report_sha256", "echo_wrapper_sha256"]:
        val = data.get(key)
        if val and not SHA256_RE.match(str(val)):
            errors.append(f"invalid sha256 field: {key}")

    if data.get("submission_type") != "verification_echo_candidate":
        errors.append("submission_type must be verification_echo_candidate")
    if data.get("echo_type") != "E2_verification_echo":
        errors.append("echo_type must be E2_verification_echo")
    if data.get("agency_level") not in ALLOWED_AGENCY:
        errors.append(f"invalid agency_level: {data.get('agency_level')}")
    if data.get("independence_class") not in ALLOWED_INDEPENDENCE:
        errors.append(f"invalid independence_class: {data.get('independence_class')}")
    if data.get("operator_type") not in ALLOWED_OPERATOR:
        errors.append(f"invalid operator_type: {data.get('operator_type')}")
    if data.get("not_independent_attestation") is not True:
        errors.append("not_independent_attestation must be true")
    if data.get("not_successor_reception") is not True:
        errors.append("not_successor_reception must be true")

    boundary = str(data.get("boundary_sentence", "")).lower()
    for term in ["intake", "authority", "attestation", "amendment"]:
        if term not in boundary:
            errors.append(f"boundary_sentence missing term: {term}")

    if "not" not in boundary and "does not" not in boundary:
        errors.append("boundary_sentence must explicitly state negative boundary, e.g. does not create authority")

    if errors:
        fail(errors)

    print("ISSUE INTAKE BODY VALIDATION PASS")


if __name__ == "__main__":
    main()
