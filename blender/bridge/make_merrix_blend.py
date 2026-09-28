# © 2026 Mathew. All rights reserved.
import bpy
bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.wm.save_as_mainfile(filepath=r"C:\Users\Mathe\OneDrive\Desktop\Meridian\art\characters\merrix\stefan\MerrixAssemble.blend")
print("CREATED", bpy.data.filepath)
