#!/usr/bin/env python3
"""TA23 create-once reservation and exact-package Zenodo publication.

The credential is read only in GitHub Actions. POST operations are never retried.
Uncertain POST outcomes require remote readback or explicit human reconciliation.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = "research/uct-paper-c-v1-20261004"
TITLE = "Unified Consciousness Theory III: Organization, Intelligence, and Experience—From Inorganic Processes to Artificial Agents"
REPORT, VERSION, DATE = "TA-TR-2026-23", "1.0", "2026-10-04"
STEM = "unified-consciousness-theory-iii"
CLIENT_BLOB = "a0cbc84cc5fd826c06d16456c4adbaa40dabc788"
PROTECTED = {21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629,22840604,22842789,22844927,22844928,22846307,22852884,22852885,22854705,22865494,22866205,22866775,22871209,22885976,22886276,22934654,22939808,22950904,23002980,23005588,23131575,23030320}
PDF_NAME = f"{STEM}-v{VERSION}.pdf"
MD_NAME = f"{STEM}-v{VERSION}.md"
FILES = {PDF_NAME, MD_NAME, "reproducibility-v1.0.zip", "README-LICENSE.txt", "REVIEW-AND-SOURCES.md", "citation.bib", "citation.ris", "citation.csl.json", "SHA256SUMS.txt"}
INPUTS = ("source-main.md", "build_uct_c_pdf.py", "reproducibility-v1.0.zip", "REVIEW-AND-SOURCES.md", "publication.py")
MAX_BYTES = 32 * 1024 * 1024
PLACEHOLDER = "__DOI_RESERVED_AT_RELEASE__"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def save(name, data):
    target = ROOT / name
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)

def input_hashes():
    return {name: sha((ROOT / name).read_bytes()) for name in INPUTS}

def validate_id(rid):
    if type(rid) is not int or rid <= 0 or rid in PROTECTED:
        raise RuntimeError("Invalid or protected prior record ID")
    return rid

def check_url(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or p.hostname != "zenodo.org" or p.username or p.password or p.port not in (None,443) or p.fragment:
        raise RuntimeError("Unexpected Zenodo transport target")
    return url

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Zenodo redirect rejected; credential not forwarded")

def client():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Credential-bearing operations require GitHub Actions")
    old = ROOT.parent / "reading-trinity-accord" / "publish_zenodo.py"
    data = old.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != CLIENT_BLOB:
        raise RuntimeError("Established Zenodo client changed")
    spec = importlib.util.spec_from_file_location("ta_verified_zenodo_client", old)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class StrictZenodo(module.Zenodo):
        def request(self, path, method="GET", data=None, authenticated=True, binary=False):
            url = check_url(path if path.startswith("https://") else "https://zenodo.org/api" + path)
            headers = {"User-Agent": "TrinityAccord-TA23/1.0"}
            if authenticated:
                headers["Authorization"] = "Bearer " + self.token
            if data is not None:
                headers["Content-Type"] = "application/octet-stream" if binary else "application/json"
                if not binary:
                    data = json.dumps(data).encode()
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            # No retries here, especially no ambiguous POST replays.
            with urllib.request.build_opener(NoRedirect()).open(request, timeout=120) as response:
                raw = response.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise RuntimeError("Zenodo response exceeded size limit")
                return json.loads(raw)
    token = os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Publication credential unavailable")
    return StrictZenodo(token)

def read(z, path, authenticated=True):
    for attempt in range(4):
        try:
            return z.request(path, authenticated=authenticated)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))

def persist():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Checkpoint pushes require GitHub Actions")
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=REPO, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError("Refusing checkpoint outside designated branch")
    if subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=REPO, text=True).strip():
        raise RuntimeError("Pre-existing staged files; refuse mixed checkpoint")
    names = ("create-intent.json", "create-response.json", "deposit.json", "preparation-attempt.json", "publication-intent.json", "publication-attempt.json", "publication-record.json", "EXPECTED-PUBLICATION.json", "format-checks.json", "published")
    paths = [str((ROOT / n).relative_to(REPO)) for n in names if (ROOT / n).exists()]
    if not paths:
        return
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], cwd=REPO, check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], cwd=REPO, check=True)
    subprocess.run(["git", "add", "--", *paths], cwd=REPO, check=True)
    if not subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=REPO, text=True).strip():
        return
    subprocess.run(["git", "commit", "-m", "research: preserve TA23 publication state [skip ci]"], cwd=REPO, check=True)
    # Never automatically rebase/replay a workflow containing a remote POST.
    subprocess.run(["git", "push", "origin", "HEAD:" + BRANCH], cwd=REPO, check=True)

def metadata(intent):
    source=(ROOT/"source-main.md").read_text(encoding="utf-8")
    abstract=source.split("## Abstract",1)[1].split("**Keywords:",1)[0].strip()
    return {"upload_type":"publication", "publication_type":"preprint", "title":TITLE,
        "creators":[{"name":"Liu, Hongju", "affiliation":"Independent researcher, Shenzhen, China"}],
        "description":"<p>"+html.escape(abstract)+"</p><p>Theoretical preprint. Conditional formal results and finite computational checks are distinguished from empirical evidence. Substantial ChatGPT assistance under the author's direction is disclosed. Not peer reviewed. No new human, animal, or pretrained language-model experiment is reported, and C1 is not claimed to be empirically validated.</p>",
        "publication_date":DATE, "version":VERSION, "access_right":"open", "license":"cc-by-4.0", "language":"eng",
        "keywords":["consciousness", "evolution", "intelligence", "self-report", "process ontology", "artificial agents", "structural identity"],
        "notes":f"{REPORT}; version {VERSION}; new independent record. TA23 release identity: {intent['reservation_token']}. DOI and preservation attest identity and availability, not truth or peer review.",
        "related_identifiers":[{"identifier":"10.5281/zenodo.23131575","relation":"references","scheme":"doi"},{"identifier":"10.5281/zenodo.23030320","relation":"references","scheme":"doi"}]}

def check_deposit(dep, identity=None):
    rid = validate_id(dep.get("id"))
    md = dep.get("metadata", {})
    doi = dep.get("doi") or md.get("prereserve_doi", {}).get("doi") or md.get("doi")
    if md.get("title") != TITLE or str(md.get("version")) != VERSION or doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Deposit title/version/DOI mismatch")
    if not any(c.get("name") == "Liu, Hongju" for c in md.get("creators", [])):
        raise RuntimeError("Deposit creator mismatch")
    if identity and (rid, doi) != (identity.get("record_id"), identity.get("doi")):
        raise RuntimeError("Deposit identity differs from checkpoint")
    intent = load("create-intent.json")
    if f"TA23 release identity: {intent['reservation_token']}" not in md.get("notes", ""):
        raise RuntimeError("Deposit does not carry this create-once identity")
    return rid, doi

def build_package():
    ident = load("deposit.json")
    rid = validate_id(ident["record_id"])
    doi = ident["doi"]
    if doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Local DOI identity mismatch")
    if (ROOT / "EXPECTED-PUBLICATION.json").exists():
        return validate_local_package()[0]
    if (ROOT / "published").exists() or (ROOT / "PUBLISH-AUTHORIZATION.json").exists():
        raise RuntimeError("Unmanifested or authorized package cannot be rebuilt automatically")
    source = (ROOT / "source-main.md").read_text(encoding="utf-8")
    if PLACEHOLDER not in source:
        raise RuntimeError("Frozen source DOI placeholder missing")
    with tempfile.TemporaryDirectory(prefix="ta23-build-", dir=ROOT) as tmp:
        pub = Path(tmp)
        (pub / MD_NAME).write_text(source.replace(PLACEHOLDER, doi), encoding="utf-8")
        subprocess.run([sys.executable, str(ROOT / "build_uct_c_pdf.py"), str(pub / MD_NAME)], cwd=ROOT, check=True)
        for name in ("reproducibility-v1.0.zip", "REVIEW-AND-SOURCES.md"):
            shutil.copyfile(ROOT / name, pub / name)
        note = "Theoretical preprint; not peer reviewed"
        (pub / "citation.bib").write_text(f"@article{{Liu2026UCTIII,\n  author = {{Liu, Hongju}},\n  title = {{{TITLE}}},\n  year = {{2026}},\n  version = {{{VERSION}}},\n  doi = {{{doi}}},\n  url = {{https://doi.org/{doi}}},\n  note = {{{note}}}\n}}\n", encoding="utf-8")
        (pub / "citation.ris").write_text(f"TY  - JOUR\nAU  - Liu, Hongju\nTI  - {TITLE}\nPY  - 2026\nDA  - {DATE}\nVL  - {VERSION}\nDO  - {doi}\nUR  - https://doi.org/{doi}\nN1  - {note}\nER  -\n", encoding="utf-8")
        csl = {"id":doi,"type":"article","title":TITLE,"author":[{"family":"Liu","given":"Hongju"}],"issued":{"date-parts":[[2026,10,4]]},"version":VERSION,"DOI":doi,"URL":"https://doi.org/"+doi,"note":note}
        (pub / "citation.csl.json").write_text(json.dumps(csl,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (pub / "README-LICENSE.txt").write_text(f"{REPORT} | Version {VERSION} | {DATE}\n{TITLE}\nDOI: {doi}\n\nAuthor: Hongju Liu. Independent researcher, Shenzhen, China.\n\nTheoretical preprint; not peer reviewed. Substantial ChatGPT assistance was used under the author's direction for research, formalization, review, writing, and computational checks. No independent external or final human line-by-line review is implied. No new human, animal, or pretrained language-model experiment is reported. C1 is not claimed to be empirically validated.\n\nLicense: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/ . This applies to newly authored material to the extent rights are held. Cited and included third-party works retain their own rights. See the reproducibility archive's rights and provenance notes.\n\nThe English PDF is the primary manuscript. Markdown, citation files, source review, reproducibility material, and SHA256SUMS are provided. DOI, OTS, and Arweave concern version identity and preservation; they do not establish truth, significance, indexing, or peer review. This paper does not amend the Trinity Accord or its earlier publications.\n", encoding="utf-8")
        # The builder may emit auxiliary files; only the declared nine assets enter the package.
        for p in pub.iterdir():
            if p.name not in FILES:
                if p.is_file(): p.unlink()
                else: raise RuntimeError("Unexpected builder directory")
        (pub / "SHA256SUMS.txt").write_text("".join(f"{sha((pub/n).read_bytes())}  {n}\n" for n in sorted(FILES-{"SHA256SUMS.txt"})),encoding="utf-8")
        rows = [{"name":n,"bytes":(pub/n).stat().st_size,"sha256":sha((pub/n).read_bytes())} for n in sorted(FILES)]
        if any(r["bytes"] <= 0 or r["bytes"] > MAX_BYTES for r in rows):
            raise RuntimeError("Invalid package file size")
        pdftext = subprocess.check_output(["pdftotext",str(pub/PDF_NAME),"-"],text=True)
        if len(pdftext)<1000 or doi not in pdftext:
            raise RuntimeError("PDF text/DOI format check failed")
        shutil.copytree(pub, ROOT / "published")
    expected = {"report_number":REPORT,"record_id":rid,"doi":doi,"title":TITLE,"version":VERSION,"file_count":len(rows),"files":rows,"source_inputs":input_hashes(),"source_commit":os.environ.get("GITHUB_SHA"),"prior_records_modified":False}
    save("EXPECTED-PUBLICATION.json", expected)
    save("format-checks.json", {"state":"FORMAT_CHECKS_PASS","pdf_sha256":next(r["sha256"] for r in rows if r["name"]==PDF_NAME),"visual_review_required":True})
    return expected

def validate_local_package():
    e = load("EXPECTED-PUBLICATION.json")
    rid = validate_id(e.get("record_id"))
    if (e.get("report_number"),e.get("title"),str(e.get("version")),e.get("doi")) != (REPORT,TITLE,VERSION,f"10.5281/zenodo.{rid}"):
        raise RuntimeError("Manifest identity mismatch")
    ident = load("deposit.json")
    if (rid,e["doi"]) != (ident.get("record_id"),ident.get("doi")):
        raise RuntimeError("Manifest differs from record checkpoint")
    if e.get("source_inputs") != input_hashes():
        raise RuntimeError("Frozen source/builder/archive/review/publisher changed")
    items = e.get("files", [])
    if len(items)!=len(FILES) or e.get("file_count")!=len(FILES) or {x.get("name") for x in items}!=FILES:
        raise RuntimeError("Manifest exact file inventory mismatch")
    pub = ROOT / "published"
    if {p.name for p in pub.iterdir()} != FILES or any(p.is_symlink() or not p.is_file() for p in pub.iterdir()):
        raise RuntimeError("Local exact file inventory mismatch")
    for item in items:
        data = (pub/item["name"]).read_bytes()
        if not 0<len(data)<=MAX_BYTES or len(data)!=item["bytes"] or sha(data)!=item["sha256"]:
            raise RuntimeError("Package byte mismatch: "+item["name"])
    sums = "".join(f"{sha((pub/n).read_bytes())}  {n}\n" for n in sorted(FILES-{"SHA256SUMS.txt"}))
    if (pub/"SHA256SUMS.txt").read_text()!=sums:
        raise RuntimeError("SHA256SUMS contents mismatch")
    if (pub/MD_NAME).read_text(encoding="utf-8") != (ROOT/"source-main.md").read_text(encoding="utf-8").replace(PLACEHOLDER,e["doi"]):
        raise RuntimeError("Manuscript changed beyond reserved DOI substitution")
    return e, sha((ROOT/"EXPECTED-PUBLICATION.json").read_bytes())

def validate_authorization(e, manifest_sha):
    pdf = next(x for x in e["files"] if x["name"]==PDF_NAME)
    review = load("visual-review.json")
    if (review.get("state"),review.get("expected_manifest_sha256"),review.get("pdf_sha256")) != ("VISUAL_REVIEW_PASS",manifest_sha,pdf["sha256"]):
        raise RuntimeError("Exact PDF visual-review gate failed")
    a = load("PUBLISH-AUTHORIZATION.json")
    if (a.get("authorization"),a.get("report_number"),str(a.get("version")),a.get("record_id"),a.get("doi"),a.get("expected_manifest_sha256"),a.get("pdf_sha256")) != ("PUBLISH_EXACT_REVIEWED_PACKAGE",REPORT,VERSION,e["record_id"],e["doi"],manifest_sha,pdf["sha256"]):
        raise RuntimeError("Exact reviewed publication authorization mismatch")

def prepare():
    z = client()
    current_inputs = input_hashes()
    if (ROOT/"create-intent.json").exists():
        intent = load("create-intent.json")
        if intent.get("source_inputs") != current_inputs:
            raise RuntimeError("Reservation source inputs changed; manual reconciliation required")
    else:
        intent = None
    if (ROOT/"deposit.json").exists():
        dep = read(z,f"/deposit/depositions/{validate_id(load('deposit.json')['record_id'])}")
        check_deposit(dep,load("deposit.json"))
    else:
        rows = read(z,"/deposit/depositions?"+urllib.parse.urlencode({"q":f'"{TITLE}"',"size":100}))
        if not isinstance(rows,list) or len(rows)>=100:
            raise RuntimeError("Incomplete draft search; no creation allowed")
        hits = [r for r in rows if r.get("metadata",{}).get("title")==TITLE and str(r.get("metadata",{}).get("version"))==VERSION]
        if len(hits)>1:
            raise RuntimeError("Multiple title/version records; no creation allowed")
        if hits:
            if intent is None:
                raise RuntimeError("Existing record without local create-once identity; review required")
            dep = hits[0]
        else:
            if intent is not None:
                raise RuntimeError("Unresolved create intent; POST will not be repeated")
            intent={"state":"CREATE_ONCE_INTENT","report_number":REPORT,"title":TITLE,"version":VERSION,"reservation_token":str(uuid.uuid4()),"source_inputs":current_inputs,"source_commit":os.environ.get("GITHUB_SHA"),"workflow_run_id":os.environ.get("GITHUB_RUN_ID")}
            save("create-intent.json",intent)
            persist()  # Durable write must succeed before creation.
            dep=z.request("/deposit/depositions","POST",{"metadata":metadata(intent)})
            save("create-response.json",{"received_record_id":dep.get("id"),"received_doi":dep.get("doi") or dep.get("metadata",{}).get("prereserve_doi",{}).get("doi"),"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
            persist()
    rid,doi=check_deposit(dep)
    save("deposit.json",{"record_id":rid,"doi":doi,"report_number":REPORT,"title":TITLE,"version":VERSION,"submitted":bool(dep.get("submitted")),"state":"RESERVED_SAME_RECORD_ONLY","prior_records_modified":False})
    persist()  # Recoverable even if subsequent build fails.
    e=build_package()
    save("preparation-attempt.json",{"state":"PREPARED_AWAITING_EXACT_PDF_VISUAL_REVIEW","record_id":rid,"doi":doi,"file_count":e["file_count"]})
    persist()
    print(json.dumps({"state":"PREPARED_AWAITING_EXACT_PDF_VISUAL_REVIEW","record_id":rid,"doi":doi,"expected_manifest_sha256":sha((ROOT/"EXPECTED-PUBLICATION.json").read_bytes())}))

def remote_files(rows, expected):
    if not isinstance(rows,list):
        raise RuntimeError("Invalid remote inventory")
    names=[r.get("filename",r.get("key")) for r in rows]
    if len(names)!=len(set(names)) or set(names)-expected:
        raise RuntimeError("Unexpected or duplicate remote files; nothing deleted")
    return dict(zip(names,rows))

def download_public(url):
    req=urllib.request.Request(check_url(url),headers={"User-Agent":"TrinityAccord-TA23-PublicReadback/1.0"})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=120) as response:
        data=response.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:
        raise RuntimeError("Public download size limit")
    return data

def publish():
    e,manifest_sha=validate_local_package()
    validate_authorization(e,manifest_sha)
    rid,doi=e["record_id"],e["doi"]
    z=client()
    dep=read(z,f"/deposit/depositions/{rid}")
    check_deposit(dep,e)
    if not dep.get("submitted"):
        if (ROOT/"publication-intent.json").exists():
            raise RuntimeError("Unresolved publish intent; POST will not be repeated")
        existing=remote_files(read(z,f"/deposit/depositions/{rid}/files"),FILES)
        # Do not rewrite metadata during publication; exact ownership was checked.
        bucket=check_url(dep["links"]["bucket"])
        if not urllib.parse.urlsplit(bucket).path.startswith("/api/files/"):
            raise RuntimeError("Unexpected draft bucket route")
        for item in e["files"]:
            data=(ROOT/"published"/item["name"]).read_bytes()
            prev=existing.get(item["name"])
            if prev and str(prev.get("checksum","")).removeprefix("md5:")==hashlib.md5(data).hexdigest() and prev.get("filesize",prev.get("size"))==len(data):
                continue
            z.request(bucket.rstrip("/")+"/"+urllib.parse.quote(item["name"],safe=""),"PUT",data,binary=True)
        uploaded=remote_files(read(z,f"/deposit/depositions/{rid}/files"),FILES)
        if set(uploaded)!=FILES:
            raise RuntimeError("Draft inventory incomplete")
        for item in e["files"]:
            r=uploaded[item["name"]]
            data=(ROOT/"published"/item["name"]).read_bytes()
            if str(r.get("checksum","")).removeprefix("md5:")!=hashlib.md5(data).hexdigest() or r.get("filesize",r.get("size"))!=len(data):
                raise RuntimeError("Uploaded draft checksum/size mismatch")
        validate_local_package()
        validate_authorization(e,manifest_sha)
        save("publication-intent.json",{"state":"PUBLISH_ONCE_INTENT","report_number":REPORT,"record_id":rid,"doi":doi,"expected_manifest_sha256":manifest_sha,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        persist()  # Durable intent before the one irreversible action.
        result=z.request(f"/deposit/depositions/{rid}/actions/publish","POST")
        check_deposit(result,e)
        if not result.get("submitted"):
            raise RuntimeError("Publish response does not confirm submission")
    public=read(z,f"/records/{rid}",authenticated=False)
    md=public.get("metadata",{})
    if (public.get("id"),public.get("doi"),md.get("title"),str(md.get("version")))!=(rid,doi,TITLE,VERSION):
        raise RuntimeError("Anonymous public record identity mismatch")
    remote=remote_files(public.get("files",[]),FILES)
    if set(remote)!=FILES:
        raise RuntimeError("Public exact inventory mismatch")
    verified=[]
    for item in e["files"]:
        links=remote[item["name"]].get("links",{})
        url=links.get("self") or links.get("download")
        data=download_public(url)
        if len(data)!=item["bytes"] or sha(data)!=item["sha256"]:
            raise RuntimeError("Anonymous public exact-byte mismatch")
        verified.append(dict(item,public_url=url))
    receipt={"state":"PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING","report_number":REPORT,"version":VERSION,"title":TITLE,"record_id":rid,"doi":doi,"record_url":f"https://zenodo.org/records/{rid}","submitted":True,"public_file_readback_pass":True,"public_readback_authenticated":False,"doi_resolution_pass":False,"doi_resolver":{"state":"NOT_CHECKED_ONLY_ZENODO_TRANSPORT_ALLOWED","matches_record":False},"expected_manifest_sha256":manifest_sha,"file_count":len(verified),"files":verified,"source_commit":e.get("source_commit"),"workflow_run_id":os.environ.get("GITHUB_RUN_ID"),"prior_records_modified":False,"peer_reviewed":False,"c1_empirically_validated":False,"ots_status":"PENDING","arweave_status":"PENDING","preservation_complete":False}
    save("publication-record.json",receipt)
    save("publication-attempt.json",{"state":receipt["state"],"record_id":rid,"doi":doi,"phase":"completed"})
    persist()
    print(json.dumps({"state":receipt["state"],"record_id":rid,"doi":doi,"public_file_readback_pass":True}))

def verify():
    e,digest=validate_local_package()
    print(json.dumps({"state":"EXACT_PACKAGE_PASS","record_id":e["record_id"],"doi":e["doi"],"expected_manifest_sha256":digest,"pdf_sha256":next(x["sha256"] for x in e["files"] if x["name"]==PDF_NAME)}))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("prepare","publish","verify","persist"))
    args=parser.parse_args()
    try:
        {"prepare":prepare,"publish":publish,"verify":verify,"persist":persist}[args.mode]()
    except Exception as exc:
        # Never print an HTTP body, URL, headers, token, or arbitrary exception text.
        if args.mode in ("prepare","publish"):
            save("preparation-attempt.json" if args.mode=="prepare" else "publication-attempt.json",{"state":"INCOMPLETE_REQUIRES_SAME_RECORD_REVIEW","error_type":type(exc).__name__,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        print("TA23 operation stopped: "+type(exc).__name__+"; inspect immutable state and reconcile same record.",file=sys.stderr)
        sys.exit(1)
