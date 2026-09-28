# © 2026 Mathew. All rights reserved.
import bpy
import os

FBX = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx\today\Arm.fbx"
BLEND = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend"
NAME = "Arm"

print("BEFORE", [o.name for o in bpy.data.objects])

if bpy.data.objects.get(NAME) is not None:
    raise RuntimeError("Arm already in the scene")

if not os.path.isfile(FBX):
    raise FileNotFoundError(FBX)

anchor = bpy.data.objects.get("GauntletArm") or bpy.data.objects.get("Gauntlet") or bpy.data.objects.get("Chest")
if anchor is not None:
    target = (anchor.location.x + 2.2, anchor.location.y, anchor.location.z)
    print("ANCHOR", anchor.name, tuple(anchor.location))
else:
    target = (12.0, 0.0, 0.3)
    print("NO_ANCHOR")

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.import_scene.fbx(filepath=FBX)
sel = list(bpy.context.selected_objects)
print("IMPORTED_RAW", [o.name for o in sel])
if not sel:
    raise RuntimeError("Arm.fbx imported nothing")

sel[0].name = NAME
for i, o in enumerate(sel[1:], start=1):
    o.name = "%s_%d" % (NAME, i)

obj = bpy.data.objects.get(NAME)
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
obj.location = target
print("ARM loc", tuple(obj.location), "dim", tuple(obj.dimensions))

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("NOW", [o.name for o in bpy.data.objects])
print("DONE arm import")
