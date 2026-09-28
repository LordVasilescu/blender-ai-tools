# © 2026 Mathew. All rights reserved.
import bpy
import os

ROOT = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx"
BLEND = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend"

# drop the A-pose screenshot empty
for obj in list(bpy.data.objects):
    if obj.name.startswith("APose") or obj.type == "EMPTY":
        bpy.data.objects.remove(obj, do_unlink=True)

already = {o.name for o in bpy.data.objects}
parts = [
    ("coat.fbx", "Coat"),
    ("pants.fbx", "Pants"),
    ("boots.fbx", "Boots"),
    ("harness.fbx", "Harness"),
    ("face.fbx", "Face"),
]

imported = []
for fname, name in parts:
    path = os.path.join(ROOT, fname)
    if not os.path.isfile(path):
        print("MISSING", path)
        continue
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.import_scene.fbx(filepath=path)
    sel = [o for o in bpy.context.selected_objects]
    if not sel:
        print("EMPTY IMPORT", fname)
        continue
    sel[0].name = name
    for i, o in enumerate(sel[1:], start=1):
        o.name = f"{name}_{i}"
    imported.append(name)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.view3d.view_all() if False else None
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("NOW", [o.name for o in bpy.data.objects])
print("ADDED", imported)
