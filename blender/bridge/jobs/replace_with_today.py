# © 2026 Mathew. All rights reserved.
import bpy
import os

ROOT = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\fbx\today"
BLEND = r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend"

# wipe everything in the scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh)
for arm in list(bpy.data.armatures):
    bpy.data.armatures.remove(arm)
for img in list(bpy.data.images):
    if img.name not in ("Render Result", "Viewer Node"):
        try:
            bpy.data.images.remove(img)
        except Exception:
            pass

order = [
    "Face.fbx",
    "ArmorOrnate.fbx",
    "ArmorFantasy.fbx",
    "Leggings.fbx",
    "Cape.fbx",
    "Boots.fbx",
    "Gauntlet.fbx",
    "GauntletArm.fbx",
]

imported = []
for fname in order:
    path = os.path.join(ROOT, fname)
    if not os.path.isfile(path):
        print("MISSING", path)
        continue
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.import_scene.fbx(filepath=path)
    sel = list(bpy.context.selected_objects)
    if not sel:
        print("EMPTY", fname)
        continue
    base = os.path.splitext(fname)[0]
    sel[0].name = base
    for i, o in enumerate(sel[1:], start=1):
        o.name = f"{base}_{i}"
    imported.append(base)

# space along X, origin to geometry
gap = 3.5
x = 0.0
for name in imported:
    obj = bpy.data.objects.get(name)
    if obj is None:
        continue
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (x, 0.0, 0.0)
    x += gap

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("NOW", [o.name for o in bpy.data.objects])
print("IMPORTED", imported)
