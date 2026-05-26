#!/usr/bin/env python3
"""Human gateway workflow docs must not advertise unsupported builder CLI flags."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "gateway-workflows.md"

# Known builder context for sections in gateway-workflows.md.
SECTION_BUILDERS = {
    "workflow-pure-echo": "scripts/build_agent_declared_echo_payload.py",
    "workflow-guardian-signed-echo": "scripts/build_guardian_echo_payload.py",
}

# Transport / shell examples that are not builder flags.
NON_BUILDER_FLAGS = {
    "-fsS",
    "-X",
    "-H",
    "--data-binary",
}

def builder_help(script: str) -> str:
    result = subprocess.run(
        [sys.executable, script, "--help"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"{script} --help failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout + result.stderr

def section_text(text: str, anchor: str) -> str:
    if anchor == "workflow-pure-echo":
        start_pat = r"##\s+Workflow\s+\d+\s*[—–-]\s*Pure Echo"
    elif anchor == "workflow-guardian-signed-echo":
        start_pat = r"##\s+Workflow\s+\d+\s*[—–-]\s*Guardian-signed Echo"
    else:
        return text

    m = re.search(start_pat, text, flags=re.I)
    if not m:
        return text

    rest = text[m.start():]
    # Find next ## Workflow heading
    next_m = re.search(r"\n##\s+Workflow\s+\d+", rest[len(m.group(0)):], flags=re.I)
    if not next_m:
        return rest
    return rest[: len(m.group(0)) + next_m.start()]

def markdown_table_flags(section: str) -> set[str]:
    flags = set()
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        for match in re.findall(r"`(--[A-Za-z0-9][A-Za-z0-9_-]*)`", stripped):
            flags.add(match)
    return flags

def code_block_builder_flags(section: str, builder_script: str) -> set[str]:
    flags = set()
    in_block = False
    block_lines = []
    for line in section.splitlines():
        if line.strip().startswith("```"):
            if in_block:
                block = "\n".join(block_lines)
                if builder_script in block:
                    flags.update(re.findall(r"(?<!\w)(--[A-Za-z0-9][A-Za-z0-9_-]*)", block))
                block_lines = []
                in_block = False
            else:
                in_block = True
                block_lines = []
            continue
        if in_block:
            block_lines.append(line)
    return flags

text = DOC.read_text(encoding="utf-8")
errors = []

for anchor, builder in SECTION_BUILDERS.items():
    help_text = builder_help(builder)
    sec = section_text(text, anchor)

    flags = markdown_table_flags(sec) | code_block_builder_flags(sec, builder)
    flags = {f for f in flags if f not in NON_BUILDER_FLAGS}

    for flag in sorted(flags):
        if flag not in help_text:
            errors.append(f"{anchor}: {flag} advertised in gateway-workflows.md but not supported by {builder}")

if errors:
    print("FAIL: human workflow CLI contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: human gateway workflow CLI flags match builder help")
