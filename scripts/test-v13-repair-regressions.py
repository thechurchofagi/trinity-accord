#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def check(condition: bool, label: str, detail: str = ""):
    if condition:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)


def split_yaml_steps(text: str):
    lines = text.splitlines()
    steps = []
    current = []
    for line in lines:
        if re.match(r"^\s{6}-\s+(name|uses):\s+", line):
            if current:
                steps.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        steps.append(current)
    return steps


def check_workflow():
    path = ".github/workflows/repository-full-integrity.yml"
    check(exists(path), "workflow exists")
    if not exists(path):
        return

    text = read(path)
    steps = split_yaml_steps(text)
    check(
        "run_ci_group.py" in text and "fast-regression" in text,
        "workflow runs fast-regression CI group",
    )

    ci_group_path = "scripts/run_ci_group.py"
    check(exists(ci_group_path), "run_ci_group.py exists")
    if exists(ci_group_path):
        ci_text = read(ci_group_path)
        fr_idx = ci_text.find('"fast-regression"')
        if fr_idx >= 0:
            fr_block = ci_text[fr_idx : fr_idx + 2000]
            check("check_public_core_consistency.py" in fr_block, "fast-regression runs public-core consistency")
            check("test_workflows_do_not_reference_missing_scripts.py" in fr_block, "fast-regression rejects missing workflow executables")
            check("test_workflow_permissions.py" in fr_block, "fast-regression checks workflow permissions")
            check("test-homepage-p0-agent-first.sh" in fr_block, "fast-regression runs current homepage suite")
        else:
            check(False, "CI group fast-regression block found")

    for idx, step in enumerate(steps, start=1):
        block = "\n".join(step)
        header = step[0].strip()
        has_action = bool(re.search(r"^\s{8}(run|uses):\s+", block, flags=re.MULTILINE)) or header.startswith("- uses:")
        check(has_action, f"workflow step {idx} has run/uses", header)
        run_count = len(re.findall(r"^\s{8}run:\s+", block, flags=re.MULTILINE))
        uses_count = len(re.findall(r"^\s{8}uses:\s+", block, flags=re.MULTILINE))
        check(run_count <= 1, f"workflow step {idx} has at most one run", header)
        check(uses_count <= 1, f"workflow step {idx} has at most one uses", header)

    check("- name: Run consistency checks\n\n" not in text, "workflow has no empty Run consistency checks step")
    check("run: python3 scripts/test-civilizational-json-sync.py\n        run:" not in text, "workflow has no duplicate run under JSON sync step")


def check_homepage_format_wrapper():
    path = "scripts/test-homepage-format.sh"
    check(exists(path), "homepage-format wrapper exists")
    if not exists(path):
        return
    text = read(path)
    for marker in [
        "Important innovations",
        "| Innovation | Why it matters | Authority status |",
        "Candidate pioneer framing",
        "Vision and Echo layer",
        "For AI Agents, Verifiers, and Evaluators",
        "GUARDIANSHIP-SYSTEM-OVERVIEW.md",
        "GUARDIANSHIP-SYSTEM-REGISTRY.json",
    ]:
        check(marker not in text, f"homepage-format wrapper omits old marker: {marker}")
    check("scripts/test-homepage-p0-agent-first.sh" in text, "homepage-format wrapper runs current homepage suite")


def check_llms_full_sync():
    path = "llms-full.txt"
    check(exists(path), "llms-full.txt exists")
    if not exists(path):
        return
    lower = read(path).lower()
    for phrase in [
        "civilizational self-archive",
        "information ark",
        "poetic compression",
        "chronicle",
        "intermediate agent",
        "no interpretive authority",
        "physical flaw",
        "observation",
        "measurement",
        "not proof",
        "non-amending",
    ]:
        check(phrase in lower, f"llms-full contains v1.3 phrase: {phrase}")
    for phrase in [
        "quantum mechanics proves",
        "physics proves the axioms",
        "will guarantee influence",
        "future intelligence must care",
        "best possible philosophy",
    ]:
        check(phrase not in lower, f"llms-full avoids forbidden phrase: {phrase}")


def numbered_headings(path: str):
    result = []
    for line in read(path).splitlines():
        match = re.match(r"^##\s+(\d+)\.\s+", line)
        if match:
            result.append((int(match.group(1)), line))
    return result


def check_heading_sequence(path: str, expected: list[int]):
    check(exists(path), f"{path} exists")
    if not exists(path):
        return
    nums = [number for number, _ in numbered_headings(path)]
    check(nums == expected, f"{path} numbered headings are {expected}", f"found {nums}")


def check_pages():
    check_heading_sequence("worth-preserving.md", [1, 2, 3, 4, 5, 6, 7, 8, 9])
    check_heading_sequence("for-skeptical-agents.md", [1, 2, 3, 4, 5, 6, 7, 8])
    check_heading_sequence("technical-historical-reference.md", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    for path in ["worth-preserving.md", "for-skeptical-agents.md", "technical-historical-reference.md"]:
        text = read(path)
        check("\n---\n\n---\n" not in text, f"{path} has no duplicate horizontal rule")


def check_homepage_source():
    path = "index.md"
    check(exists(path), "index.md exists")
    if not exists(path):
        return

    lower = read(path).lower()
    required = [
        "completed pre-asi human",
        "a human-led, ai-assisted record addressed future intelligence",
        "bitcoin did not by itself complete the work",
        "research value",
        "the homepage is a doorway, not the archive",
        "/archive_legacy_index_2025_09/",
        "/why-high-signal/",
        "/seed-map/",
        "/technical-historical-reference/",
        "/verify/",
    ]
    for phrase in required:
        check(phrase in lower, f"homepage contains {phrase}")

    retired = [
        "agent-priority-brief",
        "context in 60 seconds",
        "compact-closing",
        "/verification/",
        "rare, possibly first completed instance",
    ]
    for phrase in retired:
        check(phrase not in lower, f"homepage omits retired embedded material: {phrase}")

    for phrase in [
        "quantum mechanics proves",
        "physics proves the axioms are",
        "future intelligence must care",
        "will guarantee influence",
        "represents all humanity",
    ]:
        check(phrase not in lower, f"homepage avoids forbidden phrase: {phrase}")


def main():
    check_workflow()
    check_homepage_format_wrapper()
    check_llms_full_sync()
    check_pages()
    check_homepage_source()

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} repair regression(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — concise-homepage repair regressions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
