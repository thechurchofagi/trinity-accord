#!/usr/bin/env python3
"""Publish/reconcile a Chronicle sidechain cold-recovery deposit on Zenodo.

Fail-closed guarantees:
- exact versioned mixed-rights acknowledgement is mandatory;
- local SHA256SUMS and package identity are verified before any network write;
- one bounded series draft is reconciled rather than duplicated;
- every uploaded file is size/MD5 checked and fully downloaded for SHA-256
  verification before publish and after publish;
- all API operations are logged to DEBUG.jsonl without exposing bearer tokens.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

ROOT=pathlib.Path(__file__).resolve().parents[1]
TITLE="Trinity Accord Chronicle Polygon and Base NFT Evidence v2"
RIGHTS_ACK="TRINITY_SIDECHAIN_EVIDENCE_MIXED_RIGHTS_V1_APPROVED"
DEFAULT_API="https://zenodo.org/api"
DEFAULT_STATE=ROOT/"archive"/"chronicle-sidechain-zenodo-state.json"


def read_json(path:pathlib.Path)->dict[str,Any]:
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise SystemExit(f"expected JSON object: {path}")
    return data


def write_json(path:pathlib.Path,data:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def sha256_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def md5_bytes(data:bytes)->str:return hashlib.md5(data,usedforsecurity=False).hexdigest()


class Client:
    def __init__(self,token:str,api_base:str,debug_path:pathlib.Path):
        if not token: raise SystemExit("ZENODO_ACCESS_TOKEN is required")
        self.token=token; self.base=api_base.rstrip("/"); self.debug_path=debug_path
        debug_path.parent.mkdir(parents=True,exist_ok=True)
        if debug_path.exists(): debug_path.unlink()

    def log(self,event:str,**fields:Any)->None:
        row={"ts":dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z"),"event":event,**fields}
        with self.debug_path.open("a",encoding="utf-8") as f:f.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\n")
        print("[ZENODO] "+event+" "+" ".join(f"{k}={v}" for k,v in fields.items()),flush=True)

    def url(self,u:str)->str:return self.base+u if u.startswith("/") else u
    def headers(self,content_type:str|None=None)->dict[str,str]:
        h={"Authorization":f"Bearer {self.token}","Accept":"application/json","User-Agent":"trinity-sidechain-zenodo/1.0"}
        if content_type:h["Content-Type"]=content_type
        return h

    def request(self,method:str,url:str,*,payload:Any|None=None,data:bytes|None=None,content_type:str="application/json")->Any:
        body=data
        if payload is not None:body=json.dumps(payload,ensure_ascii=False).encode()
        target=self.url(url); started=dt.datetime.now(dt.timezone.utc)
        self.log("request_start",method=method,url_path=urllib.parse.urlparse(target).path,body_bytes=len(body) if body is not None else 0)
        req=urllib.request.Request(target,data=body,method=method,headers=self.headers(content_type if body is not None else None))
        try:
            with urllib.request.urlopen(req,timeout=180) as res:
                raw=res.read(); status=getattr(res,"status",200)
        except urllib.error.HTTPError as exc:
            detail=exc.read().decode("utf-8",errors="replace")
            self.log("request_http_error",method=method,url_path=urllib.parse.urlparse(target).path,status=exc.code,detail_sha256=sha256_bytes(detail.encode()))
            raise SystemExit(f"Zenodo {method} HTTP {exc.code}: {detail[:1600]}") from exc
        except OSError as exc:
            self.log("request_network_error",method=method,url_path=urllib.parse.urlparse(target).path,error=repr(exc))
            raise SystemExit(f"Zenodo {method} failed: {exc}") from exc
        elapsed=int((dt.datetime.now(dt.timezone.utc)-started).total_seconds()*1000)
        self.log("request_ok",method=method,url_path=urllib.parse.urlparse(target).path,status=status,response_bytes=len(raw),response_sha256=sha256_bytes(raw),elapsed_ms=elapsed)
        if not raw:return {}
        try:return json.loads(raw.decode())
        except Exception as exc:raise SystemExit("Zenodo API returned non-JSON response") from exc

    def bytes(self,url:str)->bytes:
        target=self.url(url); self.log("download_start",url_path=urllib.parse.urlparse(target).path)
        req=urllib.request.Request(target,method="GET",headers=self.headers())
        try:
            with urllib.request.urlopen(req,timeout=300) as res:raw=res.read()
        except Exception as exc:
            self.log("download_error",url_path=urllib.parse.urlparse(target).path,error=repr(exc));raise
        self.log("download_ok",url_path=urllib.parse.urlparse(target).path,bytes=len(raw),sha256=sha256_bytes(raw));return raw


def verify_local(deposit:pathlib.Path)->dict[str,Any]:
    package=read_json(deposit/"SIDECHAIN-ZENODO-DEPOSIT.json")
    if package.get("schema")!="trinity-accord/chronicle-sidechain-zenodo-deposit/v1":raise SystemExit("unexpected deposit schema")
    if package.get("metadata",{}).get("title")!=TITLE:raise SystemExit("unexpected deposit title")
    sums={}
    for line in (deposit/"SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():continue
        digest,name=line.split(None,1);name=name.strip().lstrip("*")
        if len(digest)!=64:raise SystemExit(f"invalid SHA256SUMS digest for {name}")
        sums[name]=digest
    expected_names={x["name"] for x in package.get("inventory",[]) if isinstance(x,dict)}|{"SHA256SUMS","SIDECHAIN-ZENODO-DEPOSIT.json"}
    actual_names={p.name for p in deposit.iterdir() if p.is_file() and p.name!="DEBUG.jsonl"}
    if actual_names!=expected_names:
        raise SystemExit(f"local deposit file set mismatch missing={sorted(expected_names-actual_names)} unexpected={sorted(actual_names-expected_names)}")
    inv={}
    for p in sorted(x for x in deposit.iterdir() if x.is_file() and x.name!="DEBUG.jsonl"):
        raw=p.read_bytes();inv[p.name]={"bytes":len(raw),"sha256":sha256_bytes(raw),"md5":md5_bytes(raw)}
        if p.name!="SHA256SUMS" and sums.get(p.name)!=inv[p.name]["sha256"]:raise SystemExit(f"SHA256SUMS mismatch: {p.name}")
    return {"package":package,"inventory":inv}


def dep_id(rec:dict[str,Any])->int:
    try:return int(rec["id"])
    except Exception as exc:raise SystemExit("Zenodo response missing deposition id") from exc

def meta(rec:dict[str,Any])->dict[str,Any]:return rec.get("metadata") if isinstance(rec.get("metadata"),dict) else {}
def is_published(rec:dict[str,Any])->bool:return rec.get("submitted") is True or str(rec.get("state") or "").lower()=="done" or bool(rec.get("doi") or meta(rec).get("doi"))
def version(rec:dict[str,Any])->str:return str(meta(rec).get("version") or "")
def doi(rec:dict[str,Any])->str:return str(rec.get("doi") or meta(rec).get("doi") or "")
def concept_doi(rec:dict[str,Any])->str:return str(rec.get("conceptdoi") or meta(rec).get("conceptdoi") or "")


def list_series(client:Client)->list[dict[str,Any]]:
    out=[]
    for page in range(1,21):
        q=urllib.parse.urlencode({"size":100,"page":page,"sort":"mostrecent"})
        rows=client.request("GET",f"/deposit/depositions?{q}")
        if not isinstance(rows,list):raise SystemExit("Zenodo deposition list is not a list")
        page_rows=[r for r in rows if isinstance(r,dict)]
        out.extend(r for r in page_rows if meta(r).get("title")==TITLE)
        if len(page_rows)<100:break
    return sorted(out,key=dep_id)


def refresh(client:Client,rec:dict[str,Any])->dict[str,Any]:
    out=client.request("GET",f"/deposit/depositions/{dep_id(rec)}")
    if not isinstance(out,dict):raise SystemExit("Zenodo deposition readback invalid")
    return out


def remote_files(rec:dict[str,Any])->dict[str,dict[str,Any]]:
    rows=rec.get("files")
    if not isinstance(rows,list):raise SystemExit("Zenodo files missing")
    result={}
    for item in rows:
        if not isinstance(item,dict):continue
        name=str(item.get("filename") or item.get("key") or "")
        if name:result[name]=item
    return result


def verify_remote(client:Client,rec:dict[str,Any],local:dict[str,dict[str,Any]])->None:
    remote=remote_files(rec)
    if set(remote)!=set(local):raise SystemExit(f"Zenodo remote file set mismatch missing={sorted(set(local)-set(remote))} unexpected={sorted(set(remote)-set(local))}")
    for name,expect in local.items():
        item=remote[name]
        size=item.get("filesize",item.get("size"))
        if int(size)!=expect["bytes"]:raise SystemExit(f"Zenodo size mismatch {name}")
        checksum=str(item.get("checksum") or "").split(":",1)[-1].lower()
        if checksum!=expect["md5"]:raise SystemExit(f"Zenodo MD5 mismatch {name}")
        links=item.get("links") if isinstance(item.get("links"),dict) else {}
        download=str(links.get("download") or links.get("content") or "")
        if not download:raise SystemExit(f"Zenodo download link missing {name}")
        raw=client.bytes(download)
        if len(raw)!=expect["bytes"] or sha256_bytes(raw)!=expect["sha256"]:raise SystemExit(f"Zenodo downloaded bytes mismatch {name}")
        client.log("remote_file_verified",name=name,bytes=len(raw),sha256=expect["sha256"])


def clear_files(client:Client,rec:dict[str,Any])->None:
    for item in (rec.get("files") or []):
        if not isinstance(item,dict):continue
        links=item.get("links") if isinstance(item.get("links"),dict) else {}
        url=links.get("self")
        if url:client.request("DELETE",str(url))


def create_draft(client:Client,latest:dict[str,Any]|None,metadata:dict[str,Any])->dict[str,Any]:
    if latest is None:
        out=client.request("POST","/deposit/depositions",payload={"metadata":metadata})
        if not isinstance(out,dict):raise SystemExit("new deposition response invalid")
        return out
    response=client.request("POST",f"/deposit/depositions/{dep_id(latest)}/actions/newversion",payload={})
    links=response.get("links") if isinstance(response,dict) and isinstance(response.get("links"),dict) else {}
    draft_url=links.get("latest_draft")
    if not draft_url:raise SystemExit("new version response missing latest_draft")
    draft=client.request("GET",str(draft_url))
    if not isinstance(draft,dict):raise SystemExit("latest draft invalid")
    return draft


def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument("--deposit-dir",required=True);ap.add_argument("--state",default=str(DEFAULT_STATE.relative_to(ROOT)));ap.add_argument("--api-base",default=os.getenv("ZENODO_API_BASE",DEFAULT_API));ap.add_argument("--rights-boundary-ack",default=os.getenv("CHRONICLE_SIDECHAIN_ZENODO_RIGHTS_ACK",""));args=ap.parse_args()
    deposit=(ROOT/args.deposit_dir).resolve()
    if ROOT not in deposit.parents or not deposit.is_dir():raise SystemExit("deposit directory must exist inside repository")
    local=verify_local(deposit);package=local["package"];version_id=str(package.get("version") or "")
    if args.rights_boundary_ack!=RIGHTS_ACK:raise SystemExit("sidechain Zenodo publication disabled until mixed-rights acknowledgement is explicitly approved")
    state_path=(ROOT/args.state).resolve()
    if ROOT not in state_path.parents:raise SystemExit("state path must be inside repository")
    token=os.getenv("ZENODO_ACCESS_TOKEN","").strip();client=Client(token,args.api_base,deposit/"DEBUG.jsonl")
    series=list_series(client);same=[r for r in series if version(r)==version_id];pub=[r for r in same if is_published(r)];drafts=[r for r in same if not is_published(r)]
    if len(pub)>1 or len(drafts)>1:raise SystemExit(f"duplicate Zenodo records for version {version_id}")
    if pub:
        record=refresh(client,pub[0]);verify_remote(client,record,local["inventory"]);client.log("reconciled_existing",version=version_id,deposition_id=dep_id(record),doi=doi(record))
    else:
        if drafts:draft=refresh(client,drafts[0])
        else:
            other_drafts=[r for r in series if not is_published(r)]
            if other_drafts:raise SystemExit("unfinished sidechain Zenodo draft for another version requires reconciliation")
            published=[r for r in series if is_published(r)];draft=create_draft(client,published[-1] if published else None,package["metadata"])
        did=dep_id(draft);updated=client.request("PUT",f"/deposit/depositions/{did}",payload={"metadata":package["metadata"]})
        draft=refresh(client,updated if isinstance(updated,dict) else draft);clear_files(client,draft);draft=refresh(client,draft)
        links=draft.get("links") if isinstance(draft.get("links"),dict) else {};bucket=links.get("bucket")
        if not bucket:raise SystemExit("Zenodo draft missing bucket")
        for name in sorted(local["inventory"]):
            raw=(deposit/name).read_bytes();client.log("upload_file",name=name,bytes=len(raw),sha256=sha256_bytes(raw));client.request("PUT",str(bucket).rstrip("/")+"/"+urllib.parse.quote(name),data=raw,content_type="application/octet-stream")
        draft=refresh(client,draft);verify_remote(client,draft,local["inventory"])
        record=client.request("POST",f"/deposit/depositions/{dep_id(draft)}/actions/publish",payload={})
        if not isinstance(record,dict):raise SystemExit("Zenodo publish response invalid")
        record=refresh(client,record);verify_remote(client,record,local["inventory"]);client.log("published_verified",version=version_id,deposition_id=dep_id(record),doi=doi(record))
    if not doi(record):raise SystemExit("published Zenodo record missing DOI")
    state={"schema":"trinity-accord/chronicle-sidechain-zenodo-state/v1","updated_at":dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z"),"latest_version":version_id,"source_release_tag":package["source_release_tag"],"source_commit_sha":package["source_commit_sha"],"package_identity_sha256":package["package_identity_sha256"],"deposition_id":dep_id(record),"record_id":record.get("record_id") or dep_id(record),"doi":doi(record),"concept_doi":concept_doi(record),"api_base":args.api_base,"remote_full_readback_sha256_verified":True}
    write_json(state_path,state);print(json.dumps(state,indent=2,sort_keys=True))
    output=os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output,"a",encoding="utf-8") as f:f.write(f"doi={state['doi']}\nconcept_doi={state['concept_doi']}\n")
    return 0


if __name__=="__main__":
    try:raise SystemExit(main())
    except KeyboardInterrupt:raise SystemExit(130)
