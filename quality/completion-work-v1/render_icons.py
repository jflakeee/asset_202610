import bpy,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];R=Path(args[0]).resolve();source=Path(args[1]).resolve()
for name in ('chest','ore','coin','rope','potion','wood'):
 bpy.ops.wm.open_mainfile(filepath=str(source/'blend'/f'{name}.blend'));s=bpy.context.scene;s.frame_set(1)
 s.render.film_transparent=True;s.render.image_settings.color_mode='RGBA';s.render.resolution_x=512;s.render.resolution_y=512
 s.render.filepath=str(R/'icons'/f'{name}_master.png');bpy.ops.render.render(write_still=True)
print('ICONS_RENDERED')
