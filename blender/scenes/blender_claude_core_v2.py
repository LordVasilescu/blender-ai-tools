# © 2026 Mathew. All rights reserved.
import bpy
import math
import colorsys
import random

# ============================================================
#   THE CLAUDE CORE V2 — OPUS 4.6 HYPERDRIVE EDITION
# ============================================================

random.seed(77)

# --- Nuke everything ---
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
scene.frame_end = 480
scene.render.fps = 30

# ---- HELPERS ----

def glow_mat(name, color, strength=5.0, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = 0.1
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            mat.blend_method = 'BLEND'
        except:
            pass
    return mat

def spin(obj, axis, revs=1.0, offset=0):
    obj.rotation_euler[axis] = offset
    obj.keyframe_insert(data_path="rotation_euler", index=axis, frame=1)
    obj.rotation_euler[axis] = offset + revs * 2 * math.pi
    obj.keyframe_insert(data_path="rotation_euler", index=axis, frame=480)
    try:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                if fc.array_index == axis:
                    mod = fc.modifiers.new(type='CYCLES')
    except:
        pass

print("Building the Claude Core V2... hold tight!")

# ============================================
#  1. THE CORE — color-cycling pulsing orb
# ============================================
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.3, location=(0, 0, 0))
core = bpy.context.active_object
core.name = "Claude_Core"

# Animated color-cycling material via keyframed emission
core_mat = bpy.data.materials.new(name="CoreCycleMat")
core_mat.use_nodes = True
nodes = core_mat.node_tree.nodes
links = core_mat.node_tree.links

bsdf_core = nodes["Principled BSDF"]
bsdf_core.inputs["Metallic"].default_value = 0.3
bsdf_core.inputs["Roughness"].default_value = 0.05
bsdf_core.inputs["Emission Strength"].default_value = 20.0

# Keyframe color cycling on the core
for frame in range(1, 481, 2):
    hue = (frame / 480.0) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
    bsdf_core.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf_core.inputs["Base Color"].keyframe_insert("default_value", frame=frame)
    bsdf_core.inputs["Emission Color"].default_value = (r, g, b, 1.0)
    bsdf_core.inputs["Emission Color"].keyframe_insert("default_value", frame=frame)

core.data.materials.append(core_mat)

# Pulse scale
for frame in range(1, 481):
    p = 1.0 + 0.12 * math.sin(frame * 0.12) + 0.05 * math.sin(frame * 0.31)
    core.scale = (p, p, p)
    core.keyframe_insert(data_path="scale", frame=frame)

spin(core, 2, revs=2.0)

# ============================================
#  2. LAYERED GLASS SHELLS
# ============================================
shell_configs = [
    {"radius": 1.9, "color": (0.4, 0.6, 1.0), "alpha": 0.06, "subdiv": 3, "spin_x": -0.5, "spin_z": 0.3},
    {"radius": 2.6, "color": (1.0, 0.5, 0.8), "alpha": 0.04, "subdiv": 3, "spin_x": 0.3, "spin_z": -0.4},
    {"radius": 3.2, "color": (0.3, 1.0, 0.7), "alpha": 0.03, "subdiv": 2, "spin_x": 0.2, "spin_z": 0.6},
]

for si, sc in enumerate(shell_configs):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sc["subdiv"], radius=sc["radius"], location=(0, 0, 0))
    s = bpy.context.active_object
    s.name = f"Shell_{si}"
    s.data.materials.append(glow_mat(f"ShellMat_{si}", sc["color"], strength=1.5, alpha=sc["alpha"]))
    spin(s, 0, revs=sc["spin_x"])
    spin(s, 2, revs=sc["spin_z"])

# ============================================
#  3. FIVE ORBITAL RINGS WITH MIXED SHAPES
# ============================================
ring_configs = [
    {"radius": 4.0,  "tilt_x": 75, "tilt_y": 0,   "speed": 1.0,   "color": (0.2, 0.5, 1.0),  "nodes": 10, "shape": "ico"},
    {"radius": 5.5,  "tilt_x": 50, "tilt_y": 25,  "speed": -0.8,  "color": (1.0, 0.3, 0.7),  "nodes": 14, "shape": "cube"},
    {"radius": 7.0,  "tilt_x": 30, "tilt_y": 55,  "speed": 0.6,   "color": (0.2, 1.0, 0.5),  "nodes": 12, "shape": "diamond"},
    {"radius": 8.5,  "tilt_x": 60, "tilt_y": 80,  "speed": -0.45, "color": (1.0, 0.8, 0.2),  "nodes": 8,  "shape": "torus"},
    {"radius": 10.0, "tilt_x": 15, "tilt_y": 40,  "speed": 0.35,  "color": (0.8, 0.3, 1.0),  "nodes": 16, "shape": "ico"},
]

all_nodes = []

for ri, cfg in enumerate(ring_configs):
    # Ring pivot
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    pivot = bpy.context.active_object
    pivot.name = f"RingPivot_{ri}"
    pivot.rotation_euler = (math.radians(cfg["tilt_x"]), math.radians(cfg["tilt_y"]), 0)

    # Visible ring torus
    bpy.ops.mesh.primitive_torus_add(
        major_radius=cfg["radius"], minor_radius=0.015,
        major_segments=100, minor_segments=6, location=(0, 0, 0)
    )
    ring = bpy.context.active_object
    ring.name = f"Ring_{ri}"
    ring.parent = pivot
    ring.data.materials.append(glow_mat(f"RingGlow_{ri}", cfg["color"], strength=10.0))

    # Orbiting nodes
    for ni in range(cfg["nodes"]):
        angle = (ni / cfg["nodes"]) * 2 * math.pi
        nx = cfg["radius"] * math.cos(angle)
        ny = cfg["radius"] * math.sin(angle)

        # Different shapes per ring
        if cfg["shape"] == "cube":
            bpy.ops.mesh.primitive_cube_add(size=0.35, location=(nx, ny, 0))
            node = bpy.context.active_object
            node.rotation_euler = (math.radians(45), math.radians(45), 0)
        elif cfg["shape"] == "diamond":
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.22, depth=0.45, location=(nx, ny, 0))
            node = bpy.context.active_object
        elif cfg["shape"] == "torus":
            bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.06, location=(nx, ny, 0))
            node = bpy.context.active_object
        else:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.2, location=(nx, ny, 0))
            node = bpy.context.active_object

        node.name = f"Node_{ri}_{ni}"
        node.parent = pivot

        hue = (ni / cfg["nodes"] + ri * 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1.0)
        node.data.materials.append(glow_mat(f"NodeGlow_{ri}_{ni}", (r, g, b), strength=12.0, metallic=0.9))

        # Self-spin each node
        spin(node, 0, revs=random.uniform(1, 3))
        spin(node, 2, revs=random.uniform(-2, 2))

        # Pulse each node
        for frame in range(1, 481, 3):
            p = 0.7 + 0.5 * math.sin(frame * 0.12 + ni * 2.0 + ri)
            node.scale = (p, p, p)
            node.keyframe_insert(data_path="scale", frame=frame)

        all_nodes.append(node)

    spin(pivot, 2, revs=cfg["speed"])

print(f"  Rings done: {len(all_nodes)} nodes created")

# ============================================
#  4. DNA DOUBLE HELIX
# ============================================
helix_radius = 2.2
helix_height = 14
helix_turns = 4
helix_points = 80

for strand in range(2):
    phase = strand * math.pi  # 180 degree offset for double helix
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    helix_pivot = bpy.context.active_object
    helix_pivot.name = f"HelixPivot_{strand}"

    for hi in range(helix_points):
        t = hi / helix_points
        angle = helix_turns * 2 * math.pi * t + phase
        hx = helix_radius * math.cos(angle)
        hy = helix_radius * math.sin(angle)
        hz = helix_height * t - helix_height / 2

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(hx, hy, hz))
        bead = bpy.context.active_object
        bead.name = f"Helix_{strand}_{hi}"
        bead.parent = helix_pivot

        hue = t
        r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
        bead.data.materials.append(glow_mat(f"HelixGlow_{strand}_{hi}", (r, g, b), strength=8.0))

    spin(helix_pivot, 2, revs=0.5 * (1 if strand == 0 else -1))

# Cross-links between helix strands
for hi in range(0, helix_points, 5):
    t = hi / helix_points
    angle1 = helix_turns * 2 * math.pi * t
    angle2 = angle1 + math.pi

    x1 = helix_radius * math.cos(angle1)
    y1 = helix_radius * math.sin(angle1)
    x2 = helix_radius * math.cos(angle2)
    y2 = helix_radius * math.sin(angle2)
    z = helix_height * t - helix_height / 2

    curve_data = bpy.data.curves.new(name=f"HelixLink_{hi}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.02
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    spline.bezier_points[0].co = (x1, y1, z)
    spline.bezier_points[0].handle_right_type = 'AUTO'
    spline.bezier_points[0].handle_left_type = 'AUTO'
    spline.bezier_points[1].co = (x2, y2, z)
    spline.bezier_points[1].handle_right_type = 'AUTO'
    spline.bezier_points[1].handle_left_type = 'AUTO'
    link_obj = bpy.data.objects.new(f"HelixLink_{hi}", curve_data)
    bpy.context.collection.objects.link(link_obj)
    hue = t
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 1.0)
    link_obj.data.materials.append(glow_mat(f"HelixLinkGlow_{hi}", (r, g, b), strength=6.0))

print("  DNA helix done")

# ============================================
#  5. SHOCKWAVE PULSE RINGS
# ============================================
for wi in range(5):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.5, minor_radius=0.04,
        major_segments=80, minor_segments=8, location=(0, 0, 0)
    )
    wave = bpy.context.active_object
    wave.name = f"Shockwave_{wi}"
    wave.rotation_euler.x = math.radians(90)

    wave_hue = wi / 5.0
    wr, wg, wb = colorsys.hsv_to_rgb(wave_hue, 0.7, 1.0)
    wave.data.materials.append(glow_mat(f"WaveGlow_{wi}", (wr, wg, wb), strength=15.0))

    cycle_len = 80
    offset = wi * 16  # stagger each wave

    for frame in range(1, 481):
        t = ((frame - offset) % cycle_len) / cycle_len
        if t < 0:
            t += 1.0
        radius_scale = 1.0 + t * 18.0
        thickness = max(0.01, 1.0 - t)
        wave.scale = (radius_scale, radius_scale, thickness)
        wave.keyframe_insert(data_path="scale", frame=frame)

print("  Shockwaves done")

# ============================================
#  6. FLOATING PLATONIC SOLIDS
# ============================================
platonic_configs = [
    {"type": "monkey", "pos": (5, 5, 4), "size": 0.8, "color": (1.0, 0.4, 0.1)},
    {"type": "ico",    "pos": (-6, 4, -3), "size": 1.0, "color": (0.1, 0.8, 1.0)},
    {"type": "cone",   "pos": (4, -6, 3), "size": 1.2, "color": (0.9, 0.2, 0.9)},
    {"type": "torus",  "pos": (-5, -5, -2), "size": 0.7, "color": (0.2, 1.0, 0.4)},
]

for pi_idx, pc in enumerate(platonic_configs):
    if pc["type"] == "monkey":
        bpy.ops.mesh.primitive_monkey_add(size=pc["size"], location=pc["pos"])
    elif pc["type"] == "ico":
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=pc["size"], location=pc["pos"])
    elif pc["type"] == "cone":
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=pc["size"]*0.6, depth=pc["size"], location=pc["pos"])
    elif pc["type"] == "torus":
        bpy.ops.mesh.primitive_torus_add(major_radius=pc["size"], minor_radius=pc["size"]*0.35, location=pc["pos"])

    solid = bpy.context.active_object
    solid.name = f"Platonic_{pi_idx}"
    solid.data.materials.append(glow_mat(f"PlatonicGlow_{pi_idx}", pc["color"], strength=10.0, metallic=0.95))

    spin(solid, 0, revs=random.uniform(0.5, 1.5))
    spin(solid, 1, revs=random.uniform(-1.0, 1.0))
    spin(solid, 2, revs=random.uniform(0.3, 2.0))

    # Orbit around center
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    orbit = bpy.context.active_object
    orbit.name = f"PlatonicOrbit_{pi_idx}"
    solid.parent = orbit
    spin(orbit, 2, revs=random.uniform(0.15, 0.4) * (1 if pi_idx % 2 == 0 else -1))

print("  Platonic solids done")

# ============================================
#  7. ENERGY BEAMS
# ============================================
beam_targets = random.sample(all_nodes, min(20, len(all_nodes)))
for bi, target in enumerate(beam_targets):
    curve_data = bpy.data.curves.new(name=f"Beam_{bi}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.012
    curve_data.bevel_resolution = 4

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)

    spline.bezier_points[0].co = (0, 0, 0)
    spline.bezier_points[0].handle_right_type = 'AUTO'
    spline.bezier_points[0].handle_left_type = 'AUTO'

    tx, ty, tz = target.matrix_world.translation
    mid_offset = random.uniform(-2, 2)
    spline.bezier_points[1].co = (tx, ty, tz)
    spline.bezier_points[1].handle_left = (tx * 0.4 + mid_offset, ty * 0.4 + mid_offset, tz * 0.4)
    spline.bezier_points[1].handle_right_type = 'AUTO'

    beam_obj = bpy.data.objects.new(f"Beam_{bi}", curve_data)
    bpy.context.collection.objects.link(beam_obj)

    beam_hue = bi / len(beam_targets)
    br, bg, bb = colorsys.hsv_to_rgb(beam_hue, 0.6, 1.0)
    beam_obj.data.materials.append(glow_mat(f"BeamGlow_{bi}", (br, bg, bb), strength=14.0))

print("  Energy beams done")

# ============================================
#  8. MASSIVE STARFIELD
# ============================================
for si in range(500):
    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0, math.pi)
    dist = random.uniform(18, 40)
    sx = dist * math.sin(phi) * math.cos(theta)
    sy = dist * math.sin(phi) * math.sin(theta)
    sz = dist * math.cos(phi)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.02, 0.1), location=(sx, sy, sz))
    star = bpy.context.active_object
    star.name = f"Star_{si}"

    hue = random.uniform(0.5, 0.75)
    sat = random.uniform(0.0, 0.4)
    val = random.uniform(0.6, 1.0)
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    star.data.materials.append(glow_mat(f"StarGlow_{si}", (r, g, b), strength=random.uniform(3, 20)))

    # Twinkle some stars
    if random.random() < 0.3:
        for frame in range(1, 481, 4):
            twinkle = random.uniform(0.3, 1.5)
            star.scale = (twinkle, twinkle, twinkle)
            star.keyframe_insert(data_path="scale", frame=frame)

print("  Starfield done (500 stars)")

# ============================================
#  9. OUTER HALOS
# ============================================
for hi in range(5):
    r = 11 + hi * 1.5
    bpy.ops.mesh.primitive_torus_add(
        major_radius=r, minor_radius=0.006,
        major_segments=140, minor_segments=6, location=(0, 0, 0)
    )
    halo = bpy.context.active_object
    halo.name = f"Halo_{hi}"
    halo.rotation_euler = (math.radians(90 + hi * 12), math.radians(hi * 18), 0)

    halo_hue = hi / 5.0
    hr, hg, hb = colorsys.hsv_to_rgb(halo_hue, 0.5, 1.0)
    halo.data.materials.append(glow_mat(f"HaloGlow_{hi}", (hr, hg, hb), strength=5.0))
    spin(halo, 2, revs=0.15 * (hi + 1) * (1 if hi % 2 == 0 else -1))

# ============================================
#  10. CAMERA — dramatic cinematic orbit
# ============================================
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
cam_pivot = bpy.context.active_object
cam_pivot.name = "CameraPivot"

bpy.ops.object.camera_add(location=(16, 0, 5))
cam = bpy.context.active_object
cam.name = "CinematicCam"
cam.parent = cam_pivot
cam.data.lens = 28

track = cam.constraints.new(type='TRACK_TO')
track.target = core
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
scene.camera = cam

spin(cam_pivot, 2, revs=0.4)

# Dramatic zoom + vertical sweep
for frame in range(1, 481):
    t = frame / 480.0
    cam.location.x = 16 + 4 * math.sin(t * 4 * math.pi)
    cam.location.z = 5 + 6 * math.sin(t * 2 * math.pi)
    cam.keyframe_insert(data_path="location", index=0, frame=frame)
    cam.keyframe_insert(data_path="location", index=2, frame=frame)

# ============================================
#  11. LIGHTING ARRAY
# ============================================
# Core warm light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
core_light = bpy.context.active_object
core_light.name = "CoreLight"
core_light.data.energy = 1200
core_light.data.color = (1.0, 0.55, 0.2)

# Blue rim light
bpy.ops.object.light_add(type='POINT', location=(8, -8, 5))
rim1 = bpy.context.active_object
rim1.data.energy = 600
rim1.data.color = (0.2, 0.4, 1.0)

# Pink accent light
bpy.ops.object.light_add(type='POINT', location=(-8, 6, -4))
rim2 = bpy.context.active_object
rim2.data.energy = 500
rim2.data.color = (1.0, 0.3, 0.7)

# Green under-light
bpy.ops.object.light_add(type='POINT', location=(0, 0, -8))
under = bpy.context.active_object
under.data.energy = 400
under.data.color = (0.2, 1.0, 0.5)

# Subtle sun for definition
bpy.ops.object.light_add(type='SUN', location=(10, 10, 10))
sun = bpy.context.active_object
sun.data.energy = 0.3
sun.data.color = (0.8, 0.85, 1.0)

# Animated core light pulsing
for frame in range(1, 481):
    core_light.data.energy = 1200 + 600 * math.sin(frame * 0.1)
    core_light.data.keyframe_insert("energy", frame=frame)

# ============================================
#  12. WORLD / VIEWPORT
# ============================================
world = bpy.data.worlds.get("World")
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.001, 0.001, 0.005, 1.0)
        bg.inputs["Strength"].default_value = 1.0

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                space.clip_end = 1000
                break

scene.frame_set(1)
bpy.ops.screen.animation_play()

print("")
print("  ╔════════════════════════════════════════════╗")
print("  ║  THE CLAUDE CORE V2 — HYPERDRIVE EDITION   ║")
print("  ║                                            ║")
print("  ║  Central orb: color-cycling pulsing brain  ║")
print("  ║  3 glass shells, 5 orbital rings           ║")
print("  ║  60+ orbiting nodes (mixed shapes)         ║")
print("  ║  DNA double helix with cross-links         ║")
print("  ║  5 expanding shockwave pulses              ║")
print("  ║  Floating Suzanne + platonic solids        ║")
print("  ║  20 energy beams, 500 twinkling stars      ║")
print("  ║  5 outer halos, cinematic orbit camera     ║")
print("  ║  Pulsing multi-color lighting              ║")
print("  ║                                            ║")
print("  ║  Numpad 0 = camera view | Space = play     ║")
print("  ╚════════════════════════════════════════════╝")
print("")
