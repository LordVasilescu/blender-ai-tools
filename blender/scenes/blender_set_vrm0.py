# © 2026 Mathew. All rights reserved.
import bpy

# Find the armature and force VRM 0.0 spec version
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        ext = obj.data.vrm_addon_extension
        old = ext.spec_version
        ext.spec_version = "0.0"
        print(f"Armature: {obj.name}")
        print(f"  Spec version changed: {old} → {ext.spec_version}")
        print(f"  SUCCESS! Now export: File → Export → VRM (.vrm)")
        break
else:
    print("ERROR: No armature found!")
