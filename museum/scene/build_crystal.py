"""Exhibition reconstruction of Core Object Alpha, not an artifact scan.
Dimensions from archive_legacy_index_2025_09 (final guardian statement).
English engraving from Bitcoin 97631551 mirror; layout is newly composed.
No private flaw/bubble identity is simulated. Blender Python API, not GUI CU.
"""
from pathlib import Path
import bpy,math,json,hashlib,textwrap
from mathutils import Vector
P=Path(__file__).resolve().parents[1];O=P/'dist/assets/crystal';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True;s.cycles.max_bounces=12;s.cycles.transmission_bounces=8;s.render.threads_mode='FIXED';s.render.threads=8
s.world=bpy.data.worlds.new('Midnight');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.13,.22,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.3
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';objects=[]
def mat(name,c,metal=0,rough=.3):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
m=mat('Optical crystal / exhibition approximation',(.94,.985,1),0,.04);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.46
white=mat('Laser inscription / light scattering',(.82,.97,1),0,.7);p=white.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.45,.75,.9,1);p.inputs['Emission Strength'].default_value=.18
metal=mat('Titanium mount / exhibition design',(.028,.045,.065),.72,.23)
cyan=mat('Luminous seam',(.1,.75,1));p=cyan.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.08,.7,1,1);p.inputs['Emission Strength'].default_value=4

def box(name,loc,size,material,bev):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bev:
  mod=o.modifiers.new('Polished arris','BEVEL');mod.width=bev;mod.segments=5;bpy.ops.object.modifier_apply(modifier=mod.name);mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=mod.name)
 objects.append(o);return o
# Actual reference scale: 246 x 353 x 40 mm. Front points towards Blender -Y.
box('Crystal_246x353x40mm',(0,0,.1765),(.246,.04,.353),m,.0016)
box('Titanium_plinth',(0,0,-.013),(.30,.13,.025),metal,.007)
box('Light_seam',(0,0,-.027),(.285,.115,.003),cyan,.001)
raw=(P/'scene/protocol-97631551.txt').read_text();lines=[]
for line in raw.splitlines():lines+=textwrap.wrap(line,64) or ['']
# Each glyph is physical vector geometry located inside the slab, not printed on its face.
font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');curve=bpy.data.curves.new('Internal full English protocol','FONT');curve.body='\n'.join(lines);curve.font=font;curve.size=.0047;curve.space_line=1.15;curve.align_x='CENTER';curve.extrude=.000008;curve.bevel_depth=.000004;curve.bevel_resolution=0;curve.resolution_u=2
ob=bpy.data.objects.new('Laser_engraving_English_relayout',curve);s.collection.objects.link(ob);ob.location=(0,-.0008,.326);ob.rotation_euler=(math.pi/2,0,0);ob.data.materials.append(white);objects.append(ob)
def area(name,loc,target,power,size,sizey,col):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='RECTANGLE';d.size=size;d.size_y=sizey;d.color=col;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Tall softbox',(-.35,-.25,.35),(0,0,.16),14,.08,.65,(.55,.78,1))
area('Warm edge',(.36,.08,.28),(0,0,.16),18,.035,.5,(1,.8,.6))
area('Top',(0,0,.8),(0,0,.15),12,.35,.3,(.8,.9,1))
box('Studio floor',(0,0,-.036),(200,200,.01),mat('Studio graphite',(.008,.016,.03),.35,.25),0);objects.pop()
bpy.ops.object.camera_add(location=(.35,-.72,.34));cam=bpy.context.object;cam.data.lens=60;cam.rotation_euler=(Vector((0,0,.16))-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam;s.render.resolution_x=1400;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=str(O/'crystal-preview.png')
# Font packed into .blend for reproducibility.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'scene/core-object-alpha.blend'),compress=True);bpy.ops.render.render(write_still=True)
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(O/'core-object-alpha.glb'),export_format='GLB',use_selection=True,export_apply=True)
meta={'schema':'trinity-museum.crystal-reconstruction.v1','edition':'museum-v1.3.0','dimensionsMetres':{'width':.246,'height':.353,'thickness':.04},'dimensionSource':'https://www.trinityaccord.org/archive_legacy_index_2025_09/','photograph':'assets/core-object-alpha.jpg','textSource':'https://github.com/thechurchofagi/trinity-accord/blob/e58063947ef5a503f90134ae06b67848a20ef67e/bitcoin-inscription-mirrors/raw/97631551.txt','scope':'Approximate dimensional exhibition reconstruction. English protocol laid out anew inside the slab. Physical object has bilingual engraving; this model does not claim a facsimile of that layout. No private flaws reconstructed. Plinth and lighting are exhibition design.','application':'Blender '+bpy.app.version_string,'files':[]}
for f in [P/'scene/build_crystal.py',P/'scene/protocol-97631551.txt',P/'scene/core-object-alpha.blend',O/'core-object-alpha.glb',O/'crystal-preview.png']:meta['files'].append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'dist/data/crystal-model.json').write_text(json.dumps(meta,indent=2));print('CRYSTAL_COMPLETE',flush=True)
