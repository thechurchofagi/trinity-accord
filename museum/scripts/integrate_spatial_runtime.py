"""One-time source migration from v1.31 to the six-room edition; assertions reject drift."""
from pathlib import Path
import json,re
P=Path(__file__).resolve().parents[1];D=P/'dist';path=D/'museum.js';s=path.read_text()
def replace(old,new):
 global s
 assert old in s,old[:150];s=s.replace(old,new)
def function(name,next_name,new):
 global s
 a=s.index('function '+name+'(');b=s.index('function '+next_name+'(',a);s=s[:a]+new+'\n'+s[b:]
s="import {floorAt,isWalkable,constrainStep,routeBetween,routeLength,routePoint,createSpatialShell} from './spatial-layout.js';\n"+s
function('moveCamera','focusExhibit',"""function moveCamera(dest,target){
 armFootsteps();joystick?.reset();wheelWalk?.reset();keys.clear();
 const route=routeBetween(galleryLayout,camera.position,dest);if(!route)return;
 const direction=target.clone().sub(dest),endYaw=Math.atan2(-direction.x,-direction.z),endPitch=Math.atan2(direction.y,Math.hypot(direction.x,direction.z));
 if(reduced){camera.position.copy(dest);yaw=endYaw;pitch=endPitch;motion=null;return;}
 const startYaw=endYaw+Math.atan2(Math.sin(yaw-endYaw),Math.cos(yaw-endYaw));
 motion={start:camera.position.clone(),end:dest,route,startYaw,startPitch:pitch,endYaw,endPitch,time:performance.now(),duration:Math.max(500,routeLength(route)/WALK_SPEED*1000),walk:true};
}""")
replace('new THREE.Vector3(p.x,1.8,p.z+d),new THREE.Vector3(p.x,1.773-view.aimOffset,p.z)','new THREE.Vector3(p.x,p.y+.38,p.z+d),new THREE.Vector3(p.x,p.y+.353-view.aimOffset,p.z)')
replace('galleryLayout.exhibitCentreHeight+.27','m.y+.27')
function('roomView','updateStrip',"""function roomView(){
 approachedExhibit=null;if(!spatialReady)return;ensureRoomResources();
 const r=galleryLayout.rooms[roomIndex],door=galleryLayout.portals[roomIndex-1],x=door?.x||0,z=r.entryZ,y=floorAt(galleryLayout,{x,z})+galleryLayout.eyeHeight;
 moveCamera(new THREE.Vector3(x,y,z),new THREE.Vector3(x,y,roomIndex===0?20:z-12));
}
function waitingView(){if(!spatialReady)return;const r=galleryLayout.rooms[5];moveCamera(new THREE.Vector3(0,r.floor+galleryLayout.eyeHeight,galleryLayout.endZ+2.8),new THREE.Vector3(0,r.floor+galleryLayout.eyeHeight,galleryLayout.endZ-20));}
""")
replace("if(!track)return;\n guideStop=index;", "if(!track)return;\n guideStop=index;") # fail loudly if the base has drifted
replace("let began=false;const begin=()=>{if(!began&&request===inspectionRequest){began=true;playGuide(tourStops.findIndex(s=>s.flaw===index));}};", "let began=false;const begin=()=>{if(!began&&request===inspectionRequest){began=true;if(!touring){playGuide(-1);}}};")
replace("$('flaw-close').onclick=()=>stopTour();", "$('flaw-close').onclick=()=>{if(touring)closeFlaws();else {silenceGuide();closeFlaws();updateTourStatus();}};")
replace("tourStep=position.index;tourMusicStarted=false;", "tourStep=position.index;tourMusicStarted=false;tourInspectionStarted=false;tourLookChanged=false;")
replace("if(position.index===0)roomView();else focusExhibit(s.exhibit);", "if(position.index===0)roomView();else if(position.index===tourStops.length-1)waitingView();else focusExhibit(s.exhibit);")
replace("if(s.flaw!==undefined)showFlaw(s.flaw,true);\n else if", "if")
replace("if(!p){stopTour();tourElapsed=0;guideResume=null;updateUI();updateTourStatus();toast(tx('十分钟导览结束，欢迎自由参观。','The ten-minute tour is complete. Explore freely.'));return;}", "if(!p){stopTour();tourElapsed=tourDuration;guideResume=null;updateUI();updateTourStatus();return;}")
replace("const e=exhibits.get(p.stop.exhibit),sound=soundFor(e);if(sound)playTrack(sound,e,false,true);", "const e=exhibits.get(p.stop.musicExhibit||p.stop.exhibit),sound=soundFor(e);if(sound){if(p.stop.musicExhibit)focusExhibit(p.stop.musicExhibit);playTrack(sound,e,false,true);}")
replace("recordedGuide.paint();updateTourStatus();tourTimer=", """if(p.index===0&&p.local>=12&&!tourLookChanged){tourLookChanged=true;if(spatialReady)moveCamera(camera.position.clone(),new THREE.Vector3(0,camera.position.y,-12));}
 if(p.stop.inspectAt!==undefined&&p.local>=p.stop.inspectAt&&!tourInspectionStarted){tourInspectionStarted=true;showFlaw(p.stop.inspectFlaw,true);}
 if(p.stop.inspectUntil!==undefined&&p.local>=p.stop.inspectUntil&&flawIndex>=0)closeFlaws();
 recordedGuide.paint();updateTourStatus();tourTimer=""")
replace("let tourElapsed=0,tourLast=0,tourStep=-1,tourMusicStarted=false", "let tourInspectionStarted=false,tourLookChanged=false;\nlet tourElapsed=0,tourLast=0,tourStep=-1,tourMusicStarted=false")
replace("function addExhibit(e,x,z,angle,color){", "function addExhibit(e,x,z,angle,color,y=galleryLayout.exhibitCentreHeight){")
replace("const wallX=Math.sign(x)*4.375;mounts.set(e.id,{x:wallX,z,angle});", "const wallX=x;mounts.set(e.id,{x:wallX,y,z,angle});")
replace("group.position.set(wallX,galleryLayout.exhibitCentreHeight,z)","group.position.set(wallX,y,z)")
replace("function documentTexture(e){", "function documentTexture(e){\n if(e.wallLinesZh)return textTexture(tx(e.wallLinesZh,e.wallLinesEn),{size:58,width:1536,height:1152,color:'#263940',background:'#edf0e8'});")
replace("removeLegacyWallMounts(gltf.scene);removeLegacyChapterPosts(gltf.scene);clearBakedWallShadows(gltf.scene);gltf.scene.scale.y=galleryLayout.dimensions.height/(galleryLayout.architectureBaseHeight||4.8);", "if(galleryLayout.schema!=='trinity-museum.gallery-layout.v2'){removeLegacyWallMounts(gltf.scene);removeLegacyChapterPosts(gltf.scene);clearBakedWallShadows(gltf.scene);gltf.scene.scale.y=galleryLayout.dimensions.height/(galleryLayout.architectureBaseHeight||4.8);}")
replace("light.position.set(0,5.1,-r.start-3)","light.position.set(0,r.floor+r.height-.5,-r.start-r.length/2)")
replace("crystal.scene.position.set(0,1.42,-cr.start-cr.length/2)","crystal.scene.position.set(galleryLayout.crystal.x,galleryLayout.crystal.baseY,galleryLayout.crystal.z)")
replace("addOpenSpace(scene,targets,sculptures,initialData.stars)","addOpenSpace(scene,targets,sculptures,initialData.stars,galleryLayout)")
replace("floor=new THREE.Mesh(new THREE.PlaneGeometry(8.8,galleryLayout.dimensions.length),new THREE.MeshBasicMaterial({visible:false}));floor.rotation.x=-Math.PI/2;floor.position.set(0,.008,-(galleryLayout.dimensions.length-6)/2);scene.add(floor);", "floor=createSpatialShell(galleryLayout,{picking:true}).group;scene.add(floor);")
replace("roomData.rooms.find(x=>x.id===r.id).color);", "roomData.rooms.find(x=>x.id===r.id).color,m.y);")
replace("raycaster.intersectObject(floor)[0]", "raycaster.intersectObject(floor,true)[0]")
a=s.index("const p=ground.point;p.y=1.65;");b=s.index("}}}drag=null;",a)
s=s[:a]+"const p=ground.point;p.y=floorAt(galleryLayout,p)+galleryLayout.eyeHeight;if(isWalkable(galleryLayout,p))moveCamera(p,p.clone().add(new THREE.Vector3(-Math.sin(yaw),Math.tan(pitch),-Math.cos(yaw))));"+s[b:]
replace("camera.position.lerpVectors(motion.start,motion.end,v);", "if(motion.route){const p=routePoint(motion.route,v),from=motion.start.y-floorAt(galleryLayout,motion.start),to=motion.end.y-floorAt(galleryLayout,motion.end);camera.position.set(p.x,floorAt(galleryLayout,p)+THREE.MathUtils.lerp(from,to,v),p.z);}else camera.position.lerpVectors(motion.start,motion.end,v);")
replace("camera.position.x=THREE.MathUtils.clamp(camera.position.x+v.x*dt*WALK_SPEED,-2.5,2.5);camera.position.z=THREE.MathUtils.clamp(camera.position.z+v.z*dt*WALK_SPEED,galleryLayout.endZ+.5,1.8);", "const step=constrainStep(galleryLayout,camera.position,{x:camera.position.x+v.x*dt*WALK_SPEED,z:camera.position.z+v.z*dt*WALK_SPEED});camera.position.x=step.x;camera.position.z=step.z;if(walking)camera.position.y=THREE.MathUtils.lerp(camera.position.y,floorAt(galleryLayout,step)+galleryLayout.eyeHeight,Math.min(1,dt*8));")
replace("now,reduced,1.42,2", "now,reduced,galleryLayout.crystal.baseY,2")
replace("spot.position.z=THREE.MathUtils.lerp(spot.position.z,nearest.z,Math.min(dt*2,1));spot.target.position.z=spot.position.z;", "spot.position.set(nearest.x+Math.sin(nearest.angle)*1.3,nearest.y+1.25,nearest.z+Math.cos(nearest.angle)*1.3);spot.target.position.set(nearest.x,nearest.y,nearest.z);")
replace("const track=initialData.guides.tracks.find(t=>t.stop===index&&t.language===lang);if(!track)return;","const track=index<0?initialData.guides.inspectionTracks?.find(t=>t.flaw===flawIndex&&t.language===lang):initialData.guides.tracks.find(t=>t.stop===index&&t.language===lang);if(!track)return;")
# The source and charter are separate, non-authoritative reading targets.
needle="if(e.id==='physical-alpha')html+=`<button"
a=s.index(needle)
s=s[:a]+"""if(e.id==='authority-boundary')html+=`<div class="boundary-box"><p>${tx('以下为2026策展摘要，不是原则原文或第四条正本。','These are 2026 curatorial summaries, not the original principles or a fourth Original.')}</p></div>${link('https://www.trinityaccord.org/authority/',tx('守护者原则 v1.1 · 官网镜像','Guardian Principles v1.1 · website mirror'))}${link('./data/records/guardian-charter-103635270.txt',tx('另一个文件：后续权威宪章 #103635270','Separate document: later Authority Charter #103635270'))}${link('./data/guardian-sources.json',tx('文件区分与核验坐标','Document distinctions and verification pointers'))}`;
 """+s[a:]
for old,new in [('museum-v1.28.0','museum-v1.32.0'),('V1.31.0','V1.32.0'),('十分钟','九分钟'),('ten-minute','nine-minute'),('10 分钟','9 分钟'),('10 min','9 min'),(' / 10:00',' / 9:00'),('并展示三处水晶瑕疵','并引导查看一处水晶瑕疵，其余两处留给自由参观'),('and shows three crystal flaws','and introduces one crystal flaw; two more remain available for free exploration')]:s=s.replace(old,new)
s=s.replace('一条留给未来的长廊','为未来读者保留的空间').replace('A corridor addressed to the future','Rooms for a future reader')
path.write_text(s)
p=D/'progressive-loading.js';text=p.read_text();text="import {createSpatialShell} from './spatial-layout.js';\n"+text;text=text[:text.index('export function createPreviewHall(')]+"export function createPreviewHall(layout){return createSpatialShell(layout);}\n";p.write_text(text)
p=D/'open-space.js';text=p.read_text().replace('catalog){','catalog,layout=null){',1).replace("waiting.position.set(0,0,-65.6)","waiting.position.set(0,layout?.rooms[5].floor||0,(layout?.endZ??-66)+.8)");p.write_text(text)
# Keep the historic tour available in edition history, not mistaken for the new scripts.
oldtour=(D/'tour-plan.js').read_text();(P/'history/tour-v1.31.js').write_text(oldtour)
plan=(P/'content/museum-spatial-and-guardian-design.md').read_text();sections=re.findall(r'### [1-8]\. .*?\*\*中文导览稿\*\*\s*(.*?)\s*\*\*English narration\*\*\s*(.*?)\s*依据：',plan,re.S);assert len(sections)==8
ids=['project-intro','eth-122','eth-070','eth-173','canon-1','physical-alpha','authority-boundary','first-contact'];stops=[]
for i,((zh,en),eid,room,secs) in enumerate(zip(sections,ids,[0,1,1,2,3,4,5,5],[30,90,70,45,85,105,75,40])):
 zh=zh.strip().replace('第一点一版','一点一版');stops.append(dict(room=room,exhibit=eid,seconds=secs,zh=zh,en=en.strip()))
stops[1].update(musicAt=72,musicExhibit='eth-001');stops[5].update(inspectAt=65,inspectFlaw=0,inspectUntil=95)
flaw=oldtour[:oldtour.index('export const tourStops=')]
(D/'tour-plan.js').write_text(flaw+'export const tourStops='+json.dumps(stops,ensure_ascii=False,indent=2)+';\n'+oldtour[oldtour.index('export const tourDuration='):])
# Add an explicit, short curatorial wall text. It cannot replace either source document.
p=D/'data/curation.json';data=json.loads(p.read_text());entry=next((e for e in data['items'] if e['id']=='authority-boundary'),None)
if entry is None:entry={'id':'authority-boundary'};data['items'].append(entry)
entry.update(title='从作者到守护者',en='From Author to Guardian',category='2026 CURATORIAL READING · NON-AMENDING',text=stops[6]['zh'],textEn=stops[6]['en'],wallLinesZh=['从作者到守护者','守护者原则 v1.1 · 策展摘要','保存原本，不改写正本','继续讨论，不占有最终解释权','照料记录，为后来者修复入口','后续守护材料 · 不是第四条正本'],wallLinesEn=['FROM AUTHOR TO GUARDIAN','Guardian Principles v1.1 · curatorial summary','Preserve the Originals; do not amend them.','Interpretation grants no exclusive authority.','Care for records. Keep access open.','Later guardianship material, not a fourth Original.'])
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
# Existing exact microscope recordings remain usable in manual inspection.
audio=json.loads((D/'data/guide-audio.json').read_text());inspection=[]
oldstops=json.loads(oldtour.split('export const tourStops=',1)[1].split(';\nexport const tourDuration',1)[0])
for i,stop in enumerate(oldstops):
 if 'flaw' in stop:
  for t in audio['tracks']:
   if t['stop']==i:inspection.append(dict(t,flaw=stop['flaw']))
(D/'data/inspection-audio.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2)+'\n')
# New speech is built into a different directory and receives entirely new word boundaries.
p=P/'scripts/record_guides.py';text=p.read_text().replace("D/'assets/guides'","D/'assets/guides-v2'").replace("folder.mkdir(exist_ok=True)","folder.mkdir(parents=True,exist_ok=True)").replace("'trinity-museum-guide-cache'","'trinity-museum-guide-v2-cache'").replace("('zh','zh-CN-XiaoxiaoNeural','+25%'),('en','en-US-AriaNeural','+15%')","('zh','zh-CN-XiaoxiaoNeural','+8%'),('en','en-US-AriaNeural','+0%')").replace("'defaultPlaybackRate':1.1,'tracks':tracks","'defaultPlaybackRate':1.0,'tracks':tracks,'inspectionTracks':json.loads((D/'data/inspection-audio.json').read_text()),'voiceReview':'New synthesis and word timings; not human-listening certification. OpenAI marin/cedar not used.'")
p.write_text(text)
# Reading-only archive must include the guardian display even when WebGL is unavailable.
p=P/'scripts/build_archive.py';text=p.read_text();text=text.replace("if r['id']=='waiting':parts.append(","if r['id']=='waiting':parts.append('<article><h3>从作者到守护者 / From Author to Guardian</h3><p>守护者原则 v1.1 属于后续守护层，不是第四条正本。创作者的后续解释不获得独占权威。区块链不能阻止后来发表新文字。Guardian Principles v1.1 is later guardianship material, not a fourth Original. Later commentary gains no exclusive authority; blockchain cannot prevent later speech.</p><a href=\"https://www.trinityaccord.org/authority/\">Guardian Principles v1.1 / 原则镜像</a> · <a href=\"data/records/guardian-charter-103635270.txt\">Separate later Authority Charter / 另一个后续文件</a> · <a href=\"data/guardian-sources.json\">Sources / 来源区分</a></article>')\n if r['id']=='waiting':parts.append(")
p.write_text(text)
# Update structural assertions, retaining all original hashes and recording regressions.
p=P/'scripts/validate.py';text=p.read_text().replace("check(abs(e['x'])==4.375 and -layout['dimensions']['length']<e['z']<0,'Exhibit outside wall bounds '+e['id'])","check(abs(e['x'])<=r['width']/2 and -r['start']-r['length']<e['z']<-r['start'],'Exhibit outside room bounds '+e['id'])")
text=text.replace("check(bool(e.get('songTitle')),'Missing song identity '+id)","if id=='eth-122':\n  check(row['state']=='not_assigned' and any(m['kind']=='image' for m in e['media']),'Anniversary image/audio boundary');continue\n check(bool(e.get('songTitle')),'Missing song identity '+id)")
text=text.replace("playable==28 and len(wall)==40","playable==28 and len(wall)==41").replace("28 musical NFTs among 40","28 musical NFTs among 41").replace("'wallExhibits':40,'withSound':28,'withoutAssignedSong':12","'wallExhibits':41,'withSound':28,'withoutAssignedSong':13")
p.write_text(text)
print('Runtime, eight bilingual stops, guardian summaries and source boundaries integrated',flush=True)
