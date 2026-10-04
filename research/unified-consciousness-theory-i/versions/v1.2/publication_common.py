from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, shutil, subprocess, time, urllib.error, urllib.parse, urllib.request

ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[3]
BRANCH="research/uct-paper-a-v1-2-20261004"
PREVIOUS_TITLE="Unified Consciousness Theory I: Ontic Structure, Physical Views, and the Structural Continuity from Physical Process to Conceptual Self"
TITLE="Unified Consciousness Theory I: Structural–Experiential Identity and the Continuity from Physical Process to Conceptual Self"
REPORT="TA-TR-2026-20"
VERSION="1.2"
DATE="2026-10-04"
PREVIOUS_RECORD=23030207
EXPECTED_CONCEPT="23005587"
STEM="unified-consciousness-theory-i"
SOURCE_GIT_BLOB_SHA1="310204d4e83c5478bf18d34274bcdba996ffda28"
CLIENT_BLOB="a0cbc84cc5fd826c06d16456c4adbaa40dabc788"
PROTECTED={23005588,23029358,23030207,23030320}
STATE_FILES={"create-intent.json","deposit.json","preparation-attempt.json","publication-attempt.json","publication-record.json","EXPECTED-PUBLICATION.json","format-checks.json"}
PACKAGE_FILES={
 f"{STEM}-v{VERSION}.md",f"{STEM}-v{VERSION}.pdf",
 f"VERSION-CHANGES-v{VERSION}.md",f"REVIEW-AND-SOURCES-v{VERSION}.md",
 "FORMAL-AUDIT-v1.2.md","formal-dependency-graph-v1.2.json","formal-dependency-graph-v1.2.dot",
 "README-LICENSE.txt","citation.bib","citation.ris","citation.csl.json","SHA256SUMS.txt","manifest.json"
}
MAX_FILE_BYTES=24*1024*1024

def sha(b): return hashlib.sha256(b).hexdigest()
def load(name): return json.loads((ROOT/name).read_text(encoding="utf-8"))
def save(name,value):
    if name not in STATE_FILES: raise RuntimeError("unexpected state file")
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def ensure_source():
    p=ROOT/"source-main.md"
    if not p.exists(): raise RuntimeError("frozen source missing")
    actual=subprocess.check_output(["git","hash-object",str(p)],cwd=REPO,text=True).strip()
    if actual!=SOURCE_GIT_BLOB_SHA1: raise RuntimeError("frozen source git-blob mismatch")
    s=p.read_text(encoding="utf-8")
    if s.count("__DOI_RESERVED_AT_RELEASE__")!=2: raise RuntimeError("expected exactly two DOI placeholders")
    if "1.2-RC" in s or "publication paused" in s: raise RuntimeError("release-candidate marker remained")
    for x in ("Corollary E1 — No First Conscious Ancestor","Corollary E2 — Fine-Grained Structural Chains","Conditional Lemma E3 — Connected Existence Constancy","# Appendix C. Revision-specific dependency ledger"):
        if x not in s: raise RuntimeError("frozen source missing required content: "+x)
    return p

def persist(paths=None):
    candidates=set(paths or STATE_FILES); candidates.update({"source-main.md","published"})
    rel=[]
    for name in sorted(candidates):
        p=ROOT/name
        if p.exists(): rel.append(str(p.relative_to(REPO)))
    if not rel:return
    subprocess.run(["git","config","user.name","github-actions[bot]"],cwd=REPO,check=True)
    subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],cwd=REPO,check=True)
    subprocess.run(["git","add","--",*rel],cwd=REPO,check=True)
    staged=subprocess.check_output(["git","diff","--cached","--name-only"],cwd=REPO,text=True).splitlines()
    if not staged:return
    subprocess.run(["git","commit","-m","research: preserve TA20 v1.2 publication state [skip ci]"],cwd=REPO,check=True)
    for _ in range(3):
        p=subprocess.run(["git","push","origin","HEAD:"+BRANCH],cwd=REPO)
        if p.returncode==0:return
        subprocess.run(["git","fetch","origin",BRANCH,"--prune"],cwd=REPO,check=True)
        subprocess.run(["git","rebase","origin/"+BRANCH],cwd=REPO,check=True)
    raise RuntimeError("could not persist TA20 v1.2 state")

def client():
    old=REPO/"research/reading-trinity-accord/publish_zenodo.py"
    data=old.read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=CLIENT_BLOB: raise RuntimeError("established Zenodo client changed")
    spec=importlib.util.spec_from_file_location("ta20v12client",old)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    token=os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token: raise RuntimeError("publication credential unavailable")
    return module.Zenodo(token)

def read(z,path,authenticated=True):
    last=None
    for delay in (0,3,8,15):
        if delay: time.sleep(delay)
        try:return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:last=e
    raise last

def validate_record_id(rid):
    if type(rid) is not int or rid<=0 or rid in PROTECTED: raise RuntimeError("invalid/protected v1.2 record id")
    return rid

def previous_ok(dep):
    md=dep.get("metadata",{})
    if dep.get("id")!=PREVIOUS_RECORD or md.get("title")!=PREVIOUS_TITLE or str(md.get("version"))!="1.1" or not dep.get("submitted"):
        raise RuntimeError("published v1.1 predecessor identity mismatch")
    if [c.get("name") for c in md.get("creators",[])]!=["Liu, Hongju"]: raise RuntimeError("predecessor creator mismatch")
    concept=str(dep.get("conceptrecid",""))
    if concept!=EXPECTED_CONCEPT: raise RuntimeError("unexpected conceptrecid")
    return concept

def draft_id(url):
    p=urllib.parse.urlsplit(url or "")
    parts=[x for x in p.path.split("/") if x]
    if p.scheme!="https" or p.hostname!="zenodo.org" or p.query or p.fragment or len(parts)<3 or parts[-2]!="depositions" or not parts[-1].isdigit():
        raise RuntimeError("unexpected latest_draft URL")
    return int(parts[-1])

def descendant_ok(dep,concept):
    rid=validate_record_id(dep.get("id")); md=dep.get("metadata",{})
    if str(dep.get("conceptrecid"))!=concept: raise RuntimeError("not same concept lineage")
    if [c.get("name") for c in md.get("creators",[])]!=["Liu, Hongju"]: raise RuntimeError("descendant creator mismatch")
    if dep.get("submitted"):
        if md.get("title")!=TITLE or str(md.get("version"))!=VERSION: raise RuntimeError("submitted descendant identity mismatch")
    else:
        if md.get("title") not in {PREVIOUS_TITLE,TITLE} or str(md.get("version") or "1.1") not in {"1.1",VERSION}:
            raise RuntimeError("unexpected draft metadata")
    return rid

def zenodo_metadata():
    return {
      "upload_type":"publication","publication_type":"preprint","title":TITLE,
      "creators":[{"name":"Liu, Hongju","affiliation":"Independent researcher, Shenzhen, China"}],
      "description":"<p>TA-TR-2026-20 v1.2, a linked successor to UCT I v1.1. The revision reorganizes the foundations around one tokenwise Structural–Experiential Identity commitment, derives Universal Nonempty Experience and scoped structural continuity, formalizes No First Conscious Ancestor and fine-grained structural chains, and preserves explicit ontic/view/estimate and empirical-bridge firewalls. C1 remains a strong metaphysical commitment; the work is not peer reviewed and does not claim empirical proof, certified historical priority, a unique subject selector, or a unique consciousness metric.</p>",
      "publication_date":DATE,"version":VERSION,"access_right":"open","license":"cc-by-4.0","language":"eng",
      "keywords":["consciousness","process ontology","structural identity","panexperientialism","experiential structure","continuity","evolution","subject individuation","falsifiability"],
      "related_identifiers":[{"identifier":f"10.5281/zenodo.{PREVIOUS_RECORD}","relation":"isNewVersionOf","scheme":"doi"}]
    }

def inject_identity(text,doi):
    if text.count("__DOI_RESERVED_AT_RELEASE__")!=2: raise RuntimeError("DOI release markers missing/duplicated")
    out=text.replace("__DOI_RESERVED_AT_RELEASE__",doi)
    if "__DOI_RESERVED_AT_RELEASE__" in out: raise RuntimeError("DOI marker remained")
    return out

def version_changes():
    return """# UCT I v1.2 — Version Changes

**Report:** TA-TR-2026-20
**Previous version DOI:** 10.5281/zenodo.23030207
**Version:** 1.2

Version 1.2 preserves v1.0 and v1.1 as immutable historical editions and reorganizes the foundational dependency architecture.

Main changes:
1. Treats C1 Structural–Experiential Identity as the sole consciousness-specific core axiom.
2. Derives U1 Universal Nonempty Experience from C1 plus nonempty actual-token organization.
3. Derives U2 Structural Continuity in a common isomorphism-class structural space with a predeclared topology/pseudometric.
4. Moves persistence and token/type/lineage to process ontology as P3 and P6.
5. Recasts Selfhood Non-Prerequisite as U3.
6. Adds U0 Foundational Compression; E1 No First Conscious Ancestor; E2 Fine-Grained Structural Chains; and conditional E3 Connected Existence Constancy.
7. Re-centers the evolutionary account on nonempty experience throughout plus changing experiential organization.
8. Preserves the v1.1 finite-model, subject-selection, bridge, and failure-condition architecture under corrected dependencies.
9. Expands hostile-review/prior-art comparison with IIT, neurophenomenal structuralism, panexperientialism, Russellian monism, neutral-structuralism, and critiques of metaphysical structuralism.
10. Replaces the dependency ledger with a machine-audited DAG (78 nodes, 105 edges, zero directed cycles).

No claim is made that logical compression empirically proves C1.
"""

def review_sources(doi,conceptdoi):
    return f"""# Review and Sources Record — UCT I v1.2

**Report:** {REPORT}
**Version:** {VERSION}
**DOI:** {doi}
**Concept DOI:** {conceptdoi}
**Previous DOI:** 10.5281/zenodo.{PREVIOUS_RECORD}

## Review state
- Final formal/conceptual dependency map: 78 nodes, 105 directed edges, DAG PASS, zero directed cycles.
- No forbidden application/measurement backflow into C1/U1/U2.
- E1/E2/E3 dependencies explicitly separated.
- No-Ghost-History dependency ledger corrected: P6 is needed only for numerical-token distinctness, not the experiential-equivalence conclusion.
- PDF preflight and all-page render completed on the frozen RC6 baseline.
- Targeted hostile-review and prior-art audits completed.

## Theory boundaries
- C1 is a strong metaphysical identity commitment, not empirically proven.
- U1/U2/E1/E2 are internal consequences under declared premises.
- E3 is conditional mathematics independent of C1/U1/U2.
- Evolutionary continuity alone does not prove C1.
- A unique structural topology/metric and a universal positive subject selector are not supplied.
- Process-token abundance/nonunique carving remains an acknowledged cost.
- Quantum/relativistic completion remains open.

## Prior-art posture
No priority claim is made for panexperientialism, identity theory, phenomenal structuralism, process ontology, quotient/topological methods, Russellian monism, neutral-structuralism, or the general anti-emergence idea. The claimed contribution is the specific UCT dependency architecture and its explicit empirical firewalls.
"""

def build_package():
    ensure_source(); dep=load("deposit.json")
    rid=validate_record_id(dep.get("record_id")); doi=dep.get("doi"); concept=str(dep.get("conceptrecid",""))
    if doi!=f"10.5281/zenodo.{rid}" or concept!=EXPECTED_CONCEPT: raise RuntimeError("deposit identity inconsistent")
    pub=ROOT/"published"
    if pub.exists(): shutil.rmtree(pub)
    pub.mkdir()
    main=inject_identity((ROOT/"source-main.md").read_text(encoding="utf-8"),doi)
    mdfile=pub/f"{STEM}-v{VERSION}.md"; pdffile=pub/f"{STEM}-v{VERSION}.pdf"
    mdfile.write_text(main,encoding="utf-8")
    header=ROOT/"latex-header.tex"
    subprocess.run(["pandoc",str(mdfile),"-o",str(pdffile),"--pdf-engine","xelatex","--from=markdown+tex_math_single_backslash+raw_tex","-H",str(header),"-V","mainfont=DejaVu Serif","-V","monofont=DejaVu Sans Mono","-V","papersize=a4","-V","geometry:margin=25mm"],check=True)
    (pub/f"VERSION-CHANGES-v{VERSION}.md").write_text(version_changes(),encoding="utf-8")
    conceptdoi=f"10.5281/zenodo.{concept}"
    (pub/f"REVIEW-AND-SOURCES-v{VERSION}.md").write_text(review_sources(doi,conceptdoi),encoding="utf-8")
    for n in ("FORMAL-AUDIT-v1.2.md","formal-dependency-graph-v1.2.json","formal-dependency-graph-v1.2.dot"):
        shutil.copy2(ROOT/n,pub/n)
    (pub/"README-LICENSE.txt").write_text(f"""{REPORT} | Version {VERSION} | {DATE}
{TITLE}
Version DOI: {doi}
Concept DOI: {conceptdoi}
Previous v1.1 DOI: 10.5281/zenodo.{PREVIOUS_RECORD}

Author of record and responsible depositor: Hongju Liu.
Affiliation: Independent researcher, Shenzhen, China.
Substantial ChatGPT (OpenAI GPT-5.6 Sol) assistance was used for literature retrieval, formalization, adversarial review, dependency auditing, theorem checking, drafting, editing, and publication preparation under human direction. The human author is responsible for the theory commitments and decision to publish.

This is a theoretical preprint and has not been externally peer reviewed.
CC BY 4.0 applies to newly written material to the extent rights are held. Third-party works retain their own rights.
Version 1.2 is a linked revision of v1.1; prior public records and bytes must remain unchanged.
Publication/DOI/preservation establish version identity and availability, not truth, originality, significance, peer review, or indexing.
""",encoding="utf-8")
    bib=f"""@article{{Liu2026UCTI,
  author = {{Liu, Hongju}},
  title = {{{TITLE}}},
  year = {{2026}},
  version = {{{VERSION}}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}},
  note = {{Theoretical preprint; not peer reviewed; revised version of 10.5281/zenodo.{PREVIOUS_RECORD}}}
}}
"""
    ris=f"""TY  - JOUR
AU  - Liu, Hongju
TI  - {TITLE}
PY  - 2026
DA  - {DATE}
VL  - {VERSION}
DO  - {doi}
UR  - https://doi.org/{doi}
N1  - Theoretical preprint; revised version of 10.5281/zenodo.{PREVIOUS_RECORD}; not peer reviewed
ER  -
"""
    csl={"id":doi,"type":"article","title":TITLE,"author":[{"family":"Liu","given":"Hongju"}],"issued":{"date-parts":[[2026,10,4]]},"version":VERSION,"DOI":doi,"URL":"https://doi.org/"+doi,"note":f"Theoretical preprint; revised version of 10.5281/zenodo.{PREVIOUS_RECORD}; not peer reviewed"}
    (pub/"citation.bib").write_text(bib,encoding="utf-8")
    (pub/"citation.ris").write_text(ris,encoding="utf-8")
    (pub/"citation.csl.json").write_text(json.dumps(csl,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    others=sorted(PACKAGE_FILES-{"SHA256SUMS.txt","manifest.json"})
    (pub/"SHA256SUMS.txt").write_text("\n".join(f"{sha((pub/n).read_bytes())}  {n}" for n in others)+"\n",encoding="utf-8")
    manifest={"report_number":REPORT,"version":VERSION,"record_id":rid,"doi":doi,"conceptrecid":concept,"conceptdoi":conceptdoi,"previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","title":TITLE,"source_sha256":sha((ROOT/"source-main.md").read_bytes()),"files":[]}
    for n in sorted(PACKAGE_FILES-{"manifest.json"}):
        b=(pub/n).read_bytes(); manifest["files"].append({"name":n,"bytes":len(b),"sha256":sha(b)})
    (pub/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    files=[]
    for n in sorted(PACKAGE_FILES):
        b=(pub/n).read_bytes(); files.append({"name":n,"bytes":len(b),"sha256":sha(b)})
    expected={"report_number":REPORT,"version":VERSION,"record_id":rid,"doi":doi,"conceptrecid":concept,"conceptdoi":conceptdoi,"previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","title":TITLE,"file_count":len(files),"files":files,"prior_version_files_modified":False,"source_sha256":sha((ROOT/"source-main.md").read_bytes())}
    save("EXPECTED-PUBLICATION.json",expected)
    info=subprocess.check_output(["pdfinfo",str(pdffile)],text=True)
    pages=[x for x in info.splitlines() if x.startswith("Pages:")]
    if not pages or int(pages[0].split(":",1)[1].strip())<45: raise RuntimeError("unexpected PDF page count")
    txt=subprocess.check_output(["pdftotext",str(pdffile),"-"],text=True)
    required=("Structural–Experiential Identity","No First Conscious Ancestor","Fine-Grained Structural Chains","Connected Existence Constancy","Formal-DAG audit")
    if len(txt)<50000 or any(x not in txt for x in required): raise RuntimeError("PDF text/readback check failed")
    if "__DOI_RESERVED_AT_RELEASE__" in txt: raise RuntimeError("DOI marker remained in PDF")
    save("format-checks.json",{"state":"FORMAT_CHECKS_PASS","report_number":REPORT,"version":VERSION,"pdf_generated":True,"pdf_text_extractable":True,"page_count":int(pages[0].split(":",1)[1].strip()),"source_sha256":sha((ROOT/"source-main.md").read_bytes()),"doi_placeholder_absent":True,"required_sections_present":True})
    return expected

def validate_local_package():
    e=load("EXPECTED-PUBLICATION.json")
    if (e.get("report_number"),str(e.get("version")),e.get("previous_record_id"))!=(REPORT,VERSION,PREVIOUS_RECORD): raise RuntimeError("manifest identity mismatch")
    rid=validate_record_id(e.get("record_id"))
    if e.get("doi")!=f"10.5281/zenodo.{rid}": raise RuntimeError("manifest DOI mismatch")
    pub=ROOT/"published"; names={p.name for p in pub.iterdir() if p.is_file()}
    if names!=PACKAGE_FILES: raise RuntimeError("published inventory mismatch")
    rows={x["name"]:x for x in e.get("files",[])}
    if set(rows)!=PACKAGE_FILES: raise RuntimeError("expected rows mismatch")
    for n,row in rows.items():
        b=(pub/n).read_bytes()
        if len(b)!=row["bytes"] or sha(b)!=row["sha256"]: raise RuntimeError("package hash mismatch: "+n)
    if load("format-checks.json").get("state")!="FORMAT_CHECKS_PASS": raise RuntimeError("format checks missing")
    return e,sha((ROOT/"EXPECTED-PUBLICATION.json").read_bytes())

def public_download(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!="zenodo.org" or p.username or p.password: raise RuntimeError("unexpected public host")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"UCTI-v12-public-readback"}),timeout=120) as r:
        data=r.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES: raise RuntimeError("public asset too large")
    return data

def resolver_check(doi,rid):
    out={"matches_record":False}
    for delay in (0,3,8,15):
        if delay: time.sleep(delay)
        try:
            req=urllib.request.Request("https://doi.org/"+doi,headers={"User-Agent":"UCTI-v12-doi-check"})
            with urllib.request.urlopen(req,timeout=30) as r:
                p=urllib.parse.urlsplit(r.url); ok=r.status==200 and p.hostname=="zenodo.org" and p.path.rstrip("/") in (f"/records/{rid}",f"/record/{rid}")
                out={"matches_record":ok,"http_status":r.status,"final_url":r.url}
            if ok:return out
        except Exception as e: out={"matches_record":False,"error_type":type(e).__name__}
    return out
