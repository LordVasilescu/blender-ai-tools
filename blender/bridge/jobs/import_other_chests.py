# © 2026 Mathew. All rights reserved.
import bpy
import os

ROOT = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx\today"
BLEND = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend"

print("BEFORE", [o.name for o in bpy.data.objects])

chest = bpy.data.objects.get("Chest")
if chest is None:
    raise RuntimeError("Chest missing — abort so we do not scramble the lineup")

base = tuple(chest.location)
print("CHEST_AT", base)

# extra upper-chest meshes we pulled out earlier
# ArmorOrnate = collar + pauldrons
# ArmorFantasy = full sleeveless cuirass
pieces = [
    ("ArmorOrnate.fbx", "ArmorOrnate", -4.4),
    ("ArmorFantasy.fbx", "ArmorFantasy", -2.2),
]

imported = []
for fname, name, dx in pieces:
    path = os.path.join(ROOT, fname)
    if not os.path.isfile(path):
        print("MISSING", path)
        continue
    existing = bpy.data.objects.get(name)
    if existing is not None:
        print("ALREADY", name)
        continue
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.import_scene.fbx(filepath=path)
    sel = list(bpy.context.selected_objects)
    print("IMPORTED_RAW", name, [o.name for o in sel])
    if not sel:
        print("EMPTY", fname)
        continue
    sel[0].name = name
    for i, o in enumerate(sel[1:], start=1):
        o.name = "%s_%d" % (name, i)
    obj = bpy.data.objects.get(name)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (base[0] + dx, base[1], base[2])
    print("PLACED", name, tuple(obj.location), "dim", tuple(obj.dimensions))
    imported.append(name)

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("NOW", [o.name for o in bpy.data.objects])
print("IMPORTED", imported)
print("DONE extra chests")
