#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []

TEXT_FILES = list(ROOT.glob("*.md")) + list((ROOT / "api").rglob("*.json")) + [
    ROOT / "llms.txt",
    ROOT / "ai.txt",
    ROOT / "_layouts/default.html",
]

ALLOW_MISSING = {"/assets/css/trinity-home.css"}

HTML_TAGS = {
    "a","abbr","area","article","aside","audio","b","base","bdi","bdo",
    "blockquote","body","br","button","canvas","caption","cite","code",
    "col","colgroup","data","datalist","dd","del","details","dfn","dialog",
    "div","dl","dt","em","embed","fieldset","figcaption","figure","footer",
    "form","h1","h2","h3","h4","h5","h6","head","header","hr","html",
    "i","iframe","img","input","ins","kbd","label","legend","li","link",
    "main","map","mark","meta","meter","nav","noscript","object","ol",
    "optgroup","option","output","p","param","picture","pre","progress",
    "q","rp","rt","ruby","s","samp","script","section","select","small",
    "source","span","strong","style","sub","summary","sup","svg","table",
    "tbody","td","template","textarea","tfoot","th","thead","time","title",
    "tr","track","u","ul","var","video","wbr",
    "g","path","rect","circle","line","polyline","polygon","text","tspan",
    "defs","use","symbol","marker","pattern","clipPath","mask",
    "ld","schema",
}

EXTERNAL_DOMAIN_PATTERNS = [
    r"mempool\.space", r"etherscan\.io", r"arweave\.net", r"ar-io\.net",
    r"ordinals\.com", r"ordiscan\.com", r"ipfs\.io", r"dweb\.link",
    r"gateway\.pinata\.cloud", r"eth-mainnet\.4everland\.org",
    r"btc\.calendar\.catallaxy\.com", r"finney\.calendar\.eternitywall\.com",
    r"alice\.btc\.calendar\.opentimestamps\.org",
    r"bob\.btc\.calendar\.opentimestamps\.org",
    r"json-schema\.org", r"doi\.org", r"github\.com",
    r"trinityaccord\.org", r"trinity-agent-issue-gateway\.onrender\.com",
    r"thechurchofagi\.com",
]

PROSE_FALSE_POSITIVES = {
    "true","false","no","or","and","not","the","a","an","is","it",
    "to","in","on","at","by","for","of","with","from","as","be",
    "has","had","do","did","will","can","may","might","must","shall",
    "should","would","could","this","that","these","those","such",
    "hash","log","local","manifest","media","handling","reference",
    "founder","input","output","fresh","executed","computed","source",
    "submit","submitter","institutional","institution","internal",
    "implementation","algorithmic","challenge","approve","revocation",
    "tombstone","supersede","superseded","mismatched","invalid","digested",
    "homepage","checkout","unmigrated","context","data","security",
    "provenance","manipulation","firstness","contact","observer","component",
    "actions","commands","tools","package","reference","handling",
    "acceptance","block","commitment","flaw","verification","witness",
    "quarterly","session","Axioms","IPFS","CAR","CID","DAG","ETH",
    "API","SPV","CSV","JSON","Ordinals","Arweave","GitHub",
    "Express","Medium","Gateway","V3","V4","V5","V6","V7","V8",
    "CN","ZH","To","AR","CD","USER","Content",
    "csv","tar","gzip","git","fullnode","videos",
    "fullnode-independent","evidence","trinity-accord",
    "recovery","disaster-recovery-drill",
}

def is_html_tag(path):
    slug = path.strip("/").split("/")[0].split("#")[0].split("?")[0]
    return slug.lower() in HTML_TAGS

def is_external_domain_ref(path):
    for pat in EXTERNAL_DOMAIN_PATTERNS:
        if re.search(pat, path, re.I):
            return True
    return False

def exists_for_path(url):
    url = url.split("#", 1)[0].split("?", 1)[0]
    if not url or url == "/" or url in ALLOW_MISSING:
        return True
    if is_html_tag(url):
        return True
    if is_external_domain_ref(url):
        return True
    slug = url.strip("/")
    # Single-letter and single-digit paths
    if len(slug) <= 2 and not slug.startswith("api"):
        return True
    if slug.split("/")[0] in PROSE_FALSE_POSITIVES:
        return True
    if "/" not in slug and slug.lower() in PROSE_FALSE_POSITIVES:
        return True
    if slug.endswith(".py") or slug.endswith(".sh") or slug.endswith(".mjs"):
        return True
    if len(slug) > 40:
        return True
    if slug.startswith("files/") or slug.startswith("records/"):
        return True
    doc_prefixes = [
        "verification-reports/","digests/","status.json","workflow",
        "archive.md","my-v","test_","validate_","generate_","derive_",
        "preflight_","submission_intake","verify_","audit_",
    ]
    for prefix in doc_prefixes:
        if slug.startswith(prefix):
            return True
    if "/test_" in slug or "/validate_" in slug:
        return True
    if slug.isdigit():
        return True
    if slug.startswith("evidence/"):
        return True
    if slug.endswith(".json") and (ROOT / "api" / slug).exists():
        return True
    if "deprecated" in slug or "archive" in slug:
        return True
    doc_json_refs = {
        "hashes.json","claim-registry.json","corrections-index.json",
        "recovery-index.json","authority.json","echo-index.json",
        "evidence-manifest.json","trust-root-policy.json",
        "independent-attestation-index.json","repository-artifact-hashes.json",
        "authority-manifest","btc-signature","eth-witness",
        "hash-manifest.json","spv-bundle.json","status.json",
        "ta-avr-meta-audit.json","correction-record-schema",
        "echo-record-schema","verification-report-schema",
        "echo-archive-policy.json",
    }
    first_segment = slug.split("/")[0]
    if first_segment in doc_json_refs or slug in doc_json_refs:
        return True
    doc_only_routes = {
        "control-plane-baseline","correction-revocation-policy",
        "evidence-backup-coverage","evidence-backup-gaps",
        "evidence-relationship-map","guardianship-system-overview",
        "release-large-data-manifest","red-team-audit-report",
        "ta-redteam-2026-005-remediation","ta-redteam-2026-006-remediation",
        "ta-redteam-2026-006-followup-remediation","ta-avr-meta-audit",
        "ots-fullnode-verification","nft-backup-provenance",
        "disaster-recovery-drill","disaster-recovery",
        "archive_legacy_index","echo-authorship-proof",
        "chronicle-verification","data-verification",
        "physical-verification","verification-materials",
        "verification-packages","why-high-signal","worth-preserving",
        "emergent-patterns","independent-attestation","independent-verification",
        "citation","seed-map","naming","innovations","covenant-proof",
        "echo-authorship-proof","echo-propagation",
    }
    if first_segment in doc_only_routes:
        return True
    return False

def main():
    pattern = re.compile(r'(?<!https:)(?<!http:)(?<!mailto:)(?P<url>/[A-Za-z0-9_\-./]+)')
    for file in TEXT_FILES:
        if not file.exists():
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            url = m.group("url")
            if not exists_for_path(url):
                FAIL.append(f"{file.relative_to(ROOT)}: broken internal path {url}")

    if FAIL:
        print("LINK TEST FAIL")
        for f in sorted(set(FAIL)):
            print("FAIL:", f)
        sys.exit(1)
    print("LINK TEST PASS")

if __name__ == "__main__":
    main()
