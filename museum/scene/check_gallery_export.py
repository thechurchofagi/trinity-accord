from pathlib import Path
import bpy
p=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(p/'scene/memory-gallery.blend'))
for o in list(bpy.data.objects):
 if o.type=='MESH' and not o.name.startswith('Exhibit '):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(p/'dist/assets/gallery/memory-gallery.glb'))
s=bpy.context.scene;s.cycles.samples=12;s.render.resolution_x=1000;s.render.resolution_y=625;s.render.filepath=str(p/'scene/export-check.png');bpy.ops.render.render(write_still=True)
print('EXPORTED_SCENE_RENDER_OK',flush=True)
