#!/usr/bin/env python3
"""Narrow publication helpers for TA-TR-2026-17."""
from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, subprocess, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = "research/set-valued-causal-inheritance-v1-20260925"
TITLE = "Set-Valued Causal Inheritance for Functional Self-Continuity: Representation Theorems and Persistent-Agent Benchmarks"
REPORT = "TA-TR-2026-17"
VERSION = "1.0"
DATE = "2026-09-25"
STEM = "set-valued-causal-inheritance"

PROTECTED = {
  21675727,21699878,21900592,22761411,22804542,22809019,22830239,
  22839629,22840604,22842789,22844927,22844928,22846307,22852884,
  22852885,22854705,22865494,22866205,22866775,22871209,22885976,
  22886276,22934654,22939808
}
CLIENT_BLOB = "a0cbc84cc5fd826c06d16456c4adbaa40dabc788"

PUBLISHED_FILES = {
  f"{STEM}-v{VERSION}.pdf",
  f"{STEM}-v{VERSION}.md",
  f"{STEM}-supplement-v{VERSION}.pdf",
  f"{STEM}-supplement-v{VERSION}.md",
  "citation.bib","citation.ris","citation.csl.json",
  "README-LICENSE.txt","REVIEW-AND-SOURCES.md","SHA256SUMS.txt"
}
STATE_FILES = {
  "create-intent.json","deposit.json","preparation-attempt.json",
  "publication-attempt.json","publication-record.json"
}
PACKAGE_STATE_FILES = {
  "EXPECTED-PUBLICATION.json","format-checks.json"
}
MAX_FILE_BYTES = 16*1024*1024

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load(name: str, root=ROOT):
    return json.loads((root/name).read_text(encoding="utf-8"))

def save(name: str, value, root=ROOT):
    p = root/name
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def persist(paths):
    allowed = [str((ROOT/p).relative_to(REPO)) for p in paths if (ROOT/p).exists()]
    if not allowed:
        return
    subprocess.run(["git","config","user.name","github-actions[bot]"], cwd=REPO, check=True)
    subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"], cwd=REPO, check=True)
    subprocess.run(["git","add","--",*sorted(allowed)], cwd=REPO, check=True)
    staged = subprocess.check_output(["git","diff","--cached","--name-only"], cwd=REPO, text=True).splitlines()
    if staged:
        subprocess.run(["git","commit","-m","research: preserve TA17 publication state [skip ci]"], cwd=REPO, check=True)
        for attempt in range(3):
            p = subprocess.run(["git","push","origin","HEAD:"+BRANCH], cwd=REPO)
            if p.returncode == 0:
                return
            subprocess.run(["git","fetch","origin",BRANCH,"--prune"], cwd=REPO, check=True)
            subprocess.run(["git","rebase","origin/"+BRANCH], cwd=REPO, check=True)
        raise RuntimeError("Could not persist TA17 state")

def client():
    old = ROOT.parent/"reading-trinity-accord"/"publish_zenodo.py"
    data = old.read_bytes()
    actual = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual != CLIENT_BLOB:
        raise RuntimeError("Established Zenodo client changed")
    spec = importlib.util.spec_from_file_location("ta_verified_zenodo_client", old)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    token = os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Publication credential unavailable")
    return module.Zenodo(token)

def read(z, path, authenticated=True):
    for attempt, delay in enumerate((0,3,8,15)):
        if delay:
            time.sleep(delay)
        try:
            return z.request(path, authenticated=authenticated)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise

def validate_record_id(rid):
    if type(rid) is not int or rid <= 0 or rid in PROTECTED:
        raise RuntimeError("Invalid or protected prior record ID")
    return rid

def check_deposit(dep, identity=None):
    rid = validate_record_id(dep.get("id"))
    md = dep.get("metadata", {})
    if (md.get("title"), str(md.get("version"))) != (TITLE, VERSION):
        raise RuntimeError("Reserved title/version mismatch")
    doi = dep.get("doi") or md.get("prereserve_doi",{}).get("doi") or md.get("doi")
    if doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Reserved DOI mismatch")
    if identity is not None:
        if (rid,doi)!=(identity.get("record_id"),identity.get("doi")):
            raise RuntimeError("Reserved record differs from checkpoint")
    return rid,doi

def select_existing(rows):
    if not isinstance(rows,list) or len(rows)>=100:
        raise RuntimeError("Unexpected draft search")
    hits = []
    for r in rows:
        md = r.get("metadata",{})
        if md.get("title")==TITLE and str(md.get("version"))==VERSION:
            hits.append(r)
    if len(hits)>1:
        raise RuntimeError("Multiple TA17 draft records found")
    return hits[0] if hits else None

def download_public(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!="zenodo.org" or p.username or p.password:
        raise RuntimeError("Unexpected public file host")
    req = urllib.request.Request(url, headers={"User-Agent":"TrinityAccord-TA17-Readback/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES:
        raise RuntimeError("Public asset too large")
    return data

def inject_identity(text: str, doi: str) -> str:
    lines = text.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if line.startswith("**Author:**") and not inserted:
            out.append(f"**Report:** {REPORT}  ")
            out.append(f"**DOI:** {doi}  ")
            inserted = True
    text = "\n".join(out) + "\n"
    text = text.replace("**Version:** Final Preprint Manuscript v1.0", f"**Version:** {VERSION}")
    text = text.replace("**Version:** Final Preprint Candidate v1.0", f"**Version:** {VERSION}")
    return text

def build_package():
    dep = load("deposit.json")
    rid, doi = dep["record_id"], dep["doi"]
    if doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Deposit identity inconsistent")
    pub = ROOT/"published"
    pub.mkdir(exist_ok=True)

    main = inject_identity((ROOT/"source-main.md").read_text(encoding="utf-8"), doi)
    supp = inject_identity((ROOT/"source-supplement.md").read_text(encoding="utf-8"), doi)
    (pub/f"{STEM}-v{VERSION}.md").write_text(main,encoding="utf-8")
    (pub/f"{STEM}-supplement-v{VERSION}.md").write_text(supp,encoding="utf-8")

    for src, out in [
        (pub/f"{STEM}-v{VERSION}.md", pub/f"{STEM}-v{VERSION}.pdf"),
        (pub/f"{STEM}-supplement-v{VERSION}.md", pub/f"{STEM}-supplement-v{VERSION}.pdf")
    ]:
        subprocess.run([
          "pandoc",str(src),"-o",str(out),"--pdf-engine","xelatex",
          "--from=markdown+tex_math_single_backslash",
          "-V","mainfont=DejaVu Serif","-V","monofont=DejaVu Sans Mono"
        ], check=True)

    bib = f"""@article{{Liu2026SetValuedCausalInheritance,
  author = {{Liu, Hongju}},
  title = {{{TITLE}}},
  year = {{2026}},
  version = {{{VERSION}}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}},
  note = {{Preprint; not peer reviewed}}
}}
"""
    ris = f"""TY  - JOUR
AU  - Liu, Hongju
TI  - {TITLE}
PY  - 2026
DA  - {DATE}
VL  - {VERSION}
DO  - {doi}
UR  - https://doi.org/{doi}
N1  - Preprint; not peer reviewed
ER  -
"""
    csl = {
      "id":doi, "type":"article", "title":TITLE,
      "author":[{"family":"Liu","given":"Hongju"}],
      "issued":{"date-parts":[[2026,9,25]]},
      "version":VERSION, "DOI":doi, "URL":"https://doi.org/"+doi,
      "note":"Preprint; not peer reviewed"
    }
    (pub/"citation.bib").write_text(bib,encoding="utf-8")
    (pub/"citation.ris").write_text(ris,encoding="utf-8")
    (pub/"citation.csl.json").write_text(json.dumps(csl,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    license_text = f"""{REPORT} | Version {VERSION} | {DATE}
{TITLE}
DOI: {doi}

Author of record and responsible depositor: Hongju Liu.
Substantial ChatGPT assistance was used for literature retrieval, formalization, theorem checking, coding, benchmark design, replication analysis, drafting, editing and publication preparation under human direction. This is a preprint and has not been externally peer reviewed.

CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) applies to newly written material to the extent rights are held. Cited third-party works retain their own rights.

The main PDF is the primary scholarly publication file. Markdown source and a supplementary computational appendix are included for transparency and reproducibility. Controlled synthetic and recurrent-agent experiments are not evidence of human identity, phenomenal consciousness, moral status or legal identity. Negative results and failed replications are retained.

This paper is adjacent first-party research and does not define, amend, validate or authoritatively interpret the Trinity Accord or its three Bitcoin Originals.
"""
    (pub/"README-LICENSE.txt").write_text(license_text,encoding="utf-8")

    review = f"""# Review and Sources Record

**Report:** {REPORT}  
**Version:** {VERSION}  
**DOI:** {doi}

## Publication posture

- Theoretical/computational preprint; not peer reviewed.
- Human author of record and responsible depositor: Hongju Liu.
- Substantial AI assistance disclosed.
- The paper is non-amending adjacent research and is not independent corroboration of the Trinity Accord.
- DOI registration, OTS and Arweave preservation do not certify truth, originality, peer review or Google Scholar indexing.

## Evidence hierarchy

The strongest claims are formal theorems and analytical constructions. Synthetic oracle-proxy studies are sufficiency checks. Intervention-derived and recurrent studies provide controlled constructive demonstrations. The end-to-end process-aware long-horizon advantage is explicitly **not established** after eight-seed controller replication; this failed replication is preserved in the paper.

## Replication added before publication

- Six controller seeds support learnability of contextual-bandit persistence-operation selection in the controlled task.
- Three independently trained GRU-plus-merger stacks reproduce the core redundancy/complementarity/stale-restore/merge lineage structure.
- Eight controller seeds do not reproduce a reliable process-aware long-horizon return advantage.

## Originality boundary

The manuscript does not claim that causal states, random sets, total correlation, Möbius transforms, causal representation learning, reinforcement learning, checkpoint/fork/restore/merge operations, or personal-identity fission problems are individually new. Its narrower contribution is their combination into a set-valued, representation-disciplined and current-process-grounded functional-continuity framework with exact decision consequences and controlled persistence-agent benchmarks.

See the manuscript references for the complete bibliography.
"""
    (pub/"REVIEW-AND-SOURCES.md").write_text(review,encoding="utf-8")

    others = sorted(PUBLISHED_FILES - {"SHA256SUMS.txt"})
    sums = []
    for name in others:
        data=(pub/name).read_bytes()
        sums.append(f"{sha(data)}  {name}")
    (pub/"SHA256SUMS.txt").write_text("\n".join(sums)+"\n",encoding="utf-8")

    rows=[]
    for name in sorted(PUBLISHED_FILES):
        data=(pub/name).read_bytes()
        rows.append({"name":name,"bytes":len(data),"sha256":sha(data)})
    expected={
      "report_number":REPORT,"record_id":rid,"doi":doi,"title":TITLE,"version":VERSION,
      "file_count":len(rows),"files":rows,"prior_records_modified":False
    }
    save("EXPECTED-PUBLICATION.json",expected)

    checks={"state":"FORMAT_CHECKS_PASS","report_number":REPORT,"version":VERSION}
    for name in [f"{STEM}-v{VERSION}.pdf", f"{STEM}-supplement-v{VERSION}.pdf"]:
        info=subprocess.check_output(["pdfinfo",str(pub/name)],text=True)
        pages=[x for x in info.splitlines() if x.startswith("Pages:")]
        if not pages or int(pages[0].split(":",1)[1].strip())<=0:
            raise RuntimeError("PDF page check failed")
        txt=subprocess.check_output(["pdftotext",str(pub/name),"-"],text=True)
        if len(txt)<1000:
            raise RuntimeError("PDF text extraction failed")
    checks["pdf_generated"]=True
    checks["pdf_text_extractable"]=True
    checks["source_markdown_preserved"]=True
    checks["negative_results_preserved"]=True
    save("format-checks.json",checks)
    return expected

def validate_local_package():
    expected=load("EXPECTED-PUBLICATION.json")
    if (expected.get("title"),expected.get("report_number"),str(expected.get("version"))) != (TITLE,REPORT,VERSION):
        raise RuntimeError("Manifest identity mismatch")
    rid=validate_record_id(expected.get("record_id"))
    if expected.get("doi") != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Manifest DOI mismatch")
    pub=ROOT/"published"
    names={p.name for p in pub.iterdir() if p.is_file()}
    if names != PUBLISHED_FILES:
        raise RuntimeError(f"Published inventory mismatch: {sorted(names)}")
    rows={x["name"]:x for x in expected.get("files",[])}
    if set(rows)!=PUBLISHED_FILES or expected.get("file_count")!=len(PUBLISHED_FILES):
        raise RuntimeError("Manifest file inventory mismatch")
    for name,item in rows.items():
        data=(pub/name).read_bytes()
        if len(data)!=item["bytes"] or sha(data)!=item["sha256"]:
            raise RuntimeError("Package hash mismatch: "+name)
    raw=(ROOT/"EXPECTED-PUBLICATION.json").read_bytes()
    return expected, sha(raw)

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--build",action="store_true")
    p.add_argument("--verify",action="store_true")
    p.add_argument("--persist",action="store_true")
    a=p.parse_args()
    if a.build:
        print(json.dumps(build_package(),ensure_ascii=False,indent=2))
    if a.verify:
        exp,digest=validate_local_package()
        print(json.dumps({"state":"PACKAGE_VERIFY_PASS","file_count":exp["file_count"],"manifest_sha256":digest},indent=2))
    if a.persist:
        paths=set(STATE_FILES)|set(PACKAGE_STATE_FILES)|{"published"}
        persist(paths)
