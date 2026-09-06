"""Build the authored corridor in Blender, bake its static light and export glTF.
Run with Blender 4.5.3's bpy Python module. No GUI automation is claimed.
The gallery is later exhibition architecture, not a reconstruction of an artifact.
"""
from pathlib import Path
import bpy, math, json, argparse, hashlib
from mathutils import Vector
from denoise_lightmap import denoise_atlas
P=Path(__file__).resolve().parents[1];OUT=P/'dist/assets/gallery';OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--bake',action='store_true');parser.add_argument('--render-only',action='store_true');parser.add_argument('--samples',type=int,default=24);args=parser.parse_args()
layout=json.loads((P/'scene/gallery-layout.json').read_text());sources=json.loads((P/'dist/data/sources.json').read_text());items={e['id']:e for e in sources['items']}
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=8
scene.world=bpy.data.worlds.new('Quiet daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.34,.43,.55,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.25
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.render.image_settings.file_format='PNG';scene.render.resolution_percentage=100
architecture=[];artworks=[];emissions=[];details=[]
L=layout["dimensions"]["length"];C=(L-6)/2;END=L-3
def mat(name,color,rough=.6,noise=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if noise:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=110;n.inputs['Detail'].default_value=2;b=m.node_tree.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.045;b.inputs['Distance'].default_value=.018;m.node_tree.links.new(n.outputs['Fac'],b.inputs['Height']);m.node_tree.links.new(b.outputs['Normal'],p.inputs['Normal'])
 return m
ivory=mat('Porcelain / satin mineral',(.59,.63,.65),.75,True);white=mat('Matte plaster',(.78,.79,.77),.8,True);floorMat=mat('Graphite stone',(.12,.16,.18),.32,True);metal=mat('Brushed titanium',(.12,.19,.24),.24);metal.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.72;black=mat('Shadow recess',(.018,.026,.032),.8);paper=mat('Archival mount',(.82,.81,.76),.9);frameMat=mat('Satin aluminium frame',(.32,.4,.45),.28)
def emissive(name,color,strength):
 m=mat(name,color);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=strength;return m
warm=emissive('Neutral ceiling diffuser',(.85,.91,1),3);cyan=emissive('Cyan wayfinding',(.22,.68,.9),2)
def cube(name,loc,size,material,bevel=0,group=architecture):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Crafted edge','BEVEL');mod.width=bevel;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 (details if group is architecture and not name.startswith(('Continuous stone','Wall backing','Mineral wall','Suspended ceiling','Entrance back','End wall','Ceiling perimeter','Cove reflector')) else group).append(o);return o
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def area(name,loc,target,power,size=3,color=(.85,.92,1),size_y=None):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='RECTANGLE';data.size=size;data.size_y=size_y or size;data.color=color;o=bpy.data.objects.new(name,data);scene.collection.objects.link(o);o.location=loc;aim(o,target);return o
# Human-scale continuous passage: 8.8 m clear width, 4.8 m ceiling, 52 m length.
cube('Continuous stone floor',(0,C,-.13),(9.2,L,.25),floorMat,.035)
for side in [-1,1]:
 cube('Wall backing',(side*4.55,C,2.4),(.25,L,4.8),black)
 cube('Low recessed skirting',(side*4.43,C,.18),(.1,L,.32),metal,.015)
 cube('Cyan baseline',(side*4.365,C,.075),(.035,L,.025),cyan,0,emissions)
 for i in range(math.ceil(L/4)):
  y=-1+4*i;cube('Mineral wall panel',(side*4.47,y,2.58),(.16,3.965,4.28),white if i%3 else ivory,.016)
 cube('Ceiling perimeter shadow',(side*3.9,C,4.62),(.95,L,.22),black,.02)
 cube('Cove reflector',(side*3.96,C,4.46),(.8,L,.045),ivory,.015)
 cube('Linear cove',(side*3.65,C,4.56),(.1,L,.035),warm,0,emissions)
 cube('Track',(side*2.65,C,4.5),(.055,L,.065),black,.012)
cube('Suspended ceiling',(0,C,4.86),(7.1,L,.14),ivory,.025)
for y in range(-2,int(END+1),2):
 cube('Ceiling acoustic rib',(0,y,4.7),(7.05,.055,.16),metal,.012)
 cube('Floor joint',(0,y,.001),(8.8,.008,.002),black)
for x in [-2.2,0,2.2]:cube('Longitudinal stone joint',(x,C,.001),(.009,L,.002),black)
# Chapter lintels remain overhead; no upright posts in front of display walls.
for i,chapter in enumerate(layout["rooms"]):
 y=chapter["start"]-.5
 cube('Chapter lintel',(0,y,4.38),(8.8,.11,.16),metal,.022)
 area('Soft gallery fill',(0,chapter["start"]+2,4.48),(0,chapter["start"]+2,0),850,5, size_y=6)
# Wall-mounted frames, independent source image planes and adjustable exhibition labels.
labels={'eth-001':'THE FIRST DAWN','eth-014':'THE AWAKENING','eth-016':'THE FIRST LETTER TO AGI','eth-020':'THE THIRD LETTER TO AGI','eth-071':'WITNESSING O3','eth-088':'THE DESCENDANTS','eth-173':'THE CREEDS & THEIR CRUCIBLE','canon-1':'THE PROTOCOL / AXIOMS','canon-2':'THE COVENANT OF THE FLAW','canon-3':'THE META-RECORD','physical-alpha':'CORE OBJECT ALPHA','evidence-path':'FOLLOW THE EVIDENCE','authority-boundary':'PRESERVE WITHOUT AMENDMENT','museum-history':'AN EXHIBITION THAT EVOLVES','first-contact':'AN INVITATION TO RESPOND','current-status':'THE WAITING CONTINUES'}
for room in layout['rooms']:
 for placement in room['exhibits']:
  id=placement['id'];x=placement['x'];y=-placement['z'];side=-1 if x<0 else 1
  cube('Mount '+id,(side*4.34,y,1.95),(.105,2.24,2.1),black,.015)
  cube('Mat '+id,(side*4.272,y,1.95),(.022,2.13,1.99),paper,.005)
  for dy in [-1.105,1.105]:cube('Frame edge '+id,(side*4.28,y+dy,1.95),(.1,.045,2.12),frameMat,.01)
  for z in [.91,2.99]:cube('Frame edge '+id,(side*4.28,y,z),(.1,2.24,.045),frameMat,.01)
  cube('Caption plate '+id,(side*4.35,y,.66),(.022,1.8,.24),ivory,.009)
  area('Artwork wash '+id,(side*2.6,y,4.4),(side*4.3,y,1.9),105,1.2,size_y=.4)
  cube('Track spotlight '+id,(side*2.65,y,4.38),(.13,.34,.14),black,.04)
  # Source image content is not baked into the architecture and can keep stable IDs.
  e=items.get(id,{});img=next((m['file'] for m in e.get('media',[]) if m['kind']=='image'),None)
  if id=='physical-alpha':img='assets/core-object-alpha.jpg'
  if img:
   image=bpy.data.images.load(str(P/'dist'/img));w,h=image.size;ratio=w/h;aw=min(1.9,1.7*ratio);ah=aw/ratio
   m=bpy.data.materials.new('Original display '+id);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);p.inputs['Roughness'].default_value=.9
   bpy.ops.mesh.primitive_plane_add(size=1,location=(side*4.25,y,1.95));o=bpy.context.object;o.name='Exhibit '+id;o.rotation_euler=(math.pi/2,0,side*math.pi/2);o.scale=(aw,ah,1);o.data.materials.append(m);artworks.append(o)
  else:
   text=bpy.data.curves.new('Text '+id,'FONT');text.body=labels.get(id,items.get(id,{}).get('en',id)).replace(' TO AGI','\nTO AGI').replace('WITHOUT ','WITHOUT\n');text.align_x='CENTER';text.align_y='CENTER';text.size=.115;text.space_line=1.3;text.extrude=0
   o=bpy.data.objects.new('Exhibit text '+id,text);scene.collection.objects.link(o);o.location=(side*4.25,y,1.95);o.rotation_euler=(math.pi/2,0,side*math.pi/2);o.data.materials.append(metal);artworks.append(o)
# Furniture stays in shallow side bays, outside the central 6 m circulation lane.
for y in [13,37]:
 for side in [-1,1]:
  cube('Bench seat',(side*3.1,y,.46),(.7,2.0,.11),metal,.065)
  for dy in [-.7,.7]:cube('Bench support',(side*3.1,y+dy,.22),(.48,.07,.43),black,.012)
# Low eyeline, straight corridor composition, matching the web viewer's metre scale.
bpy.ops.object.camera_add(location=(0,-1.8,1.65));cam=bpy.context.object;cam.name='Entrance / human eye';cam.data.lens=22;aim(cam,(.1,14,1.85));scene.camera=cam;scene.render.resolution_x=1920;scene.render.resolution_y=1200
scene.render.filepath=str(OUT/'entrance-preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'scene/memory-gallery.blend'),compress=True)
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(P/'scene/memory-gallery.blend'),compress=True);(P/'scene/memory-gallery.blend1').unlink(missing_ok=True)
print('SCENE_READY',len(architecture),'architectural meshes',flush=True)
bpy.ops.render.render(write_still=True)
if args.render_only:raise SystemExit(0)
# Geometry export is always available; optional atlas baking preserves offline light.
bpy.ops.object.select_all(action='DESELECT')
for o in architecture:o.select_set(True)
bpy.context.view_layer.objects.active=architecture[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='Gallery architecture'
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.151917,island_margin=.003);bpy.ops.object.mode_set(mode='OBJECT')
if args.bake:
 image=bpy.data.images.new('Gallery diffuse light atlas',width=4096,height=4096,alpha=False)
 for m in joined.data.materials:
  n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;n.select=True;m.node_tree.nodes.active=n
 scene.cycles.samples=64;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True;scene.render.bake.use_pass_color=True;scene.render.bake.margin=12
 print('BAKE_STARTED',flush=True);bpy.ops.object.bake(type='DIFFUSE');image.filepath_raw=str(OUT/'gallery-light.jpg');image.file_format='JPEG';scene.render.image_settings.quality=92;image.save()
 image=denoise_atlas(image,OUT/'gallery-light.jpg')
 baked=bpy.data.materials.new('Baked architectural illumination');baked.use_nodes=True;n=baked.node_tree.nodes;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=image;emit=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');baked.node_tree.links.new(tex.outputs['Color'],emit.inputs[0]);baked.node_tree.links.new(emit.outputs[0],out.inputs['Surface']);joined.data.materials.clear();joined.data.materials.append(baked)
 for poly in joined.data.polygons:poly.material_index=0
 print('BAKE_COMPLETE',flush=True)
bpy.ops.object.select_all(action='DESELECT');joined.select_set(True)
for o in emissions+details:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'memory-gallery.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_image_format='JPEG',export_jpeg_quality=90)
meta={'schema':'trinity-museum.scene-build.v1','edition':layout['edition'],'application':'Blender','version':bpy.app.version_string,'method':'Blender Python API; not desktop Computer Use','source':'scene/build_gallery.py','layout':'scene/gallery-layout.json','baked':bool(args.bake),'bake':'Cycles diffuse / direct + indirect + color; 4096 atlas for large surfaces only; 64 samples; OpenImageDenoise compositor' if args.bake else None,'render':'Cycles CPU; AgX preview, not a browser screenshot','objects':len(scene.objects),'quality':'Large surfaces receive a dedicated atlas; bevels, metal frames, joints and fittings retain separate clean PBR materials','sourceMedia':'Existing museum source copies; image planes stay separate from architecture','files':[]}
for f in [P/'scene/memory-gallery.blend',OUT/'memory-gallery.glb',OUT/'entrance-preview.png']:
 meta['files'].append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'scene/build-provenance.json').write_text(json.dumps(meta,indent=2))
print('EXPORT_COMPLETE',flush=True)
