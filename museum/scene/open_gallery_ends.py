"""Open the existing baked corridor without recomputing its light atlas.
Removes the two end-wall surfaces and obsolete destination bar. Existing
UVs, artwork mounts, and material maps survive unchanged.
"""
from pathlib import Path
import bpy,bmesh,json
P=Path(__file__).resolve().parents[1]
layout=json.loads((P/'scene/gallery-layout.json').read_text())
end=layout['dimensions']['length']-3
bpy.ops.wm.open_mainfile(filepath=str(P/'scene/memory-gallery.blend'))
for o in list(bpy.data.objects):
 if o.name.startswith(('Entrance back wall','End wall','Luminous destination')):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'scene/memory-gallery.blend'),compress=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(P/'dist/assets/gallery/memory-gallery.glb'))
removed=0
for o in list(bpy.data.objects):
 if o.name.startswith('Luminous destination'):
  bpy.data.objects.remove(o,do_unlink=True);continue
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);faces=[]
 for f in bm.faces:
  ys=[(o.matrix_world@v.co).y for v in f.verts]
  if all(abs(y+3)<.13 for y in ys) or all(abs(y-end)<.13 for y in ys):faces.append(f)
 removed+=len(faces);bmesh.ops.delete(bm,geom=faces,context='FACES');bm.to_mesh(o.data);bm.free()
assert removed>=0
bpy.ops.export_scene.gltf(filepath=str(P/'dist/assets/gallery/memory-gallery.glb'),export_format='GLB',export_apply=True)
print('Opened both ends; removed',removed,'wall faces')
