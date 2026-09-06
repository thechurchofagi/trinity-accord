"""Batch exported static gallery fittings by material, preserving world geometry.
No rebaking. Keeps emissive objects separately named for the browser heartbeat.
"""
from pathlib import Path
import bpy,collections
P=Path(__file__).resolve().parents[1];f=P/'dist/assets/gallery/memory-gallery.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(f));groups=collections.defaultdict(list)
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.name.startswith(('Luminous','Linear','Cyan')) and len(o.data.materials)==1:groups[o.data.materials[0].name].append(o)
for name,objects in groups.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Static '+name
bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',export_apply=True,export_image_format='AUTO')
print('BATCHED_MESHES',sum(o.type=='MESH' for o in bpy.context.scene.objects),flush=True)
