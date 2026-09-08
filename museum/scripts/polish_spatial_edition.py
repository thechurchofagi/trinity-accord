"""Idempotent staging refinement. Original media and evidence are never modified."""
from pathlib import Path
import json,math
P=Path(__file__).resolve().parents[1];D=P/'dist'
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
L=read(D/'data/gallery-layout.json');A=L['architecture']
if L.get('stagingRevision')==2:raise SystemExit('Staging revision 2 already applied')
L['stagingRevision']=2
L['portals'][-1].update(x=2.65,width=2.6)
colours=[('#bfc7c5','#38464b','#7a898b'),('#c8c6bc','#394349','#7a8688'),('#899798','#2b393f','#4c5c64'),('#81949c','#24343f','#233743'),('#233c4a','#172c38','#172b39'),('#203441','#13242e','#0f1e28')]
for i,(wall,floor,ceiling) in enumerate(colours):
 for name,colour in [('wall',wall),('floor',floor),('ceiling',ceiling)]:L['materials'][f'{name}{i}']=dict(color=colour,roughness=.9)
L['materials']['light'].update(color='#b4ced2');L['materials']['metal'].update(color='#3f5863',roughness=.5)
A[:]=[a for a in A if a['name'] not in ['Portal shoulder','Portal lintel','Portal metal reveal','Door light','Width transition']]
for a in A:
 name=a['name']
 for i,r in enumerate(L['rooms']):
  if name==r['id']+' wall':a['material']=f'wall{i}'
  elif name==r['id']+' ceiling':a['material']=f'ceiling{i}'
  elif name==r['id']+' floor' or (i==2 and name in ['Formation floor','Accessible centre ramp','Three shallow side steps']):a['material']=f'floor{i}'
 if name=='Three shallow side steps':a['position'][1]+=.35/3
 if name=='Observation window sill':a['material']='metal'
def box(name,pos,size,mat='metal',yaw=0):A.append(dict(name=name,position=pos,size=size,material=mat,rotationY=yaw,floor=False))
def end_width(r,depth):
 xs=[p[0] for p in r['footprint'] if abs(p[1]-depth)<1e-5];return max(xs)-min(xs)
# Close both footprints at every boundary, not only the smaller doorway wall.
for i,d in enumerate(L['portals']):
 left,right=L['rooms'][i:i+2];depth=d['depth'];w=max(end_width(left,depth),end_width(right,depth));bottom=min(left['floor'],right['floor']);top=max(left['floor']+left['height'],right['floor']+right['height']);lo=d['x']-d['width']/2;hi=d['x']+d['width']/2;doorTop=right['floor']+3.7
 for a,b in [(-w/2,lo),(hi,w/2)]:
  if b>a:box('Portal shoulder',[(a+b)/2,(bottom+top)/2,-depth],[b-a,top-bottom,.24],f'wall{i+1}')
 box('Portal lintel',[d['x'],(doorTop+top)/2,-depth],[d['width'],top-doorTop,.24],f'wall{i+1}')
 for x in [lo,hi]:box('Portal metal reveal',[x,(doorTop+right['floor'])/2,-depth],[.055,3.7,.30])
 box('Door light',[d['x'],doorTop-.08,-depth],[d['width']-.1,.025,.30],'light')
for i,r in enumerate(L['rooms']):
 poly=r['footprint']
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if abs(a[1]-b[1])<1e-5 and any(abs(a[1]-v)<1e-5 for v in [r['start'],r['start']+r['length']]):continue
  dx=b[0]-a[0];dz=b[1]-a[1];box('Recessed skirting',[(a[0]+b[0])/2,r['floor']+.055,-(a[1]+b[1])/2],[math.hypot(dx,dz),.11,.22],'metal',math.atan2(dz,dx))
 for e in r['exhibits']:
  if e['id'].startswith('canon-'):e.update(y=2.5,displayWidth=3.0,displayHeight=2.25)
  elif e['id']=='authority-boundary':e.update(y=2.35,displayWidth=2.5,displayHeight=1.875)
box('Crystal low plinth',[0,.46,L['crystal']['z']],[.82,.22,.82],'metal')
for p in [D/'data/gallery-layout.json',P/'scene/gallery-layout.json']:write(p,L)
p=D/'tour-plan.js';s=p.read_text();start=s.index('export const tourStops=')+len('export const tourStops=');end=s.index(';\nexport const tourDuration',start);stops=json.loads(s[start:end]);stops[1],stops[2]=stops[2],stops[1]
for stop,seconds in zip(stops,[30,70,70,55,100,100,75,40]):
 stop['seconds']=seconds;stop.pop('musicAt',None);stop.pop('musicExhibit',None)
stops[1].update(musicAt=55,musicExhibit='eth-049');stops[4]['cameraShots']=[dict(at=45,exhibit='canon-2'),dict(at=68,exhibit='canon-3')];stops[5].update(inspectAt=60,inspectUntil=85)
p.write_text(s[:start]+json.dumps(stops,ensure_ascii=False,indent=2)+s[end:])
p=D/'data/guide-audio.json';guides=read(p)
for t in guides['tracks']:
 if t['stop']==1:t['stop']=2
 elif t['stop']==2:t['stop']=1
write(p,guides)
p=D/'spatial-layout.js';s=p.read_text().replace('Math.floor(t*3)','Math.ceil(t*3)');p.write_text(s)
p=P/'scene/build_spatial_gallery.py';s=p.read_text().replace('s.cycles.samples=24','s.cycles.samples=48').replace('default_value=.4','default_value=.16').replace("rgb=tuple(int(defn['color'][i:i+2],16)/255 for i in (1,3,5))","srgb=tuple(int(defn['color'][i:i+2],16)/255 for i in (1,3,5));rgb=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in srgb)").replace('default_value=2\n materials','default_value=1.1\n materials').replace("data.energy=700 if r['id'] not in ['material','waiting'] else 380","data.energy=520 if r['id'] not in ['material','waiting'] else 130")
s=s.replace('atlas.pack()',"""atlas.pack()
saved_location=cam.location.copy();saved_rotation=cam.rotation_euler.copy();cam.location=(0,-10,2);aim(cam,(0,-20,2));s.view_settings.view_transform='Standard';s.use_nodes=True;nodes=s.node_tree.nodes;nodes.clear();image=nodes.new('CompositorNodeImage');image.image=atlas;denoise=nodes.new('CompositorNodeDenoise');denoise.use_hdr=True;output=nodes.new('CompositorNodeComposite');s.node_tree.links.new(image.outputs['Image'],denoise.inputs['Image']);s.node_tree.links.new(denoise.outputs['Image'],output.inputs['Image']);s.render.resolution_x=2048;s.render.resolution_y=2048;s.render.filepath=str(O/'spatial-light-denoised.png');bpy.ops.render.render(write_still=True);s.use_nodes=False;s.view_settings.view_transform='AgX';cam.location=saved_location;cam.rotation_euler=saved_rotation
clean=bpy.data.images.load(str(O/'spatial-light-denoised.png'),check_existing=False);clean.colorspace_settings.name='sRGB';atlas=clean;atlas.pack();s.render.resolution_x=1280;s.render.resolution_y=800
""")
s=s.replace('24 samples; no new artwork','48 samples plus compositor denoising; no new artwork');p.write_text(s)
p=D/'open-space.js';s=p.read_text();a=s.index(' const frame=new THREE.Mesh(new THREE.TorusGeometry');b=s.index(' const c=document.createElement',a)
s=s[:a]+" const frame=new THREE.Mesh(new THREE.BoxGeometry(.8,.9,.24),titanium);frame.position.set(-3,.45,1.3);waiting.add(frame);frame.userData.exhibit='first-contact';targets.push(frame);\n"+s[b:]
s=s.replace('new THREE.PlaneGeometry(3.1,.775)','new THREE.PlaneGeometry(.76,.19)').replace('sign.position.set(0,1.95,.09)','sign.position.set(-3,.78,1.43)');p.write_text(s)
p=D/'crystal-viewer.js';s=p.read_text().replace('strength:{value:.95}','strength:{value:.42}').replace('reduced?.95:.95+.065','reduced?.42:.42+.035');p.write_text(s)
p=D/'museum.js';s=p.read_text()
def rep(a,b):
 global s
 assert a in s,a[:100];s=s.replace(a,b)
rep('let spatialReady=false,selectedExhibit=null,galleryLayout;','let spatialReady=false,selectedExhibit=null,galleryLayout,architecturalOccluder=null;')
rep('const preview=createPreviewHall(galleryLayout);scene.add(preview.group);','const preview=createPreviewHall(galleryLayout);scene.add(preview.group);architecturalOccluder=preview.group;')
rep('scene.add(gltf.scene);gltf.scene.traverse','scene.add(gltf.scene);architecturalOccluder=gltf.scene;gltf.scene.traverse')
rep('const img=imageOf(e),height=img?1.7:1.425;',"const img=imageOf(e),config=galleryLayout.rooms.flatMap(r=>r.exhibits).find(m=>m.id===e.id),width=config?.displayWidth||1.9,height=config?.displayHeight||(img?1.7:1.425);")
rep('mounts.set(e.id,{x:wallX,y,z,angle})','mounts.set(e.id,{x:wallX,y,z,angle,width,height})')
rep('new THREE.PlaneGeometry(1.9,height)','new THREE.PlaneGeometry(width,height)')
rep('if(!img){plane.material.map=documentTexture(e);',"if(!img){for(const child of group.children)if(child!==plane)child.position.y+=Math.max(0,(height-1.425)/2);makeWallFrame(group,width,height);plane.material.map=documentTexture(e);")
rep('observationView(2.05,2.34,camera.fov','observationView((m.width||1.9)+.15,(m.height||1.7)+.66,camera.fov')
a=s.index(" if(id==='physical-alpha')loadCrystal?.();");b=s.index(' const m=mounts.get(id);',a)
s=s[:a]+""" if(id==='physical-alpha'){
  loadCrystal?.();const p={x:galleryLayout.crystal.x,y:galleryLayout.crystal.baseY,z:galleryLayout.crystal.z};
  const view=observationView(.78,1.08,camera.fov,camera.aspect,mobile),d=Math.max(1.5,view.distance);
  moveCamera(new THREE.Vector3(p.x,p.y+.38,p.z+d),new THREE.Vector3(p.x,p.y+.353-view.aimOffset,p.z));return;
 }
"""+s[b:]
a=s.index('function goRoom(');b=s.index('\nlet tourInspectionStarted',a)
s=s[:a]+"""function goRoom(i,keepTour=false){
 if(i<0||i>=roomData.rooms.length)return;if(!keepTour)stopTour();closePanel();roomIndex=i;selectedExhibit=roomData.rooms[i].featuredExhibit||roomData.rooms[i].exhibits[0];hovered=null;$('hover-label').hidden=true;updateUI();history.replaceState(null,'','#'+roomData.rooms[i].id);ensureRoomResources();
 if(spatialReady&&!keepTour){if(i===5)waitingView();else roomView();if(motion){motion.walk=false;motion.duration=reduced?0:1400;}}
}
"""+s[b:]
rep('tourLookChanged=false;silenceGuide()','tourLookChanged=false;tourShotIndex=0;silenceGuide()')
rep('let tourInspectionStarted=false,tourLookChanged=false;','let tourInspectionStarted=false,tourLookChanged=false,tourShotIndex=0;')
rep('if(motion)motion.duration=reduced?0:Math.min(7000,Math.max(2200,motion.duration));','if(motion)motion.duration=reduced?0:Math.min(14000,Math.max(1800,motion.duration));')
rep('if(p.stop.musicExhibit)focusExhibit(p.stop.musicExhibit);playTrack(sound,e,false,true);','playTrack(sound,exhibits.get(p.stop.exhibit),false,true);')
rep('recordedGuide.paint();updateTourStatus();tourTimer=',"if(p.stop.cameraShots&&tourShotIndex<p.stop.cameraShots.length&&p.local>=p.stop.cameraShots[tourShotIndex].at){const shot=p.stop.cameraShots[tourShotIndex++];focusExhibit(shot.exhibit);if(motion)motion.duration=reduced?0:Math.min(10500,motion.duration);}\n recordedGuide.paint();updateTourStatus();tourTimer=")
pos=s.index('function bindNavigation(');s=s[:pos]+"function visibleHit(hit){if(!hit)return false;const wall=architecturalOccluder&&raycaster.intersectObject(architecturalOccluder,true)[0];return !wall||hit.distance<=wall.distance+.035;}\n"+s[pos:]
rep('hovered=hit&&hit.distance<32?','hovered=visibleHit(hit)&&hit.distance<32?')
rep('if(hit&&hit.distance<32)approachExhibit','if(visibleHit(hit)&&hit.distance<32)approachExhibit')
rep('if(ground&&ground.distance<28)','if(visibleHit(ground)&&ground.distance<28)')
rep('yaw=THREE.MathUtils.lerp(motion.startYaw,motion.endYaw??0,v);',"if(motion.route&&motion.walk&&routeLength(motion.route)>3&&v<.83){const a=routePoint(motion.route,v),b=routePoint(motion.route,Math.min(1,v+.02)),heading=Math.atan2(-(b.x-a.x),-(b.z-a.z));yaw+=Math.atan2(Math.sin(heading-yaw),Math.cos(heading-yaw))*Math.min(1,dt*3);}else {const aim=motion.endYaw??0;yaw+=Math.atan2(Math.sin(aim-yaw),Math.cos(aim-yaw))*Math.min(1,dt*4);if(t===1)yaw=aim;}")
s=s.replace('museum-v1.32.0 · 2026-09-07','museum-v1.32.0 · 2026-09-08');p.write_text(s)
p=D/'museum.css';s=p.read_text();s+='\n/* Spatial edition: keep the scene readable without a fixed instruction rail. */\n.room-label{text-shadow:0 1px 12px #000a}\n#hint{display:none}\n';p.write_text(s)
p=P/'scripts/check_exterior.mjs';s=p.read_text().replace("assert.equal(sculptures[0].base,.65);assert.equal(targets.length,3);","assert.equal(sculptures.length,0);assert.equal(targets.length,2);assert.ok(targets.every(t=>t.position.x<0),'Invitation must stay out of the central sky view');");p.write_text(s)
p=P/'scripts/check_guided_visit.mjs';s=p.read_text().replace('const context={spatialReady:false,','const context={tourShotIndex:0,reduced:false,spatialReady:false,').replace("['eth-001',{id:'eth-001'}]","['eth-049',{id:'eth-049'}]");p.write_text(s)
print('STAGING_REVISION_2: six room palettes, offset crystal exit, larger Originals, restrained light, guided views, wall occlusion',flush=True)
