#!/usr/bin/env python3
"""Exact finite checks for R184.

The program checks a declared toy organization. It contains no phenomenal
variable and supplies no human or deployed-agent evidence.
"""

from itertools import product
import json
from pathlib import Path

ROUTES = frozenset({"M", "Q"})
ARCHS = ("M_ONLY", "Q_ONLY", "RED_M_PRIORITY", "RED_Q_PRIORITY")


def command(arch, m, q):
    """Return resumed target, or None if no installed route can supply it."""
    if arch == "M_ONLY":
        return m
    if arch == "Q_ONLY":
        return q
    if arch == "RED_M_PRIORITY":
        return m if m is not None else q
    if arch == "RED_Q_PRIORITY":
        return q if q is not None else m
    raise ValueError(arch)


def installed(arch):
    if arch == "M_ONLY":
        return frozenset({"M"})
    if arch == "Q_ONLY":
        return frozenset({"Q"})
    return ROUTES


def successful_supports(arch):
    """Deletion-only family, with retained route content equal to target."""
    family = []
    for keep_m, keep_q in product((0, 1), repeat=2):
        keep = frozenset(r for r, b in (("M", keep_m), ("Q", keep_q)) if b)
        m = 1 if "M" in keep and "M" in installed(arch) else None
        q = 1 if "Q" in keep and "Q" in installed(arch) else None
        if command(arch, m, q) == 1:
            family.append(keep)
    return family


def minimal_sets(family):
    return [s for s in family if not any(t < s for t in family)]


checks = []


def check(name, condition, cases, detail=None):
    if not condition:
        raise AssertionError(name)
    checks.append({"name": name, "passed": True, "cases": cases, "detail": detail})


# Baseline episode enumeration: obstruction is present during t1, removed at t2,
# and no directive event occurs at t2. Labels are crossed but are not dynamics.
rows = []
for tau, arch, keep_m, keep_q, deliberate, report, substrate in product(
    (0, 1), ARCHS, (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)
):
    keep = frozenset(r for r, b in (("M", keep_m), ("Q", keep_q)) if b)
    m = tau if "M" in keep and "M" in installed(arch) else None
    q = tau if "Q" in keep and "Q" in installed(arch) else None
    out = command(arch, m, q)
    rows.append(
        {
            "tau": tau,
            "arch": arch,
            "support": sorted(keep),
            "deliberate_label": deliberate,
            "report": report,
            "substrate_label": substrate,
            "blocked_t1": 1,
            "released_t2": 1,
            "new_directive_t2": 0,
            "resumed": out,
            "success": out == tau,
        }
    )

check("baseline enumeration has 256 rows", len(rows) == 256, len(rows))
check("no row contains a release-time directive", all(r["new_directive_t2"] == 0 for r in rows), len(rows))

# Target specificity under isolated paths.
for arch in ("M_ONLY", "Q_ONLY"):
    outs = [command(arch, tau if arch == "M_ONLY" else None, tau if arch == "Q_ONLY" else None) for tau in (0, 1)]
    check(f"{arch} isolated route follows target swap", outs == [0, 1], 2)

# Exact deletion families and R183 individual/disjunctive analysis.
families = {arch: successful_supports(arch) for arch in ARCHS}
minima = {arch: minimal_sets(fam) for arch, fam in families.items()}
check("M-only minimum is {M}", minima["M_ONLY"] == [frozenset({"M"})], 4)
check("Q-only minimum is {Q}", minima["Q_ONLY"] == [frozenset({"Q"})], 4)
for arch in ("RED_M_PRIORITY", "RED_Q_PRIORITY"):
    mins = set(minima[arch])
    core = set.intersection(*(set(s) for s in mins)) if mins else set()
    hits_both = all(ROUTES.intersection(s) for s in mins)
    check(f"{arch} has two singleton minima", mins == {frozenset({"M"}), frozenset({"Q"})}, 4)
    check(f"{arch} has empty individual core", core == set(), 2)
    check(f"{arch} requires disjunction {{M,Q}}", hits_both, 2)

# Equal intact behavior cannot identify priority or route use.
intact_equal = []
for tau in (0, 1):
    intact_equal.append(command("RED_M_PRIORITY", tau, tau) == command("RED_Q_PRIORITY", tau, tau) == tau)
check("equal intact resumption underdetermines redundant priority", all(intact_equal), 2)

# A predeclared conflict perturbation distinguishes the installed consumer rule.
conflicts = []
for tau in (0, 1):
    m, q = tau, 1 - tau
    conflicts.append(
        {
            "tau": tau,
            "M_priority": command("RED_M_PRIORITY", m, q),
            "Q_priority": command("RED_Q_PRIORITY", m, q),
        }
    )
check(
    "conflict intervention distinguishes redundant consumer rules",
    all(x["M_priority"] == x["tau"] and x["Q_priority"] == 1 - x["tau"] for x in conflicts),
    2,
)

# Reflex/deliberate, report and substrate labels do not select dynamics.
groups = {}
for r in rows:
    key = (r["tau"], r["arch"], tuple(r["support"]))
    groups.setdefault(key, set()).add((r["resumed"], r["success"]))
check("deliberate/reflex label is dynamically inert", all(len(v) == 1 for v in groups.values()), len(rows))
check("report label is dynamically inert", all(len(v) == 1 for v in groups.values()), len(rows))
check("biological/prosthetic label is dynamically inert", all(len(v) == 1 for v in groups.values()), len(rows))

result = {
    "schema": "uct-r184-target-persistence-check/1.0",
    "finite_rows": len(rows),
    "checks": checks,
    "architectures": {
        a: {
            "successful_supports": [sorted(s) for s in families[a]],
            "minimal_supports": [sorted(s) for s in minima[a]],
        }
        for a in ARCHS
    },
    "conflict_witnesses": conflicts,
    "limits": [
        "toy equations only",
        "no phenomenal variable",
        "no actual human or deployed-agent admission",
        "deletion family assumes retained route content remains target-correct",
        "labels are deliberately inert controls, not claims that real substrate or policy is irrelevant",
    ],
}

out = Path(__file__).with_name("MODEL_RESULTS.json")
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"rows": len(rows), "checks": len(checks), "result": str(out)}, indent=2))
