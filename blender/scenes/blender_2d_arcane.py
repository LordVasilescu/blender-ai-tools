# © 2026 Mathew. All rights reserved.
import bpy
import math
import random

# ============================================================
#   ARCANE TRANSMISSION — 2D Animation (Blender 5.0)
#   Uses Curves + Emission for glowing magic circle
# ============================================================

random.seed(42)

# --- Nuke scene ---
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
scene.render.fps = 24

# Dark background
world = bpy.data.worlds.get("World")
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.003, 0.003, 0.012, 1.0)
        bg.inputs["Strength"].default_value = 1.0

print("Building Arcane Transmission v2...")

# ---- MATERIALS ----
def glow_mat(name, color, strength=8.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Roughness"].default_value = 0.0
    return mat

# Color palette
mat_blue = glow_mat("ArcaneBlue", (0.3, 0.6, 1.0), 10)
mat_cyan = glow_mat("ArcaneCyan", (0.15, 0.85, 1.0), 12)
mat_purple = glow_mat("ArcanePurple", (0.6, 0.3, 1.0), 10)
mat_gold = glow_mat("ArcaneGold", (1.0, 0.85, 0.3), 15)
mat_white = glow_mat("ArcaneWhite", (0.9, 0.95, 1.0), 20)
mat_pink = glow_mat("ArcanePink", (1.0, 0.4, 0.7), 10)

# ---- HELPERS ----
def make_circle_curve(name, radius, bevel=0.015, mat=None, segments=64):
    """Create a glowing circle using a bezier circle curve."""
    bpy.ops.curve.primitive_bezier_circle_add(radius=radius, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = name
    obj.data.bevel_depth = bevel
    obj.data.bevel_resolution = 4
    obj.data.resolution_u = segments
    if mat:
        obj.data.materials.append(mat)
    return obj

def make_polygon_curve(name, radius, sides, bevel=0.012, mat=None, rotation=0):
    """Create a glowing polygon using a curve."""
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 3

    spline = curve_data.splines.new('POLY')
    spline.points.add(sides)  # +1 for closing
    for i in range(sides + 1):
        angle = rotation + (i / sides) * 2 * math.pi
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        spline.points[i].co = (x, y, 0, 1)
    spline.use_cyclic_u = True

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def make_line(name, x1, y1, x2, y2, bevel=0.008, mat=None):
    """Create a glowing line."""
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 2

    spline = curve_data.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (x1, y1, 0, 1)
    spline.points[1].co = (x2, y2, 0, 1)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def make_star_curve(name, cx, cy, outer_r, inner_r, points, bevel=0.012, mat=None, rotation=0):
    """Create a glowing star shape."""
    curve_data = bpy.data.curves.new(name=name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = bevel
    curve_data.bevel_resolution = 3

    spline = curve_data.splines.new('POLY')
    total = points * 2
    spline.points.add(total)
    for i in range(total + 1):
        angle = rotation + (i / total) * 2 * math.pi
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        spline.points[i].co = (x, y, 0, 1)
    spline.use_cyclic_u = True

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def make_dot(name, x, y, radius=0.04, mat=None):
    """Create a small glowing sphere (particle dot)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=8, ring_count=6, location=(x, y, 0))
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def spin(obj, axis, revs, total=360):
    """Animate rotation."""
    obj.rotation_euler[axis] = 0
    obj.keyframe_insert(data_path="rotation_euler", index=axis, frame=1)
    obj.rotation_euler[axis] = revs * 2 * math.pi
    obj.keyframe_insert(data_path="rotation_euler", index=axis, frame=total)
    try:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                if fc.array_index == axis:
                    mod = fc.modifiers.new(type='CYCLES')
    except:
        pass

# ============================================================
#  LAYER 1: OUTER RING
# ============================================================
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
outer_pivot = bpy.context.active_object
outer_pivot.name = "OuterPivot"

# Main circles
c1 = make_circle_curve("OuterCircle1", 4.0, 0.025, mat_blue)
c1.parent = outer_pivot
c2 = make_circle_curve("OuterCircle2", 3.9, 0.01, mat_cyan)
c2.parent = outer_pivot
c3 = make_circle_curve("OuterCircle3", 3.5, 0.018, mat_blue)
c3.parent = outer_pivot

# Tick marks between circles
for i in range(48):
    angle = (i / 48) * 2 * math.pi
    r1 = 3.52
    r2 = 3.88 if i % 2 == 0 else 3.7
    x1, y1 = r1 * math.cos(angle), r1 * math.sin(angle)
    x2, y2 = r2 * math.cos(angle), r2 * math.sin(angle)
    tick = make_line(f"Tick_{i}", x1, y1, x2, y2, 0.006, mat_cyan)
    tick.parent = outer_pivot

# Rune dots around the ring
for i in range(24):
    angle = (i / 24) * 2 * math.pi
    rx = 3.72 * math.cos(angle)
    ry = 3.72 * math.sin(angle)
    rune = make_dot(f"RuneDot_{i}", rx, ry, 0.035, mat_gold)
    rune.parent = outer_pivot

spin(outer_pivot, 2, 0.3)
print("  Outer ring done")

# ============================================================
#  LAYER 2: MIDDLE RING (counter-rotating)
# ============================================================
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
mid_pivot = bpy.context.active_object
mid_pivot.name = "MidPivot"

c4 = make_circle_curve("MidCircle1", 3.0, 0.02, mat_purple)
c4.parent = mid_pivot
c5 = make_circle_curve("MidCircle2", 2.5, 0.015, mat_cyan)
c5.parent = mid_pivot

# Hexagon
hex1 = make_polygon_curve("Hexagon", 2.75, 6, 0.015, mat_gold)
hex1.parent = mid_pivot

# Triangle
tri1 = make_polygon_curve("Triangle1", 2.75, 3, 0.012, mat_cyan, math.radians(30))
tri1.parent = mid_pivot

# Inverted triangle (Star of David)
tri2 = make_polygon_curve("Triangle2", 2.75, 3, 0.012, mat_cyan, math.radians(90))
tri2.parent = mid_pivot

# Radial lines from center to hexagon vertices
for i in range(6):
    angle = (i / 6) * 2 * math.pi
    x = 2.75 * math.cos(angle)
    y = 2.75 * math.sin(angle)
    line = make_line(f"Radial_{i}", 0, 0, x, y, 0.006, mat_blue)
    line.parent = mid_pivot

spin(mid_pivot, 2, -0.5)
print("  Middle ring done")

# ============================================================
#  LAYER 3: INNER RING (fast spin + pulse)
# ============================================================
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
inner_pivot = bpy.context.active_object
inner_pivot.name = "InnerPivot"

c6 = make_circle_curve("InnerCircle1", 2.0, 0.018, mat_purple)
c6.parent = inner_pivot
c7 = make_circle_curve("InnerCircle2", 1.5, 0.012, mat_gold)
c7.parent = inner_pivot

# Pentagon
pent = make_polygon_curve("Pentagon", 1.75, 5, 0.014, mat_white)
pent.parent = inner_pivot

# 5-pointed star
star = make_star_curve("Star5", 0, 0, 1.75, 0.7, 5, 0.012, mat_gold, math.radians(-18))
star.parent = inner_pivot

# Small inner circle
c8 = make_circle_curve("CoreCircle", 0.8, 0.015, mat_cyan)
c8.parent = inner_pivot
c9 = make_circle_curve("CoreDot", 0.3, 0.02, mat_white)
c9.parent = inner_pivot

# Center cross
cx1 = make_line("CenterH", -0.5, 0, 0.5, 0, 0.01, mat_gold)
cx1.parent = inner_pivot
cx2 = make_line("CenterV", 0, -0.5, 0, 0.5, 0.01, mat_gold)
cx2.parent = inner_pivot

spin(inner_pivot, 2, 1.0)

# Pulsing scale
for frame in range(1, 361):
    p = 1.0 + 0.06 * math.sin(frame * 0.15)
    inner_pivot.scale = (p, p, 1)
    inner_pivot.keyframe_insert(data_path="scale", frame=frame)

print("  Inner ring done")

# ============================================================
#  LAYER 4: ORBITING RUNE SATELLITES
# ============================================================
sat_mats = [mat_blue, mat_purple, mat_gold, mat_cyan, mat_pink, mat_white]

for si in range(8):
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    sat_orbit = bpy.context.active_object
    sat_orbit.name = f"SatOrbit_{si}"

    orbit_r = 4.5 + (si % 2) * 0.4
    base_angle = (si / 8) * 2 * math.pi
    direction = 1 if si % 2 == 0 else -1

    # Satellite body: small circle + polygon
    sat_circle = make_circle_curve(f"SatCircle_{si}", 0.2, 0.01, sat_mats[si % len(sat_mats)])
    sat_poly = make_polygon_curve(f"SatPoly_{si}", 0.14, 3 + si % 4, 0.008, sat_mats[(si + 2) % len(sat_mats)], math.radians(si * 45))

    sat_circle.parent = sat_orbit
    sat_poly.parent = sat_orbit

    # Orbit animation
    for frame in range(1, 361):
        angle = base_angle + frame * 0.008 * direction
        sat_orbit.location.x = orbit_r * math.cos(angle)
        sat_orbit.location.y = orbit_r * math.sin(angle)
        sat_orbit.keyframe_insert(data_path="location", frame=frame)

        # Self spin
        sat_orbit.rotation_euler.z = frame * 0.02 * direction
        sat_orbit.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)

        # Pulse
        ps = 0.7 + 0.5 * math.sin(frame * 0.1 + si * 1.2)
        sat_orbit.scale = (ps, ps, 1)
        sat_orbit.keyframe_insert(data_path="scale", frame=frame)

print("  Satellites done")

# ============================================================
#  LAYER 5: ENERGY PARTICLES (floating upward)
# ============================================================
print("  Generating energy particles...")
particle_mats = [mat_blue, mat_cyan, mat_gold, mat_white, mat_pink]

for pi in range(60):
    start_angle = random.uniform(0, 2 * math.pi)
    start_radius = random.uniform(0.3, 3.8)
    speed = random.uniform(0.015, 0.05)
    spiral = random.uniform(-0.008, 0.008)
    size = random.uniform(0.02, 0.06)
    birth = random.randint(1, 280)
    lifetime = random.randint(60, 150)
    pmat = random.choice(particle_mats)

    dot = make_dot(f"Particle_{pi}", 0, 0, size, pmat)

    for frame in range(1, 361):
        age = frame - birth
        if age < 0 or age > lifetime:
            # Hide particle
            dot.scale = (0.001, 0.001, 0.001)
            dot.keyframe_insert(data_path="scale", frame=frame)
            dot.location = (0, 0, -10)
            dot.keyframe_insert(data_path="location", frame=frame)
            continue

        t = age / lifetime
        current_angle = start_angle + age * spiral
        current_radius = start_radius * (1 - t * 0.5)
        rise = age * speed

        x = current_radius * math.cos(current_angle)
        y = current_radius * math.sin(current_angle) + rise

        dot.location = (x, y, 0)
        dot.keyframe_insert(data_path="location", frame=frame)

        # Fade in/out via scale
        if t < 0.15:
            s = t / 0.15
        elif t > 0.7:
            s = (1 - t) / 0.3
        else:
            s = 1.0
        s = max(0.01, s)
        dot.scale = (s, s, s)
        dot.keyframe_insert(data_path="scale", frame=frame)

print("  Particles done (60 particles)")

# ============================================================
#  LAYER 6: ENERGY BURST RINGS (periodic expanding)
# ============================================================
burst_times = [60, 120, 180, 240, 300]

for bi, bt in enumerate(burst_times):
    burst_ring = make_circle_curve(f"Burst_{bi}", 0.5, 0.03, mat_white)

    for frame in range(1, 361):
        age = frame - bt
        if age < 0 or age > 30:
            burst_ring.scale = (0.001, 0.001, 0.001)
        else:
            t = age / 30.0
            expand = 0.5 + t * 8.0
            fade = max(0.01, 1.0 - t)
            burst_ring.scale = (expand, expand, fade)
        burst_ring.keyframe_insert(data_path="scale", frame=frame)

print("  Burst rings done")

# ============================================================
#  LAYER 7: OUTER HALO RINGS
# ============================================================
for hi in range(4):
    r = 5.5 + hi * 0.8
    halo = make_circle_curve(f"Halo_{hi}", r, 0.005, [mat_blue, mat_purple, mat_cyan, mat_pink][hi])
    spin(halo, 2, 0.1 * (hi + 1) * (1 if hi % 2 == 0 else -1))

# ============================================================
#  GLOBAL PULSE
# ============================================================
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
pulse_ctrl = bpy.context.active_object
pulse_ctrl.name = "PulseCtrl"

# Parent main pivots
for name in ["OuterPivot", "MidPivot", "InnerPivot"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.parent = pulse_ctrl

for frame in range(1, 361):
    p = 1.0 + 0.025 * math.sin(frame * 0.08)
    pulse_ctrl.scale = (p, p, 1)
    pulse_ctrl.keyframe_insert(data_path="scale", frame=frame)

# ============================================================
#  CAMERA (orthographic top-down)
# ============================================================
bpy.ops.object.camera_add(location=(0, 0, 15))
cam = bpy.context.active_object
cam.name = "ArcaneCam"
cam.rotation_euler = (0, 0, 0)
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 14
scene.camera = cam

# Gentle camera drift
for frame in range(1, 361):
    cam.location.x = 0.4 * math.sin(frame * 0.008)
    cam.location.y = 0.3 * math.cos(frame * 0.012)
    cam.keyframe_insert(data_path="location", frame=frame)

# ============================================================
#  LIGHTING
# ============================================================
bpy.ops.object.light_add(type='POINT', location=(0, 0, 3))
light = bpy.context.active_object
light.data.energy = 50
light.data.color = (0.3, 0.5, 1.0)

# Pulsing light
for frame in range(1, 361):
    light.data.energy = 50 + 30 * math.sin(frame * 0.08)
    light.data.keyframe_insert("energy", frame=frame)

# ============================================================
#  RENDER & VIEWPORT
# ============================================================
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except:
    scene.render.engine = 'BLENDER_EEVEE'

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
print("  ╔═══════════════════════════════════════════════╗")
print("  ║   ARCANE TRANSMISSION v2 — Blender 5.0        ║")
print("  ║                                               ║")
print("  ║   3 rotating magic circles (curves + glow)    ║")
print("  ║   Hexagon, Star of David, Pentagram, Star     ║")
print("  ║   48 tick marks + 24 rune dots                ║")
print("  ║   60 floating energy particles                ║")
print("  ║   8 orbiting rune satellites                  ║")
print("  ║   5 expanding energy burst rings              ║")
print("  ║   4 outer halos + global pulse                ║")
print("  ║   Pulsing blue point light                    ║")
print("  ║                                               ║")
print("  ║   Numpad 0 = camera view | Space = play       ║")
print("  ╚═══════════════════════════════════════════════╝")
print("")
