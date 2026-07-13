#!/usr/bin/env python3
"""Round 7 full-system audit for Trinity Accord.

This script is intentionally read-only with respect to the audited repository.
It combines static inventory, workflow/security analysis, contract-drift scans,
internal-link checks, writer-collision analysis, registered-test coverage, and
selected existing dynamic gates. Findings are candidates until manually
validated; the report separates deterministic failures from heuristics.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


EXCLUDED_PREFIXES = (
    ".git/",
    "audit-results/round7/",
)
SELF_FILES = {
    "audit/round7_system_audit.py",
    ".github/workflows/round7-system-audit.yml",
}
TEXT_SUFFIXES = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".jsonl",
    ".yml", ".yaml", ".md", ".html", ".xml", ".txt", ".sh", ".toml",
    ".ini", ".cfg", ".css", ".scss", ".rb", ".go", ".rs",
}
WORKFLOW_DIR = ".github/workflows"
REPO = "thechurchofagi/trinity-accord"
SITE = "https://www.trinityaccord.org"
GATEWAY = "https://trinity-record-chain-gateway.onrender.com"


@dataclass
class Finding:
    id: str
    severity: str
    category: str
    title: str
    path: str = ""
    line: int | None = None
    evidence: str = ""
    confidence: str = "high"
    deterministic: bool = True


@dataclass
class CommandResult:
    name: str
    command: list[str]
    returncode: int
    duration_seconds: float
    stdout_tail: str
    stderr_tail: str
    changed_files: list[str]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(repo: Path, command: list[str], *, timeout: int = 900, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(
        command,
        cwd=repo,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=merged,
    )


def tracked_files(repo: Path) -> list[str]:
    result = run(repo, ["git", "ls-files", "-z"], timeout=60)
    if result.returncode != 0:
        raise SystemExit(result.stderr)
    files = [p for p in result.stdout.split("\0") if p]
    return sorted(
        p for p in files
        if not p.startswith(EXCLUDED_PREFIXES) and p not in SELF_FILES
    )


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def read_text(repo: Path, path: str) -> str | None:
    p = repo / path
    if p.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def add(findings: list[Finding], **kwargs: Any) -> None:
    findings.append(Finding(**kwargs))


def normalize_action_ref(value: str) -> bool:
    if value.startswith("./"):
        return True
    if "@" not in value:
        return False
    ref = value.rsplit("@", 1)[1]
    return bool(re.fullmatch(r"[0-9a-fA-F]{40}", ref))


def scan_workflows(repo: Path, files: list[str], findings: list[Finding]) -> dict[str, list[str]]:
    writers: dict[str, list[str]] = defaultdict(list)
    for path in files:
        if not path.startswith(WORKFLOW_DIR + "/") or not path.endswith((".yml", ".yaml")):
            continue
        text = read_text(repo, path) or ""
        lines = text.splitlines()

        for match in re.finditer(r"(?m)^\s*-?\s*uses:\s*([^\s#]+)", text):
            action = match.group(1).strip("'\"")
            if not normalize_action_ref(action):
                add(
                    findings,
                    id="WF-UNPINNED-ACTION",
                    severity="high",
                    category="workflow-security",
                    title="GitHub Action is not pinned to a full commit SHA",
                    path=path,
                    line=line_number(text, match.start()),
                    evidence=action,
                )

        if re.search(r"(?m)^\s*pull_request_target\s*:", text):
            add(
                findings,
                id="WF-PULL-REQUEST-TARGET",
                severity="critical",
                category="workflow-security",
                title="pull_request_target workflow requires manual trust-boundary review",
                path=path,
                evidence="pull_request_target trigger present",
            )

        write_perm = bool(re.search(r"(?ms)^permissions:\s*\n(?:\s+.*\n)*?\s+contents:\s*write\b", text))
        pr_trigger = bool(re.search(r"(?m)^\s*pull_request\s*:", text))
        checkout_head = bool(re.search(r"ref:\s*\$\{\{\s*github\.event\.pull_request\.(?:head\.sha|head\.ref)", text))
        if write_perm and pr_trigger and checkout_head:
            add(
                findings,
                id="WF-UNTRUSTED-PR-WRITE",
                severity="critical",
                category="workflow-security",
                title="Workflow combines contents:write with pull-request head checkout",
                path=path,
                evidence="contents: write + pull_request + PR head ref",
            )

        if "contents: write" in text and "timeout-minutes:" not in text:
            add(
                findings,
                id="WF-WRITE-NO-TIMEOUT",
                severity="medium",
                category="workflow-reliability",
                title="Write-capable workflow has no job timeout",
                path=path,
                evidence="contents: write without timeout-minutes",
            )

        mutates = bool(re.search(r"\bgit\s+(?:push|commit|add)\b|/deploys\b|actions/workflows/.+/dispatches", text))
        if mutates and "concurrency:" not in text:
            add(
                findings,
                id="WF-MUTATOR-NO-CONCURRENCY",
                severity="high",
                category="workflow-race",
                title="Mutating workflow has no concurrency guard",
                path=path,
                evidence="git mutation/deployment dispatch without workflow concurrency",
            )

        if re.search(r"\bgit\s+add\s+-A\b", text):
            add(
                findings,
                id="WF-GIT-ADD-ALL",
                severity="medium",
                category="workflow-scope",
                title="Workflow stages every changed file with git add -A",
                path=path,
                evidence="git add -A may capture unrelated generated or evidence files",
                deterministic=False,
                confidence="medium",
            )

        for match in re.finditer(r"\bgit\s+push\s+(?:origin\s+)?(?:HEAD:)?main\b", text):
            add(
                findings,
                id="WF-DIRECT-MAIN-PUSH",
                severity="high",
                category="workflow-integrity",
                title="Workflow directly pushes to main",
                path=path,
                line=line_number(text, match.start()),
                evidence=match.group(0),
            )

        # Direct workflow-dispatch interpolation into shell is a shell-injection boundary.
        for match in re.finditer(r"\$\{\{\s*(?:github\.event\.inputs|inputs)\.[^}]+\}\}", text):
            start = match.start()
            prefix = text[max(0, start - 600):start]
            if "run:" in prefix and not re.search(r"env:\s*(?:\n|.){0,500}$", prefix):
                add(
                    findings,
                    id="WF-INPUT-IN-RUN",
                    severity="high",
                    category="workflow-security",
                    title="Workflow input appears directly inside a run script",
                    path=path,
                    line=line_number(text, start),
                    evidence=match.group(0),
                    deterministic=False,
                    confidence="medium",
                )

        # Approximate files written/staged by each workflow.
        for match in re.finditer(r"(?m)^\s*git\s+add\s+(.+)$", text):
            value = match.group(1).strip()
            if value == "-A":
                writers["*"] .append(path)
                continue
            for token in re.findall(r"(?:'[^']+'|\"[^\"]+\"|\S+)", value):
                token = token.strip("'\"")
                if token.startswith("-") or "$" in token or "*" in token:
                    continue
                writers[token].append(path)
        for match in re.finditer(r"(?m)>\s*([A-Za-z0-9_./-]+\.(?:json|md|txt|yml|yaml))", text):
            writers[match.group(1)].append(path)

        # Detect checkout defaults in write workflows: default ref on PR is a merge ref.
        if write_perm and pr_trigger:
            checkout_blocks = re.findall(r"uses:\s*actions/checkout@[^\n]+(?:\n\s+with:\n(?:\s+[^\n]+\n)*)?", text)
            if checkout_blocks and all("ref:" not in block for block in checkout_blocks):
                add(
                    findings,
                    id="WF-WRITE-PR-MERGE-REF",
                    severity="high",
                    category="workflow-integrity",
                    title="Write workflow checks out the default pull-request merge ref",
                    path=path,
                    evidence="contents: write workflow has pull_request trigger and checkout without explicit ref",
                )

        # Flag workflows that commit after a rebase without re-running the generator/test.
        if "git rebase" in text and "git commit" in text:
            rebase_pos = text.find("git rebase")
            commit_pos = text.find("git commit", rebase_pos)
            between = text[rebase_pos:commit_pos] if commit_pos > rebase_pos else ""
            if commit_pos > rebase_pos and not re.search(r"python|node|npm|pytest|generate|update_", between):
                add(
                    findings,
                    id="WF-REBASE-NO-REGEN",
                    severity="high",
                    category="workflow-race",
                    title="Workflow rebases generated changes without re-running generation or validation",
                    path=path,
                    evidence="git rebase followed by commit with no visible regeneration step",
                    deterministic=False,
                    confidence="medium",
                )

    for target, workflow_paths in sorted(writers.items()):
        unique = sorted(set(workflow_paths))
        if target != "*" and len(unique) > 1:
            add(
                findings,
                id="WF-MULTIPLE-WRITERS",
                severity="high",
                category="workflow-race",
                title="Multiple workflows appear to write the same tracked path",
                path=target,
                evidence=", ".join(unique),
                deterministic=False,
                confidence="medium",
            )
    return {key: sorted(set(value)) for key, value in writers.items()}


def scan_python(repo: Path, files: list[str], findings: list[Finding]) -> None:
    for path in files:
        if not path.endswith(".py") or path.startswith(("tests/", "audit/")) or "/test_" in path or Path(path).name.startswith("test_"):
            continue
        text = read_text(repo, path)
        if text is None:
            continue
        try:
            tree = ast.parse(text, filename=path)
        except SyntaxError as exc:
            add(
                findings,
                id="PY-SYNTAX",
                severity="critical",
                category="code-correctness",
                title="Tracked Python file cannot be parsed",
                path=path,
                line=exc.lineno,
                evidence=str(exc),
            )
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = ""
                if isinstance(func, ast.Attribute):
                    name = func.attr
                elif isinstance(func, ast.Name):
                    name = func.id
                if name in {"run", "Popen", "call", "check_call", "check_output"}:
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            add(
                                findings,
                                id="PY-SHELL-TRUE",
                                severity="high",
                                category="code-security",
                                title="subprocess call uses shell=True",
                                path=path,
                                line=getattr(node, "lineno", None),
                                evidence=ast.get_source_segment(text, node) or "shell=True",
                                deterministic=False,
                                confidence="medium",
                            )
                if name in {"urlopen", "get", "post", "request"}:
                    source = ast.get_source_segment(text, node) or ""
                    if ("urllib" in text or "requests" in text) and "timeout=" not in source and len(source) < 1000:
                        add(
                            findings,
                            id="PY-HTTP-NO-TIMEOUT",
                            severity="medium",
                            category="network-reliability",
                            title="HTTP request may omit an explicit timeout",
                            path=path,
                            line=getattr(node, "lineno", None),
                            evidence=source[:300],
                            deterministic=False,
                            confidence="low",
                        )
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    catches_exception = handler.type is None or (
                        isinstance(handler.type, ast.Name) and handler.type.id in {"Exception", "BaseException"}
                    )
                    if catches_exception and len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                        add(
                            findings,
                            id="PY-EXCEPTION-PASS",
                            severity="medium",
                            category="code-reliability",
                            title="Broad exception is silently ignored",
                            path=path,
                            line=getattr(handler, "lineno", None),
                            evidence="except Exception: pass",
                            deterministic=False,
                            confidence="medium",
                        )


def scan_javascript(repo: Path, files: list[str], findings: list[Finding]) -> None:
    for path in files:
        if not path.endswith((".js", ".mjs", ".cjs", ".ts")) or "/test" in path or path.startswith("audit/"):
            continue
        text = read_text(repo, path) or ""
        patterns = [
            (r"\beval\s*\(", "JS-EVAL", "high", "Dynamic eval is present"),
            (r"new\s+Function\s*\(", "JS-NEW-FUNCTION", "high", "Dynamic Function constructor is present"),
            (r"exec(?:Sync|FileSync)?\s*\([^\n]*\$\{", "JS-SHELL-INTERPOLATION", "high", "Interpolated value appears in command execution"),
            (r"fetch\s*\([^\n]+\)(?![^\n]*AbortSignal|[^\n]*signal)", "JS-FETCH-NO-TIMEOUT", "low", "fetch call may have no timeout/abort signal"),
        ]
        for regex, ident, severity, title in patterns:
            for match in re.finditer(regex, text):
                add(
                    findings,
                    id=ident,
                    severity=severity,
                    category="code-security" if severity == "high" else "network-reliability",
                    title=title,
                    path=path,
                    line=line_number(text, match.start()),
                    evidence=match.group(0)[:250],
                    deterministic=False,
                    confidence="low" if severity == "low" else "medium",
                )


def scan_json(repo: Path, files: list[str], findings: list[Finding]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    parsed: dict[str, Any] = {}
    schema_ids: dict[str, list[str]] = defaultdict(list)
    for path in files:
        if not path.endswith(".json"):
            continue
        try:
            value = json.loads((repo / path).read_text(encoding="utf-8"))
            parsed[path] = value
        except Exception as exc:
            add(
                findings,
                id="JSON-INVALID",
                severity="critical",
                category="data-integrity",
                title="Tracked JSON file is invalid",
                path=path,
                evidence=f"{type(exc).__name__}: {exc}",
            )
            continue
        if isinstance(value, dict) and isinstance(value.get("$id"), str):
            schema_ids[value["$id"]].append(path)

    for schema_id, paths in schema_ids.items():
        if len(paths) < 2:
            continue
        canonical = [json.dumps(parsed[p], sort_keys=True, separators=(",", ":")) for p in paths]
        if len(set(canonical)) > 1:
            add(
                findings,
                id="SCHEMA-ID-DIVERGENCE",
                severity="high",
                category="contract-drift",
                title="Multiple different JSON schemas share the same $id",
                path=paths[0],
                evidence=f"$id={schema_id}; files={', '.join(paths)}",
            )
    return parsed, {k: sorted(v) for k, v in schema_ids.items()}


def route_candidates(path: str) -> list[str]:
    value = path.split("?", 1)[0].split("#", 1)[0]
    if not value:
        return []
    value = urllib.parse.unquote(value)
    if value.startswith("/"):
        value = value[1:]
    if value.endswith("/"):
        return [value + "index.md", value + "index.html", value.rstrip("/") + ".md"]
    suffix = PurePosixPath(value).suffix
    if suffix:
        return [value]
    return [value, value + ".md", value + ".html", value + "/index.md", value + "/index.html"]


def scan_internal_links(repo: Path, files: list[str], findings: list[Finding]) -> None:
    existing = set(files)
    for path in files:
        if not path.endswith((".md", ".html")):
            continue
        text = read_text(repo, path) or ""
        links: list[tuple[str, int]] = []
        for match in re.finditer(r"\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)", text):
            links.append((match.group(1), match.start(1)))
        for match in re.finditer(r"(?:href|src)=['\"]([^'\"]+)['\"]", text):
            links.append((match.group(1), match.start(1)))
        for raw, offset in links:
            if raw.startswith(("http://", "https://", "mailto:", "javascript:", "data:")) or raw.startswith("#"):
                continue
            target = raw.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            if target.startswith("/"):
                candidates = route_candidates(target)
            else:
                joined = str((PurePosixPath(path).parent / target))
                normalized = str(PurePosixPath(joined))
                candidates = route_candidates(normalized)
            if not any(candidate in existing or (repo / candidate).exists() for candidate in candidates):
                add(
                    findings,
                    id="DOC-BROKEN-INTERNAL-LINK",
                    severity="medium",
                    category="public-surface",
                    title="Internal documentation/site link has no repository target",
                    path=path,
                    line=line_number(text, offset),
                    evidence=f"{raw} -> tried {candidates[:5]}",
                    deterministic=False,
                    confidence="medium",
                )


def scan_contract_strings(repo: Path, files: list[str], findings: list[Finding]) -> dict[str, dict[str, list[str]]]:
    patterns = {
        "receipt_12_only": re.compile(r"\^?rcg-\[0-9\]\{8\}-\[a-f0-9\]\{12\}\$?"),
        "prelaunch_status": re.compile(r"mainnet_prelaunch_testing"),
        "legacy_gateway_url": re.compile(r"https://trinity-agent-issue-gateway\.onrender\.com"),
        "render_docs_path": re.compile(r"trinity-record-chain-gateway\.onrender\.com/docs/"),
        "guardian_rotation": re.compile(r"guardian_key_rotation|guardian-key-rotation"),
        "direct_old_submit": re.compile(r"/(?:agent-submit|gateway/submit)\b"),
    }
    hits: dict[str, dict[str, list[str]]] = {name: defaultdict(list) for name in patterns}
    for path in files:
        text = read_text(repo, path)
        if text is None:
            continue
        for name, regex in patterns.items():
            for match in regex.finditer(text):
                hits[name][path].append(f"L{line_number(text, match.start())}:{match.group(0)}")
    for path, values in hits["render_docs_path"].items():
        add(
            findings,
            id="CONTRACT-RENDER-DOCS",
            severity="high",
            category="public-surface",
            title="Repository still references nonexistent documentation on the Render API host",
            path=path,
            evidence="; ".join(values[:5]),
        )
    return {name: {p: v for p, v in mapping.items()} for name, mapping in hits.items()}


def registered_tests(repo: Path, files: list[str], findings: list[Finding]) -> dict[str, Any]:
    test_files = sorted(
        p for p in files
        if (Path(p).name.startswith("test_") and p.endswith((".py", ".js", ".mjs")))
    )
    registry_paths = [
        p for p in files
        if p.startswith(".github/workflows/") or p in {
            "scripts/run_ci_group.py",
            "scripts/run_current_system_tests.py",
            "package.json",
        }
    ]
    registry_text = "\n".join(read_text(repo, p) or "" for p in registry_paths)
    unregistered = []
    for test_path in test_files:
        name = Path(test_path).name
        if name not in registry_text and test_path not in registry_text:
            unregistered.append(test_path)
            add(
                findings,
                id="TEST-UNREGISTERED",
                severity="medium",
                category="test-coverage",
                title="Tracked test appears not to be executed by CI or the current-system registry",
                path=test_path,
                evidence="filename/path not found in workflow or test-runner registries",
                deterministic=False,
                confidence="medium",
            )
    return {"test_count": len(test_files), "unregistered": unregistered, "registries": registry_paths}


def snapshot_tracked(repo: Path, files: list[str]) -> dict[str, str]:
    output: dict[str, str] = {}
    for path in files:
        p = repo / path
        try:
            if p.is_file():
                output[path] = sha256_bytes(p.read_bytes())
        except OSError:
            pass
    return output


def changed_since(repo: Path, before: dict[str, str], files: list[str]) -> list[str]:
    after = snapshot_tracked(repo, files)
    changed = sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))
    result = run(repo, ["git", "status", "--porcelain"], timeout=60)
    for line in result.stdout.splitlines():
        if len(line) > 3:
            changed.append(line[3:])
    return sorted(set(changed))


def run_dynamic(repo: Path, files: list[str], findings: list[Finding]) -> list[CommandResult]:
    commands = [
        ("python_compile", [sys.executable, "-m", "compileall", "-q", "scripts", "apps"]),
        ("render_manual_deploy_contract", [sys.executable, "scripts/test_render_manual_deploy_contract.py"]),
        ("record_chain_verify", [sys.executable, "scripts/trinity_record_chain.py", "verify"]),
        ("p0_current", [sys.executable, "scripts/run_ci_group.py", "p0-current"]),
        ("current_system", [sys.executable, "scripts/run_current_system_tests.py"]),
        ("gateway_pytest", [sys.executable, "-m", "pytest", "-q", "apps/record_chain_intake_gateway/tests"]),
    ]
    results: list[CommandResult] = []
    for name, command in commands:
        before = snapshot_tracked(repo, files)
        started = time.monotonic()
        try:
            completed = run(
                repo,
                command,
                timeout=1500,
                env={"PYTHONPATH": "apps/record_chain_intake_gateway:."},
            )
            rc = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            rc = 124
            stdout = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
            stderr += "\nTIMEOUT"
        duration = time.monotonic() - started
        changed = changed_since(repo, before, files)
        result = CommandResult(
            name=name,
            command=command,
            returncode=rc,
            duration_seconds=round(duration, 3),
            stdout_tail=stdout[-12000:],
            stderr_tail=stderr[-12000:],
            changed_files=changed,
        )
        results.append(result)
        if rc != 0:
            add(
                findings,
                id="DYNAMIC-FAIL",
                severity="critical" if name in {"record_chain_verify", "p0_current", "current_system"} else "high",
                category="dynamic-validation",
                title=f"Dynamic audit command failed: {name}",
                evidence=f"returncode={rc}; stderr_tail={stderr[-1000:]}",
            )
        if changed:
            add(
                findings,
                id="TEST-MUTATES-REPO",
                severity="high",
                category="test-isolation",
                title=f"Dynamic audit command changed tracked working-tree state: {name}",
                evidence=", ".join(changed[:30]),
                deterministic=True,
            )
        # Reset any generated tracked/untracked state before the next command.
        run(repo, ["git", "reset", "--hard", "HEAD"], timeout=60)
        run(repo, ["git", "clean", "-fd"], timeout=60)
    return results


def live_json(url: str, *, method: str = "GET", body: bytes | None = None, timeout: int = 60) -> tuple[int, Any, str]:
    headers = {"User-Agent": "trinity-round7-audit/1.0", "Cache-Control": "no-cache"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", "replace")
            try:
                return response.status, json.loads(raw), raw
            except json.JSONDecodeError:
                return response.status, None, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            return exc.code, json.loads(raw), raw
        except json.JSONDecodeError:
            return exc.code, None, raw
    except Exception as exc:
        return 0, None, f"{type(exc).__name__}: {exc}"


def run_live_checks(findings: list[Finding]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    targets = [
        ("site_root", SITE + "/", "GET", None),
        ("public_home_status", SITE + "/api/public-home-status.json", "GET", None),
        ("gateway_health", GATEWAY + "/healthz", "GET", None),
        ("gateway_readiness", GATEWAY + "/record-chain/readiness", "GET", None),
        ("gateway_preflight_invalid", GATEWAY + "/record-chain/preflight", "POST", b"{}"),
        ("builder_help", SITE + "/docs/record-chain-builder-help/", "GET", None),
    ]
    for name, url, method, body in targets:
        status, parsed, raw = live_json(url, method=method, body=body)
        entry = {"name": name, "url": url, "status": status, "json": parsed, "body_sha256": sha256_bytes(raw.encode("utf-8")), "body_preview": raw[:500]}
        checks.append(entry)
        if status == 0 or status >= 500:
            add(
                findings,
                id="LIVE-UNAVAILABLE",
                severity="high",
                category="live-surface",
                title=f"Live surface unavailable or server-erroring: {name}",
                evidence=f"status={status}; {raw[:300]}",
            )
    by_name = {item["name"]: item for item in checks}
    health = by_name.get("gateway_health", {}).get("json")
    readiness = by_name.get("gateway_readiness", {}).get("json")
    if isinstance(health, dict) and health.get("ok") is not True:
        add(findings, id="LIVE-GATEWAY-HEALTH", severity="critical", category="live-surface", title="Gateway health does not report ok=true", evidence=json.dumps(health)[:500])
    if isinstance(readiness, dict) and readiness.get("submit_ready") is not True:
        add(findings, id="LIVE-GATEWAY-READINESS", severity="critical", category="live-surface", title="Gateway readiness does not report submit_ready=true", evidence=json.dumps(readiness)[:500])
    help_body = by_name.get("builder_help", {}).get("body_preview", "")
    # body_preview is too short for anchors; fetch full one more time for deterministic check.
    status, _parsed, raw = live_json(SITE + "/docs/record-chain-builder-help/")
    if status != 200 or 'id="validation-errors"' not in raw or 'id="security-violations"' not in raw:
        add(findings, id="LIVE-HELP-ANCHORS", severity="high", category="live-surface", title="Live recovery page lacks required anchors", evidence=f"status={status}")
    return checks


def dedupe_findings(findings: Iterable[Finding]) -> list[Finding]:
    seen: set[tuple[Any, ...]] = set()
    output: list[Finding] = []
    for item in findings:
        key = (item.id, item.path, item.line, item.evidence)
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return sorted(output, key=lambda f: (order.get(f.severity, 9), f.category, f.path, f.line or 0, f.id))


def markdown_report(report: dict[str, Any]) -> str:
    findings = report["findings"]
    lines = [
        "# Trinity Accord Round 7 — Full-System Audit",
        "",
        f"Audited repository: `{report['repository']}`",
        f"Tracked files scanned: **{report['inventory']['tracked_files']}**",
        f"Workflows scanned: **{report['inventory']['workflows']}**",
        f"Python files: **{report['inventory']['python_files']}**",
        f"JSON files: **{report['inventory']['json_files']}**",
        "",
        "## Finding summary",
        "",
    ]
    counts = report["finding_counts"]
    lines.append(" | ".join(f"**{severity}: {counts.get(severity, 0)}**" for severity in ["critical", "high", "medium", "low"]))
    lines.extend(["", "Deterministic findings are direct failures or exact contract violations. Heuristic findings require source-level confirmation before modification.", ""])
    for severity in ["critical", "high", "medium", "low"]:
        group = [item for item in findings if item["severity"] == severity]
        if not group:
            continue
        lines.extend([f"## {severity.title()} findings", ""])
        for index, item in enumerate(group, 1):
            location = item["path"]
            if item.get("line"):
                location += f":{item['line']}"
            label = "deterministic" if item["deterministic"] else f"heuristic/{item['confidence']}"
            lines.append(f"### {severity[0].upper()}{index}. {item['title']}")
            lines.append("")
            lines.append(f"- ID: `{item['id']}`")
            lines.append(f"- Category: `{item['category']}`")
            lines.append(f"- Evidence class: `{label}`")
            if location:
                lines.append(f"- Location: `{location}`")
            if item["evidence"]:
                lines.append(f"- Evidence: `{item['evidence'][:1800]}`")
            lines.append("")
    lines.extend(["## Dynamic gates", ""])
    for result in report["dynamic_results"]:
        lines.append(f"- `{result['name']}`: rc={result['returncode']}, {result['duration_seconds']}s, changed={result['changed_files'] or 'none'}")
    lines.extend(["", "## Live checks", ""])
    for check in report["live_checks"]:
        lines.append(f"- `{check['name']}`: HTTP {check['status']} — `{check['url']}`")
    lines.extend(["", "## Notes", "", "- Existing immutable Bitcoin/Record-Chain/OTS/Arweave evidence was not modified.", "- Findings about historical files or intentionally retired surfaces must be evaluated against the canonical/non-amending boundary before fixing.", "- The audit script excludes itself and its generated reports from drift calculations.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-dynamic", action="store_true")
    parser.add_argument("--skip-live", action="store_true")
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    files = tracked_files(repo)
    findings: list[Finding] = []
    writers = scan_workflows(repo, files, findings)
    scan_python(repo, files, findings)
    scan_javascript(repo, files, findings)
    parsed_json, schema_ids = scan_json(repo, files, findings)
    scan_internal_links(repo, files, findings)
    contract_hits = scan_contract_strings(repo, files, findings)
    test_registry = registered_tests(repo, files, findings)

    dynamic_results = [] if args.skip_dynamic else [asdict(item) for item in run_dynamic(repo, files, findings)]
    live_checks = [] if args.skip_live else run_live_checks(findings)
    findings = dedupe_findings(findings)
    counts: dict[str, int] = defaultdict(int)
    for item in findings:
        counts[item.severity] += 1

    report = {
        "schema": "trinityaccord.audit.round7.v1",
        "repository": REPO,
        "inventory": {
            "tracked_files": len(files),
            "workflows": sum(1 for p in files if p.startswith(WORKFLOW_DIR + "/") and p.endswith((".yml", ".yaml"))),
            "python_files": sum(1 for p in files if p.endswith(".py")),
            "javascript_files": sum(1 for p in files if p.endswith((".js", ".mjs", ".cjs", ".ts"))),
            "json_files": sum(1 for p in files if p.endswith(".json")),
            "markdown_files": sum(1 for p in files if p.endswith(".md")),
        },
        "finding_counts": dict(counts),
        "findings": [asdict(item) for item in findings],
        "dynamic_results": dynamic_results,
        "live_checks": live_checks,
        "workflow_writers": writers,
        "schema_ids": schema_ids,
        "contract_hits": contract_hits,
        "test_registry": test_registry,
        "parsed_json_count": len(parsed_json),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "report.md").write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({"finding_counts": dict(counts), "output": str(output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
