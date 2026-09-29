from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, shutil, subprocess, time, urllib.error, urllib.parse, urllib.request

ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[3]
BRANCH="research/uct-paper-a-v1-1-20260929"
PREVIOUS_TITLE="Unified Consciousness Theory I: From Experience Existence to Experiential Structure"
TITLE="Unified Consciousness Theory I: Ontic Structure, Physical Views, and the Structural Continuity from Physical Process to Conceptual Self"
REPORT="TA-TR-2026-20"
VERSION="1.1"
DATE="2026-09-29"
PREVIOUS_RECORD=23005588
STEM="unified-consciousness-theory-i"
SOURCE_GIT_BLOB_SHA1="74e94ca89489a63742fd2c0a2a6b7b1f2f7edeed"
CLIENT_BLOB="a0cbc84cc5fd826c06d16456c4adbaa40dabc788"
PROTECTED={21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629,22840604,22842789,22844927,22844928,22846307,22852884,22852885,22854705,22865494,22866205,22866775,22871209,22885976,22886276,22934654,22939808,22950904,23002980,23005588,23008262}
STATE_FILES={"create-intent.json","deposit.json","preparation-attempt.json","publication-attempt.json","publication-record.json","EXPECTED-PUBLICATION.json","format-checks.json"}
PACKAGE_FILES={
    f"{STEM}-v{VERSION}.md",
    f"{STEM}-v{VERSION}.pdf",
    "VERSION-CHANGES-v1.1.md",
    "REVIEW-AND-SOURCES-v1.1.md",
    "README-LICENSE.txt",
    "citation.bib",
    "citation.ris",
    "citation.csl.json",
    "SHA256SUMS.txt",
    "manifest.json",
}
MAX_FILE_BYTES=20*1024*1024

def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def load(name):return json.loads((ROOT/name).read_text(encoding="utf-8"))
def save(name,value):
    if name not in STATE_FILES: raise RuntimeError("unexpected state file")
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def ensure_source():
    out=ROOT/"source-main.md"
    if not out.exists(): raise RuntimeError("frozen source missing")
    actual_blob=subprocess.check_output(["git","hash-object",str(out)],cwd=REPO,text=True).strip()
    if actual_blob!=SOURCE_GIT_BLOB_SHA1: raise RuntimeError("frozen source git-blob mismatch")
    return out

def persist(paths=None):
    candidates=set(paths or STATE_FILES)
    candidates.update({"source-main.md","published"})
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
    subprocess.run(["git","commit","-m","research: preserve TA20 v1.1 publication state [skip ci]"],cwd=REPO,check=True)
    for _ in range(3):
        p=subprocess.run(["git","push","origin","HEAD:"+BRANCH],cwd=REPO)
        if p.returncode==0:return
        subprocess.run(["git","fetch","origin",BRANCH,"--prune"],cwd=REPO,check=True)
        subprocess.run(["git","rebase","origin/"+BRANCH],cwd=REPO,check=True)
    raise RuntimeError("could not persist TA20 v1.1 state")

def client():
    old=REPO/"research/reading-trinity-accord/publish_zenodo.py"
    data=old.read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=CLIENT_BLOB: raise RuntimeError("established Zenodo client changed")
    spec=importlib.util.spec_from_file_location("ta20v11client",old)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    token=os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:raise RuntimeError("publication credential unavailable")
    return module.Zenodo(token)

def read(z,path,authenticated=True):
    last=None
    for delay in (0,3,8,15):
        if delay:time.sleep(delay)
        try:return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:last=e
    raise last

def validate_record_id(rid):
    if type(rid) is not int or rid<=0 or rid in PROTECTED:raise RuntimeError("invalid/protected v1.1 record id")
    return rid

def previous_ok(dep):
    md=dep.get("metadata",{})
    if dep.get("id")!=PREVIOUS_RECORD or md.get("title")!=PREVIOUS_TITLE or str(md.get("version"))!="1.0" or not dep.get("submitted"):
        raise RuntimeError("published predecessor identity mismatch")
    if [c.get("name") for c in md.get("creators",[])]!=["Liu, Hongju"]:raise RuntimeError("predecessor creator mismatch")
    concept=str(dep.get("conceptrecid",""))
    if not concept.isdigit():raise RuntimeError("conceptrecid unavailable")
    return concept

def draft_id(url):
    p=urllib.parse.urlsplit(url or "")
    parts=[x for x in p.path.split("/") if x]
    if p.scheme!="https" or p.hostname!="zenodo.org" or p.query or p.fragment or len(parts)<3 or parts[-2]!="depositions" or not parts[-1].isdigit():
        raise RuntimeError("unexpected latest_draft URL")
    return int(parts[-1])

def descendant_ok(dep,concept):
    rid=validate_record_id(dep.get("id"))
    md=dep.get("metadata",{})
    if str(dep.get("conceptrecid"))!=concept:raise RuntimeError("not same concept lineage")
    if [c.get("name") for c in md.get("creators",[])]!=["Liu, Hongju"]:raise RuntimeError("descendant creator mismatch")
    if dep.get("submitted"):
        if md.get("title")!=TITLE or str(md.get("version"))!=VERSION:raise RuntimeError("submitted descendant identity mismatch")
    else:
        if md.get("title") not in {PREVIOUS_TITLE,TITLE} or str(md.get("version") or "1.0") not in {"1.0",VERSION}:
            raise RuntimeError("unexpected draft metadata")
    return rid

def zenodo_metadata():
    return {
      "upload_type":"publication",
      "publication_type":"preprint",
      "title":TITLE,
      "creators":[{"name":"Liu, Hongju","affiliation":"Independent researcher, Shenzhen, China"}],
      "description":"<p>TA-TR-2026-20 v1.1, a strengthened successor version of Unified Consciousness Theory I. This revision distinguishes token-relative ontic organization from scientific views and estimates, makes the A5-OI injective structural-identity commitment explicit, repairs theorem dependencies, adds a scoped subject non-selection theorem, develops a structural-evolutionary synthesis from elementary physical processes to conceptual selfhood, and introduces failure-prone operational bridge methodology. A1 and A5-OI remain foundational/metaphysical commitments; the evolutionary examples do not prove them. Not peer reviewed.</p>",
      "publication_date":DATE,
      "version":VERSION,
      "access_right":"open",
      "license":"cc-by-4.0",
      "language":"eng",
      "keywords":["consciousness","panexperientialism","process ontology","causal structure","phenomenal structure","multiscale processes","subject individuation","evolution","self-model","falsifiability"]
    }

def inject_identity(text,doi):
    old="**v1.1 DOI:** to be assigned only at release"
    if old not in text:raise RuntimeError("v1.1 DOI release marker missing")
    text=text.replace(old,f"**v1.1 DOI:** {doi}")
    text=text.replace("**Version:** 1.1-rc3","**Version:** 1.1")
    text=text.replace("**Status:** Internal release-candidate manuscript after claim, prior-art, and reference-layout audit; not peer reviewed; not yet released as v1.1","**Status:** Foundational theory preprint; not peer reviewed.")
    text=text.replace("v1.1-rc3","v1.1")
    if "rc3" in text:raise RuntimeError("release-candidate marker remained in DOI-bound main source")
    return text

def version_changes():
    return """# UCT I v1.1 — Version Changes

**Report:** TA-TR-2026-20
**Previous version:** v1.0, DOI 10.5281/zenodo.23005588
**Version:** v1.1

Version 1.1 preserves v1.0 as an immutable historical edition and explicitly strengthens/clarifies the theory.

Main changes:
1. Adds A5-OI, an ontic-token injective structural-identity commitment, stronger than the explicitly one-way A5b formula in v1.0.
2. Separates actual token, full ontic organization, scientific view, scientific estimate, and subject.
3. Makes token-relative completeness explicit and removes analyst-selected grain from the ontology.
4. Repairs theorem dependencies: non-summative combination, strict enrichment, latent-memory divergence, and related converse claims are explicitly A5-OI-dependent.
5. Adds Probe Invariance, No Future Contamination, and Causally Screened History.
6. Adds a scoped symmetric-overlap non-selection theorem for canonical subject extraction.
7. Adds a structural-evolutionary synthesis from elementary physical process to conceptual selfhood, explicitly not as a proof of A1/A5.
8. Introduces Bridge Sufficiency Hypotheses, Operational Structural Correspondence, the Physical Token/View Selection Protocol, and No Post-Hoc Token/View Rescue.
9. Demotes FPRF, binary macrofield membership, H-V* as a basal valence ontology, and RREP as a universal generator.
10. Expands explicit open obligations: macroprocess implementation, approximate metrics, subject individuation, valence, semantic representation, relativity, quantum formulation, and direct empirical isolation of full A5-OI.

No claim is made that v1.0 already contained all v1.1 theorems.
"""

def review_sources(doi,conceptdoi):
    return f"""# Review and Sources Record — UCT I v1.1

**Report:** {REPORT}
**Version:** {VERSION}
**DOI:** {doi}
**Concept DOI:** {conceptdoi}
**Previous DOI:** 10.5281/zenodo.{PREVIOUS_RECORD}

## Review state
- Full formal dependency map constructed and machine-audited.
- Final freeze-candidate graph: 114 nodes, 197 directed edges, DAG PASS, zero directed cycles.
- A5 strength ambiguity repaired by explicit versioned A5-OI commitment.
- Claim-by-claim audit completed.
- Targeted prior-art audit completed.
- 27-page rc3 preview visually reviewed with no clipping, overlap, black squares, or broken glyphs.
- Reference-layout audit completed.

## Theory boundaries
- A1 and A5-OI are strong foundational/metaphysical commitments, not empirically proven results.
- Finite experiments test explicit operational bridge packages rather than isolated full ontic A5-OI.
- Evolutionary and comparative biological evidence is explanatory/application material and does not prove A1/A5.
- Positive universal subject individuation remains open.
- The exact physical grounding of human unpleasantness remains open.
- The hard problem is not claimed deductively solved.
- Historical global priority is not certified.

## Prior-art posture
No novelty is claimed for panexperientialism, identity theory in general, phenomenal/causal structuralism, process metaphysics, overlapping-conscious-system concerns, combination/decombination problems, or theory-unification methodology. The contribution claimed is the specific process-token structural-identity conjunction and dependency architecture developed in the main paper.
"""

def build_package():
    ensure_source()
    dep=load("deposit.json")
    rid=validate_record_id(dep.get("record_id"));doi=dep.get("doi");concept=str(dep.get("conceptrecid",""))
    if doi!=f"10.5281/zenodo.{rid}" or not concept.isdigit():raise RuntimeError("deposit identity inconsistent")
    pub=ROOT/"published"
    if pub.exists():shutil.rmtree(pub)
    pub.mkdir()
    main=inject_identity((ROOT/"source-main.md").read_text(encoding="utf-8"),doi)
    mdfile=pub/f"{STEM}-v{VERSION}.md";pdffile=pub/f"{STEM}-v{VERSION}.pdf"
    mdfile.write_text(main,encoding="utf-8")
    subprocess.run(["pandoc",str(mdfile),"-o",str(pdffile),"--pdf-engine","xelatex","--from=markdown+tex_math_single_backslash","-V","mainfont=DejaVu Serif","-V","monofont=DejaVu Sans Mono","-V","papersize=a4","-V","geometry:margin=25mm"],check=True)
    (pub/"VERSION-CHANGES-v1.1.md").write_text(version_changes(),encoding="utf-8")
    conceptdoi=f"10.5281/zenodo.{concept}"
    (pub/"REVIEW-AND-SOURCES-v1.1.md").write_text(review_sources(doi,conceptdoi),encoding="utf-8")
    (pub/"README-LICENSE.txt").write_text(f"""{REPORT} | Version {VERSION} | {DATE}
{TITLE}
Version DOI: {doi}
Concept DOI: {conceptdoi}
Previous v1.0 DOI: 10.5281/zenodo.{PREVIOUS_RECORD}

Author of record and responsible depositor: Hongju Liu.
Affiliation: Independent researcher, Shenzhen, China.
Substantial ChatGPT (OpenAI GPT-5.6 Sol) assistance was used for literature retrieval, formalization, adversarial review, theorem checking, drafting, editing, and publication preparation under human direction. The human author of record is responsible for the theory commitments and decision to publish.

This is a foundational theory preprint and has not been externally peer reviewed.
CC BY 4.0 applies to newly written material to the extent rights are held. Third-party works retain their own rights.

Version 1.1 is a linked revision of v1.0. The v1.0 Zenodo record and bytes must remain unchanged.
Publication, DOI, OTS, and Arweave preservation establish version identity and availability, not truth, originality, significance, peer review, or indexing.
This paper is adjacent first-party research and does not define, amend, validate, or authoritatively interpret the Trinity Accord or its Bitcoin Originals.
""",encoding="utf-8")
    bib=f"""@article{{Liu2026UCTI,
  author = {{Liu, Hongju}},
  title = {{{TITLE}}},
  year = {{2026}},
  version = {{{VERSION}}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}},
  note = {{Foundational theory preprint; not peer reviewed; revised version of 10.5281/zenodo.{PREVIOUS_RECORD}}}
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
N1  - Foundational theory preprint; revised version of 10.5281/zenodo.{PREVIOUS_RECORD}; not peer reviewed
ER  -
"""
    csl={"id":doi,"type":"article","title":TITLE,"author":[{"family":"Liu","given":"Hongju"}],"issued":{"date-parts":[[2026,9,29]]},"version":VERSION,"DOI":doi,"URL":"https://doi.org/"+doi,"note":f"Foundational theory preprint; revised version of 10.5281/zenodo.{PREVIOUS_RECORD}; not peer reviewed"}
    (pub/"citation.bib").write_text(bib,encoding="utf-8")
    (pub/"citation.ris").write_text(ris,encoding="utf-8")
    (pub/"citation.csl.json").write_text(json.dumps(csl,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    others=sorted(PACKAGE_FILES-{"SHA256SUMS.txt","manifest.json"})
    sums="\n".join(f"{sha((pub/n).read_bytes())}  {n}" for n in others)+"\n"
    (pub/"SHA256SUMS.txt").write_text(sums,encoding="utf-8")
    manifest={"report_number":REPORT,"version":VERSION,"record_id":rid,"doi":doi,"conceptrecid":concept,"conceptdoi":conceptdoi,"previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","title":TITLE,"source_sha256":sha((ROOT/"source-main.md").read_bytes()),"files":[]}
    for n in sorted(PACKAGE_FILES-{"manifest.json"}):
        b=(pub/n).read_bytes();manifest["files"].append({"name":n,"bytes":len(b),"sha256":sha(b)})
    (pub/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    files=[]
    for n in sorted(PACKAGE_FILES):
        b=(pub/n).read_bytes();files.append({"name":n,"bytes":len(b),"sha256":sha(b)})
    expected={"report_number":REPORT,"version":VERSION,"record_id":rid,"doi":doi,"conceptrecid":concept,"conceptdoi":conceptdoi,"previous_record_id":PREVIOUS_RECORD,"previous_doi":f"10.5281/zenodo.{PREVIOUS_RECORD}","title":TITLE,"file_count":len(files),"files":files,"prior_version_files_modified":False,"source_sha256":sha((ROOT/"source-main.md").read_bytes())}
    save("EXPECTED-PUBLICATION.json",expected)
    info=subprocess.check_output(["pdfinfo",str(pdffile)],text=True)
    pages=[x for x in info.splitlines() if x.startswith("Pages:")]
    if not pages or int(pages[0].split(":",1)[1].strip())<20:raise RuntimeError("unexpected PDF page count")
    txt=subprocess.check_output(["pdftotext",str(pdffile),"-"],text=True)
    if len(txt)<20000 or "A5-OI" not in txt or "No Post-Hoc Token/View Rescue" not in txt:raise RuntimeError("PDF text/readback check failed")
    if "__DOI_RESERVED_AT_RELEASE__" in txt or "to be assigned only at release" in txt:raise RuntimeError("DOI marker remained in PDF")
    save("format-checks.json",{"state":"FORMAT_CHECKS_PASS","report_number":REPORT,"version":VERSION,"pdf_generated":True,"pdf_text_extractable":True,"page_count":int(pages[0].split(":",1)[1].strip()),"source_sha256":sha((ROOT/"source-main.md").read_bytes()),"a5_oi_present":True,"no_post_hoc_rescue_present":True,"doi_placeholder_absent":True})
    return expected

def validate_local_package():
    e=load("EXPECTED-PUBLICATION.json")
    if (e.get("report_number"),str(e.get("version")),e.get("previous_record_id"))!=(REPORT,VERSION,PREVIOUS_RECORD):raise RuntimeError("manifest identity mismatch")
    rid=validate_record_id(e.get("record_id"))
    if e.get("doi")!=f"10.5281/zenodo.{rid}":raise RuntimeError("manifest DOI mismatch")
    pub=ROOT/"published";names={p.name for p in pub.iterdir() if p.is_file()}
    if names!=PACKAGE_FILES:raise RuntimeError("published inventory mismatch")
    rows={x["name"]:x for x in e.get("files",[])}
    if set(rows)!=PACKAGE_FILES:raise RuntimeError("expected rows mismatch")
    for n,row in rows.items():
        b=(pub/n).read_bytes()
        if len(b)!=row["bytes"] or sha(b)!=row["sha256"]:raise RuntimeError("package hash mismatch: "+n)
    gates=load("format-checks.json")
    if gates.get("state")!="FORMAT_CHECKS_PASS":raise RuntimeError("format checks missing")
    return e,sha((ROOT/"EXPECTED-PUBLICATION.json").read_bytes())

def public_download(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!="zenodo.org" or p.username or p.password:raise RuntimeError("unexpected public host")
    req=urllib.request.Request(url,headers={"User-Agent":"UCTI-v11-public-readback"})
    with urllib.request.urlopen(req,timeout=120) as r:data=r.read(MAX_FILE_BYTES+1)
    if len(data)>MAX_FILE_BYTES:raise RuntimeError("public asset too large")
    return data

def resolver_check(doi,rid):
    out={"matches_record":False}
    for delay in (0,3,8,15):
        if delay:time.sleep(delay)
        try:
            req=urllib.request.Request("https://doi.org/"+doi,headers={"User-Agent":"UCTI-v11-doi-check"})
            with urllib.request.urlopen(req,timeout=30) as r:
                p=urllib.parse.urlsplit(r.url)
                ok=r.status==200 and p.hostname=="zenodo.org" and p.path.rstrip("/") in (f"/records/{rid}",f"/record/{rid}")
                out={"matches_record":ok,"http_status":r.status,"final_url":r.url}
            if ok:return out
        except Exception as e:out={"matches_record":False,"error_type":type(e).__name__}
    return out
