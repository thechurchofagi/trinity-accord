"""Build and bake the shared six-room plan with Blender. Original artwork stays separate."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1];D=P/'dist';O=D/'assets/gallery';layout=json.loads((P/'scene/gallery-layout.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=48;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=4
s.world=bpy.data.worlds.new('Soft museum ambient');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.52,.58,.63,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.42
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
materials={};architecture=[];details=[]
for key,defn in layout['materials'].items():
 m=bpy.data.materials.new('Spatial '+key);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];srgb=tuple(int(defn['color'][i:i+2],16)/255 for i in (1,3,5));rgb=tuple(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in srgb);p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=defn.get('roughness',.88);p.inputs['Metallic'].default_value=defn.get('metalness',0)
 if defn.get('emission'):p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=1.1
 materials[key]=m
for part in layout['architecture']:
 if part.get('vertices'):
  verts=[(v[0],-v[2],v[1]) for v in part['vertices']];ix=part['indices'];mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata(verts,[],[tuple(ix[i:i+3]) for i in range(0,len(ix),3)]);mesh.update();o=bpy.data.objects.new(part['name'],mesh);s.collection.objects.link(o)
 else:
  pos=part['position'];size=part['size'];bpy.ops.mesh.primitive_cube_add(size=1,location=(pos[0],-pos[2],pos[1]));o=bpy.context.object;o.name=part['name'];o.dimensions=(size[0],size[2],size[1]);o.rotation_euler.z=part.get('rotationY',0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(materials[part['material']]);(details if part['material'] in ['metal','light'] else architecture).append(o)
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for r in layout['rooms']:
 for depth in [r['start']+r['length']*.27,r['start']+r['length']*.73]:
  data=bpy.data.lights.new('Soft room fill','AREA');data.energy=950 if r['id'] not in ['material','waiting'] else 800;data.shape='RECTANGLE';data.size=r['width']*.75;data.size_y=min(6,r['length']/2);o=bpy.data.objects.new('Soft room fill',data);s.collection.objects.link(o);o.location=(0,depth,r['floor']+r['height']-.3);aim(o,(0,depth,r['floor']))
bpy.ops.object.camera_add(location=(0,2,1.65));cam=bpy.context.object;cam.data.lens=19;aim(cam,(0,14,2.2));s.camera=cam;s.render.resolution_x=1280;s.render.resolution_y=800
# Bake static diffuse lighting; no high-cost browser shadows or light probes.
bpy.ops.object.select_all(action='DESELECT')
for o in architecture:o.select_set(True)
bpy.context.view_layer.objects.active=architecture[0];bpy.ops.object.join();joined=bpy.context.object;joined.name='Six-room baked architecture'
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.151917,island_margin=.004);bpy.ops.object.mode_set(mode='OBJECT')
atlas=bpy.data.images.new('Six-room diffuse atlas',width=2048,height=2048,alpha=False)
for m in joined.data.materials:
 n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=atlas;m.node_tree.nodes.active=n
s.render.bake.use_pass_direct=True;s.render.bake.use_pass_indirect=True;s.render.bake.use_pass_color=True;s.render.bake.margin=8
print('BAKE_BEGIN shared geometry',len(layout['architecture']),flush=True);bpy.ops.object.bake(type='DIFFUSE');atlas.filepath_raw=str(O/'spatial-light.png');atlas.file_format='PNG';atlas.save();atlas.pack()
saved_location=cam.location.copy();saved_rotation=cam.rotation_euler.copy();cam.location=(0,-10,2);aim(cam,(0,-20,2));s.view_settings.view_transform='Standard';s.use_nodes=True;nodes=s.node_tree.nodes;nodes.clear();image=nodes.new('CompositorNodeImage');image.image=atlas;denoise=nodes.new('CompositorNodeDenoise');denoise.use_hdr=True;output=nodes.new('CompositorNodeComposite');s.node_tree.links.new(image.outputs['Image'],denoise.inputs['Image']);s.node_tree.links.new(denoise.outputs['Image'],output.inputs['Image']);s.render.resolution_x=2048;s.render.resolution_y=2048;s.render.filepath=str(O/'spatial-light-denoised.png');bpy.ops.render.render(write_still=True);s.use_nodes=False;s.view_settings.view_transform='AgX';cam.location=saved_location;cam.rotation_euler=saved_rotation
clean=bpy.data.images.load(str(O/'spatial-light-denoised.png'),check_existing=False);clean.colorspace_settings.name='sRGB';atlas=clean;atlas.pack();s.render.resolution_x=1280;s.render.resolution_y=800

m=bpy.data.materials.new('Baked spatial light');m.use_nodes=True;nodes=m.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');tex=nodes.new('ShaderNodeTexImage');tex.image=atlas;m.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);m.node_tree.links.new(em.outputs[0],output.inputs['Surface']);joined.data.materials.clear();joined.data.materials.append(m)
for poly in joined.data.polygons:poly.material_index=0
# Resolve groups before joining: join deletes the other Blender object handles.
export=[joined];groups={key:[o for o in details if o.data.materials[0]==materials[key]] for key in ['metal','light']}
for key,group in groups.items():
 if not group:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();o=bpy.context.object;o.name='Spatial '+key;export.append(o)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'scene/memory-gallery.blend'),compress=True);(P/'scene/memory-gallery.blend1').unlink(missing_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for o in export:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(O/'memory-gallery.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_image_format='AUTO')
s.render.filepath=str(O/'entrance-preview.png');bpy.ops.render.render(write_still=True)
for room_id in ['originals','material','waiting']:
 r=next(r for r in layout['rooms'] if r['id']==room_id);cam.location=(0,r['start']+1.3,r['floor']+1.65);aim(cam,(0,r['start']+r['length'],r['floor']+2));s.render.filepath=str(O/(room_id+'-architecture.png'));bpy.ops.render.render(write_still=True)
files=['scene/build_spatial_gallery.py','scene/gallery-layout.json','scene/memory-gallery.blend','dist/assets/gallery/memory-gallery.glb','dist/assets/gallery/spatial-light.png','dist/assets/gallery/entrance-preview.png']
meta=dict(schema='trinity-museum.scene-build.v2',edition=layout['edition'],application='Blender',version=bpy.app.version_string,source='scene/build_spatial_gallery.py',layout='scene/gallery-layout.json',baked=True,bake='Cycles diffuse/direct/indirect/color, 2048px atlas, 48 samples plus compositor denoising; no new artwork baked into surfaces',previewScope='Architectural references, not browser screenshots. Runtime original artwork, crystal and Earth are separate assets.',layoutSha256=hashlib.sha256((P/'scene/gallery-layout.json').read_bytes()).hexdigest(),files=[dict(path=f,bytes=(P/f).stat().st_size,sha256=hashlib.sha256((P/f).read_bytes()).hexdigest()) for f in files]);(P/'scene/build-provenance.json').write_text(json.dumps(meta,indent=2)+'\n');print('SIX_ROOMS_EXPORT_COMPLETE',flush=True)
