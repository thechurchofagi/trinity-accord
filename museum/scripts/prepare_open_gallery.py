"""Upgrade the existing exhibition layout without moving or rewriting source exhibits."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];D=P/'dist';EDITION='museum-v1.34.0'
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
layout=json.loads((D/'data/gallery-layout.json').read_text())
if layout.get('edition')==EDITION:
 print('Open gallery layout already prepared.');raise SystemExit(0)
parts=[]
for p in layout['architecture']:
 if p.get('floor') or p['name'] in ['Portal shoulder','Portal lintel','Portal metal reveal','Door light']:continue
 depth=-p.get('position',[0,0,0])[2]
 offset=.35 if depth>=40 else 0
 if p.get('vertices'):
  if any(p['name'].startswith(k) for k in ['originals','waiting']):
   for v in p['vertices']:v[1]-=.35
 elif p.get('position'):p['position'][1]-=offset
 if p['material']=='gold':
  p['size'][2]=.24
  if 'jamb' in p['name']:p['size'][0]=.20;p['position'][0]=(-1 if p['position'][0]<0 else 1)*5.90
  elif 'sill' in p['name']:p['size'][1]=.20;p['position'][1]=.10
  elif 'head' in p['name']:p['size'][1]=.20;p['position'][1]=5.90
 parts.append(p)
for r in layout['rooms']:
 offset=r['floor'];r['floor']=0
 for m in r['exhibits']:m['y']-=offset
 poly=r['footprint'];parts.append(dict(name=r['id']+' level tiled floor',vertices=[[x,0,-z] for x,z in poly],indices=[v for i in range(1,len(poly)-1) for v in [0,i,i+1]],material='stone',floor=True))
for d in layout['portals']:
 d.update(visualOnly=True,x=0)
 # The dodecagonal Originals hall has a naturally narrower footprint at its ends.
 width={6:9,30:8,40:3.75,54:3.75}[d['depth']];d['width']=width
 for x in [-width/2+.04,width/2-.04]:parts.append(dict(name='Light boundary edge',position=[x,1.75,-d['depth']],size=[.018,3.5,.018],material='boundary',floor=False,passThrough=True))
 parts.append(dict(name='Light boundary threshold',position=[0,.009,-d['depth']],size=[width,.008,.035],material='boundary',floor=False,passThrough=True))
 parts.append(dict(name='Light boundary canopy',position=[0,3.5,-d['depth']],size=[width,.014,.014],material='boundary',floor=False,passThrough=True))
layout.update(edition=EDITION,ramp=None,architecture=parts)
layout['crystal']['baseY']=layout['crystal']['pedestalHeight']
layout['runtimeAdaptation']='Level tile floors; pass-through luminous room boundaries. Shared geometry drives export, preview and walking.'
layout['materials'].update(stone=dict(color='#d9d5c9',roughness=.78),plaster=dict(color='#c4c2b9',roughness=.93),dark=dict(color='#767e7d',roughness=.94),gold=dict(color='#c8ac6e',roughness=.34,metalness=1),boundary=dict(color='#b0e7ef',emission=True,opacity=.38))
for p in [D/'data/gallery-layout.json',P/'scene/gallery-layout.json']:save(p,layout)
for name in ['rooms.json','sources.json','audio-audit.json','crystal-model.json','curation.json','space-design.json']:
 p=D/'data'/name;d=json.loads(p.read_text());d['edition']=EDITION
 if name=='rooms.json':
  for r in d['rooms']:r['floor']=0
 save(p,d)
print('Prepared level floors, four pass-through light boundaries, restrained gold frame.')
