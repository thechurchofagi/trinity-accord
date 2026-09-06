"""Denoise a Cycles light atlas with Blender's OpenImageDenoise compositor."""
from pathlib import Path
import bpy

def denoise_atlas(image, output):
 output=Path(output);tmp=bpy.data.scenes.new('Atlas denoising');tmp.render.engine='CYCLES';tmp.cycles.samples=1;tmp.render.resolution_x=4;tmp.render.resolution_y=4;tmp.render.resolution_percentage=100
 camera=bpy.data.objects.new('Atlas camera',bpy.data.cameras.new('Atlas camera'));tmp.collection.objects.link(camera);tmp.camera=camera;tmp.use_nodes=True;n=tmp.node_tree.nodes;n.clear();source=n.new('CompositorNodeImage');source.image=image;denoise=n.new('CompositorNodeDenoise');save=n.new('CompositorNodeOutputFile');save.base_path=str(output.parent);save.file_slots[0].path='atlas-denoised-';save.format.file_format='PNG';save.format.color_depth='16';tmp.view_settings.view_transform='Standard';tmp.view_settings.look='None';tmp.node_tree.links.new(source.outputs['Image'],denoise.inputs['Image']);tmp.node_tree.links.new(denoise.outputs['Image'],save.inputs[0]);bpy.ops.render.render(scene=tmp.name)
 f=output.parent/'atlas-denoised-0001.png';result=bpy.data.images.load(str(f));_ = result.pixels[0];result.filepath_raw=str(output);result.file_format='JPEG';result.save();f.unlink();bpy.data.scenes.remove(tmp);return result
if __name__=='__main__':
 import sys
 source=Path(sys.argv[1]);out=Path(sys.argv[2]);denoise_atlas(bpy.data.images.load(str(source)),out)
