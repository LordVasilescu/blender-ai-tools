# © 2026 Mathew. All rights reserved.
import bpy
import os

FBX = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx\today\Chest.fbx"
BLEND = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend"

print("BEFORE", [o.name for o in bpy.data.objects])

old_locs = {}
for name in ("ArmorOrnate", "ArmorFantasy"):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        old_locs[name] = tuple(obj.location)
        print("OLD", name, "loc", old_locs[name], "dim", tuple(obj.dimensions))

to_remove = []
for obj in list(bpy.data.objects):
    n = obj.name
    if (
        n == "ArmorOrnate"
        or n.startswith("ArmorOrnate_")
        or n == "ArmorFantasy"
        or n.startswith("ArmorFantasy_")
        or "armorornate" in n.lower()
        or "armorfantasy" in n.lower()
    ):
        to_remove.append(obj)

print("REMOVE", [o.name for o in to_remove])
for obj in to_remove:
    bpy.data.objects.remove(obj, do_unlink=True)

for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
for arm in list(bpy.data.armatures):
    if arm.users == 0:
        bpy.data.armatures.remove(arm)

if not os.path.isfile(FBX):
    raise FileNotFoundError(FBX)

bpy.ops.object.select_all(action="DESELECT")
bpy.ops.import_scene.fbx(filepath=FBX)
sel = list(bpy.context.selected_objects)
print("IMPORTED_RAW", [o.name for o in sel])
if not sel:
    raise RuntimeError("Chest.fbx imported nothing")

sel[0].name = "Chest"
for i, o in enumerate(sel[1:], start=1):
    o.name = "Chest_%d" % i

main = bpy.data.objects.get("Chest")
if main is None:
    raise RuntimeError("Chest object missing after rename")

bpy.ops.object.select_all(action="DESELECT")
main.select_set(True)
bpy.context.view_layer.objects.active = main
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
target = old_locs.get("ArmorOrnate") or old_locs.get("ArmorFantasy") or (3.5, 0.0, 0.0)
main.location = target
print("CHEST loc", tuple(main.location), "dim", tuple(main.dimensions))

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("NOW", [o.name for o in bpy.data.objects])
print("DONE chest swap")
