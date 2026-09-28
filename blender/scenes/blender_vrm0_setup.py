# © 2026 Mathew. All rights reserved.
import bpy

# ============================================================
#   TATSUMAKI VRM 0.x SETUP
#   Run this with the Tatsumaki .blend file open!
#   Then export: File → Export → VRM (.vrm) → select VRM 0.x
# ============================================================

print("Setting up VRM 0.x configuration for Tatsumaki...")

# --- Find the armature ---
rig = None
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        rig = obj
        print(f"  Found armature: {obj.name}")
        break

if not rig:
    raise Exception("No armature found! Open the Tatsumaki .blend file first.")

# Ensure the VRM addon is installed
try:
    vrm_ext = rig.data.vrm_addon_extension
    print("  VRM addon extension found on armature.")
except AttributeError:
    raise Exception(
        "VRM addon not installed or not enabled!\n"
        "Go to Edit → Preferences → Get Extensions → search 'VRM' → Install"
    )

# ============================================================
#  CRITICAL: Set spec version to VRM 0.x
# ============================================================
vrm_ext.spec_version = "0.0"
print(f"  Spec version set to: {vrm_ext.spec_version}")

# ============================================================
#  STEP 1: VRM 0.x HUMANOID BONE MAPPING
#  Maps Lily Rig / Auto-Rig Pro bones → VRM humanoid standard
# ============================================================
print("  Setting up humanoid bone mapping...")

# Access the VRM 0.x humanoid data
vrm0 = vrm_ext.vrm0
humanoid = vrm0.humanoid

# Clear existing bone mappings
humanoid.human_bones.clear()

# Lily Rig → VRM Humanoid bone mapping
# VRM requires specific bone names for the humanoid skeleton
bone_mapping = {
    # --- Required bones ---
    "hips":             "root.x",
    "spine":            "spine_01.x",
    "chest":            "spine_02.x",
    "upperChest":       "spine_03.x",
    "neck":             "neck.x",
    "head":             "head.x",

    # Left leg
    "leftUpperLeg":     "thigh_fk.l",
    "leftLowerLeg":     "leg_fk.l",
    "leftFoot":         "foot_fk.l",
    "leftToes":         "toes_01.l",

    # Right leg
    "rightUpperLeg":    "thigh_fk.r",
    "rightLowerLeg":    "leg_fk.r",
    "rightFoot":        "foot_fk.r",
    "rightToes":        "toes_01.r",

    # Left arm
    "leftShoulder":     "shoulder.l",
    "leftUpperArm":     "arm_fk.l",
    "leftLowerArm":     "forearm_fk.l",
    "leftHand":         "hand.l",

    # Right arm
    "rightShoulder":    "shoulder.r",
    "rightUpperArm":    "arm_fk.r",
    "rightLowerArm":    "forearm_fk.r",
    "rightHand":        "hand.r",

    # Eyes
    "leftEye":          "Eye.l.001",
    "rightEye":         "Eye.r.001",
    "jaw":              "jawbone.x",

    # Left hand fingers
    "leftThumbProximal":       "thumb1.l",
    "leftThumbIntermediate":   "c_thumb2.l",
    "leftThumbDistal":         "c_thumb3.l",
    "leftIndexProximal":       "index1.l",
    "leftIndexIntermediate":   "c_index2.l",
    "leftIndexDistal":         "c_index3.l",
    "leftMiddleProximal":      "middle1.l",
    "leftMiddleIntermediate":  "c_middle2.l",
    "leftMiddleDistal":        "c_middle3.l",
    "leftRingProximal":        "ring1.l",
    "leftRingIntermediate":    "c_ring2.l",
    "leftRingDistal":          "c_ring3.l",
    "leftLittleProximal":      "pinky1.l",
    "leftLittleIntermediate":  "c_pinky2.l",
    "leftLittleDistal":        "c_pinky3.l",

    # Right hand fingers
    "rightThumbProximal":      "thumb1.r",
    "rightThumbIntermediate":  "c_thumb2.r",
    "rightThumbDistal":        "c_thumb3.r",
    "rightIndexProximal":      "index1.r",
    "rightIndexIntermediate":  "c_index2.r",
    "rightIndexDistal":        "c_index3.r",
    "rightMiddleProximal":     "middle1.r",
    "rightMiddleIntermediate": "c_middle2.r",
    "rightMiddleDistal":       "c_middle3.r",
    "rightRingProximal":       "ring1.r",
    "rightRingIntermediate":   "c_ring2.r",
    "rightRingDistal":         "c_ring3.r",
    "rightLittleProximal":     "pinky1.r",
    "rightLittleIntermediate": "c_pinky2.r",
    "rightLittleDistal":       "c_pinky3.r",
}

# Get list of all bones in the armature for validation
armature_bones = set(rig.data.bones.keys())
mapped_count = 0
skipped = []

for vrm_bone_name, blender_bone_name in bone_mapping.items():
    if blender_bone_name in armature_bones:
        hb = humanoid.human_bones.add()
        hb.bone = vrm_bone_name
        hb.node.bone_name = blender_bone_name
        mapped_count += 1
    else:
        skipped.append(f"    {vrm_bone_name} → {blender_bone_name} (NOT FOUND)")

print(f"  Mapped {mapped_count} bones successfully.")
if skipped:
    print(f"  Skipped {len(skipped)} bones (not found in armature):")
    for s in skipped:
        print(s)

# ============================================================
#  STEP 2: VRM 0.x BLEND SHAPE GROUPS (Expressions)
#  Maps shape keys → VRM blend shape proxies for face tracking
# ============================================================
print("  Setting up blend shape groups...")

blend_shape_master = vrm0.blend_shape_master

# Clear existing
blend_shape_master.blend_shape_groups.clear()

# Find the main mesh with shape keys
main_mesh = None
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        keys = obj.data.shape_keys.key_blocks
        # Look for the mesh with the most shape keys (likely the body)
        if main_mesh is None or len(keys) > len(main_mesh.data.shape_keys.key_blocks):
            main_mesh = obj

if main_mesh:
    print(f"  Using mesh: {main_mesh.name} ({len(main_mesh.data.shape_keys.key_blocks)} shape keys)")

    # VRM 0.x standard blend shape presets
    # Maps VRM preset name → shape key name(s) on the model
    expression_mapping = {
        # --- Eye expressions ---
        "blink": [("Eye Closed", 1.0)],
        "blink_l": [("Eye Closed L", 1.0)],
        "blink_r": [("Eye Closed R", 1.0)],

        # --- Mouth / Visemes ---
        "a": [("Mouth", 0.0)],  # Mouth shape key at 0 = open
        "o": [("Mouth", 0.3)],
        "i": [("Mouth", 0.7)],
        "u": [("Mouth", 0.5)],
        "e": [("Mouth", 0.2)],

        # --- Emotions ---
        "angry": [("3. Expression Angry", 1.0)],
        "fun": [("Eye Wink", 1.0)],
        "sorrow": [("1. Expression Embarrassed", 1.0)],
    }

    keys = main_mesh.data.shape_keys.key_blocks
    available_keys = set(keys.keys())

    for preset_name, shape_key_list in expression_mapping.items():
        group = blend_shape_master.blend_shape_groups.add()
        group.preset_name = preset_name
        group.name = preset_name

        for sk_name, sk_value in shape_key_list:
            if sk_name in available_keys:
                bind = group.binds.add()
                bind.mesh.mesh_object_name = main_mesh.name
                bind.index = sk_name
                bind.weight = sk_value

    # Also set up blend shapes on other meshes (EyeLashes, etc.)
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not obj.data.shape_keys or obj == main_mesh:
            continue

        obj_keys = obj.data.shape_keys.key_blocks
        obj_key_names = set(obj_keys.keys())

        # Add eye-related shapes from EyeLashes, EyeLinesLower, etc.
        eye_shapes = {
            "blink": "Eye Closed",
            "blink_l": "Eye Closed L",
            "blink_r": "Eye Closed R",
        }

        for preset_name, sk_name in eye_shapes.items():
            if sk_name in obj_key_names:
                # Find existing group or create
                existing_group = None
                for g in blend_shape_master.blend_shape_groups:
                    if g.name == preset_name:
                        existing_group = g
                        break

                if existing_group:
                    bind = existing_group.binds.add()
                    bind.mesh.mesh_object_name = obj.name
                    bind.index = sk_name
                    bind.weight = 1.0
                    print(f"    Added {sk_name} from {obj.name} to {preset_name}")

    print(f"  Created {len(blend_shape_master.blend_shape_groups)} blend shape groups.")
else:
    print("  WARNING: No mesh with shape keys found!")

# ============================================================
#  STEP 3: VRM META (required for export)
# ============================================================
print("  Setting up VRM metadata...")

meta = vrm0.meta
meta.title = "Tatsumaki VTuber Model"
meta.author = "Custom"
meta.version = "1.0"
meta.allowed_user_name = "Everyone"
meta.violent_ussage_name = "Disallow"  # Note: this is the actual field name
meta.sexual_ussage_name = "Disallow"
meta.commercial_ussage_name = "Allow"
meta.license_name = "Other"

# ============================================================
#  STEP 4: FIRST PERSON (eye tracking settings)
# ============================================================
print("  Setting up first person / eye tracking...")

first_person = vrm0.first_person

# Set the head bone for first person offset
first_person.first_person_bone.bone_name = "head.x"
first_person.first_person_bone_offset = (0, 0.06, 0)

# Look at settings (eye tracking)
look_at = first_person.look_at_type_name
# This controls how eyes move when tracking

# ============================================================
#  DONE - INSTRUCTIONS
# ============================================================
print("")
print("  ╔═══════════════════════════════════════════════════╗")
print("  ║   VRM 0.x SETUP COMPLETE!                         ║")
print("  ║                                                   ║")
print("  ║   Now export:                                     ║")
print("  ║   1. File → Export → VRM (.vrm)                   ║")
print("  ║   2. In the export panel on the right:            ║")
print("  ║      - Set 'Spec Version' to 'VRM 0.0'           ║")
print("  ║   3. Save as: Tatsumaki_VTuber_V0.vrm             ║")
print("  ║   4. Load in VSeeFace!                            ║")
print("  ║                                                   ║")
print("  ╚═══════════════════════════════════════════════════╝")
print("")

# List all bones found for debugging
print("  --- Armature bones available (first 30) ---")
for i, bone_name in enumerate(sorted(armature_bones)):
    if i >= 30:
        print(f"  ... and {len(armature_bones) - 30} more")
        break
    print(f"    {bone_name}")
