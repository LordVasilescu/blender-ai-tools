# © 2026 Mathew. All rights reserved.
"""Run on Blender GUI start. Frames the view and turns on material preview."""
import bpy


def _go():
    try:
        for obj in bpy.data.objects:
            obj.hide_set(False)
            obj.hide_viewport = False
            obj.select_set(obj.type == "MESH")
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.shading.type = "MATERIAL"
                for region in area.regions:
                    if region.type != "WINDOW":
                        continue
                    ov = {
                        "window": window,
                        "screen": window.screen,
                        "area": area,
                        "region": region,
                    }
                    with bpy.context.temp_override(**ov):
                        bpy.ops.view3d.view_all(center=False)
        print("[Meridian Bridge] boot framed MATERIAL view")
    except Exception as e:
        print("[Meridian Bridge] boot frame failed:", e)
    return None


bpy.app.timers.register(_go, first_interval=2.0)
