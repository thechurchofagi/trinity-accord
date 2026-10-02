#!/usr/bin/env python3
"""Publish one internally reviewed TA22 preprint using the established client.

Reserve once, bind DOI to sources/PDFs, require exact-package review, publish
the same record, and verify public bytes without credentials. No older deposit
or published edition is edited. The credential stays in GitHub Actions.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
BRANCH = "research/rlc-prefix-separable-v1-20261002"
TITLE = "Exponential Run Complexity of Prefix-Separable Orders on the Boolean Cube"
REPORT = "TA-TR-2026-22"
VERSION = "1.0"
DATE = "2026-10-02"
STEM = "rlc-prefix-separable"
CLIENT_BLOB = "a0cbc84cc5fd826c06d16456c4adbaa40dabc788"
PROTECTED = {21675727,21699878,21900592,22761411,22804542,22809019,22830239,
             22839629,22840604,22842789,22844927,22844928,22846307,22852884,
             22852885,22854705,22865494,22866205,22866775,22871209,22885976,
             22886276,22934654,22939808,22950904,22991126,23002980,23005587,
             23005588,23008261,23008262,23030207,23030320}
PUBLISHED_FILES = {f"{STEM}-v{VERSION}.md",f"{STEM}-v{VERSION}.pdf",
                   f"{STEM}-supplement-v{VERSION}.md",f"{STEM}-supplement-v{VERSION}.pdf",
                   "verify_theorem.py","verification-receipt.json","AUDIT-RECEIPT.json",
                   "citation.bib","citation.ris","citation.csl.json",
                   "README-LICENSE.txt","REVIEW-AND-SOURCES.md","SHA256SUMS.txt"}
MAX_FILE_BYTES = 16 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(name):
    return json.loads((ROOT / name).read_text())


def save(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + "\n")


def persist():
    paths = [str((ROOT / name).relative_to(REPO)) for name in
             ["create-intent.json","deposit.json","preparation-attempt.json",
              "publication-attempt.json","publication-record.json","EXPECTED-PUBLICATION.json",
              "format-checks.json","published"] if (ROOT / name).exists()]
    if not paths:
        return
    subprocess.run(["git","config","user.name","github-actions[bot]"],cwd=REPO,check=True)
    subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],cwd=REPO,check=True)
    subprocess.run(["git","add","--",*paths],cwd=REPO,check=True)
    if subprocess.run(["git","diff","--cached","--quiet"],cwd=REPO).returncode == 0:
        return
    subprocess.run(["git","diff","--cached","--check"],cwd=REPO,check=True)
    subprocess.run(["git","commit","-m","research: preserve TA22 publication state [skip ci]"],cwd=REPO,check=True)
    for _ in range(3):
        if subprocess.run(["git","push","origin","HEAD:"+BRANCH],cwd=REPO).returncode == 0:
            return
        subprocess.run(["git","fetch","origin",BRANCH,"--prune"],cwd=REPO,check=True)
        subprocess.run(["git","rebase","origin/"+BRANCH],cwd=REPO,check=True)
    raise RuntimeError("Publication checkpoint could not be persisted")


def client():
    path = ROOT.parent / "reading-trinity-accord" / "publish_zenodo.py"
    data = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != CLIENT_BLOB:
        raise RuntimeError("Established Zenodo client identity changed")
    spec = importlib.util.spec_from_file_location("verified_ta22_zenodo_client",path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    token = os.environ.get("ZENODO_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Publication credential unavailable")
    return module.Zenodo(token)


def read(z, path, authenticated=True):
    for attempt in range(4):
        try:
            return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
            if attempt == 3:
                raise
            time.sleep(3 * (attempt + 1))


def source_review():
    audit = load("AUDIT-RECEIPT.json")
    if (audit.get("state"),audit.get("report_number"),audit.get("version")) != (
            "INTERNAL_MATHEMATICAL_REVIEW_PASS",REPORT,VERSION):
        raise RuntimeError("Mathematical review not complete")
    expected = {"source-main.md","source-supplement.md","verify_theorem.py","verification-receipt.json"}
    rows = audit.get("source_files",[])
    if {row.get("name") for row in rows} != expected or len(rows) != len(expected):
        raise RuntimeError("Source review inventory mismatch")
    for row in rows:
        if digest((ROOT / row["name"]).read_bytes()) != row["sha256"]:
            raise RuntimeError("Reviewed source changed: " + row["name"])
    result = load("verification-receipt.json")
    if result.get("state") != "FINITE_THEOREM_CHECKS_PASS" or result.get("verification_script_sha256") != digest((ROOT / "verify_theorem.py").read_bytes()):
        raise RuntimeError("Finite verification receipt mismatch")


def metadata():
    return {"upload_type":"publication","publication_type":"preprint","title":TITLE,
            "creators":[{"name":"Liu, Hongju","affiliation":"Independent researcher, Shenzhen, China"}],
            "description":"<p>Mathematical preprint proving that a prefix-separable order on the standard Boolean cube can require Omega(2^n/n^2) monotone runs under every generic additive sweep. The liminf of n^2 M_n/2^n is at least 1/(8 log 3). The proof combines a fixed signed-tree family, a deterministic comparison-multiplicity bound, a small-tail estimate and sweep-chamber counts.</p><p>Existing signed-tree representations, alternating-run statistics and concentration methods are explicitly credited. A positive-density lower bound remains open. Complete analytic proofs and reproducible finite checks are included.</p><p>Human author of record and responsible depositor: Hongju Liu. Substantial ChatGPT (OpenAI) assistance under human direction is disclosed. Internal review; not externally peer reviewed. Adjacent first-party research, not an amendment of the Trinity Accord.</p>",
            "notes":REPORT+"; version "+VERSION+". Global historical priority is not certified.",
            "publication_date":DATE,"version":VERSION,"access_right":"open","license":"cc-by-4.0",
            "language":"eng","keywords":["Boolean cube","prefix separation","pseudo-sweep",
                    "alternating runs","separable permutations","linear ranking","probabilistic method"]}


def check_deposit(dep, identity=None):
    rid = dep.get("id")
    if type(rid) is not int or rid <= 0 or rid in PROTECTED:
        raise RuntimeError("Invalid or protected prior record ID")
    md = dep.get("metadata",{})
    if md.get("title") != TITLE or str(md.get("version")) != VERSION:
        raise RuntimeError("Reserved title/version mismatch")
    if [x.get("name") for x in md.get("creators",[])] != ["Liu, Hongju"] or REPORT not in md.get("notes",""):
        raise RuntimeError("Reserved creator/report mismatch")
    doi = dep.get("doi") or md.get("prereserve_doi",{}).get("doi") or md.get("doi")
    if doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Reserved DOI mismatch")
    if identity and (rid,doi) != (identity.get("record_id"),identity.get("doi")):
        raise RuntimeError("Reservation changed from checkpoint")
    return rid,doi


def build_package():
    source_review()
    identity = load("deposit.json")
    rid,doi = identity["record_id"],identity["doi"]
    if type(rid) is not int or rid in PROTECTED or doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Local reservation identity mismatch")
    pub = ROOT / "published"
    pub.mkdir(exist_ok=True)
    for source,name in [("source-main.md",f"{STEM}-v{VERSION}"),("source-supplement.md",f"{STEM}-supplement-v{VERSION}")]:
        text = (ROOT / source).read_text()
        if text.count("__DOI_RESERVED_AT_RELEASE__") != 1:
            raise RuntimeError("DOI placeholder inventory mismatch")
        target = pub / (name + ".md")
        target.write_text(text.replace("__DOI_RESERVED_AT_RELEASE__",doi))
        subprocess.run(["pandoc",str(target),"-o",str(pub / (name + ".pdf")),"--pdf-engine=xelatex",
                        "--from=markdown+tex_math_single_backslash","-V","mainfont=DejaVu Serif",
                        "-V","monofont=DejaVu Sans Mono"],check=True)
    for name in ["verify_theorem.py","verification-receipt.json","AUDIT-RECEIPT.json"]:
        shutil.copyfile(ROOT / name,pub / name)
    (pub / "citation.bib").write_text(f"@misc{{Liu2026PrefixSeparable,\n  author = {{Liu, Hongju}},\n  title = {{{TITLE}}},\n  year = {{2026}},\n  version = {{{VERSION}}},\n  doi = {{{doi}}},\n  url = {{https://doi.org/{doi}}},\n  note = {{{REPORT}; mathematical preprint; not peer reviewed}}\n}}\n")
    (pub / "citation.ris").write_text(f"TY  - RPRT\nAU  - Liu, Hongju\nTI  - {TITLE}\nPY  - 2026\nDA  - {DATE}\nVL  - {VERSION}\nDO  - {doi}\nUR  - https://doi.org/{doi}\nN1  - {REPORT}; mathematical preprint; not peer reviewed\nER  -\n")
    csl = {"id":doi,"type":"report","title":TITLE,"author":[{"family":"Liu","given":"Hongju"}],
           "issued":{"date-parts":[[2026,10,2]]},"version":VERSION,"number":REPORT,
           "DOI":doi,"URL":"https://doi.org/"+doi,"note":"Mathematical preprint; not peer reviewed"}
    (pub / "citation.csl.json").write_text(json.dumps(csl,indent=2)+"\n")
    (pub / "README-LICENSE.txt").write_text(f"{TITLE}\n{REPORT} | Version {VERSION} | {DATE}\nDOI: {doi}\n\nHuman author of record and responsible depositor: Hongju Liu.\nAffiliation: Independent researcher, Shenzhen, China.\nSubstantial ChatGPT (OpenAI) assistance under human direction is disclosed.\nThis is a mathematical preprint, not externally peer reviewed.\n\nThe primary publication is the English main PDF. The English supplement, Markdown sources, finite verifier and receipts are supplied for transparency. The theorem is analytic; finite computation does not prove historical priority or replace the all-dimensional proof. A dimension-independent positive-density bound remains open.\n\nCC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their rights.\n\nAdjacent first-party research; this does not amend the Trinity Accord or its Bitcoin Originals. DOI/OTS/Arweave establish version identity and preservation, not scientific correctness or peer review.\n")
    (pub / "REVIEW-AND-SOURCES.md").write_text(f"# Internal Review and Sources\n\nReport: {REPORT}. Version: {VERSION}. DOI: {doi}.\n\nThe analytic proof was internally checked for strict prefix separation, ancestor comparison signs, deterministic multiplicity bounds, unconditioned independent spins, bounded differences, the small-tail dichotomy, all-sweep union bounds and the liminf constant. The deposited finite verifier covers 5,161,156 rank sequences, 36,127,300 one-spin comparisons, 7,898 prefix cuts, and 5,912 statistic-identity permutations. Coverage limits are given in the supplement and receipt.\n\nThe mathematical review receipt binds the original reviewed sources and verification script. Publication additionally requires a separate review of the exact DOI-bound PDFs and manifest. No independent external peer review or separate final human line-by-line verification is claimed.\n\nThe main manuscript references the directly relevant original works of Padrol and Philippe; Maclagan; Edelman, Gvozdeva and Slinko; Bassino et al.; Gessel and Zhuang; McDiarmid; Stanley; and Pinsky. Known tree representations, ancestor rules and run statistics are credited. The contribution is the proved quantitative combination under the standard-cube prefix condition and all-sweep requirement; exhaustive historical priority is not certified.\n\nThe constant-density conjecture and deterministic explicit constructions achieving the general lower bound remain open here. This version contains no Gray-family extremal claim or biological-data claim.\n")
    (pub / "SHA256SUMS.txt").write_text("".join(digest((pub / name).read_bytes())+"  "+name+"\n" for name in sorted(PUBLISHED_FILES-{"SHA256SUMS.txt"})))
    if {p.name for p in pub.iterdir() if p.is_file()} != PUBLISHED_FILES:
        raise RuntimeError("Published file inventory mismatch")
    rows = [{"name":name,"bytes":(pub / name).stat().st_size,"sha256":digest((pub / name).read_bytes())} for name in sorted(PUBLISHED_FILES)]
    expected = {"report_number":REPORT,"title":TITLE,"version":VERSION,"record_id":rid,"doi":doi,
                "file_count":len(rows),"files":rows,"prior_records_modified":False}
    save("EXPECTED-PUBLICATION.json",expected)
    for name in sorted(n for n in PUBLISHED_FILES if n.endswith(".pdf")):
        text = subprocess.check_output(["pdftotext",str(pub / name),"-"],text=True)
        if doi not in text or len(text) < 1000 or "__DOI_RESERVED_AT_RELEASE__" in text:
            raise RuntimeError("PDF text/identity check failed: " + name)
    save("format-checks.json",{"state":"FORMAT_CHECKS_PASS_PENDING_VISUAL_REVIEW","doi":doi,
                                "pdf_text_extractable":True,"doi_bound":True})
    return expected


def validate_package():
    source_review()
    expected = load("EXPECTED-PUBLICATION.json")
    if (expected.get("report_number"),expected.get("title"),expected.get("version")) != (REPORT,TITLE,VERSION):
        raise RuntimeError("Package identity mismatch")
    rid,doi = expected.get("record_id"),expected.get("doi")
    if type(rid) is not int or rid <= 0 or rid in PROTECTED or doi != f"10.5281/zenodo.{rid}":
        raise RuntimeError("Invalid package record identity")
    rows = expected.get("files",[])
    if expected.get("file_count") != len(PUBLISHED_FILES) or len(rows) != len(PUBLISHED_FILES) or {x.get("name") for x in rows} != PUBLISHED_FILES:
        raise RuntimeError("Package manifest inventory mismatch")
    if {p.name for p in (ROOT / "published").iterdir() if p.is_file()} != PUBLISHED_FILES:
        raise RuntimeError("Local inventory differs from manifest")
    for item in rows:
        data = (ROOT / "published" / item["name"]).read_bytes()
        if len(data) != item["bytes"] or digest(data) != item["sha256"]:
            raise RuntimeError("Exact package changed: " + item["name"])
    return expected,digest((ROOT / "EXPECTED-PUBLICATION.json").read_bytes())


def prepare():
    source_review()
    z = client()
    if (ROOT / "deposit.json").exists():
        identity = load("deposit.json")
        dep = read(z,f"/deposit/depositions/{int(identity['record_id'])}")
        check_deposit(dep,identity)
    else:
        rows = read(z,"/deposit/depositions?"+urllib.parse.urlencode({"q":f'"{TITLE}"',"size":100}))
        hits = [r for r in rows if r.get("metadata",{}).get("title") == TITLE and str(r.get("metadata",{}).get("version")) == VERSION]
        if len(hits) > 1:
            raise RuntimeError("Multiple matching records; reconcile before proceeding")
        if hits:
            dep = hits[0]
        else:
            if (ROOT / "create-intent.json").exists():
                raise RuntimeError("Unresolved prior creation intent; do not create another record")
            save("create-intent.json",{"state":"CREATE_ONCE_INTENT","title":TITLE,"version":VERSION,
                                       "report_number":REPORT,"workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
            persist()
            dep = z.request("/deposit/depositions","POST",{"metadata":metadata()})
    rid,doi = check_deposit(dep)
    if dep.get("submitted"):
        raise RuntimeError("Already published; resume readback without rebuilding frozen files")
    save("deposit.json",{"state":"RESERVED_NOT_PUBLISHED","record_id":rid,"doi":doi,"report_number":REPORT,
                         "title":TITLE,"version":VERSION,"prior_records_modified":False})
    build_package()
    save("preparation-attempt.json",{"state":"DOI_BOUND_PACKAGE_PREPARED","record_id":rid,"doi":doi,
                                    "workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
    print(json.dumps(load("deposit.json"),indent=2))


def require_publication_review(expected, manifest_hash):
    authorization = load("PUBLISH-AUTHORIZATION.json")
    review = load("FINAL-REVIEW.json")
    required = (REPORT,VERSION,expected["record_id"],expected["doi"],manifest_hash)
    actual = tuple(authorization.get(k) for k in ["report_number","version","record_id","doi","expected_manifest_sha256"])
    if actual != required or authorization.get("authorization") != "PUBLISH_EXACT_REVIEWED_PACKAGE":
        raise RuntimeError("Exact-package authorization mismatch")
    if review.get("state") != "EXACT_DOI_BOUND_PACKAGE_REVIEW_PASS" or review.get("expected_manifest_sha256") != manifest_hash or review.get("pdf_visual_review_pass") is not True:
        raise RuntimeError("Final DOI-bound PDF review missing or mismatched")


def download_public(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "zenodo.org" or parsed.username or parsed.password:
        raise RuntimeError("Unexpected public download host")
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"TA22-PublicReadback/1.0"}),timeout=90) as response:
        data = response.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise RuntimeError("Public asset exceeds size limit")
    return data


def resolver_check(doi,rid):
    result = {"state":"RESOLVER_PENDING","matches_record":False}
    for attempt in range(3):
        try:
            with urllib.request.urlopen("https://doi.org/"+doi,timeout=30) as response:
                parsed = urllib.parse.urlsplit(response.url)
                valid = response.status == 200 and parsed.hostname == "zenodo.org" and parsed.path.rstrip("/") in (f"/records/{rid}",f"/record/{rid}")
                result = {"state":"RESOLVER_PASS" if valid else "RESOLVER_TARGET_MISMATCH",
                          "http_status":response.status,"final_url":response.url,"matches_record":valid}
                if valid:
                    return result
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as error:
            result = {"state":"RESOLVER_PENDING","error_type":type(error).__name__,"matches_record":False}
        if attempt < 2:
            time.sleep(5)
    return result


def publish():
    expected,manifest_hash = validate_package()
    require_publication_review(expected,manifest_hash)
    rid,doi = expected["record_id"],expected["doi"]
    z = client()
    dep = read(z,f"/deposit/depositions/{rid}")
    check_deposit(dep,expected)
    if not dep.get("submitted"):
        dep = z.request(f"/deposit/depositions/{rid}","PUT",{"metadata":metadata()})
        check_deposit(dep,expected)
        remote = {item["filename"]:item for item in read(z,f"/deposit/depositions/{rid}/files")}
        if set(remote) - PUBLISHED_FILES:
            raise RuntimeError("Unexpected draft files; no deletion or publication")
        bucket = dep["links"]["bucket"]
        parsed = urllib.parse.urlsplit(bucket)
        if parsed.scheme != "https" or parsed.hostname != "zenodo.org" or not parsed.path.startswith("/api/files/"):
            raise RuntimeError("Unexpected upload bucket")
        for item in expected["files"]:
            data = (ROOT / "published" / item["name"]).read_bytes()
            previous = remote.get(item["name"])
            md5 = hashlib.md5(data).hexdigest()
            if previous and str(previous.get("checksum","")).removeprefix("md5:") == md5 and previous.get("filesize") == len(data):
                continue
            z.request(bucket.rstrip("/")+"/"+urllib.parse.quote(item["name"],safe=""),"PUT",data,binary=True)
        remote = {item["filename"]:item for item in read(z,f"/deposit/depositions/{rid}/files")}
        if set(remote) != PUBLISHED_FILES:
            raise RuntimeError("Draft inventory mismatch")
        for item in expected["files"]:
            actual = remote[item["name"]]
            data = (ROOT / "published" / item["name"]).read_bytes()
            if actual.get("filesize") != len(data) or str(actual.get("checksum","")).removeprefix("md5:") != hashlib.md5(data).hexdigest():
                raise RuntimeError("Draft checksum mismatch")
        save("publication-attempt.json",{"state":"PUBLICATION_INTENT_FOR_RESERVED_RECORD","record_id":rid,
                                         "doi":doi,"expected_manifest_sha256":manifest_hash,"new_record_creation":False})
        persist()
        check_deposit(z.request(f"/deposit/depositions/{rid}/actions/publish","POST"),expected)
    public = read(z,f"/records/{rid}",authenticated=False)
    check_deposit(public,expected)
    remote = {item["key"]:item for item in public.get("files",[])}
    if set(remote) != PUBLISHED_FILES:
        raise RuntimeError("Public inventory mismatch")
    verified = []
    for item in expected["files"]:
        url = remote[item["name"]]["links"].get("self") or remote[item["name"]]["links"].get("download")
        data = download_public(url)
        if len(data) != item["bytes"] or digest(data) != item["sha256"]:
            raise RuntimeError("Public exact-byte mismatch: " + item["name"])
        verified.append(dict(item,public_url=url))
    resolution = resolver_check(doi,rid)
    receipt = {"state":"PUBLISHED_AND_PUBLIC_READBACK_PASS" if resolution["matches_record"] else "PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING",
               "report_number":REPORT,"title":TITLE,"version":VERSION,"record_id":rid,"doi":doi,
               "record_url":f"https://zenodo.org/records/{rid}","submitted":True,"file_count":len(verified),
               "files":verified,"expected_manifest_sha256":manifest_hash,"public_readback_authenticated":False,
               "public_file_readback_pass":True,"doi_resolution_pass":resolution["matches_record"],"doi_resolver":resolution,
               "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO,text=True).strip(),
               "workflow_run_id":os.environ.get("GITHUB_RUN_ID"),"prior_doi_records_modified":False,
               "bitcoin_originals_modified":False,"peer_reviewed":False,"global_originality_certified":False,
               "manuscript_language":"eng"}
    save("publication-record.json",receipt)
    save("publication-attempt.json",{"state":receipt["state"],"record_id":rid,"doi":doi,"phase":"completed"})
    print(json.dumps(receipt,indent=2))


def verify():
    expected,manifest_hash = validate_package()
    print(json.dumps({"state":"EXACT_PACKAGE_HASH_CHECK_PASS","record_id":expected["record_id"],
                      "doi":expected["doi"],"file_count":expected["file_count"],
                      "expected_manifest_sha256":manifest_hash},indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode",choices=["prepare","publish","verify","persist"])
    args = parser.parse_args()
    try:
        {"prepare":prepare,"publish":publish,"verify":verify,"persist":persist}[args.mode]()
    except Exception as error:
        if args.mode in ("prepare","publish"):
            save("preparation-attempt.json" if args.mode == "prepare" else "publication-attempt.json",
                 {"state":"INCOMPLETE_REQUIRES_SAME_RECORD_RESUMPTION","error_type":type(error).__name__,
                  "workflow_run_id":os.environ.get("GITHUB_RUN_ID")})
        print(type(error).__name__+": "+str(error),file=sys.stderr)
        sys.exit(1)
