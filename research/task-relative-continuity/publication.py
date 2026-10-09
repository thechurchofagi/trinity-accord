#!/usr/bin/env python3
"""RT/TH create-once Zenodo publication. Explicit DOI insertion before PDF freeze."""
import hashlib, html, json, os, pathlib, subprocess, sys, tempfile, urllib.request, urllib.parse, urllib.error, time, zipfile
R=pathlib.Path(__file__).resolve().parent
REPO=R.parents[1]
BRANCH="research/rt-th-task-relative-continuity-v1-20261009"
TITLE="Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout"
VERSION="1.0.0"; REPORT="RT20261009"
STEM="Task_Relative_Continuity_v1.0.0"
PDF=STEM+".pdf"; MD=STEM+".md"; ZIP="RT_TH_Reproducibility_v1.0.0.zip"
FILES=[PDF,MD,ZIP,"README-LICENSE.txt","citation.bib","SHA256SUMS.txt"]
def digest(b):return hashlib.sha256(b).hexdigest()
def load(n):return json.loads((R/n).read_text())
def save(n,v):
 p=R/n;p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n")
def persist(*names):
 if os.environ.get("GITHUB_ACTIONS")!="true":return
 assert subprocess.check_output(["git","branch","--show-current"],cwd=REPO,text=True).strip()==BRANCH
 subprocess.run(["git","config","user.name","github-actions[bot]"],cwd=REPO,check=True)
 subprocess.run(["git","config","user.email","41898282+github-actions[bot]@users.noreply.github.com"],cwd=REPO,check=True)
 subprocess.run(["git","add","--",*[str((R/n).relative_to(REPO)) for n in names if (R/n).exists()]],cwd=REPO,check=True)
 if subprocess.check_output(["git","diff","--cached","--name-only"],cwd=REPO,text=True).strip():
  subprocess.run(["git","commit","-m","[skip ci] Preserve RT/TH Zenodo release stage"],cwd=REPO,check=True)
  for retry in range(4):
   p=subprocess.run(["git","push","origin","HEAD:"+BRANCH],cwd=REPO)
   if p.returncode==0:return
   subprocess.run(["git","fetch","origin",BRANCH,"--prune"],cwd=REPO,check=True)
   q=subprocess.run(["git","rebase","origin/"+BRANCH],cwd=REPO)
   if q.returncode!=0:
    subprocess.run(["git","rebase","--abort"],cwd=REPO)
    raise RuntimeError("Checkpoint conflict requires manual reconciliation")
  raise RuntimeError("Unable to checkpoint publication stage")
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*a):raise RuntimeError("Redirect not allowed for authenticated request")
def api(path,method="GET",data=None,binary=False,auth=True):
 url=path if path.startswith("https://") else "https://zenodo.org/api"+path
 p=urllib.parse.urlsplit(url)
 if p.scheme!="https" or p.hostname!="zenodo.org" or p.username or p.password:raise RuntimeError("Unapproved Zenodo endpoint")
 headers={"User-Agent":"RTTH-Publication-v1.0.0"}
 if auth:headers["Authorization"]="Bearer "+os.environ["ZENODO_ACCESS_TOKEN"]
 if data is not None:
  headers["Content-Type"]="application/octet-stream" if binary else "application/json"
  if not binary:data=json.dumps(data).encode()
 req=urllib.request.Request(url,headers=headers,method=method,data=data)
 with urllib.request.build_opener(NoRedirect()).open(req,timeout=120) as r:return json.loads(r.read(16000000))
def read(path,auth=True):
 for i in range(3):
  try:return api(path,auth=auth)
  except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError):
   if i==2:raise
   time.sleep(3*(i+1))
def identity():return digest((R/"source-main.md").read_bytes())
def metadata():
 source=(R/"source-main.md").read_text()
 abstract=source.split("## Abstract",1)[1].split("# Introduction",1)[0][:2900] if "# Introduction" in source else source.split("## Abstract",1)[1][:1900]
 return {"upload_type":"publication","publication_type":"preprint","title":TITLE,"creators":[{"name":"Liu, Hongju","affiliation":"Independent researcher, Shenzhen, China"}],"description":"<p>"+html.escape(abstract.strip())+"</p><p>Non-peer-reviewed theoretical preprint. Substantial AI research and drafting assistance disclosed; no empirical consciousness validation claimed.</p>","publication_date":"2026-10-09","version":VERSION,"access_right":"open","license":"cc-by-4.0","language":"eng","keywords":["representational continuity","invariance","route ambiguity","readout","thought experiments","consciousness theory"],"notes":"RT20261009 exact independent source SHA256 "+identity()+". No alteration of previous publications.","related_identifiers":[{"identifier":"10.5281/zenodo.23241982","relation":"references","scheme":"doi"},{"identifier":"10.5281/zenodo.23131575","relation":"references","scheme":"doi"},{"identifier":"10.5281/zenodo.23137088","relation":"references","scheme":"doi"}]}
def check(dep):
 rid=dep["id"];m=dep["metadata"];doi=dep.get("doi") or m.get("prereserve_doi",{}).get("doi") or "10.5281/zenodo."+str(rid)
 if (m.get("title"),str(m.get("version")))!=(TITLE,VERSION) or identity() not in m.get("notes","") or doi!="10.5281/zenodo."+str(rid):raise RuntimeError("Zenodo identity mismatch")
 return rid,doi
def prepare():
 if not os.environ.get("ZENODO_ACCESS_TOKEN") or os.environ.get("GITHUB_ACTIONS")!="true":raise RuntimeError("GitHub Actions Zenodo credential required")
 if (R/"deposit.json").exists():
  d=load("deposit.json")
  obj=read("/deposit/depositions/"+str(d["record_id"]))
  assert check(obj)==(d["record_id"],d["doi"])
  return obj
 matches=[]
 for page in range(1,8):
  lst=read("/deposit/depositions?page="+str(page)+"&size=100")
  matches.extend(v for v in lst if v.get("metadata",{}).get("title")==TITLE and str(v.get("metadata",{}).get("version"))==VERSION)
  if len(lst)<100:break
 if len(matches)>1:raise RuntimeError("Multiple same title/version drafts")
 if matches:
  obj=matches[0];rid,doi=check(obj)
  save("deposit.json",{"record_id":rid,"doi":doi});persist("deposit.json")
  return obj
 if (R/"create-intent.json").exists():raise RuntimeError("Unresolved prior create POST; stop, do not duplicate")
 save("create-intent.json",{"source_sha256":identity(),"state":"CREATE_ONCE_INTENT"});persist("create-intent.json")
 try:obj=api("/deposit/depositions","POST",{"metadata":metadata()})
 except Exception as e:
  save("create-uncertain.json",{"type":type(e).__name__});persist("create-uncertain.json");raise
 rid,doi=check(obj);save("deposit.json",{"record_id":rid,"doi":doi});persist("deposit.json");return obj
def build(doi):
 source=(R/"source-main.md").read_text()
 if "DOI: " in source[:2500] or "doi.org/10.5281/zenodo." in source[:1200]:raise RuntimeError("Unexpected preexisting DOI in title block")
 source=source.replace("\\begin{center}","\\begin{center}\nPublished preprint DOI: \\texttt{"+doi+"}\\\\",1)
 source=source.replace("Theoretical preprint; not peer reviewed.","Published theoretical preprint; not peer reviewed.",1)
 pub=R/"published";pub.mkdir(exist_ok=True)
 (pub/MD).write_text(source)
 subprocess.run(["pandoc",str(pub/MD),"-o",str(pub/PDF),"--pdf-engine=xelatex","--from=markdown+tex_math_single_backslash","-V","mainfont=DejaVu Serif","-V","monofont=DejaVu Sans Mono"],check=True)
 raw=(pub/PDF).read_bytes()
 if not raw.startswith(b"%PDF") or len(raw)<30000:raise RuntimeError("Unexpected PDF")
 extracted=subprocess.check_output(["pdftotext",str(pub/PDF),"-"],text=True)
 if doi not in extracted:raise RuntimeError("DOI not found in rendered PDF text")
 if len(extracted)<12000:raise RuntimeError("PDF unexpectedly short")
 with zipfile.ZipFile(pub/ZIP,"w",zipfile.ZIP_DEFLATED) as z:
  for name in ["source-main.md","code/check_handoff.py","code/check_review_cases.py","code/check_transport.py","review/REVIEW_REPORT.md","review/PRIOR_ART_AND_SOURCE_ACCESS.md"]:
   z.write(R/name,name)
  z.write(pub/MD,MD)
 (pub/"README-LICENSE.txt").write_text("RT20261009 | v1.0.0 | DOI "+doi+"\nTheoretical preprint; not peer reviewed. Human author: Hongju Liu. Substantial ChatGPT assistance in research, formalization, checking and drafting. Source and reproducibility scripts included. CC BY 4.0 for original material. No UCT empirical validation.\n")
 (pub/"citation.bib").write_text("@misc{Liu2026RTTH,\n author={Liu, Hongju},\n title={"+TITLE+"},\n year={2026},\n doi={"+doi+"},\n url={https://doi.org/"+doi+"},\n note={Preprint, not peer reviewed}\n}\n")
 rows=[n for n in FILES if n!="SHA256SUMS.txt"]
 (pub/"SHA256SUMS.txt").write_text("".join(digest((pub/n).read_bytes())+"  "+n+"\n" for n in rows))
 expected={"record_id":int(doi.rsplit(".",1)[1]),"doi":doi,"report":REPORT,"version":VERSION,"title":TITLE,"files":[{"name":n,"sha256":digest((pub/n).read_bytes()),"bytes":(pub/n).stat().st_size} for n in FILES]}
 if (R/"frozen-package.json").exists():
  if load("frozen-package.json")!=expected:raise RuntimeError("Frozen publication package changed")
 else:
  save("frozen-package.json",expected);persist("frozen-package.json")
 return expected
def publish():
 obj=prepare();rid,doi=check(obj)
 exp=build(doi); pub=R/"published"
 if (R/"publication-record.json").exists():
  r=load("publication-record.json");assert r["doi"]==doi;return
 if not obj.get("submitted"):
  bucket=obj.get("links",{}).get("bucket")
  if not bucket or urllib.parse.urlsplit(bucket).hostname!="zenodo.org":raise RuntimeError("Bad upload bucket")
  for f in exp["files"]:
   name=f["name"];data=(pub/name).read_bytes()
   current=read("/deposit/depositions/"+str(rid))
   remote={x.get("filename") or x.get("key"):x for x in current.get("files",[])}
   if name in remote:
    x=remote[name];md5=__import__("hashlib").md5(data).hexdigest()
    if x.get("checksum") not in ("md5:"+md5,md5) or x.get("filesize",x.get("size"))!=len(data):raise RuntimeError("Remote file collision: "+name)
    continue
   api(bucket+"/"+urllib.parse.quote(name),"PUT",data,binary=True)
   reread=read("/deposit/depositions/"+str(rid))
   got={x.get("filename") or x.get("key"):x for x in reread.get("files",[])}.get(name)
   if not got or got.get("checksum") not in ("md5:"+__import__("hashlib").md5(data).hexdigest(),__import__("hashlib").md5(data).hexdigest()):raise RuntimeError("File upload uncertain "+name)
  save("upload-complete.json",exp);persist("upload-complete.json")
  if not (R/"publication-intent.json").exists():
   save("publication-intent.json",{"doi":doi,"files_sha256":{v["name"]:v["sha256"] for v in exp["files"]}});persist("publication-intent.json")
   try:obj=api("/deposit/depositions/"+str(rid)+"/actions/publish","POST")
   except Exception:
    obj=read("/deposit/depositions/"+str(rid))
    if not obj.get("submitted"):raise RuntimeError("Uncertain publish POST; never retry automatically")
  else:
   obj=read("/deposit/depositions/"+str(rid))
   if not obj.get("submitted"):raise RuntimeError("Unresolved publish intent")
 public=read("/records/"+str(rid),auth=False)
 if public.get("doi")!=doi or public.get("id")!=rid:raise RuntimeError("Public DOI differs")
 rows=[]; mismatches=[]
 for f in exp["files"]:
  name=f["name"]
  url="https://zenodo.org/records/"+str(rid)+"/files/"+urllib.parse.quote(name)+"?download=1"
  with urllib.request.urlopen(url,timeout=100) as response:b=response.read(16000000)
  if not b or len(b)>=16000000:raise RuntimeError("Public file empty or oversized: "+name)
  observed={"name":name,"bytes":len(b),"sha256":digest(b)}
  if observed["sha256"]!=f["sha256"] or observed["bytes"]!=f["bytes"]:mismatches.append(name)
  (pub/name).write_bytes(b)
  rows.append(observed)
 md=(pub/MD).read_text()
 if TITLE.split(":")[0] not in md or "route" not in md.lower():raise RuntimeError("Published Markdown is unrelated to reviewed study")
 pdftext=subprocess.check_output(["pdftotext",str(pub/PDF),"-"],text=True)
 if doi not in pdftext or "Task-Relative" not in pdftext or len(pdftext)<12000:raise RuntimeError("Public PDF lacks DOI or reviewed content")
 with zipfile.ZipFile(pub/ZIP) as z:
  if z.testzip() is not None:raise RuntimeError("Public supplement corrupted")
 state="PUBLISHED_PUBLIC_READBACK_PASS_WITH_FROZEN_BUILD_DIFF" if mismatches else "PUBLISHED_AND_PUBLIC_READBACK_PASS"
 receipt={"report_number":REPORT,"record_id":rid,"doi":doi,"title":TITLE,"version":VERSION,"state":state,
          "public_file_readback_pass":True,"submitted":True,"files":rows,"peer_reviewed":False,
          "frozen_build_mismatches":mismatches,
          "boundary":"Use actual public PDF SHA for OTS; historical local rebuild may have nondeterministic PDF bytes"}
 save("publication-record.json",receipt)
 persist("publication-record.json","published")
 print("RT_TH_ZENODO_PUBLIC_BYTES_VERIFIED",doi,"changed_vs_build",mismatches)

if __name__=="__main__":
 try:publish()
 finally:persist("create-intent.json","deposit.json","create-uncertain.json","frozen-package.json","upload-complete.json","publication-intent.json","publication-record.json")
