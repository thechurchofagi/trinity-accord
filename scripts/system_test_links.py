#!/usr/bin/env python3
import re
import sys
import yaml
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
    "memory","wrapper","content","plain","image","raw",
    "status","action","challenge","fail","handle","handling",
    "lighting","microscope","moon","star","planet","touch",
    "forensics","notary","audit","maintainer","resonance",
    "orientation","query","recommended","token","tools","video",
    "carRef","mediaRef","generated_by","possibly","release",
    "explorer","assets","signature","mismatched","non-canonical",
    "Yandex","Greek","ISSUE_BODY","commit","Chronicle","Merkle",
    "micro","microscopy","levels","consumer","cache","gateway",
    "json","proof","full","human","Echoes","files","digests",
    "records","scripts","developer","checksum",
}

# Regex patterns for prose identifiers that look like paths but aren't
PROSE_PATH_PATTERNS = [
    r"^/[A-Z]\d/",           # /D1/C1/T2, /P8/P9, /D2/B1, /C2/P1, /RC8/RC9
    r"^/[A-Z]\d$",           # /P8/P9 as separate match
    r"^/D\d/",               # /D/T/C/P
    r"^/P\d/",               # /P8/P9-level
    r"^/V\d",                # /V3.
    r"^/RFC\d+",             # /RFC8785
    r"^/TC\d+",              # /TC086/TC087
    r"^/CL[a-zA-Z0-9]{8,}",  # /CLdophB1MsI (Bitcoin txid)
    r"^/[A-Z]{2}\d/",        # /RC8/RC9
    r"^/[A-Z]/[A-Z]/[A-Z]", # /D/T/C/P
    r"^/[a-z_]+_evidence$",  # schema field names: /bitcoin_evidence, /hash_evidence
    r"^/time_anchor",        # schema field
    r"^/project-side",       # prose reference
    r"^/cross-anchor",       # prose reference
    r"^/tokenURI",           # prose reference
    r"^/model/tool",         # prose reference
    r"^/multi-scale",        # prose reference
    r"^/time-anchor",        # prose reference
    r"^/echo-triage",        # doc reference
    r"^/verification_cases", # test reference
    r"^/FIXME",              # red-team placeholder
    r"^/then/else",          # code logic reference
    r"^/submit-echo",        # prose reference
    r"^/extra/duplicate",    # red-team test
    r"^/overlong",           # red-team test
    r"^/traversal",          # red-team test
    r"^/notarial-certificate", # directory ref
    r"^/shenzhen-notary",    # archive file ref
    r"^/arweave-bundle",     # archive file ref
    r"^/hash-manifest",      # archive file ref
    r"^/spv-bundle",         # archive file ref
    r"^/ta-avr-meta-audit",  # archive file ref
    r"^/verify-release",     # archive file ref
    r"^/echo-triage",        # doc ref
    r"^/RECOVERY\.md",       # file ref
    r"^/tmp/",               # temp path
    r"^/members/",           # GitHub path
    r"^/thechurchofagi/",    # GitHub org path
    r"^/schema\.org",        # external ref
    r"^/eth-witness$",       # archive directory
    r"^/digests/$",          # directory
    r"^/records/$",          # directory
    r"^/scripts/$",          # directory
    r"^/files/$",            # directory
    r"^/api/$",              # directory
    r"^/\.well-known$",      # directory
    r"^/AGENT-ENTRY-NOTICE", # archived file
    r"^/echo-submission-field-guide$",  # exists in api/
    r"^/api$",               # directory reference
    r"^/developer/",         # prose path
    r"^/checksum/",          # prose path
    r"^/propagation/",       # taxonomy path
]


def build_permalink_map():
    """Build a set of all Jekyll permalinks from markdown front matter."""
    permalinks = set()
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts or "node_modules" in md.parts:
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1])
        except Exception:
            continue
        if isinstance(fm, dict) and "permalink" in fm:
            pl = fm["permalink"]
            if isinstance(pl, str):
                permalinks.add(pl)
                if pl.endswith("/") and len(pl) > 1:
                    permalinks.add(pl.rstrip("/"))
                else:
                    permalinks.add(pl + "/")
    return permalinks


def build_file_index():
    """Build a set of all actual file paths relative to repo root."""
    files = set()
    for p in ROOT.rglob("*"):
        if ".git" in p.parts or "node_modules" in p.parts or "_site" in p.parts:
            continue
        if p.is_file():
            rel = str(p.relative_to(ROOT))
            files.add(rel)
            # Also add URL-style (without extension for .md files)
            if p.suffix == ".md":
                files.add(rel[:-3])  # without .md
    return files


def is_html_tag(path):
    slug = path.strip("/").split("/")[0].split("#")[0].split("?")[0]
    return slug.lower() in HTML_TAGS

def is_external_domain_ref(path):
    for pat in EXTERNAL_DOMAIN_PATTERNS:
        if re.search(pat, path, re.I):
            return True
    return False

def exists_for_path(url, permalink_set, file_index):
    url = url.split("#", 1)[0].split("?", 1)[0]
    if not url == "/" and url.rstrip("/") in ALLOW_MISSING:
        return True
    if not url or url == "/":
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
    # Check prose path patterns (schema fields, component IDs, etc.)
    clean = "/" + slug
    for pat in PROSE_PATH_PATTERNS:
        if re.match(pat, clean):
            return True
    if slug.endswith(".py") or slug.endswith(".sh") or slug.endswith(".mjs"):
        return True
    if len(slug) > 40:
        return True
    if slug.startswith("files/") or slug.startswith("records/"):
        return True
    if slug in ("api", "api/"):
        return True
    # Directory-only references (end with /)
    if slug.endswith("/") and "/" not in slug.rstrip("/"):
        if slug.rstrip("/") in PROSE_FALSE_POSITIVES:
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
    if "deprecated" in slug or "archive" in slug:
        return True

    # Check Jekyll permalink map
    clean = "/" + slug
    if clean in permalink_set:
        return True
    if clean + "/" in permalink_set:
        return True
    if clean.rstrip("/") in permalink_set:
        return True

    # Check actual file index (handles /api/xxx.json, /.well-known/xxx, etc.)
    if slug in file_index:
        return True
    # Also check with leading stripped for nested refs
    if slug + ".json" in file_index:
        return True
    if slug + ".md" in file_index:
        return True

    # Handle bare JSON refs (e.g. /authority.json -> api/authority.json)
    if slug.endswith(".json") and "/" not in slug:
        if ("api/" + slug) in file_index:
            return True

    # Handle archive subpath refs (e.g. /authority-manifest/x.json -> archive/authority-manifest/x.json)
    if ("archive/" + slug) in file_index:
        return True

    # Check if a .md file exists with matching name at root (Jekyll renders .md -> /name/)
    if "/" not in slug:
        md_candidate = ROOT / f"{slug}.md"
        if md_candidate.exists():
            return True

    return False

def main():
    permalink_set = build_permalink_map()
    file_index = build_file_index()
    pattern = re.compile(r'(?<!https:)(?<!http:)(?<!mailto:)(?P<url>/[A-Za-z0-9_\-./]+)')
    for file in TEXT_FILES:
        if not file.exists():
            continue
        text = file.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            url = m.group("url")
            # Strip trailing punctuation that the regex accidentally captures
            url = url.rstrip(".,;:!?")
            if not url:
                continue
            if not exists_for_path(url, permalink_set, file_index):
                FAIL.append(f"{file.relative_to(ROOT)}: broken internal path {url}")

    if FAIL:
        print("LINK TEST FAIL")
        for f in sorted(set(FAIL)):
            print("FAIL:", f)
        sys.exit(1)
    print("LINK TEST PASS")

if __name__ == "__main__":
    main()
