# © 2026 Mathew. All rights reserved.
import bpy
import math
import random

# ============================================================
#   CHIBI VTUBER — Procedural Anime Character
# ============================================================

random.seed(99)

# --- Nuke scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in bpy.data.meshes:
    bpy.data.meshes.remove(m)
for m in bpy.data.materials:
    bpy.data.materials.remove(m)
for c in bpy.data.curves:
    bpy.data.curves.remove(c)
for a in bpy.data.armatures:
    bpy.data.armatures.remove(a)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 360
scene.render.fps = 24

# Switch to EEVEE for toon shading (Shader to RGB only works in EEVEE)
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in dir(bpy.types) else 'BLENDER_EEVEE'

# ---- MATERIALS ----

def flat_mat(name, color, outline=False):
    """Toon/flat shaded material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (600, 0)

    diffuse = nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (*color, 1.0)
    diffuse.location = (0, 0)

    # Shader to RGB for toon effect
    s2rgb = nodes.new('ShaderNodeShaderToRGB')
    s2rgb.location = (200, 0)
    links.new(diffuse.outputs['BSDF'], s2rgb.inputs['Shader'])

    # ColorRamp for cell shading (2-3 tone)
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (400, 0)
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position = 0.0
    # Shadow color (darker version)
    sr, sg, sb = [max(0, c * 0.5) for c in color]
    ramp.color_ramp.elements[0].color = (sr, sg, sb, 1.0)
    ramp.color_ramp.elements[1].position = 0.35
    ramp.color_ramp.elements[1].color = (*color, 1.0)

    links.new(s2rgb.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], output.inputs['Surface'])

    return mat

def emissive_mat(name, color, strength=3.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def simple_mat(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat

# Define colors
SKIN = (1.0, 0.85, 0.75)
HAIR = (0.35, 0.55, 0.95)       # Blue anime hair
HAIR_DARK = (0.2, 0.35, 0.75)
EYE_COLOR = (0.2, 0.7, 1.0)     # Bright blue
EYE_DARK = (0.05, 0.2, 0.5)
WHITE = (1.0, 1.0, 1.0)
BLACK = (0.02, 0.02, 0.02)
BLUSH = (1.0, 0.6, 0.6)
MOUTH = (0.9, 0.45, 0.45)
OUTFIT = (0.9, 0.9, 0.95)       # White hoodie
OUTFIT_ACCENT = (0.35, 0.55, 0.95)  # Blue accents
RIBBON = (1.0, 0.4, 0.6)        # Pink ribbon

print("Building VTuber character...")

# Create all materials
skin_mat = flat_mat("Skin", SKIN)
hair_mat = flat_mat("Hair", HAIR)
hair_dark_mat = flat_mat("HairDark", HAIR_DARK)
eye_white_mat = simple_mat("EyeWhite", WHITE)
iris_mat = emissive_mat("Iris", EYE_COLOR, 0.5)
pupil_mat = simple_mat("Pupil", BLACK)
highlight_mat = emissive_mat("Highlight", WHITE, 5.0)
blush_mat = flat_mat("Blush", BLUSH)
mouth_mat = simple_mat("Mouth", MOUTH)
outfit_mat = flat_mat("Outfit", OUTFIT)
accent_mat = flat_mat("Accent", OUTFIT_ACCENT)
ribbon_mat = flat_mat("Ribbon", RIBBON)
black_mat = simple_mat("Black", BLACK)

# Helper to set smooth shading
def smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

# ============================================
#  HEAD
# ============================================
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 5.5))
head = bpy.context.active_object
head.name = "Head"
head.scale = (1.0, 0.95, 1.05)
head.data.materials.append(skin_mat)
smooth(head)

# Chin area — slight elongation
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.55, location=(0, -0.2, 4.8))
chin = bpy.context.active_object
chin.name = "Chin"
chin.scale = (0.85, 0.7, 0.9)
chin.data.materials.append(skin_mat)
smooth(chin)

# ============================================
#  EYES — Large anime style
# ============================================
for side, sx in [("L", -0.38), ("R", 0.38)]:
    # Eye white (sclera)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(sx, -0.78, 5.55))
    sclera = bpy.context.active_object
    sclera.name = f"Sclera_{side}"
    sclera.scale = (0.85, 0.5, 1.1)
    sclera.data.materials.append(eye_white_mat)
    smooth(sclera)

    # Iris (large, colored)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(sx, -0.95, 5.5))
    iris = bpy.context.active_object
    iris.name = f"Iris_{side}"
    iris.scale = (0.75, 0.4, 0.95)
    iris.data.materials.append(iris_mat)
    smooth(iris)

    # Pupil
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(sx, -1.02, 5.48))
    pupil = bpy.context.active_object
    pupil.name = f"Pupil_{side}"
    pupil.scale = (0.7, 0.4, 0.85)
    pupil.data.materials.append(pupil_mat)
    smooth(pupil)

    # Highlight (big sparkle — top right)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(sx + 0.08, -1.05, 5.62))
    hl1 = bpy.context.active_object
    hl1.name = f"Highlight1_{side}"
    hl1.data.materials.append(highlight_mat)
    smooth(hl1)

    # Highlight (small sparkle — bottom left)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(sx - 0.05, -1.05, 5.42))
    hl2 = bpy.context.active_object
    hl2.name = f"Highlight2_{side}"
    hl2.data.materials.append(highlight_mat)
    smooth(hl2)

    # Upper eyelid (for blink animation)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(sx, -0.76, 5.7))
    lid = bpy.context.active_object
    lid.name = f"Eyelid_{side}"
    lid.scale = (0.9, 0.55, 0.5)
    lid.data.materials.append(skin_mat)
    smooth(lid)

    # Eyelash line
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(sx, -0.92, 5.72))
    lash = bpy.context.active_object
    lash.name = f"Eyelash_{side}"
    lash.scale = (2.8, 0.3, 0.15)
    lash.data.materials.append(black_mat)

    # Eyebrow
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(sx, -0.82, 5.95))
    brow = bpy.context.active_object
    brow.name = f"Eyebrow_{side}"
    brow.scale = (2.2, 0.3, 0.15)
    brow.rotation_euler.z = -0.1 * (1 if side == "L" else -1)
    brow.data.materials.append(hair_dark_mat)

# ============================================
#  BLUSH MARKS
# ============================================
for side, sx in [("L", -0.55), ("R", 0.55)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(sx, -0.8, 5.25))
    blush = bpy.context.active_object
    blush.name = f"Blush_{side}"
    blush.scale = (1.2, 0.5, 0.6)
    blush.data.materials.append(blush_mat)
    smooth(blush)

# ============================================
#  NOSE (tiny, anime style)
# ============================================
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=(0, -0.92, 5.3))
nose = bpy.context.active_object
nose.name = "Nose"
nose.data.materials.append(skin_mat)
smooth(nose)

# ============================================
#  MOUTH
# ============================================
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, -0.85, 5.05))
mouth = bpy.context.active_object
mouth.name = "Mouth"
mouth.scale = (1.8, 0.7, 0.6)
mouth.data.materials.append(mouth_mat)
smooth(mouth)

# Little fang (cute anime fang)
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.03, depth=0.06, location=(0.08, -0.9, 5.02))
fang = bpy.context.active_object
fang.name = "Fang"
fang.rotation_euler = (math.radians(180), 0, 0)
fang.data.materials.append(simple_mat("Fang", WHITE))

# ============================================
#  EARS
# ============================================
for side, sx in [("L", -0.9), ("R", 0.9)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(sx, -0.25, 5.4))
    ear = bpy.context.active_object
    ear.name = f"Ear_{side}"
    ear.scale = (0.4, 0.6, 0.9)
    ear.data.materials.append(skin_mat)
    smooth(ear)

# ============================================
#  CAT EARS (classic VTuber!)
# ============================================
for side, sx in [("L", -0.55), ("R", 0.55)]:
    # Outer ear
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.35, depth=0.7, location=(sx, -0.1, 6.55))
    cat_ear = bpy.context.active_object
    cat_ear.name = f"CatEar_{side}"
    cat_ear.rotation_euler = (math.radians(10), math.radians(15 * (1 if side == "L" else -1)), 0)
    cat_ear.data.materials.append(hair_mat)
    smooth(cat_ear)

    # Inner ear (pink)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.2, depth=0.5, location=(sx, -0.18, 6.5))
    inner_ear = bpy.context.active_object
    inner_ear.name = f"CatEarInner_{side}"
    inner_ear.rotation_euler = (math.radians(10), math.radians(15 * (1 if side == "L" else -1)), 0)
    inner_ear.data.materials.append(ribbon_mat)
    smooth(inner_ear)

# ============================================
#  HAIR — Anime style with bangs and side strands
# ============================================
# Main hair volume (back)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0, 0.1, 5.6))
hair_back = bpy.context.active_object
hair_back.name = "HairBack"
hair_back.scale = (1.05, 1.0, 1.1)
hair_back.data.materials.append(hair_mat)
smooth(hair_back)

# Hair top volume
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(0, -0.2, 6.2))
hair_top = bpy.context.active_object
hair_top.name = "HairTop"
hair_top.scale = (1.3, 1.1, 0.7)
hair_top.data.materials.append(hair_mat)
smooth(hair_top)

# Bangs (fringe pieces across forehead)
bang_positions = [
    (-0.5, -0.8, 5.95, 0.15, 0.08, 0.4, -0.15),
    (-0.25, -0.85, 5.9, 0.13, 0.08, 0.45, -0.05),
    (0.0, -0.87, 5.88, 0.14, 0.08, 0.48, 0.0),
    (0.25, -0.85, 5.9, 0.13, 0.08, 0.45, 0.05),
    (0.5, -0.8, 5.95, 0.15, 0.08, 0.4, 0.15),
]

for bi, (bx, by, bz, sx, sy, sz, rot) in enumerate(bang_positions):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(bx, by, bz))
    bang = bpy.context.active_object
    bang.name = f"Bang_{bi}"
    bang.scale = (sx / 0.3, sy / 0.3, sz / 0.3)
    bang.rotation_euler.z = rot
    bang.data.materials.append(hair_mat)
    smooth(bang)

# Side hair strands (long, flowing)
for side, sx_base in [("L", -0.85), ("R", 0.85)]:
    for si in range(5):
        t = si / 5.0
        z = 5.5 - t * 3.5
        x = sx_base * (1.0 + t * 0.3)
        y = -0.3 + t * 0.4

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18 - t * 0.03, location=(x, y, z))
        strand = bpy.context.active_object
        strand.name = f"SideHair_{side}_{si}"
        strand.scale = (0.7, 0.7, 1.2)
        strand.data.materials.append(hair_mat if si % 2 == 0 else hair_dark_mat)
        smooth(strand)

# Back hair (long flowing strands down the back)
for si in range(8):
    t = si / 8.0
    angle = (t - 0.5) * 1.2
    x = math.sin(angle) * 0.6
    y = 0.5 + t * 0.8
    z = 5.3 - t * 4.0

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25 - t * 0.02, location=(x, y, z))
    back_strand = bpy.context.active_object
    back_strand.name = f"BackHair_{si}"
    back_strand.scale = (1.5, 0.8, 1.3)
    back_strand.data.materials.append(hair_mat if si % 3 != 0 else hair_dark_mat)
    smooth(back_strand)

# Ahoge (antenna hair — anime staple!)
ahoge_pts = [(0, -0.3, 6.6), (0.1, -0.5, 7.0), (0.25, -0.4, 7.3), (0.15, -0.2, 7.5)]
for ai, (ax, ay, az) in enumerate(ahoge_pts):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06 - ai * 0.01, location=(ax, ay, az))
    ahoge = bpy.context.active_object
    ahoge.name = f"Ahoge_{ai}"
    ahoge.scale = (0.8, 0.8, 1.5)
    ahoge.data.materials.append(hair_mat)
    smooth(ahoge)

print("  Head & hair done")

# ============================================
#  RIBBON / HAIR ACCESSORY
# ============================================
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0.6, -0.4, 5.9))
ribbon_center = bpy.context.active_object
ribbon_center.name = "RibbonCenter"
ribbon_center.data.materials.append(ribbon_mat)

for ri, (rx, ry, rz, rsx) in enumerate([
    (0.75, -0.35, 6.05, 0.2), (0.45, -0.35, 6.05, 0.2),
    (0.75, -0.35, 5.75, 0.15), (0.45, -0.35, 5.75, 0.15)
]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(rx, ry, rz))
    bow = bpy.context.active_object
    bow.name = f"Bow_{ri}"
    bow.scale = (rsx / 0.1, 0.6, 1.2)
    bow.data.materials.append(ribbon_mat)
    smooth(bow)

# ============================================
#  BODY — Cute hoodie/outfit
# ============================================
# Neck
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.4, location=(0, 0, 4.5))
neck = bpy.context.active_object
neck.name = "Neck"
neck.data.materials.append(skin_mat)
smooth(neck)

# Torso (hoodie)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(0, 0.05, 3.5))
torso = bpy.context.active_object
torso.name = "Torso"
torso.scale = (1.0, 0.75, 1.2)
torso.data.materials.append(outfit_mat)
smooth(torso)

# Hood collar
bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.12, location=(0, -0.1, 4.3))
collar = bpy.context.active_object
collar.name = "Collar"
collar.scale = (1.1, 0.9, 0.6)
collar.data.materials.append(outfit_mat)
smooth(collar)

# Hoodie pocket (front detail)
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, -0.62, 3.1))
pocket = bpy.context.active_object
pocket.name = "Pocket"
pocket.scale = (5, 0.5, 2)
pocket.data.materials.append(accent_mat)

# Hoodie strings
for side, hsx in [("L", -0.08), ("R", 0.08)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.6, location=(hsx, -0.55, 3.9))
    string = bpy.context.active_object
    string.name = f"HoodieString_{side}"
    string.data.materials.append(accent_mat)

# ============================================
#  ARMS
# ============================================
for side, sx in [("L", -1.0), ("R", 1.0)]:
    # Upper arm
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(sx * 0.9, 0, 3.8))
    shoulder = bpy.context.active_object
    shoulder.name = f"Shoulder_{side}"
    shoulder.scale = (0.8, 0.75, 1.0)
    shoulder.data.materials.append(outfit_mat)
    smooth(shoulder)

    # Lower arm (sleeve)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.8, location=(sx * 1.1, -0.1, 3.2))
    arm = bpy.context.active_object
    arm.name = f"Arm_{side}"
    arm.rotation_euler = (math.radians(10), math.radians(-15 * (1 if side == "L" else -1)), 0)
    arm.data.materials.append(outfit_mat)
    smooth(arm)

    # Sleeve cuff
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.06, location=(sx * 1.15, -0.15, 2.8))
    cuff = bpy.context.active_object
    cuff.name = f"Cuff_{side}"
    cuff.data.materials.append(accent_mat)
    smooth(cuff)

    # Hand
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(sx * 1.2, -0.2, 2.6))
    hand = bpy.context.active_object
    hand.name = f"Hand_{side}"
    hand.scale = (0.9, 0.7, 1.0)
    hand.data.materials.append(skin_mat)
    smooth(hand)

print("  Body done")

# ============================================
#  LOWER BODY (skirt area)
# ============================================
bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=1.0, radius2=0.7, depth=1.2, location=(0, 0.05, 2.5))
skirt = bpy.context.active_object
skirt.name = "Skirt"
skirt.data.materials.append(accent_mat)
smooth(skirt)

# ============================================
#  ANIMATION — Idle motions
# ============================================

# Collect all character objects
char_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' or obj.type == 'CURVE']

# Group everything under an empty
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
char_root = bpy.context.active_object
char_root.name = "VTuber_Root"

# Parent all to root
for obj in char_objects:
    if obj.parent is None:
        obj.parent = char_root

# Breathing / idle bob animation on root
for frame in range(1, 361):
    t = frame / 360.0
    bob_z = 0.05 * math.sin(frame * 0.08)
    bob_x = 0.02 * math.sin(frame * 0.04)
    tilt = 0.03 * math.sin(frame * 0.06)

    char_root.location = (bob_x, 0, bob_z)
    char_root.rotation_euler = (tilt * 0.5, 0, tilt)
    char_root.keyframe_insert(data_path="location", frame=frame)
    char_root.keyframe_insert(data_path="rotation_euler", frame=frame)

# Blink animation (move eyelids down periodically)
for side in ["L", "R"]:
    lid = bpy.data.objects.get(f"Eyelid_{side}")
    if lid:
        for frame in range(1, 361):
            # Blink at frames ~60, 120, 200, 280
            blink_frames = [60, 62, 64, 120, 122, 124, 200, 202, 204, 280, 282, 284]
            if frame in blink_frames:
                lid.location.z = 5.5  # Eyelid drops to cover eye
            else:
                lid.location.z = 5.7  # Normal open position
            lid.keyframe_insert(data_path="location", index=2, frame=frame)

# Ahoge wiggle
for ai in range(4):
    ahoge = bpy.data.objects.get(f"Ahoge_{ai}")
    if ahoge:
        base_x, base_y, base_z = ahoge.location
        for frame in range(1, 361):
            wiggle = 0.05 * (ai + 1) * math.sin(frame * 0.2 + ai)
            ahoge.location.x = base_x + wiggle
            ahoge.keyframe_insert(data_path="location", index=0, frame=frame)

# Cat ear twitch (occasional)
for side in ["L", "R"]:
    ear = bpy.data.objects.get(f"CatEar_{side}")
    if ear:
        base_rot = ear.rotation_euler.y
        for frame in range(1, 361):
            twitch = 0
            if frame in range(90, 100) or frame in range(220, 230):
                twitch = 0.2 * math.sin((frame % 10) * 0.8)
            ear.rotation_euler.y = base_rot + twitch * (1 if side == "L" else -1)
            ear.keyframe_insert(data_path="rotation_euler", index=1, frame=frame)

print("  Animations done")

# ============================================
#  ENVIRONMENT
# ============================================
# Soft pastel background
world = bpy.data.worlds.get("World")
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.85, 0.88, 0.95, 1.0)
        bg.inputs["Strength"].default_value = 1.0

# Floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 1.8))
floor = bpy.context.active_object
floor.name = "Floor"
floor.data.materials.append(simple_mat("FloorMat", (0.9, 0.85, 0.95)))

# ============================================
#  LIGHTING (soft anime lighting)
# ============================================
# Key light (warm, from front-above)
bpy.ops.object.light_add(type='AREA', location=(2, -5, 8))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 150
key.data.size = 5
key.data.color = (1.0, 0.95, 0.9)
key.rotation_euler = (math.radians(50), 0, math.radians(10))

# Fill light (cool, from side)
bpy.ops.object.light_add(type='AREA', location=(-4, -3, 6))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 60
fill.data.size = 3
fill.data.color = (0.85, 0.9, 1.0)

# Rim light (behind, for edge definition)
bpy.ops.object.light_add(type='AREA', location=(0, 4, 7))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 100
rim.data.size = 4
rim.data.color = (0.9, 0.95, 1.0)
rim.rotation_euler = (math.radians(120), 0, 0)

# ============================================
#  CAMERA
# ============================================
bpy.ops.object.camera_add(location=(0, -6.5, 5.2))
cam = bpy.context.active_object
cam.name = "VTuberCam"
cam.data.lens = 65  # Slightly telephoto for portrait
cam.rotation_euler = (math.radians(78), 0, 0)
scene.camera = cam

# ============================================
#  VIEWPORT
# ============================================
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                space.clip_end = 500
                break

scene.frame_set(1)
bpy.ops.screen.animation_play()

print("")
print("  ╔════════════════════════════════════════╗")
print("  ║   CHIBI VTUBER — Procedural Anime      ║")
print("  ║                                        ║")
print("  ║   Blue hair + cat ears + ahoge         ║")
print("  ║   Anime eyes with sparkle highlights   ║")
print("  ║   Blush marks + fang + ribbon          ║")
print("  ║   White hoodie with blue accents       ║")
print("  ║   Animated: breathing, blinking,       ║")
print("  ║     ear twitches, ahoge wiggle         ║")
print("  ║   Toon-shaded cel materials            ║")
print("  ║                                        ║")
print("  ║   Numpad 0 = camera | Space = play     ║")
print("  ╚════════════════════════════════════════╝")
print("")
