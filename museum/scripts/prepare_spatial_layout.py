"""Author six rooms from one geometry plan, shared by Blender, preview and navigation."""
from pathlib import Path
import json,math
P=Path(__file__).resolve().parents[1];D=P/'dist';EDITION='museum-v1.32.0'
def read(name):return json.loads((D/'data'/name).read_text())
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
rooms=read('rooms.json');layout=read('gallery-layout.json');architecture=[]
widths=[9,9,8,14,9,12];lengths=[6,24,10,14,9,9];heights=[5,5,4.5,8,5,6]
layout.update(schema='trinity-museum.gallery-layout.v2',edition=EDITION,dimensions=dict(width=14,length=72,height=8),architectureBaseHeight=8,eyeHeight=1.65,endZ=-72,ramp=dict(start=35.8,end=40,width=2.8,rise=.35),crystal=dict(x=0,z=-58.5,baseY=1.77),portals=[dict(depth=d,x=x,width=w) for d,x,w in [(6,0,3.2),(30,-1,3.2),(40,0,2.8),(54,0,2.8),(63,1,3.2)]])
layout['runtimeAdaptation']='No scale adaptation: shared per-room floor, portal and architecture geometry. All measurements are later exhibition design.'
layout['materials']={'plaster':dict(color='#d5d4ce'),'stone':dict(color='#777d7c',roughness=.92),'dark':dict(color='#4b5155'),'metal':dict(color='#64747b',roughness=.4,metalness=.65),'light':dict(color='#dae6e9',emission=True)}
def box(name,pos,size,mat='plaster',yaw=0,floor=False):architecture.append(dict(name=name,position=pos,size=size,material=mat,rotationY=yaw,floor=floor))
def surface(name,points,y,mat='stone',ceiling=False):
 verts=[[x,y,-z] for x,z in points];idx=[]
 for i in range(1,len(verts)-1):idx.extend([0,i+1,i] if ceiling else [0,i,i+1])
 architecture.append(dict(name=name,vertices=verts,indices=idx,material=mat,floor=not ceiling))
def wall_segment(a,b,y,h,mat='plaster',name='Wall'):
 dx=b[0]-a[0];dz=b[1]-a[1];box(name,[(a[0]+b[0])/2,y+h/2,-(a[1]+b[1])/2],[math.hypot(dx,dz),h,.20],mat,math.atan2(dz,dx))
def portal_wall(depth,width,height,y,door):
 left,right=-width/2,width/2;lo,hi=door['x']-door['width']/2,door['x']+door['width']/2
 for a,b in [(left,lo),(hi,right)]:
  if b>a:wall_segment((a,depth),(b,depth),y,height,name='Portal shoulder')
 door_h=3.7
 box('Portal lintel',[door['x'],y+(door_h+height)/2,-depth],[door['width'],max(.12,height-door_h),.24])
 for x in [lo,hi]:box('Portal metal reveal',[x,y+door_h/2,-depth],[.045,door_h,.27],'metal')
 box('Door light',[door['x'],y+door_h-.06,-depth],[door['width'],.035,.29],'light')
start=0
for i,(r,rr) in enumerate(zip(layout['rooms'],rooms['rooms'])):
 w,l,h=widths[i],lengths[i],heights[i];f=.35 if i>=3 else 0
 r.update(width=w,length=l,height=h,start=start,floor=f,entryZ=-start-1.1)
 if i==3:
  rad=7/math.cos(math.pi/12);poly=[[round(rad*math.cos(math.pi/12+k*math.pi/6),6),round(start+7+rad*math.sin(math.pi/12+k*math.pi/6),6)] for k in range(12)]
 else:poly=[[-w/2,start],[w/2,start],[w/2,start+l],[-w/2,start+l]]
 r['footprint']=poly;rr['z']=-start;rr['width']=w;rr['length']=l;rr['height']=h;rr['floor']=f
 ids=[e['id'] for e in r['exhibits']]
 if i==1 and 'eth-122' not in ids:ids.insert(ids.index('eth-146'),'eth-122')
 r['exhibits']=[];rr['exhibits']=ids
 rows=math.ceil(len(ids)/2)
 for j,eid in enumerate(ids):
  side=-1 if j%2==0 else 1;z=-start-1.1-j//2*((l-2.2)/max(1,rows-1));x=side*(w/2-.115);angle=-side*math.pi/2
  if i==3:
   x,z,angle=[(-6.87,-47,math.pi/2),(6.87,-47,-math.pi/2),(-3.4425,-52.962587,math.pi/6)][j]
  if i==2:z=-start-1.5-j//2*2.2
  if i==5:z=-start-2.1-j//2*3.3
  r['exhibits'].append(dict(id=eid,x=round(x,6),z=round(z,6),angle=angle,y=f+layout['exhibitCentreHeight']))
 if i==2:
  surface('Formation floor',[[x,z] for x,z in [[-w/2,start],[w/2,start],[w/2,35.8],[-w/2,35.8]]],0)
  rw=layout['ramp']['width'];a,b=35.8,40
  architecture.append(dict(name='Accessible centre ramp',vertices=[[-rw/2,0,-a],[rw/2,0,-a],[rw/2,.35,-b],[-rw/2,.35,-b]],indices=[0,1,2,0,2,3],material='stone',floor=True))
  for side in [-1,1]:
   for step in range(3):box('Three shallow side steps',[side*(w+rw)/4,step*.35/3-.07,-(a+(step+.5)*(b-a)/3)],[(w-rw)/2,.14,(b-a)/3],'stone',floor=True)
 else:surface(r['id']+' floor',poly,f)
 surface(r['id']+' ceiling',poly,f+h,'dark' if i in [4,5] else 'plaster',True)
 for a,b in zip(poly,poly[1:]+poly[:1]):
  # Room ends receive portals, or an open observation window, below.
  if abs(a[1]-b[1])<1e-5 and (abs(a[1]-start)<1e-5 or abs(a[1]-start-l)<1e-5):continue
  wall_segment(a,b,f,h,'dark' if i in [4,5] else 'plaster',r['id']+' wall')
  dx=b[0]-a[0];dz=b[1]-a[1]
  box('Recessed edge light',[(a[0]+b[0])/2,f+h-.15,-(a[1]+b[1])/2],[max(.1,math.hypot(dx,dz)-.3),.028,.055],'light',math.atan2(dz,dx))
 if i>0:
  d=layout['portals'][i-1];portal_wall(start,w if i!=3 else 3.751289,max(h,(heights[i-1]+(0.35 if i-1>=3 else 0))-f),f,d)
 # Close width changes at the far boundary outside the narrower next room.
 if i<5 and w>widths[i+1]:
  nw=widths[i+1]
  for side in [-1,1]:wall_segment((side*nw/2,start+l),(side*w/2,start+l),f,h,'dark' if i==4 else 'plaster','Width transition')
 if i in [0,5]:
  depth=0 if i==0 else 72
  for side in [-1,1]:box('Observation window jamb',[side*(w/2-.35),f+h/2,-depth],[.7,h,.65],'metal')
  box('Observation window sill',[0,f+.25,-depth],[w,.5,.65],'metal');box('Observation window head',[0,f+h-.35,-depth],[w,.7,.65],'metal')
 if i==1:
  for depth in range(8,30,4):box('Chronicle ceiling segment',[0,h-.12,-depth],[w-.2,.08,.06],'metal')
 start+=l
layout['architecture']=architecture
rooms['edition']=EDITION;rooms['updated']='2026-09-08'
rooms['rooms'][5]['featuredExhibit']='authority-boundary'
write(D/'data/rooms.json',rooms);write(D/'data/gallery-layout.json',layout);write(P/'scene/gallery-layout.json',layout)
for name in ['sources.json','audio-audit.json','crystal-model.json','curation.json']:
 data=read(name);data['edition']=EDITION;write(D/'data'/name,data)
print('Prepared six rooms, 72m route, shared architecture primitives:',len(architecture),flush=True)
