#!/usr/bin/env python3
from __future__ import annotations
import hashlib, html, json, os, pathlib, subprocess, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = "research/uct-paper-a-v1-2-20261004"
PRIOR_ID = 23030207
EXPECTED_CONCEPT = "23005587"
REPORT = "TA-TR-2026-20"
VERSION = "1.2"
TITLE = "Unified Consciousness Theory I: Structural–Experiential Identity and the Continuity from Physical Process to Conceptual Self"
MAIN_MD = "unified-consciousness-theory-i-v1.2.md"
MAIN_PDF = "unified-consciousness-theory-i-v1.2.pdf"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def write_json(path: pathlib.Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))

def require(cond, msg):
    if not cond:
        raise RuntimeError(msg)

def persist(message="research: checkpoint UCT I v1.2 release [skip ci]"):
    subprocess.run(["git","config","user.name","trinity-research-release-bot"],cwd=REPO,check=True)
    subprocess.run(["git","config","user.email","actions@github.com"],cwd=REPO,check=True)
    rel = str(ROOT.relative_to(REPO))
    subprocess.run(["git","add","--",rel],cwd=REPO,check=True)
    batch=REPO/"research/paper-timestamps/2026-10-04-uct-i-v12"
    if batch.exists():
        subprocess.run(["git","add","--",str(batch.relative_to(REPO))],cwd=REPO,check=True)
    if subprocess.run(["git","diff","--cached","--quiet"],cwd=REPO).returncode == 0:
        return
    subprocess.run(["git","commit","-m",message],cwd=REPO,check=True)
    for _ in range(4):
        if subprocess.run(["git","push","origin","HEAD:"+BRANCH],cwd=REPO).returncode == 0:
            return
        subprocess.run(["git","fetch","origin",BRANCH,"--prune"],cwd=REPO,check=True)
        subprocess.run(["git","rebase","origin/"+BRANCH],cwd=REPO,check=True)
    raise RuntimeError("Unable to persist release checkpoint")

class Zenodo:
    def __init__(self):
        token=os.environ.get("ZENODO_ACCESS_TOKEN")
        if not token:
            raise RuntimeError("ZENODO_ACCESS_TOKEN unavailable")
        self.token=token
    def request(self, url_or_path, method="GET", payload=None, binary=False, authenticated=True):
        url=url_or_path if url_or_path.startswith("https://") else "https://zenodo.org/api"+url_or_path
        u=urllib.parse.urlsplit(url)
        require(u.scheme=="https" and u.hostname=="zenodo.org" and not u.username and not u.password, "Unexpected Zenodo URL")
        headers={"User-Agent":"UCT-I-v1.2-Release/1.0"}
        if authenticated:
            headers["Authorization"]="Bearer "+self.token
        data=None
        if payload is not None:
            if binary:
                data=payload
                headers["Content-Type"]="application/octet-stream"
            else:
                data=json.dumps(payload).encode()
                headers["Content-Type"]="application/json"
        req=urllib.request.Request(url,data=data,method=method,headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=180) as resp:
                raw=resp.read()
                if not raw:
                    return {}
                return json.loads(raw.decode())
        except urllib.error.HTTPError as e:
            body=e.read().decode(errors="replace")
            raise RuntimeError(f"Zenodo {method} {u.path} -> {e.code}: {body[:1200]}")
    def download_public(self, url):
        u=urllib.parse.urlsplit(url)
        require(u.scheme=="https" and u.hostname=="zenodo.org","Unexpected public file URL")
        req=urllib.request.Request(url,headers={"User-Agent":"UCT-I-v1.2-Public-Readback/1.0"})
        with urllib.request.urlopen(req,timeout=180) as resp:
            return resp.read()

def file_fingerprint(record):
    out=[]
    for f in record.get("files",[]):
        name=f.get("key",f.get("filename"))
        checksum=f.get("checksum","").removeprefix("md5:")
        size=int(f.get("size",f.get("filesize",-1)))
        out.append((name,checksum,size))
    return sorted(out)

def draft_link(dep):
    link=dep.get("links",{}).get("latest_draft")
    if not link:
        return None
    u=urllib.parse.urlsplit(link)
    require(u.scheme=="https" and u.hostname=="zenodo.org" and u.path.startswith("/api/deposit/depositions/"),"Unexpected latest_draft URL")
    if u.path.rstrip("/").split("/")[-1] == str(dep.get("id")):
        return None
    return link

def delete_draft_file(z, rid, item):
    fid=item.get("id")
    require(fid is not None,"Draft file ID missing")
    endpoint=f"/deposit/depositions/{rid}/files/{urllib.parse.quote(str(fid),safe='')}"
    try:
        z.request(endpoint,"DELETE")
    except Exception:
        rows=z.request(f"/deposit/depositions/{rid}/files")
        if any(str(f.get("id"))==str(fid) for f in rows):
            raise

def build_release(doi: str):
    release=ROOT/"release"
    release.mkdir(parents=True,exist_ok=True)
    template=(ROOT/"source-template.md").read_text(encoding="utf-8")
    require("__DOI_RESERVED_AT_RELEASE__" in template,"DOI placeholder missing")
    text=template.replace("__DOI_RESERVED_AT_RELEASE__",doi)
    require("__DOI_RESERVED_AT_RELEASE__" not in text,"Unresolved DOI placeholder")
    (release/MAIN_MD).write_text(text,encoding="utf-8")

    for src,dst in [
        ("RELEASE-NOTES.md","RELEASE-NOTES.md"),
        ("UCT-II-v1.1-COMPATIBILITY.md","UCT-II-v1.1-COMPATIBILITY.md"),
        ("FORMAL-DEPENDENCY-AUDIT.md","FORMAL-DEPENDENCY-AUDIT.md"),
        ("dependency-graph.json","dependency-graph.json"),
        ("dependency-graph.dot","dependency-graph.dot"),
    ]:
        (release/dst).write_bytes((ROOT/src).read_bytes())

    cmd=["pandoc","-f","markdown+tex_math_single_backslash+raw_tex",str(release/MAIN_MD),
         "-s","-H",str(ROOT/"header.tex"),"-V","geometry:margin=1in","-V","fontsize=11pt",
         "--pdf-engine=xelatex","-o",str(release/MAIN_PDF)]
    subprocess.run(cmd,cwd=REPO,check=True)

    (release/"README-LICENSE.txt").write_text(
        "Unified Consciousness Theory I v1.2\n"
        f"DOI: {doi}\n"
        "Author: Hongju Liu\n"
        "License: CC BY 4.0 unless a deposited file states otherwise.\n"
        "Publication, DOI registration, timestamping and archival preservation establish version identity and availability; "
        "they do not establish truth, originality, peer review, significance or indexing.\n", encoding="utf-8")

    (release/"citation.bib").write_text(f"""@misc{{liu2026ucti_v12,
  author = {{Liu, Hongju}},
  title = {{{TITLE}}},
  year = {{2026}},
  month = {{10}},
  version = {{1.2}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}},
  note = {{TA-TR-2026-20; theoretical preprint; not peer reviewed}}
}}
""",encoding="utf-8")
    write_json(release/"citation.csl.json",{
      "id":doi,"type":"article","title":TITLE,"author":[{"family":"Liu","given":"Hongju"}],
      "issued":{"date-parts":[[2026,10,4]]},"version":"1.2","DOI":doi,
      "URL":"https://doi.org/"+doi,"publisher":"Zenodo"
    })
    (release/"citation.ris").write_text(f"""TY  - RPRT
TI  - {TITLE}
AU  - Liu, Hongju
PY  - 2026
DA  - 2026/10/04
ET  - 1.2
DO  - {doi}
UR  - https://doi.org/{doi}
N1  - TA-TR-2026-20; theoretical preprint; not peer reviewed
ER  -
""",encoding="utf-8")

    rows=[]
    for p in sorted(release.iterdir()):
        if p.is_file() and p.name!="SHA256SUMS.txt":
            b=p.read_bytes()
            rows.append((p.name,len(b),sha256(b)))
    (release/"SHA256SUMS.txt").write_text("".join(f"{h}  {name}\n" for name,_,h in rows),encoding="utf-8")
    rows2=[]
    for p in sorted(release.iterdir()):
        if p.is_file():
            b=p.read_bytes()
            rows2.append({"name":p.name,"bytes":len(b),"sha256":sha256(b)})
    expected={
      "schema":"trinityaccord.uct-v12-publication.v1",
      "report_number":REPORT,"version":VERSION,"title":TITLE,
      "doi":doi,"files":rows2,
      "main_pdf":MAIN_PDF,"main_markdown":MAIN_MD,
      "boundary":"Exact v1.2 release package; prior v1.0 and v1.1 published files must remain unchanged. Publication does not imply peer review or empirical validation of C1."
    }
    write_json(ROOT/"EXPECTED-PUBLICATION.json",expected)
    return expected

def prepare():
    z=Zenodo()
    prior=z.request(f"/records/{PRIOR_ID}",authenticated=False)
    require(int(prior.get("id"))==PRIOR_ID,"Prior public record identity mismatch")
    require(prior.get("doi")==f"10.5281/zenodo.{PRIOR_ID}","Prior DOI mismatch")
    require(str(prior.get("conceptrecid"))==EXPECTED_CONCEPT,"Prior concept family mismatch")
    prior_path=ROOT/"prior-public-v1.1.json"
    if not prior_path.exists():
        write_json(prior_path,prior)
        persist()

    dep_path=ROOT/"deposit.json"
    if dep_path.exists():
        ident=load_json(dep_path)
        rid=int(ident["record_id"])
        draft=z.request(f"/deposit/depositions/{rid}")
        require(not draft.get("submitted"),"Stored successor already published; use publish/readback path")
    else:
        old=z.request(f"/deposit/depositions/{PRIOR_ID}")
        require(old.get("submitted") is True,"Prior deposition is not published")
        require(str(old.get("metadata",{}).get("version"))=="1.1","Prior deposition version mismatch")
        link=draft_link(old)
        if link:
            raise RuntimeError("An unpublished successor draft already exists without this release checkpoint; inspect before adoption")
        latest=prior.get("links",{}).get("latest")
        if latest:
            u=urllib.parse.urlsplit(latest)
            latestid=u.path.rstrip("/").split("/")[-1]
            require(not (latestid.isdigit() and int(latestid)!=PRIOR_ID),"A newer published version already exists")
        intent=ROOT/"newversion-intent.json"
        require(not intent.exists(),"Unresolved previous newversion intent")
        write_json(intent,{
          "state":"NEWVERSION_ONCE_INTENT","prior_record_id":PRIOR_ID,"version":VERSION,
          "authorization":"User explicitly requested publication of UCT I v1.2 on 2026-10-04.",
          "workflow_run_id":os.environ.get("GITHUB_RUN_ID")
        })
        persist()
        response=z.request(f"/deposit/depositions/{PRIOR_ID}/actions/newversion","POST")
        link=draft_link(response)
        require(link is not None,"newversion did not return a successor draft")
        draft=z.request(link)
        rid=int(draft["id"])
    require(rid!=PRIOR_ID and not draft.get("submitted"),"Invalid successor draft")
    require(str(draft.get("conceptrecid"))==EXPECTED_CONCEPT,"Successor concept family mismatch")

    metadata={
      "upload_type":"publication","publication_type":"preprint","title":TITLE,
      "creators":[{"name":"Liu, Hongju","affiliation":"Independent researcher, Shenzhen, China"}],
      "description":"<p>Version 1.2 of Unified Consciousness Theory I. This revision reorganizes the foundations around one tokenwise Structural–Experiential Identity axiom, derives Universal Nonempty Experience and structural continuity under declared comparison geometry, and formalizes the No First Conscious Ancestor, fine-grained-chain and connected-existence results.</p><p>Theoretical preprint; not peer reviewed. C1 remains a strong metaphysical commitment and is not empirically established. Human author of record and responsible depositor: Hongju Liu. Substantial ChatGPT assistance is disclosed. This research is adjacent and non-amending with respect to the Trinity Accord.</p>",
      "publication_date":"2026-10-04","version":"1.2","access_right":"open","license":"cc-by-4.0","language":"eng",
      "keywords":["consciousness","process ontology","structural identity","axiom minimization","evolution","experiential structure","theory unification"],
      "related_identifiers":[{"identifier":f"10.5281/zenodo.{PRIOR_ID}","relation":"isNewVersionOf","scheme":"doi"}],
      "prereserve_doi":True
    }
    draft=z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":metadata})
    doi=draft.get("metadata",{}).get("prereserve_doi",{}).get("doi") or draft.get("doi")
    require(doi==f"10.5281/zenodo.{rid}","Reserved successor DOI mismatch")
    write_json(ROOT/"deposit.json",{
      "state":"RESERVED_NOT_PUBLISHED","record_id":rid,"doi":doi,"conceptrecid":str(draft.get("conceptrecid")),
      "prior_record_id":PRIOR_ID,"prior_doi":f"10.5281/zenodo.{PRIOR_ID}","version":VERSION,
      "report_number":REPORT,"title":TITLE,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")
    })
    persist()

    expected=build_release(doi)

    rows=z.request(f"/deposit/depositions/{rid}/files")
    inherited_names={f.get("filename",f.get("key")) for f in rows}
    prior_names={f.get("key",f.get("filename")) for f in prior.get("files",[])}
    unknown=inherited_names-prior_names
    require(not unknown,f"Unrecognized files in successor draft: {sorted(unknown)}")
    for item in rows:
        delete_draft_file(z,rid,item)

    draft=z.request(f"/deposit/depositions/{rid}")
    bucket=draft.get("links",{}).get("bucket")
    require(bucket,"Draft bucket missing")
    u=urllib.parse.urlsplit(bucket)
    require(u.scheme=="https" and u.hostname=="zenodo.org" and u.path.startswith("/api/files/"),"Unexpected bucket URL")
    release=ROOT/"release"
    for item in expected["files"]:
        name=item["name"]
        z.request(bucket+"/"+urllib.parse.quote(name,safe=""),"PUT",(release/name).read_bytes(),binary=True)

    listing=z.request(f"/deposit/depositions/{rid}/files")
    require({f.get("filename",f.get("key")) for f in listing}=={x["name"] for x in expected["files"]},"Draft file set mismatch")
    for item in listing:
        name=item.get("filename",item.get("key"))
        local=(release/name).read_bytes()
        require(item.get("checksum","").removeprefix("md5:")==hashlib.md5(local).hexdigest(),f"Draft checksum mismatch: {name}")

    prior_now=z.request(f"/records/{PRIOR_ID}",authenticated=False)
    require(file_fingerprint(prior_now)==file_fingerprint(prior),"Prior v1.1 public file fingerprints changed")
    manifest_bytes=(ROOT/"EXPECTED-PUBLICATION.json").read_bytes()
    write_json(ROOT/"preparation.json",{
      "state":"PREPARED_EXACT_DRAFT_NOT_PUBLISHED","record_id":rid,"doi":doi,
      "expected_manifest_sha256":sha256(manifest_bytes),"file_count":len(expected["files"]),
      "main_pdf_sha256":next(x["sha256"] for x in expected["files"] if x["name"]==MAIN_PDF),
      "prior_v1_1_files_unchanged":True,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")
    })
    persist("research: prepare exact UCT I v1.2 DOI-bound package [skip ci]")
    print(json.dumps(load_json(ROOT/"preparation.json"),indent=2))

def public_readback(z, expected, rid, doi):
    public=None
    for i in range(12):
        try:
            public=z.request(f"/records/{rid}",authenticated=False)
            break
        except Exception:
            if i==11: raise
            time.sleep(5)
    require(public and public.get("doi")==doi,"Public DOI identity mismatch")
    require(str(public.get("metadata",{}).get("version"))=="1.2","Public version mismatch")
    require(public.get("metadata",{}).get("title")==TITLE,"Public title mismatch")
    expected_map={x["name"]:x for x in expected["files"]}
    require({f["key"] for f in public.get("files",[])}==set(expected_map),"Public file set mismatch")
    readback=[]
    for f in public["files"]:
        name=f["key"]; data=z.download_public(f["links"]["self"]); e=expected_map[name]
        require(len(data)==e["bytes"] and sha256(data)==e["sha256"],f"Public byte mismatch: {name}")
        readback.append({**e,"public_url":f["links"]["self"],"matches_local":True})
    return public,readback

def publish():
    z=Zenodo()
    dep=load_json(ROOT/"deposit.json")
    expected=load_json(ROOT/"EXPECTED-PUBLICATION.json")
    auth=load_json(ROOT/"PUBLISH-AUTHORIZATION.json")
    manifest_hash=sha256((ROOT/"EXPECTED-PUBLICATION.json").read_bytes())
    require(auth.get("authorized") is True,"Publication authorization missing")
    require(auth.get("expected_manifest_sha256")==manifest_hash,"Authorization manifest mismatch")
    pdf_hash=next(x["sha256"] for x in expected["files"] if x["name"]==MAIN_PDF)
    require(auth.get("reviewed_pdf_sha256")==pdf_hash,"Authorization PDF hash mismatch")
    rid=int(dep["record_id"]);doi=dep["doi"]
    draft=z.request(f"/deposit/depositions/{rid}")
    if draft.get("submitted"):
        public,readback=public_readback(z,expected,rid,doi)
    else:
        require(str(draft.get("metadata",{}).get("version"))=="1.2","Draft version mismatch")
        rows=z.request(f"/deposit/depositions/{rid}/files")
        require({f.get("filename",f.get("key")) for f in rows}=={x["name"] for x in expected["files"]},"Draft file set changed")
        intent=ROOT/"publish-intent.json"
        if intent.exists():
            raise RuntimeError("Prior publish intent exists but draft still unpublished; stop rather than blind retry")
        write_json(intent,{
          "state":"PUBLISH_ONCE_INTENT","record_id":rid,"doi":doi,"version":VERSION,
          "expected_manifest_sha256":manifest_hash,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")
        })
        persist()
        response=z.request(f"/deposit/depositions/{rid}/actions/publish","POST")
        require(response.get("submitted") is True,"Zenodo did not report publication")
        public,readback=public_readback(z,expected,rid,doi)

    prior_saved=load_json(ROOT/"prior-public-v1.1.json")
    prior_now=z.request(f"/records/{PRIOR_ID}",authenticated=False)
    require(file_fingerprint(prior_now)==file_fingerprint(prior_saved),"Prior v1.1 file fingerprints changed")
    receipt={
      "state":"PUBLISHED_AND_PUBLIC_READBACK_PASS","report_number":REPORT,"record_id":rid,"doi":doi,
      "title":TITLE,"version":VERSION,"conceptrecid":str(public.get("conceptrecid")),
      "record_url":f"https://zenodo.org/records/{rid}","submitted":True,
      "public_file_readback_pass":True,"file_count":len(readback),"files":readback,
      "prior_record_id":PRIOR_ID,"prior_doi":f"10.5281/zenodo.{PRIOR_ID}",
      "prior_v1_1_files_unchanged":True,"publication_source_commit":os.environ.get("GITHUB_SHA"),
      "workflow_run_id":os.environ.get("GITHUB_RUN_ID"),"peer_reviewed":False,
      "empirical_validation_of_C1":False
    }
    write_json(ROOT/"publication.json",receipt)

    pdf_entry=next(x for x in readback if x["name"]==MAIN_PDF)
    batch=REPO/"research/paper-timestamps/2026-10-04-uct-i-v12"
    batch.mkdir(parents=True,exist_ok=True)
    write_json(batch/"targets.json",{
      "schema":"trinityaccord.paper-ots-targets.v1","batch":"2026-10-04-uct-i-v12","paper_count":1,
      "papers":[{
        "report":REPORT,"record_id":rid,"doi":doi,"version":VERSION,"title":TITLE,
        "receipt_path":str((ROOT/"publication.json").relative_to(REPO)),
        "pdfs":[{"name":MAIN_PDF,"bytes":pdf_entry["bytes"],"sha256":pdf_entry["sha256"],"role":"Complete English theoretical preprint"}]
      }],
      "boundary":"Non-amending exact-PDF preservation; timestamp/archive identity is not peer review, truth, originality or authorship proof."
    })
    persist("research: publish UCT I v1.2 and preserve public readback [skip ci]")
    print(json.dumps(receipt,indent=2))

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("action",choices=["prepare","publish"])
    args=ap.parse_args()
    try:
        prepare() if args.action=="prepare" else publish()
    finally:
        try: persist()
        except Exception: pass
