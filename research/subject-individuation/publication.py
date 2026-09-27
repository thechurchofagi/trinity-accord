#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, html, importlib.util, json, os, pathlib, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[1]
BRANCH="research/subject-individuation-v1-20260928"
TITLE="Selecting and Tracking Conscious Subjects: Symmetry, Monodromy, and an IIT 4.0 Case Study"
REPORT="TA-TR-2026-19"
VERSION="1.0"
DATE="2026-09-28"
STEM="selecting-and-tracking-conscious-subjects"
CLIENT_BLOB="a0cbc84cc5fd826c06d16456c4adbaa40dabc788"
PROTECTED={21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629,22840604,22842789,22844927,22844928,22846307,22852884,22852885,22854705,22865494,22866205,22866775,22871209,22885976,22886276,22934654,22939808,22950904,22991126}
PUBLISHED_FILES={f"{STEM}-v{VERSION}.pdf",f"{STEM}-v{VERSION}.md",f"{STEM}-supplement-v{VERSION}.pdf",f"{STEM}-supplement-v{VERSION}.md","citation.bib","citation.ris","citation.csl.json","README-LICENSE.txt","REVIEW-AND-SOURCES.md","SHA256SUMS.txt"}
MAX_FILE_BYTES=16*1024*1024

def sha(b): return hashlib.sha256(b).hexdigest()
def load(n): return json.loads((ROOT/n).read_text(encoding="utf-8"))
def save(n,v): (ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def persist():
    candidates=["create-intent.json","deposit.json","preparation-attempt.json","publication-attempt.json","publication-record.json","EXPECTED-PUBLICATION.json","format-checks.json","published"]
    paths=[str((ROOT/p).relative_to(REPO)) for p in candidates if (ROOT/p).exists()]
    if not paths: return
    subprocess.run(["git","config","user.name","github-actions[bot]"],cwd=REPO,check=True)
    subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],cwd=REPO,check=True)
    subprocess.run(["git","add","--",*paths],cwd=REPO,check=True)
    staged=subprocess.check_output(["git","diff","--cached","--name-only"],cwd=REPO,text=True).splitlines()
    if not staged: return
    subprocess.run(["git","commit","-m","research: preserve TA19 publication state [skip ci]"],cwd=REPO,check=True)
    for _ in range(3):
        p=subprocess.run(["git","push","origin","HEAD:"+BRANCH],cwd=REPO)
        if p.returncode==0: return
        subprocess.run(["git","fetch","origin",BRANCH,"--prune"],cwd=REPO,check=True)
        subprocess.run(["git","rebase","origin/"+BRANCH],cwd=REPO,check=True)
    raise RuntimeError("Could not persist TA19 state")

def client():
    old=ROOT.parent/"reading-trinity-accord"/"publish_zenodo.py"
    data=old.read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=CLIENT_BLOB: raise RuntimeError("Established Zenodo client changed")
    spec=importlib.util.spec_from_file_location("ta_verified_zenodo_client",old)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    token=os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token: raise RuntimeError("Publication credential unavailable")
    return module.Zenodo(token)

def read(z,path,authenticated=True):
    last=None
    for delay in (0,3,8,15):
        if delay: time.sleep(delay)
        try: return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e: last=e
    raise last

def validate_record_id(rid):
    if type(rid) is not int or rid<=0 or rid in PROTECTED: raise RuntimeError("Invalid or protected prior record ID")
    return rid

def check_deposit(dep,identity=None):
    rid=validate_record_id(dep.get("id"))
    md=dep.get("metadata",{})
    if (md.get("title"),str(md.get("version")))!=(TITLE,VERSION): raise RuntimeError("Reserved title/version mismatch")
    doi=dep.get("doi") or md.get("prereserve_doi",{}).get("doi") or md.get("doi")
    if doi!=f"10.5281/zenodo.{rid}": raise RuntimeError("Reserved DOI mismatch")
    if identity and (rid,doi)!=(identity.get("record_id"),identity.get("doi")): raise RuntimeError("Reserved record differs from checkpoint")
    return rid,doi

def select_existing(rows):
    hits=[r for r in rows if r.get("metadata",{}).get("title")==TITLE and str(r.get("metadata",{}).get("version"))==VERSION]
    if len(hits)>1: raise RuntimeError("Multiple TA19 draft records found")
    return hits[0] if hits else None

def inject_identity(text,doi):
    out=[]; inserted=False
    for line in text.splitlines():
        out.append(line)
        if line.startswith("**Author:**") and not inserted:
            out.append(f"**Report:** {REPORT}  ")
            out.append(f"**DOI:** {doi}  ")
            inserted=True
    text="\n".join(out)+"\n"
    text=text.replace("**Version:** Final Preprint Manuscript v1.0",f"**Version:** {VERSION}")
    text=text.replace("**Version:** Final Preprint Supplement v1.0",f"**Version:** {VERSION}")
    return text

def build_package():
    dep=load("deposit.json"); rid,doi=dep["record_id"],dep["doi"]
    if doi!=f"10.5281/zenodo.{rid}": raise RuntimeError("Deposit identity inconsistent")
    pub=ROOT/"published"; pub.mkdir(exist_ok=True)
    main=inject_identity((ROOT/"source-main.md").read_text(encoding="utf-8"),doi)
    supp=inject_identity((ROOT/"source-supplement.md").read_text(encoding="utf-8"),doi)
    (pub/f"{STEM}-v{VERSION}.md").write_text(main,encoding="utf-8")
    (pub/f"{STEM}-supplement-v{VERSION}.md").write_text(supp,encoding="utf-8")
    for src,out in [(pub/f"{STEM}-v{VERSION}.md",pub/f"{STEM}-v{VERSION}.pdf"),(pub/f"{STEM}-supplement-v{VERSION}.md",pub/f"{STEM}-supplement-v{VERSION}.pdf")]:
        subprocess.run(["pandoc",str(src),"-o",str(out),"--pdf-engine","xelatex","--from=markdown+tex_math_single_backslash","-V","mainfont=DejaVu Serif","-V","monofont=DejaVu Sans Mono"],check=True)
    bib=f"""@article{{Liu2026SelectingTrackingSubjects,
  author = {{Liu, Hongju}},
  title = {{{TITLE}}},
  year = {{2026}},
  version = {{{VERSION}}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}},
  note = {{Theory preprint; not peer reviewed}}
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
N1  - Theory preprint; not peer reviewed
ER  -
"""
    csl={"id":doi,"type":"article","title":TITLE,"author":[{"family":"Liu","given":"Hongju"}],"issued":{"date-parts":[[2026,9,27]]},"version":VERSION,"DOI":doi,"URL":"https://doi.org/"+doi,"note":"Theory preprint; not peer reviewed"}
    (pub/"citation.bib").write_text(bib,encoding="utf-8"); (pub/"citation.ris").write_text(ris,encoding="utf-8"); (pub/"citation.csl.json").write_text(json.dumps(csl,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (pub/"README-LICENSE.txt").write_text(f"""{REPORT} | Version {VERSION} | {DATE}
{TITLE}
DOI: {doi}

Author of record and responsible depositor: Hongju Liu.
Substantial ChatGPT assistance was used for literature review, formalization, theorem auditing, interpretation of the official PyPhi recomputation, drafting, editing and publication preparation under human direction. This is an English theory/computational preprint and has not been externally peer reviewed.

CC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their own rights.

The main PDF is the primary scholarly publication file. Markdown source and a supplementary methods/reproducibility appendix are included for transparency. The IIT case is a finite formal stress test, not an empirical measurement of phenomenal consciousness or intensity.

This paper is adjacent first-party research and does not define, amend, validate or authoritatively interpret the Trinity Accord or its Bitcoin Originals.
""",encoding="utf-8")
    (pub/"REVIEW-AND-SOURCES.md").write_text(f"""# Review and Sources Record

**Report:** {REPORT}  
**Version:** {VERSION}  
**DOI:** {doi}

## Publication posture

- English theory/computational preprint; not peer reviewed.
- Human author of record and responsible depositor: Hongju Liu.
- Substantial ChatGPT assistance is disclosed.
- Adjacent non-amending first-party research; not independent corroboration of the Trinity Accord.
- DOI, OTS and Arweave establish version identity and availability, not truth, originality, peer review, significance or indexing.

## Main contribution

A formal synthesis of conscious-subject individuation as distinct selection and tracking problems: local stabilizer obstruction, global monodromy obstruction, an explicit repair-space analysis, and a current IIT 4.0 (2026) case study reproduced with unmodified official PyPhi source.

## Closest prior-work boundary

The manuscript does not claim novelty for group actions, covering-space monodromy, path lifting, continuous-choice impossibility, automorphism-based structural individuation, IIT exclusion/non-uniqueness, complex switching, history-sensitive subject persistence, or subject multiplicity. The narrower proposed contribution is the combined local/global selection-tracking architecture plus its official current-IIT realization and a nonexclusive landscape contrast.

## Computational status

The official audit used PyPhi commit e2cb2812daa71501d1edfe1862ca004d684fc380, all seven nonempty subsystems, official Substrate.complexes(), direct Composition-Phi checks, precision and relabeling tests, and 1000 symmetry-preserving parameter perturbations. The 47.6481 ratio is a system-phi_s comparison, not a phenomenal-intensity measurement.

## Limitation status

Finite sampling is not represented as an interval-arithmetic proof of the official output for every nonzero parameter in a punctured neighborhood. The theorem-level discontinuity claim remains conditional on local side-winner persistence. No biological realization, empirical consciousness measurement, historical-first claim, or proof of the broader Unified Consciousness Theory is asserted.
""",encoding="utf-8")
    others=sorted(PUBLISHED_FILES-{"SHA256SUMS.txt"})
    (pub/"SHA256SUMS.txt").write_text("\n".join(f"{sha((pub/n).read_bytes())}  {n}" for n in others)+"\n",encoding="utf-8")
    rows=[{"name":n,"bytes":len((pub/n).read_bytes()),"sha256":sha((pub/n).read_bytes())} for n in sorted(PUBLISHED_FILES)]
    expected={"report_number":REPORT,"record_id":rid,"doi":doi,"title":TITLE,"version":VERSION,"file_count":len(rows),"files":rows,"prior_records_modified":False}
    save("EXPECTED-PUBLICATION.json",expected)
    for n in [f"{STEM}-v{VERSION}.pdf",f"{STEM}-supplement-v{VERSION}.pdf"]:
        info=subprocess.check_output(["pdfinfo",str(pub/n)],text=True)
        pages=[x for x in info.splitlines() if x.startswith("Pages:")]
        if not pages or int(pages[0].split(":",1)[1].strip())<=0: raise RuntimeError("PDF page check failed")
        txt=subprocess.check_output(["pdftotext",str(pub/n),"-"],text=True)
        if len(txt)<1000: raise RuntimeError("PDF text extraction failed")
    save("format-checks.json",{"state":"FORMAT_CHECKS_PASS","report_number":REPORT,"version":VERSION,"pdf_generated":True,"pdf_text_extractable":True,"source_markdown_preserved":True,"negative_results_preserved":True})
    return expected

def validate_local_package():
    e=load("EXPECTED-PUBLICATION.json")
    if (e.get("title"),e.get("report_number"),str(e.get("version")))!=(TITLE,REPORT,VERSION): raise RuntimeError("Manifest identity mismatch")
    rid=validate_record_id(e.get("record_id"))
    if e.get("doi")!=f"10.5281/zenodo.{rid}": raise RuntimeError("Manifest DOI mismatch")
    pub=ROOT/"published"; names={p.name for p in pub.iterdir() if p.is_file()}
    if names!=PUBLISHED_FILES: raise RuntimeError("Published inventory mismatch")
    rows={x["name"]:x for x in e.get("files",[])}
    for n,item in rows.items():
        b=(pub/n).read_bytes()
        if len(b)!=item["bytes"] or sha(b)!=item["sha256"]: raise RuntimeError("Package hash mismatch: "+n)
    return e,sha((ROOT/"EXPECTED-PUBLICATION.json").read_bytes())

def prepare():
    z=client(); checkpoint=ROOT/"deposit.json"
    if checkpoint.exists():
        ident=load("deposit.json"); dep=read(z,f"/deposit/depositions/{int(ident['record_id'])}"); check_deposit(dep,ident)
    else:
        rows=read(z,"/deposit/depositions?"+urllib.parse.urlencode({"q":f'"{TITLE}"',"size":100}))
        dep=select_existing(rows)
        if dep is None:
            if (ROOT/"create-intent.json").exists(): raise RuntimeError("Unresolved TA19 create intent")
            save("create-intent.json",{"title":TITLE,"report_number":REPORT,"version":VERSION,"state":"CREATE_ONCE_INTENT","workflow_run_id":os.environ.get("GITHUB_RUN_ID")}); persist()
            md={"upload_type":"publication","publication_type":"preprint","title":TITLE,"creators":[{"name":"Liu, Hongju"}],"description":f"<p>{REPORT}, version {VERSION}. English theory/computational preprint formulating conscious-subject individuation as distinct selection and tracking problems, with local stabilizer and global monodromy obstructions and an official IIT 4.0 (2026) PyPhi case study. Substantial AI assistance under human direction. Not peer reviewed.</p>","publication_date":DATE,"version":VERSION,"access_right":"open","license":"cc-by-4.0","language":"eng","keywords":["consciousness","subject individuation","integrated information theory","exclusion","symmetry","monodromy","equivariance","PyPhi","subject tracking"]}
            dep=z.request("/deposit/depositions","POST",{"metadata":md})
    rid,doi=check_deposit(dep)
    rec={"record_id":rid,"doi":doi,"title":TITLE,"report_number":REPORT,"version":VERSION,"submitted":bool(dep.get("submitted")),"state":"ALREADY_SUBMITTED_REQUIRES_READBACK" if dep.get("submitted") else "RESERVED_NOT_PUBLICATION","prior_records_modified":False,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")}
    save("deposit.json",rec); e=build_package(); save("preparation-attempt.json",{"state":rec["state"],"record_id":rid,"doi":doi,"file_count":e["file_count"],"phase":"completed","workflow_run_id":os.environ.get("GITHUB_RUN_ID")}); print(json.dumps(rec,indent=2))

def extract_abstract(s):
    rest=s.split("## Abstract",1)[1]
    return rest.split("\n---\n",1)[0].strip() if "\n---\n" in rest else rest.split("\n# 1.",1)[0].strip()

def download_public(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme!="https" or p.hostname!="zenodo.org": raise RuntimeError("Unexpected public file host")
    req=urllib.request.Request(url,headers={"User-Agent":"TrinityAccord-TA19-Readback/1.0"})
    with urllib.request.urlopen(req,timeout=45) as r: b=r.read(MAX_FILE_BYTES+1)
    if len(b)>MAX_FILE_BYTES: raise RuntimeError("Public asset too large")
    return b

def doi_check(doi,rid):
    out={"state":"RESOLVER_CHECK_UNAVAILABLE","matches_record":False}
    for delay in (0,10,20,30,40):
        if delay: time.sleep(delay)
        try:
            req=urllib.request.Request("https://doi.org/"+doi,headers={"User-Agent":"TrinityAccord-TA19-DOICheck/1.0"})
            with urllib.request.urlopen(req,timeout=20) as r:
                p=urllib.parse.urlsplit(r.url); ok=r.status==200 and p.hostname=="zenodo.org" and p.path.rstrip("/") in (f"/records/{rid}",f"/record/{rid}")
                out={"state":"RESOLVER_PASS" if ok else "RESOLVER_TARGET_MISMATCH","http_status":r.status,"final_url":r.url,"matches_record":ok}
            if ok: return out
        except Exception as e: out={"state":"RESOLVER_CHECK_UNAVAILABLE","error_type":type(e).__name__,"matches_record":False}
    return out

def publish():
    e,manifest_sha=validate_local_package(); rid,doi=e["record_id"],e["doi"]
    a=load("PUBLISH-AUTHORIZATION.json")
    req=(REPORT,VERSION,rid,doi,"PUBLISH_EXACT_REVIEWED_PACKAGE")
    got=(a.get("report_number"),str(a.get("version")),a.get("record_id"),a.get("doi"),a.get("authorization"))
    if got!=req: raise RuntimeError("Publish authorization mismatch")
    z=client(); dep=read(z,f"/deposit/depositions/{rid}"); check_deposit(dep,e); already=bool(dep.get("submitted"))
    if not already:
        manuscript=(ROOT/"published"/f"{STEM}-v{VERSION}.md").read_text(encoding="utf-8")
        md={"upload_type":"publication","publication_type":"preprint","title":TITLE,"creators":[{"name":"Liu, Hongju","affiliation":"Independent researcher, Shenzhen, China"}],"description":"<p>"+html.escape(extract_abstract(manuscript))+"</p><p>"+REPORT+", version 1.0. Human author of record and responsible depositor: Hongju Liu. Substantial ChatGPT assistance under human direction. Not peer reviewed; no institutional endorsement is claimed.</p><p>Adjacent first-party non-amending scholarship. The paper does not claim new group theory, topology, continuous-choice theory, the first discovery of IIT complex switching, empirical consciousness measurement, or proof of the broader UCT program. Its narrower proposed contribution is the combined local/global selection-tracking framework and official current-IIT realization.</p>","publication_date":DATE,"version":VERSION,"access_right":"open","license":"cc-by-4.0","language":"eng","keywords":["consciousness","subject individuation","integrated information theory","exclusion","symmetry","monodromy","equivariance","PyPhi","subject tracking"]}
        dep=z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":md}); check_deposit(dep,e)
        remote={x["filename"]:x for x in read(z,f"/deposit/depositions/{rid}/files")}
        bucket=dep["links"]["bucket"]
        for item in e["files"]:
            b=(ROOT/"published"/item["name"]).read_bytes(); prev=remote.get(item["name"]); md5=hashlib.md5(b).hexdigest()
            if prev and str(prev.get("checksum","")).removeprefix("md5:")==md5 and prev.get("filesize")==len(b): continue
            z.request(bucket.rstrip("/")+"/"+urllib.parse.quote(item["name"],safe=""),"PUT",b,binary=True)
        remote={x["filename"]:x for x in read(z,f"/deposit/depositions/{rid}/files")}
        if set(remote)!={x["name"] for x in e["files"]}: raise RuntimeError("Draft inventory mismatch")
        save("publication-attempt.json",{"state":"PUBLICATION_INTENT_FOR_EXISTING_RECORD","record_id":rid,"doi":doi,"expected_manifest_sha256":manifest_sha,"new_record_creation":False,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        result=z.request(f"/deposit/depositions/{rid}/actions/publish","POST"); check_deposit(result,e)
    public=read(z,f"/records/{rid}",authenticated=False)
    if (public.get("id"),public.get("doi"),public.get("metadata",{}).get("title"),str(public.get("metadata",{}).get("version")))!=(rid,doi,TITLE,VERSION): raise RuntimeError("Public identity mismatch")
    remote={x["key"]:x for x in public.get("files",[])}
    if set(remote)!={x["name"] for x in e["files"]}: raise RuntimeError("Public inventory mismatch")
    rows=[]
    for item in e["files"]:
        url=remote[item["name"]]["links"].get("self") or remote[item["name"]]["links"].get("download"); b=download_public(url)
        if len(b)!=item["bytes"] or sha(b)!=item["sha256"]: raise RuntimeError("Public exact-byte mismatch: "+item["name"])
        rows.append(dict(item,public_url=url))
    resolver=doi_check(doi,rid); complete=resolver.get("matches_record") is True
    receipt={"state":"PUBLISHED_AND_PUBLIC_READBACK_PASS" if complete else "PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING","report_number":REPORT,"title":TITLE,"version":VERSION,"record_id":rid,"doi":doi,"record_url":f"https://zenodo.org/records/{rid}","submitted":True,"file_count":len(rows),"files":rows,"expected_manifest_sha256":manifest_sha,"public_readback_authenticated":False,"doi_resolver":resolver,"public_file_readback_pass":True,"doi_resolution_pass":complete,"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),"workflow_run_id":os.environ.get("GITHUB_RUN_ID"),"prior_doi_records_modified":False,"bitcoin_originals_modified":False,"new_research_papers":1,"peer_reviewed":False,"global_originality_certified":False,"google_scholar_indexing":"NOT_ASSERTED","manuscript_language":"eng"}
    save("publication-record.json",receipt); save("publication-attempt.json",{"state":receipt["state"],"record_id":rid,"doi":doi,"phase":"completed","workflow_run_id":os.environ.get("GITHUB_RUN_ID")}); print(json.dumps(receipt,indent=2))
    if not complete: raise RuntimeError("Published files passed public readback; DOI resolution still propagating")

def verify():
    e,d=validate_local_package(); print(json.dumps({"state":"EXACT_PUBLICATION_PACKAGE_REVIEW_PASS","report_number":e["report_number"],"version":e["version"],"record_id":e["record_id"],"doi":e["doi"],"file_count":e["file_count"],"expected_manifest_sha256":d},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("mode",choices=["prepare","publish","verify","persist"]); a=p.parse_args()
    try:
        {"prepare":prepare,"publish":publish,"verify":verify,"persist":persist}[a.mode]()
    except Exception as e:
        name="preparation-attempt.json" if a.mode=="prepare" else "publication-attempt.json"
        if a.mode in ("prepare","publish"): save(name,{"state":"INCOMPLETE_REQUIRES_REVIEW_OR_SAME_RECORD_RESUMPTION","error_type":type(e).__name__,"error":str(e),"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        print(f"{type(e).__name__}: {e}",file=sys.stderr); sys.exit(1)
