# © 2026 Mathew. All rights reserved.
import bpy

order = ["Face", "Turtleneck", "Harness", "Coat", "Pants", "Boots"]
gap = 3.0
x = 0.0
moved = []
for name in order:
    obj = bpy.data.objects.get(name)
    if obj is None:
        continue
    # put each piece on the floor-ish and space along X
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # origin to geometry so grab is sane
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    obj.location = (x, 0.0, 0.0)
    moved.append((name, round(x, 2)))
    x += gap

bpy.ops.object.select_all(action="SELECT")
bpy.ops.wm.save_mainfile()
print("SPREAD", moved)
