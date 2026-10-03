"""Read-only recovery of a linked draft when legacy latest_draft is stale."""
import json
import publication as p

z=p.client()
old=p.read(z,f'/deposit/depositions/{p.PREVIOUS_RECORD}')
concept=str(old.get('conceptrecid'))
def safe(d):
    md=d.get('metadata',{})
    return {'id':d.get('id'),'conceptrecid':d.get('conceptrecid'),
            'submitted':d.get('submitted'),'title':md.get('title'),
            'version':md.get('version'),'creators':[c.get('name') for c in md.get('creators',[])],
            'doi':d.get('doi') or md.get('prereserve_doi'),
            'links':{k:v for k,v in d.get('links',{}).items() if k in ('self','latest_draft','latest','record','record_html')}}
print(json.dumps({'predecessor':safe(old)},indent=2))
matches=[]
for page in (1,2,3):
    rows=p.read(z,f'/deposit/depositions?status=draft&sort=mostrecent&size=100&page={page}')
    if not isinstance(rows,list):raise RuntimeError('Unexpected deposition listing shape')
    for d in rows:
        md=d.get('metadata',{})
        if str(d.get('conceptrecid'))==concept or md.get('title')==p.TITLE:
            matches.append(safe(p.read(z,f"/deposit/depositions/{d['id']}")))
    if len(rows)<100:break
print(json.dumps({'read_only':True,'matching_drafts':matches},indent=2))
