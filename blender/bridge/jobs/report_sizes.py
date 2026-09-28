# © 2026 Mathew. All rights reserved.
import bpy

print("FILE", bpy.data.filepath)
print("COUNT", len(bpy.data.objects))
print("---")
rows = []
for obj in sorted(bpy.data.objects, key=lambda o: o.name.lower()):
    if obj.type not in {"MESH", "EMPTY", "ARMATURE"}:
        continue
    d = obj.dimensions
    s = obj.scale
    loc = obj.location
    verts = len(obj.data.vertices) if obj.type == "MESH" else 0
    print(
        "OBJ",
        obj.name,
        "type",
        obj.type,
        "loc",
        (round(loc.x, 3), round(loc.y, 3), round(loc.z, 3)),
        "dim",
        (round(d.x, 3), round(d.y, 3), round(d.z, 3)),
        "scale",
        (round(s.x, 3), round(s.y, 3), round(s.z, 3)),
        "verts",
        verts,
    )
print("DONE sizes")
