# © 2026 Mathew. All rights reserved.
import bpy
from mathutils import Vector

FBX = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx\turtleneck.fbx"
REF = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\apose_front.jpg"
BLEND = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend"

# wipe leftover cubes
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

bpy.ops.import_scene.fbx(filepath=FBX)
imported = [o for o in bpy.context.selected_objects]
for i, o in enumerate(imported):
    o.name = "Turtleneck" if i == 0 else f"Turtleneck_{i}"

# reference image on Y=0, facing camera (front)
bpy.ops.object.empty_add(type="IMAGE", location=(0.0, -0.6, 1.0))
empty = bpy.context.active_object
empty.name = "APose_Front_Ref"
empty.empty_display_size = 2.0
img = bpy.data.images.load(REF, check_existing=True)
empty.data = img

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("IMPORTED turtleneck", [o.name for o in imported], "ref", empty.name)
