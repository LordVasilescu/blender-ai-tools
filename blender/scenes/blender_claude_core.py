# © 2026 Mathew. All rights reserved.
import bpy
import math
import colorsys
import random

# ============================================
#   THE CLAUDE CORE — Opus 4.6 Special
# ============================================

random.seed(42)

# --- Nuke the scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for m in bpy.data.meshes:
    bpy.data.meshes.remove(m)
for m in bpy.data.materials:
    bpy.data.materials.remove(m)
for c in bpy.data.curves:
    bpy.data.curves.remove(c)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 360
scene.render.fps = 30

# --- Helper: make emissive material ---
def make_glow_mat(name, color, emission_strength=5.0, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = emission_strength
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = 0.1
    return mat

# --- Helper: animate rotation over full timeline ---
def animate_rotation(obj, axis, revolutions=1, offset=0):
    for frame in [1, 360]:
        angle = offset + (frame / 360.0) * revolutions * 2 * math.pi
        obj.rotation_euler[axis] = angle
        obj.keyframe_insert(data_path="rotation_euler", index=axis, frame=frame)
    # Make it loop properly
    if obj.animation_data and obj.animation_data.action:
        try:
            for fc in obj.animation_data.action.fcurves:
                for mod in fc.modifiers:
                    fc.modifiers.remove(mod)
                mod = fc.modifiers.new(type='CYCLES')
        except:
            pass

# ==============================
#  1. CENTRAL CORE ORB
# ==============================
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.2, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "Claude_Core"

# Warm amber/orange Anthropic-inspired glow
core_mat = make_glow_mat("CoreGlow", (1.0, 0.55, 0.15), emission_strength=15.0)
core.data.materials.append(core_mat)

# Animate pulsing scale
for frame in range(1, 361):
    pulse = 1.0 + 0.08 * math.sin(frame * 0.1)
    core.scale = (pulse, pulse, pulse)
    core.keyframe_insert(data_path="scale", frame=frame)

# Slow self-rotation
animate_rotation(core, 2, revolutions=1)

# ==============================
#  2. INNER GLASS SHELL
# ==============================
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.8, location=(0, 0, 0))
shell = bpy.context.active_object
shell.name = "InnerShell"
shell_mat = bpy.data.materials.new(name="ShellMat")
shell_mat.use_nodes = True
bsdf = shell_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.4, 0.6, 1.0, 1.0)
bsdf.inputs["Alpha"].default_value = 0.08
bsdf.inputs["Roughness"].default_value = 0.0
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Emission Color"].default_value = (0.3, 0.5, 1.0, 1.0)
bsdf.inputs["Emission Strength"].default_value = 1.0
shell_mat.blend_method = 'BLEND' if hasattr(shell_mat, 'blend_method') else None
shell.data.materials.append(shell_mat)
animate_rotation(shell, 0, revolutions=-0.5)
animate_rotation(shell, 2, revolutions=0.3)

# ==============================
#  3. ORBITAL RINGS
# ==============================
ring_configs = [
    {"radius": 3.5, "tilt_x": 70, "tilt_y": 0,  "speed": 1.0, "color": (0.2, 0.6, 1.0),  "nodes": 8},
    {"radius": 5.0, "tilt_x": 45, "tilt_y": 30, "speed": -0.7, "color": (1.0, 0.4, 0.8),  "nodes": 12},
    {"radius": 6.5, "tilt_x": 20, "tilt_y": 60, "speed": 0.5,  "color": (0.3, 1.0, 0.6),  "nodes": 10},
]

all_nodes = []

for ri, cfg in enumerate(ring_configs):
    # Ring pivot (empty that rotates)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    pivot = bpy.context.active_object
    pivot.name = f"RingPivot_{ri}"
    pivot.rotation_euler = (math.radians(cfg["tilt_x"]), math.radians(cfg["tilt_y"]), 0)

    # Visible ring (torus)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=cfg["radius"],
        minor_radius=0.02,
        major_segments=80,
        minor_segments=8,
        location=(0, 0, 0)
    )
    ring = bpy.context.active_object
    ring.name = f"Ring_{ri}"
    ring.parent = pivot
    ring_mat = make_glow_mat(f"RingGlow_{ri}", cfg["color"], emission_strength=8.0)
    ring.data.materials.append(ring_mat)

    # Orbiting nodes on this ring
    for ni in range(cfg["nodes"]):
        angle = (ni / cfg["nodes"]) * 2 * math.pi
        nx = cfg["radius"] * math.cos(angle)
        ny = cfg["radius"] * math.sin(angle)

        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.2, location=(nx, ny, 0))
        node = bpy.context.active_object
        node.name = f"Node_{ri}_{ni}"
        node.parent = pivot

        # Gradient color per node
        hue = (ni / cfg["nodes"] + ri * 0.33) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        node_mat = make_glow_mat(f"NodeGlow_{ri}_{ni}", (r, g, b), emission_strength=10.0, metallic=0.9)
        node.data.materials.append(node_mat)

        # Pulse each node
        for frame in range(1, 361):
            p = 0.8 + 0.4 * math.sin(frame * 0.15 + ni * 1.5)
            node.scale = (p, p, p)
            node.keyframe_insert(data_path="scale", frame=frame)

        all_nodes.append(node)

    # Animate ring rotation
    animate_rotation(pivot, 2, revolutions=cfg["speed"])

# ==============================
#  4. ENERGY BEAMS (curves from core to some nodes)
# ==============================
beam_targets = random.sample(all_nodes, min(12, len(all_nodes)))
for bi, target in enumerate(beam_targets):
    curve_data = bpy.data.curves.new(name=f"Beam_{bi}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.015
    curve_data.bevel_resolution = 4

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)

    # Start at core
    spline.bezier_points[0].co = (0, 0, 0)
    spline.bezier_points[0].handle_right = (0.5, 0.5, 0.5)
    spline.bezier_points[0].handle_left = (-0.5, -0.5, -0.5)

    # End at node world location (approximate static position)
    tx, ty, tz = target.matrix_world.translation
    spline.bezier_points[1].co = (tx, ty, tz)
    spline.bezier_points[1].handle_left = (tx * 0.5, ty * 0.5, tz * 0.5)
    spline.bezier_points[1].handle_right = (tx * 1.2, ty * 1.2, tz * 1.2)

    beam_obj = bpy.data.objects.new(f"Beam_{bi}", curve_data)
    bpy.context.collection.objects.link(beam_obj)

    beam_color = colorsys.hsv_to_rgb(bi / len(beam_targets), 0.6, 1.0)
    beam_mat = make_glow_mat(f"BeamGlow_{bi}", beam_color, emission_strength=12.0)
    beam_obj.data.materials.append(beam_mat)

# ==============================
#  5. STARFIELD
# ==============================
for si in range(300):
    # Random point on a sphere
    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0, math.pi)
    dist = random.uniform(12, 25)
    sx = dist * math.sin(phi) * math.cos(theta)
    sy = dist * math.sin(phi) * math.sin(theta)
    sz = dist * math.cos(phi)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.02, 0.08), location=(sx, sy, sz))
    star = bpy.context.active_object
    star.name = f"Star_{si}"

    brightness = random.uniform(0.5, 1.0)
    hue = random.uniform(0.55, 0.72)  # Blue-ish white stars
    r, g, b = colorsys.hsv_to_rgb(hue, random.uniform(0.0, 0.3), brightness)
    star_mat = make_glow_mat(f"StarGlow_{si}", (r, g, b), emission_strength=random.uniform(3, 15))
    star.data.materials.append(star_mat)

# ==============================
#  6. FLOATING TEXT RINGS (decorative halos)
# ==============================
for hi in range(3):
    r = 8.5 + hi * 1.2
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=0.008,
        major_segments=120, minor_segments=6,
        location=(0, 0, 0)
    )
    halo = bpy.context.active_object
    halo.name = f"Halo_{hi}"
    halo.rotation_euler = (math.radians(90 + hi * 15), math.radians(hi * 20), 0)
    halo_mat = make_glow_mat(f"HaloGlow_{hi}", (0.6, 0.8, 1.0), emission_strength=4.0)
    halo.data.materials.append(halo_mat)
    animate_rotation(halo, 2, revolutions=0.2 * (hi + 1) * (1 if hi % 2 == 0 else -1))

# ==============================
#  7. CAMERA (orbiting)
# ==============================
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
cam_pivot = bpy.context.active_object
cam_pivot.name = "CameraPivot"

bpy.ops.object.camera_add(location=(14, 0, 6))
cam = bpy.context.active_object
cam.name = "OrbitalCam"
cam.parent = cam_pivot
cam.data.lens = 30

# Point camera at center
track = cam.constraints.new(type='TRACK_TO')
track.target = core
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

scene.camera = cam
animate_rotation(cam_pivot, 2, revolutions=0.25)

# slight vertical bob
for frame in range(1, 361):
    cam.location.z = 6 + 2 * math.sin(frame * 0.03)
    cam.keyframe_insert(data_path="location", index=2, frame=frame)

# ==============================
#  8. LIGHTING
# ==============================
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
core_light = bpy.context.active_object
core_light.name = "CoreLight"
core_light.data.energy = 800
core_light.data.color = (1.0, 0.6, 0.2)

bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 0.5
sun.data.color = (0.7, 0.8, 1.0)

# ==============================
#  9. DARK WORLD
# ==============================
world = bpy.data.worlds.get("World")
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.002, 0.002, 0.008, 1.0)
        bg.inputs["Strength"].default_value = 1.0

# ==============================
#  10. VIEWPORT SETUP & PLAY
# ==============================
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
print("  ╔══════════════════════════════════════╗")
print("  ║    THE CLAUDE CORE — Opus 4.6        ║")
print("  ║    Press Space to pause/play          ║")
print("  ║    Press Numpad 0 for camera view     ║")
print("  ╚══════════════════════════════════════╝")
print("")
