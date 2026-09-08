"""Denoise and tone the exhibition-only bake; never touch historical media."""
from pathlib import Path
import bpy,hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from mathutils import Vector
P=Path(__file__).resolve().parents[1];D=P/'dist';A=D/'assets/gallery';H=lambda b:hashlib.sha256(b).hexdigest()
source=A/'spatial-light.png';input_sha=H(source.read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(P/'scene/memory-gallery.blend'))
s=bpy.context.scene;mesh=bpy.data.objects['Six-room baked architecture'];mesh.data.update()
im=Image.open(source).convert('RGB');width,height=im.size
# Light sampling noise is not a wall texture. Keep blur below baked UV padding.
im=im.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(1.4))
masks={k:Image.new('L',im.size) for k in ['floor','ceiling','bright-wall','dark-wall']};draws={k:ImageDraw.Draw(v) for k,v in masks.items()}
uv=mesh.data.uv_layers.active.data;normal_matrix=mesh.matrix_world.to_3x3().inverted().transposed()
for face in mesh.data.polygons:
 normal=normal_matrix@face.normal;centre=mesh.matrix_world@face.center
 key='floor' if normal.z>.7 else 'ceiling' if normal.z<-.7 else 'dark-wall' if centre.y>=54 else 'bright-wall'
 points=[(round(uv[i].uv.x*(width-1)),round((1-uv[i].uv.y)*(height-1))) for i in face.loop_indices]
 draws[key].polygon(points,fill=255)
factors={'floor':.24,'ceiling':.32,'bright-wall':.68,'dark-wall':.16}
pixels=np.asarray(im,dtype=np.float32)/255
linear=np.where(pixels<=.04045,pixels/12.92,((pixels+.055)/1.055)**2.4)
for key,mask in masks.items():
 region=np.asarray(mask.filter(ImageFilter.MaxFilter(5)))>0;linear[region]*=factors[key]
srgb=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
Image.fromarray(np.uint8(np.clip(srgb,0,1)*255+.5)).save(source,optimize=True)
atlas=bpy.data.images['Six-room diffuse atlas']
if atlas.packed_file:atlas.unpack(method='REMOVE')
atlas.filepath=str(source);atlas.reload();atlas.pack()
s.cycles.samples=4;s.cycles.use_denoising=True
bpy.ops.wm.save_as_mainfile(filepath=str(P/'scene/memory-gallery.blend'),compress=True);(P/'scene/memory-gallery.blend1').unlink(missing_ok=True)
bpy.ops.object.select_all(action='DESELECT')
for name in ['Six-room baked architecture','Spatial metal','Spatial light']:bpy.data.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(A/'memory-gallery.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_image_format='AUTO')
layout=json.loads((P/'scene/gallery-layout.json').read_text());cam=s.camera
def aim(target):cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
for room_id,name in [('entrance','entrance-preview.png'),('originals','originals-architecture.png'),('material','material-architecture.png'),('waiting','waiting-architecture.png')]:
 r=next(r for r in layout['rooms'] if r['id']==room_id);cam.location=(0,r['start']+1.3,r['floor']+1.65);aim((0,r['start']+r['length'],r['floor']+2));s.render.filepath=str(A/name);bpy.ops.render.render(write_still=True)
p=P/'scene/build-provenance.json';meta=json.loads(p.read_text());meta['postprocess']={'script':'scene/polish_spatial_light.py','inputAtlasSha256':input_sha,'denoise':'Median radius 1 + Gaussian sigma 1.4 pixels; below the original UV island padding','linearLightFactors':factors,'scope':'Exhibition architecture only; original artwork/evidence untouched','referenceSamples':4}
paths=[f['path'] for f in meta['files']]+['scene/polish_spatial_light.py']
meta['files']=[dict(path=f,bytes=(P/f).stat().st_size,sha256=H((P/f).read_bytes())) for f in dict.fromkeys(paths)];p.write_text(json.dumps(meta,indent=2)+'\n')
print('ARCHITECTURAL_LIGHT_POLISHED',flush=True)
