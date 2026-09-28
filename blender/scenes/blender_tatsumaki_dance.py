# © 2026 Mathew. All rights reserved.
import bpy
import math

# ============================================================
#   TATSUMAKI DANCE ANIMATION
#   Run this with the Tatsumaki .blend file already open!
# ============================================================

print("Starting Tatsumaki dance animation...")

# --- Find the armature ---
rig = bpy.data.objects.get("Tatsumaki_Rig_rig")
if not rig:
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            rig = obj
            print(f"  Found armature: {obj.name}")
            break

if not rig:
    raise Exception("No armature found! Make sure the Tatsumaki .blend file is open.")

# --- Settings ---
BPM = 125
FPS = 24
FRAMES_PER_BEAT = (FPS * 60) / BPM  # ~11.52
TOTAL_BEATS = 64  # 8 measures of 4/4 time
TOTAL_FRAMES = int(TOTAL_BEATS * FRAMES_PER_BEAT)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES
scene.render.fps = FPS

def beat_to_frame(beat):
    """Convert beat number to frame number."""
    return int(1 + beat * FRAMES_PER_BEAT)

# --- Activate rig and enter pose mode ---
bpy.context.view_layer.objects.active = rig
rig.select_set(True)
bpy.ops.object.mode_set(mode='POSE')

# --- Create a new action so we don't overwrite existing data ---
action_name = "TatsumakiDance"
if action_name in bpy.data.actions:
    bpy.data.actions.remove(bpy.data.actions[action_name])
action = bpy.data.actions.new(name=action_name)
rig.animation_data_create()
rig.animation_data.action = action

# --- Helper functions ---
def pb(name):
    """Get pose bone by name."""
    return rig.pose.bones.get(name)

def key_loc(bone_name, frame, loc):
    """Keyframe bone location."""
    bone = pb(bone_name)
    if not bone:
        return
    bone.location = loc
    bone.keyframe_insert(data_path='location', frame=frame)

def key_rot(bone_name, frame, rot):
    """Keyframe bone rotation (euler)."""
    bone = pb(bone_name)
    if not bone:
        return
    bone.rotation_mode = 'XYZ'
    bone.rotation_euler = [math.radians(r) for r in rot]
    bone.keyframe_insert(data_path='rotation_euler', frame=frame)

def key_scale(bone_name, frame, scale):
    """Keyframe bone scale."""
    bone = pb(bone_name)
    if not bone:
        return
    bone.scale = scale
    bone.keyframe_insert(data_path='scale', frame=frame)

# --- Reset all pose bones to rest position ---
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.pose.rot_clear()
bpy.ops.pose.loc_clear()
bpy.ops.pose.scale_clear()
bpy.ops.pose.select_all(action='DESELECT')

print("  Rig found and reset. Building dance keyframes...")

# ============================================================
#  DANCE CHOREOGRAPHY
#  8 measures, 4 beats each, 125 BPM
#
#  Measures 1-2: Bounce start + gentle sway
#  Measures 3-4: Arms up wave + hip sway
#  Measures 5-6: Side stepping + arm pump
#  Measures 7-8: Spin + finale pose
# ============================================================

# Key control bones:
# Root/hips:    c_root.x (location for bounce, rotation for sway)
# Spine:        c_spine_01.x, c_spine_02.x
# Head:         c_head.x
# Arms FK:      c_arm_fk.l/r, c_forearm_fk.l/r, c_hand_fk.l/r
# Feet IK:      c_foot_ik.l/r
# Traj:         c_traj (master position)

# -----------------------------------------------
#  CONTINUOUS HIP BOUNCE (the rhythmic foundation)
# -----------------------------------------------
print("  Adding hip bounce...")
for beat in range(TOTAL_BEATS + 1):
    frame = beat_to_frame(beat)

    # Bounce: down on beat, up on off-beat
    bounce_y = -0.03 * abs(math.sin(beat * math.pi))

    # Sway: gentle side-to-side
    sway_x = 0.015 * math.sin(beat * math.pi * 0.5)

    # Hip rotation sway
    hip_tilt = 4 * math.sin(beat * math.pi * 0.5)

    key_loc("c_root.x", frame, (sway_x, 0, bounce_y))
    key_rot("c_root.x", frame, (0, 0, hip_tilt))

# -----------------------------------------------
#  CONTINUOUS SPINE WAVE
# -----------------------------------------------
print("  Adding spine movement...")
for beat_idx in range(TOTAL_BEATS * 2 + 1):  # half-beat resolution
    beat = beat_idx * 0.5
    frame = beat_to_frame(beat)

    # Spine follows hips with delay
    spine1_rot = 3 * math.sin(beat * math.pi * 0.5 - 0.3)
    spine2_rot = 2 * math.sin(beat * math.pi * 0.5 - 0.6)

    # Forward/back chest movement
    spine2_fwd = 2 * math.sin(beat * math.pi)

    key_rot("c_spine_01.x", frame, (spine2_fwd * 0.3, 0, spine1_rot))
    key_rot("c_spine_02.x", frame, (spine2_fwd * 0.5, 0, spine2_rot))

# -----------------------------------------------
#  HEAD BOB
# -----------------------------------------------
print("  Adding head movement...")
for beat_idx in range(TOTAL_BEATS * 2 + 1):
    beat = beat_idx * 0.5
    frame = beat_to_frame(beat)

    head_tilt = 5 * math.sin(beat * math.pi * 0.5 - 0.5)
    head_nod = 3 * math.sin(beat * math.pi - 0.2)

    key_rot("c_head.x", frame, (head_nod, 0, head_tilt))

# -----------------------------------------------
#  MEASURES 1-2: Gentle start, arms at sides swaying
# -----------------------------------------------
print("  Choreographing measures 1-2...")
for beat in range(0, 8):
    frame = beat_to_frame(beat)
    t = beat / 8.0  # ramp up energy

    # Arms gently sway at sides
    arm_swing = 10 * t * math.sin(beat * math.pi * 0.5)

    key_rot("c_arm_fk.l", frame, (arm_swing, 0, -5))
    key_rot("c_arm_fk.r", frame, (-arm_swing, 0, 5))
    key_rot("c_forearm_fk.l", frame, (0, 0, -10 - 5 * t))
    key_rot("c_forearm_fk.r", frame, (0, 0, 10 + 5 * t))

# -----------------------------------------------
#  MEASURES 3-4: Arms up wave + bigger sway
# -----------------------------------------------
print("  Choreographing measures 3-4...")

# Beat 8: Arms start rising
key_rot("c_arm_fk.l", beat_to_frame(8), (-40, 10, -20))
key_rot("c_arm_fk.r", beat_to_frame(8), (-40, -10, 20))
key_rot("c_forearm_fk.l", beat_to_frame(8), (0, 0, -40))
key_rot("c_forearm_fk.r", beat_to_frame(8), (0, 0, 40))

# Beat 9-10: Arms up, wave left
key_rot("c_arm_fk.l", beat_to_frame(9), (-80, 20, -30))
key_rot("c_arm_fk.r", beat_to_frame(9), (-60, -10, 15))
key_rot("c_forearm_fk.l", beat_to_frame(9), (0, 0, -50))
key_rot("c_forearm_fk.r", beat_to_frame(9), (0, 0, 50))
key_rot("c_hand_fk.l", beat_to_frame(9), (0, 20, 0))
key_rot("c_hand_fk.r", beat_to_frame(9), (0, -20, 0))

# Beat 10: Wave right
key_rot("c_arm_fk.l", beat_to_frame(10), (-60, -10, -15))
key_rot("c_arm_fk.r", beat_to_frame(10), (-80, -20, 30))
key_rot("c_forearm_fk.l", beat_to_frame(10), (0, 0, -50))
key_rot("c_forearm_fk.r", beat_to_frame(10), (0, 0, 50))
key_rot("c_hand_fk.l", beat_to_frame(10), (0, -20, 0))
key_rot("c_hand_fk.r", beat_to_frame(10), (0, 20, 0))

# Beat 11: Wave left again
key_rot("c_arm_fk.l", beat_to_frame(11), (-80, 20, -30))
key_rot("c_arm_fk.r", beat_to_frame(11), (-60, -10, 15))
key_rot("c_hand_fk.l", beat_to_frame(11), (0, 20, 10))
key_rot("c_hand_fk.r", beat_to_frame(11), (0, -20, -10))

# Beat 12: Wave right
key_rot("c_arm_fk.l", beat_to_frame(12), (-60, -10, -15))
key_rot("c_arm_fk.r", beat_to_frame(12), (-80, -20, 30))
key_rot("c_hand_fk.l", beat_to_frame(12), (0, -15, -10))
key_rot("c_hand_fk.r", beat_to_frame(12), (0, 15, 10))

# Beat 13-14: Arms cross and uncross
key_rot("c_arm_fk.l", beat_to_frame(13), (-50, 30, -10))
key_rot("c_arm_fk.r", beat_to_frame(13), (-50, -30, 10))
key_rot("c_forearm_fk.l", beat_to_frame(13), (0, 0, -80))
key_rot("c_forearm_fk.r", beat_to_frame(13), (0, 0, 80))

key_rot("c_arm_fk.l", beat_to_frame(14), (-70, -15, -25))
key_rot("c_arm_fk.r", beat_to_frame(14), (-70, 15, 25))
key_rot("c_forearm_fk.l", beat_to_frame(14), (0, 0, -30))
key_rot("c_forearm_fk.r", beat_to_frame(14), (0, 0, 30))

# Beat 15: Arms come down
key_rot("c_arm_fk.l", beat_to_frame(15), (-30, 0, -15))
key_rot("c_arm_fk.r", beat_to_frame(15), (-30, 0, 15))
key_rot("c_forearm_fk.l", beat_to_frame(15), (0, 0, -20))
key_rot("c_forearm_fk.r", beat_to_frame(15), (0, 0, 20))

# -----------------------------------------------
#  MEASURES 5-6: Step dance + arm pump
# -----------------------------------------------
print("  Choreographing measures 5-6...")

for beat in range(16, 32):
    frame = beat_to_frame(beat)
    local_beat = beat - 16

    # Alternating arm pumps
    if local_beat % 2 == 0:
        # Right arm up, left down
        key_rot("c_arm_fk.l", frame, (-20, 0, -10))
        key_rot("c_arm_fk.r", frame, (-90, -15, 20))
        key_rot("c_forearm_fk.l", frame, (0, 0, -30))
        key_rot("c_forearm_fk.r", frame, (0, -30, 60))
        key_rot("c_hand_fk.r", frame, (0, 0, 15))
    else:
        # Left arm up, right down
        key_rot("c_arm_fk.l", frame, (-90, 15, -20))
        key_rot("c_arm_fk.r", frame, (-20, 0, 10))
        key_rot("c_forearm_fk.l", frame, (0, 30, -60))
        key_rot("c_forearm_fk.r", frame, (0, 0, 30))
        key_rot("c_hand_fk.l", frame, (0, 0, -15))

    # Stepping side to side with feet
    step_offset = 0.06 * math.sin(local_beat * math.pi * 0.5)
    step_height = 0.02 * abs(math.sin(local_beat * math.pi))

    key_loc("c_foot_ik.l", frame, (step_offset, 0, step_height if local_beat % 4 < 2 else 0))
    key_loc("c_foot_ik.r", frame, (-step_offset, 0, 0 if local_beat % 4 < 2 else step_height))

    # Extra spine twist for energy
    twist = 8 * math.sin(local_beat * math.pi * 0.5)
    key_rot("c_spine_02.x", frame, (3, twist * 0.5, twist))

# -----------------------------------------------
#  MEASURES 7-8: Spin + finale
# -----------------------------------------------
print("  Choreographing measures 7-8 (finale)...")

# Beat 32-35: Build up — arms out to sides
for beat in range(32, 36):
    frame = beat_to_frame(beat)
    t = (beat - 32) / 4.0

    # Arms spread wide
    arm_out = -40 - t * 50
    key_rot("c_arm_fk.l", frame, (arm_out * 0.3, 0, arm_out))
    key_rot("c_arm_fk.r", frame, (arm_out * 0.3, 0, -arm_out))
    key_rot("c_forearm_fk.l", frame, (0, 0, -20))
    key_rot("c_forearm_fk.r", frame, (0, 0, 20))

    # Reset feet
    key_loc("c_foot_ik.l", frame, (0, 0, 0))
    key_loc("c_foot_ik.r", frame, (0, 0, 0))

# Beat 36-43: Spin! (rotate the root/trajectory)
spin_start = 36
spin_end = 44
spin_beats = spin_end - spin_start

for beat_sub in range(spin_beats * 4 + 1):  # quarter-beat resolution for smooth spin
    beat = spin_start + beat_sub * 0.25
    frame = beat_to_frame(beat)
    t = (beat - spin_start) / spin_beats

    # Full 360 spin
    spin_angle = t * 360

    key_rot("c_root_master.x", frame, (0, 0, spin_angle))

    # Arms pull in during spin, then out
    if t < 0.5:
        arm_angle = -60 + t * 40
        forearm = -60
    else:
        arm_angle = -40 - (t - 0.5) * 60
        forearm = -30

    key_rot("c_arm_fk.l", frame, (arm_angle * 0.3, 0, arm_angle))
    key_rot("c_arm_fk.r", frame, (arm_angle * 0.3, 0, -arm_angle))
    key_rot("c_forearm_fk.l", frame, (0, 0, forearm))
    key_rot("c_forearm_fk.r", frame, (0, 0, -forearm))

# Beat 44-48: Spin stops, feet reset
key_rot("c_root_master.x", beat_to_frame(44), (0, 0, 360))

# Beat 48-56: Victory arm pump sequence
print("  Adding victory sequence...")
for beat in range(44, 52):
    frame = beat_to_frame(beat)
    local = beat - 44

    if local % 4 == 0:
        # Both arms up!
        key_rot("c_arm_fk.l", frame, (-120, 15, -30))
        key_rot("c_arm_fk.r", frame, (-120, -15, 30))
        key_rot("c_forearm_fk.l", frame, (0, 0, -40))
        key_rot("c_forearm_fk.r", frame, (0, 0, 40))
    elif local % 4 == 1:
        key_rot("c_arm_fk.l", frame, (-100, 10, -25))
        key_rot("c_arm_fk.r", frame, (-100, -10, 25))
        key_rot("c_forearm_fk.l", frame, (0, 0, -50))
        key_rot("c_forearm_fk.r", frame, (0, 0, 50))
    elif local % 4 == 2:
        # Fist pump right
        key_rot("c_arm_fk.l", frame, (-40, 0, -15))
        key_rot("c_arm_fk.r", frame, (-130, -20, 25))
        key_rot("c_forearm_fk.l", frame, (0, 0, -30))
        key_rot("c_forearm_fk.r", frame, (0, -40, 70))
    else:
        # Fist pump left
        key_rot("c_arm_fk.l", frame, (-130, 20, -25))
        key_rot("c_arm_fk.r", frame, (-40, 0, 15))
        key_rot("c_forearm_fk.l", frame, (0, 40, -70))
        key_rot("c_forearm_fk.r", frame, (0, 0, 30))

    key_loc("c_foot_ik.l", frame, (0, 0, 0))
    key_loc("c_foot_ik.r", frame, (0, 0, 0))

# Beat 52-56: Cool down to rest
for beat in range(52, 57):
    frame = beat_to_frame(beat)
    t = (beat - 52) / 4.0

    key_rot("c_arm_fk.l", frame, (-120 * (1 - t), 15 * (1 - t), -30 * (1 - t)))
    key_rot("c_arm_fk.r", frame, (-120 * (1 - t), -15 * (1 - t), 30 * (1 - t)))
    key_rot("c_forearm_fk.l", frame, (0, 0, -40 * (1 - t)))
    key_rot("c_forearm_fk.r", frame, (0, 0, 40 * (1 - t)))

# Final rest at beat 56-64
for beat in range(57, 65):
    frame = beat_to_frame(beat)
    key_rot("c_arm_fk.l", frame, (0, 0, -5))
    key_rot("c_arm_fk.r", frame, (0, 0, 5))
    key_rot("c_forearm_fk.l", frame, (0, 0, -10))
    key_rot("c_forearm_fk.r", frame, (0, 0, 10))
    key_rot("c_root_master.x", frame, (0, 0, 360))

# -----------------------------------------------
#  SHOULDER MOVEMENT (follows arms, adds life)
# -----------------------------------------------
print("  Adding shoulder movement...")
for beat_idx in range(TOTAL_BEATS * 2 + 1):
    beat = beat_idx * 0.5
    frame = beat_to_frame(beat)

    shoulder_shrug = 3 * math.sin(beat * math.pi)
    key_rot("c_shoulder.l", frame, (shoulder_shrug, 0, 0))
    key_rot("c_shoulder.r", frame, (-shoulder_shrug, 0, 0))

# ============================================================
#  SHAPE KEY ANIMATIONS (expressions!)
# ============================================================
print("  Adding facial expressions...")

# Find mesh objects with shape keys
for obj in bpy.data.objects:
    if obj.type != 'MESH' or not obj.data.shape_keys:
        continue

    keys = obj.data.shape_keys.key_blocks

    # --- Blinking ---
    for key_name in ["Eye Closed", "Eye Closed L", "Eye Closed R"]:
        sk = keys.get(key_name)
        if not sk:
            continue

        # Blink at specific beats
        blink_beats = [4, 12, 20, 28, 36, 44, 50, 58]
        for blink_beat in blink_beats:
            f = beat_to_frame(blink_beat)
            # Open -> closed -> open (3 frames)
            sk.value = 0.0
            sk.keyframe_insert("value", frame=f - 3)
            sk.value = 1.0
            sk.keyframe_insert("value", frame=f)
            sk.value = 0.0
            sk.keyframe_insert("value", frame=f + 3)

    # --- Mouth open on energetic sections ---
    sk_mouth = keys.get("Mouth")
    if sk_mouth:
        # Mouth more open during energetic parts
        for beat in range(0, TOTAL_BEATS + 1, 2):
            f = beat_to_frame(beat)
            if 16 <= beat <= 48:  # energetic section
                sk_mouth.value = 0.7 + 0.3 * abs(math.sin(beat * math.pi * 0.5))
            else:
                sk_mouth.value = 1.0
            sk_mouth.keyframe_insert("value", frame=f)

    # --- Expression: Embarrassed during first measures, then switch ---
    sk_embarrassed = keys.get("1. Expression Embarrassed")
    if sk_embarrassed:
        # Shy at start
        sk_embarrassed.value = 0.4
        sk_embarrassed.keyframe_insert("value", frame=1)
        sk_embarrassed.value = 0.6
        sk_embarrassed.keyframe_insert("value", frame=beat_to_frame(4))
        # Fade out as she gets into it
        sk_embarrassed.value = 0.2
        sk_embarrassed.keyframe_insert("value", frame=beat_to_frame(12))
        sk_embarrassed.value = 0.0
        sk_embarrassed.keyframe_insert("value", frame=beat_to_frame(16))

    # --- Eye wink during pose moments ---
    sk_wink = keys.get("Eye Wink R")
    if sk_wink:
        for wink_beat in [24, 48]:
            f = beat_to_frame(wink_beat)
            sk_wink.value = 0.0
            sk_wink.keyframe_insert("value", frame=f - 2)
            sk_wink.value = 1.0
            sk_wink.keyframe_insert("value", frame=f)
            sk_wink.value = 1.0
            sk_wink.keyframe_insert("value", frame=f + 6)
            sk_wink.value = 0.0
            sk_wink.keyframe_insert("value", frame=f + 8)

# ============================================================
#  FINALIZE
# ============================================================
bpy.ops.object.mode_set(mode='OBJECT')

# Set to frame 1 and play
scene.frame_set(1)

# Switch to material preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                break

bpy.ops.screen.animation_play()

print("")
print("  ╔════════════════════════════════════════════════╗")
print("  ║   TATSUMAKI DANCE — Animation Complete!        ║")
print("  ║                                                ║")
print("  ║   64 beats @ 125 BPM (~30 seconds)            ║")
print("  ║   Measures 1-2: Gentle bounce & sway          ║")
print("  ║   Measures 3-4: Arms up wave                  ║")
print("  ║   Measures 5-6: Step dance + arm pump         ║")
print("  ║   Measures 7-8: Spin + victory + cool down    ║")
print("  ║                                                ║")
print("  ║   Includes: blinking, expressions, winks      ║")
print("  ║                                                ║")
print("  ║   Space = play/pause | Numpad 0 = camera      ║")
print("  ║   Left/Right arrows = scrub through frames    ║")
print("  ╚════════════════════════════════════════════════╝")
print("")
