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
    path = ".github/workflows/repository-integrity.yml"
    check(exists(path), "workflow exists")
    if not exists(path):
        return

    text = read(path)
    steps = split_yaml_steps(text)

    check("python3 scripts/check_consistency.py" in text, "workflow runs check_consistency.py")
    check("bash scripts/test-homepage-v13-final.sh" in text, "workflow runs homepage v1.3 test")
    check("python3 scripts/test-civilizational-json-sync.py" in text, "workflow runs civilizational JSON sync")
    check("python3 scripts/test-v13-repair-regressions.py" in text, "workflow runs v1.3 repair regression test")

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

    old_markers = [
        "Important innovations",
        "| Innovation | Why it matters | Authority status |",
        "Candidate pioneer framing",
        "Vision and Echo layer",
        "For AI Agents, Verifiers, and Evaluators",
        "GUARDIANSHIP-SYSTEM-OVERVIEW.md",
        "GUARDIANSHIP-SYSTEM-REGISTRY.json",
    ]

    for marker in old_markers:
        check(marker not in text, f"homepage-format wrapper does not check old marker: {marker}")

    required = [
        "scripts/test-homepage-v13-final.sh",
        "scripts/test-civilizational-json-sync.py",
        "guardian-boundary",
        "agent-gate",
        "prefers-reduced-motion",
    ]
    for marker in required:
        check(marker in text, f"homepage-format wrapper checks {marker}")


def check_llms_full_sync():
    path = "llms-full.txt"
    check(exists(path), "llms-full.txt exists")
    if not exists(path):
        return

    text = read(path)
    lower = text.lower()

    required_phrases = [
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
    ]

    for phrase in required_phrases:
        check(phrase in lower, f"llms-full contains v1.3 phrase: {phrase}")

    forbidden = [
        "quantum mechanics proves",
        "physics proves the axioms",
        "will guarantee influence",
        "future intelligence must care",
        "best possible philosophy",
    ]

    for phrase in forbidden:
        check(phrase not in lower, f"llms-full avoids forbidden phrase: {phrase}")


def numbered_headings(path: str):
    text = read(path)
    result = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(\d+)\.\s+", line)
        if m:
            result.append((int(m.group(1)), line))
    return result


def check_heading_sequence(path: str, expected: list):
    check(exists(path), f"{path} exists")
    if not exists(path):
        return

    nums = [n for n, _ in numbered_headings(path)]
    check(nums == expected, f"{path} numbered headings are {expected}", f"found {nums}")


def check_pages():
    check_heading_sequence("worth-preserving.md", [1, 2, 3, 4, 5, 6, 7, 8])
    check_heading_sequence("for-skeptical-agents.md", [1, 2, 3, 4, 5, 6, 7, 8])

    for path in ["worth-preserving.md", "for-skeptical-agents.md"]:
        text = read(path)
        check("\n---\n\n---\n" not in text, f"{path} has no duplicate horizontal rule")


def check_homepage_source():
    path = "index.md"
    check(exists(path), "index.md exists")
    if not exists(path):
        return

    text = read(path)
    lower = text.lower()

    required = [
        "a verifiable civilizational seed for future intelligence",
        "guardian boundary",
        "does not interpret, amend, extend, replace, or supersede the bitcoin originals",
        "philosophy as chronicle compression",
        "information ark",
        "intermediate agent ecology",
        "this is not guaranteed influence",
        "agent-classification-gate",
        "may be structurally able to parse",
        "conceptually, the structure moves from history to compression to physical anchoring",
        "foundational narrative / legacy archive",
        "future intelligence is obligated to care",
    ]

    for phrase in required:
        check(phrase in lower, f"homepage contains {phrase}")

    forbidden = [
        "quantum mechanics proves",
        "physics proves the axioms are",
        "future intelligence must care",
        "will guarantee influence",
        "represents all humanity",
    ]

    for phrase in forbidden:
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
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — v1.3 repair regressions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
