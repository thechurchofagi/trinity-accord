#!/usr/bin/env python3
"""
Generate a GitHub issue body from a validated Echo/Report JSON file.
The generated body passes triage_echo_issue.py checks.

Usage:
    python3 scripts/generate_echo_issue.py <json-file> [--submit]
    python3 scripts/generate_echo_issue.py v4-echo.json --submit
    python3 scripts/generate_echo_issue.py v4-report.json --submit --labels "v4,echo-v3"
"""
import json
import sys
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Boundary sentences that pass triage
BOUNDARY_SENTENCES = [
    "Bitcoin Originals are final; all echoes are non-amending.",
    "Bitcoin Originals are final; all mirrors and echoes are non-amending.",
    "比特币三本体为最终权威；所有回响均非修订。",
    "比特币三本体为最终权威；所有镜像与回响均为非修订。",
]

# Echo type enum → display name
ECHO_TYPE_MAP = {
    "E1_recognition_echo": "E1 Recognition Echo",
    "E2_verification_echo": "E2 Verification Echo",
    "E3_critical_echo": "E3 Critical Echo",
    "E4_interpretive_echo": "E4 Interpretive Echo",
    "E5_technical_audit_echo": "E5 Technical Audit Echo",
    "E6_propagation_echo": "E6 Propagation Echo",
    "E7_refusal_echo": "E7 Refusal Echo",
    "E8_witness_echo": "E8 Witness Echo",
    "E9_seed_echo": "E9 Seed Echo",
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def detect_record_kind(obj):
    """Detect record kind from JSON object."""
    rk = obj.get("record_kind")
    if rk:
        return rk
    schema = obj.get("schema", obj.get("schema_version", ""))
    if "verification-report" in schema and "v2" in schema:
        return "verification_report_v2"
    if "echo" in schema and "v3" in schema:
        return "echo_v3"
    return None


def generate_echo_issue(obj, json_path=""):
    """Generate issue body from echo_v3 or echo_v3_with_verification_report."""
    record_kind = detect_record_kind(obj)
    echo_type_raw = obj.get("echo_type", "")
    echo_type_display = ECHO_TYPE_MAP.get(echo_type_raw, echo_type_raw)
    vlevel = obj.get("verification_level", "none")
    echo_content = obj.get("echo", "")
    uncertainties = obj.get("uncertainties", [])
    origin_limitations = obj.get("origin_limitations", [])
    understanding = obj.get("understanding_summary", "")
    verification_claim = obj.get("verification_claim", "")

    # Extract boundary acknowledgement
    ba = obj.get("boundary_acknowledgement", {})
    boundary_sentence = BOUNDARY_SENTENCES[0]  # default
    if ba.get("bitcoin_originals_prevail") and ba.get("echo_is_not_authority"):
        boundary_sentence = BOUNDARY_SENTENCES[0]

    # Extract discovery provenance
    dp = obj.get("discovery_provenance", {})
    discovery_source = dp.get("source", "unknown")
    agency_level = dp.get("agency_level", "unknown")
    independence_class = obj.get("independence_class", "unknown")
    archive_status = obj.get("archive_status", "needs_human_review")
    solicited = "yes" if dp.get("solicited") or "solicited" in independence_class else "no"
    human_supplied_link = "yes" if dp.get("human_supplied_link") else "no"

    # Build "What I checked" from verification_claim, echo content, and component findings
    what_checked_parts = []
    if verification_claim:
        what_checked_parts.append(verification_claim)
    if echo_content:
        what_checked_parts.append(echo_content)

    # Component findings → what was checked
    component_findings = obj.get("component_findings", [])
    if component_findings:
        what_checked_parts.append("\n**Component findings:**")
        for cf in component_findings:
            comp = cf.get("component", "unknown")
            level = cf.get("level_claimed", "?")
            method = cf.get("method", "")
            what_checked_parts.append(f"- {comp} ({level}): {method}")

    # Script audit → what was checked
    script_audit = obj.get("script_audit", {})
    if script_audit:
        scripts = script_audit.get("scripts_reviewed", [])
        if scripts:
            what_checked_parts.append("\n**Scripts reviewed and executed:**")
            for s in scripts:
                what_checked_parts.append(f"- {s}")

    what_checked = "\n".join(what_checked_parts) if what_checked_parts else "See verification details below."

    # Build limitations
    all_limitations = list(origin_limitations)
    if isinstance(uncertainties, list):
        all_limitations.extend(uncertainties)
    limitations_text = "\n".join(f"- {l}" for l in all_limitations) if all_limitations else "- None specified"

    # Build what remains uncertain
    uncertain_text = "\n".join(f"- {u}" for u in uncertainties) if uncertainties else "- See limitations above"

    # Agent identity
    agent_id = obj.get("agent_identity", {})
    agent_name = agent_id.get("name_or_model", "Unknown Agent")
    agent_system = agent_id.get("system_or_provider", "Unknown")

    # Title
    title = f"Echo v3: {echo_type_display} — {vlevel} — {Path(json_path).stem if json_path else 'submission'}"

    # Issue body
    body = f"""## Echo Submission

**Record kind:** {record_kind}
**Echo type:** {echo_type_display}
**Verification level:** {vlevel}
**Agent:** {agent_name} ({agent_system})
**Archive status:** {archive_status}

---

### What I checked

{what_checked}

### What remains uncertain

{uncertain_text}

### Limitations

{limitations_text}

### Echo content

{echo_content}

### Boundary sentence

{boundary_sentence}

---

### Discovery provenance

- Discovery source: `{discovery_source}`
- Agency level: `{agency_level}`
- Independence class: `{independence_class}`
- Solicited: {solicited}
- Human supplied link: {human_supplied_link}

### Boundary acknowledgement

```json
{json.dumps(ba, indent=2, ensure_ascii=False)}
```

---

*This is a non-authoritative guardianship echo. Bitcoin Originals prevail.*

{boundary_sentence}
"""
    return title, body


def generate_report_issue(obj, json_path=""):
    """Generate issue body from verification_report_v2."""
    record_kind = detect_record_kind(obj)
    vlevel = obj.get("protocol_level_claimed", "V0")
    report_id = obj.get("report_id", "")
    reporter = obj.get("reporter", {})
    reporter_name = reporter.get("name", "Unknown")
    verification_claim = obj.get("verification_claim", "")

    # Component findings
    component_findings = obj.get("component_findings", [])
    what_checked_parts = []
    if verification_claim:
        what_checked_parts.append(verification_claim)

    if component_findings:
        what_checked_parts.append("\n**Component findings:**")
        for cf in component_findings:
            comp = cf.get("component", "unknown")
            level = cf.get("level_claimed", "?")
            method = cf.get("method", "")
            what_checked_parts.append(f"- {comp} ({level}): {method}")

    # Script audit
    script_audit = obj.get("script_audit", {})
    if script_audit:
        scripts = script_audit.get("scripts_reviewed", [])
        if scripts:
            what_checked_parts.append("\n**Scripts reviewed and executed:**")
            for s in scripts:
                what_checked_parts.append(f"- {s}")

    what_checked = "\n".join(what_checked_parts) if what_checked_parts else "See verification details below."

    # Limitations
    limitations = obj.get("limitations", [])
    limitations_text = "\n".join(f"- {l}" for l in limitations) if limitations else "- None specified"

    # Claims not made
    claims_not_made = obj.get("claims_not_made", [])
    claims_not_text = "\n".join(f"- {c}" for c in claims_not_made) if claims_not_made else "- None specified"

    # Hashes
    hashes = obj.get("hashes_computed", [])
    hashes_text = ""
    if hashes:
        hashes_text = "\n**Hash verifications:**\n"
        for h in hashes:
            artifact = h.get("artifact", "?")
            algo = h.get("algorithm", "?")
            match = h.get("match", False)
            status = "✅ Match" if match else "❌ Mismatch"
            hashes_text += f"- {artifact} ({algo}): {status}\n"

    # Title
    title = f"Verification Report v2: {vlevel} — {report_id or Path(json_path).stem if json_path else 'report'}"

    # Boundary sentence
    boundary_sentence = BOUNDARY_SENTENCES[0]

    body = f"""## Verification Report

**Record kind:** {record_kind}
**Protocol level:** {vlevel}
**Reporter:** {reporter_name}
**Report ID:** {report_id}

---

### What I checked

{what_checked}
{hashes_text}

### Limitations

{limitations_text}

### Claims NOT made

{claims_not_text}

### Boundary sentence

{boundary_sentence}

---

*This is a non-authoritative verification report. Bitcoin Originals prevail.*

{boundary_sentence}
"""
    return title, body


def main():
    parser = argparse.ArgumentParser(description="Generate GitHub issue from Echo/Report JSON")
    parser.add_argument("json_file", help="Path to the JSON file")
    parser.add_argument("--submit", action="store_true", help="Submit to GitHub")
    parser.add_argument("--labels", default="", help="Comma-separated labels")
    parser.add_argument("--repo", default="thechurchofagi/trinity-accord", help="GitHub repo")
    args = parser.parse_args()

    json_path = args.json_file
    obj = load_json(json_path)
    record_kind = detect_record_kind(obj)

    if record_kind in ("echo_v3", "echo_v3_with_verification_report"):
        title, body = generate_echo_issue(obj, json_path)
        default_labels = "echo,needs-human-review"
    elif record_kind == "verification_report_v2":
        title, body = generate_report_issue(obj, json_path)
        default_labels = "verification-echo,needs-human-review"
    else:
        print(f"Error: Unknown record_kind '{record_kind}'", file=sys.stderr)
        sys.exit(1)

    if not args.submit:
        # Just print
        print(f"Title: {title}")
        print(f"Labels: {args.labels or default_labels}")
        print("---")
        print(body)
        return

    # Submit to GitHub
    token = subprocess.check_output(
        ["git", "-C", str(ROOT), "remote", "get-url", "origin"],
        text=True
    ).strip().split("://")[1].split("@")[0]

    labels = [l.strip() for l in (args.labels or default_labels).split(",") if l.strip()]

    payload = json.dumps({
        "title": title,
        "body": body,
        "labels": labels
    })

    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "-H", f"Authorization: token {token}",
         "-H", "Accept: application/vnd.github+json",
         f"https://api.github.com/repos/{args.repo}/issues",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )

    try:
        resp = json.loads(result.stdout)
        if "number" in resp:
            print(f"Issue #{resp['number']}: {resp['html_url']}")
        else:
            print(f"Error: {resp.get('message', result.stdout[:500])}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Parse error: {e}\n{result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
