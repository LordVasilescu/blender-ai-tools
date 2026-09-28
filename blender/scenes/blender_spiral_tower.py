# © 2026 Mathew. All rights reserved.
import bpy
import math
import colorsys

# --- Clean the scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Delete leftover meshes/materials
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# --- Settings ---
num_cubes = 120
height = 20
radius = 3
turns = 4
cube_size = 0.4

# --- Build the spiral ---
for i in range(num_cubes):
    t = i / num_cubes
    angle = turns * 2 * math.pi * t
    z = height * t

    x = radius * math.cos(angle) * (1 - t * 0.5)
    y = radius * math.sin(angle) * (1 - t * 0.5)

    bpy.ops.mesh.primitive_cube_add(size=cube_size, location=(x, y, z))
    cube = bpy.context.active_object
    cube.rotation_euler = (angle, angle * 0.5, angle * 0.3)

    # Scale cubes smaller as they go up
    s = 1.0 - t * 0.7
    cube.scale = (s, s, s)

    # Rainbow material with emission glow
    hue = t
    r, g, b = colorsys.hsv_to_rgb(hue, 0.9, 1.0)

    mat = bpy.data.materials.new(name=f"Rainbow_{i}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Emission Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 2.0
    bsdf.inputs["Metallic"].default_value = 0.8
    bsdf.inputs["Roughness"].default_value = 0.2

    cube.data.materials.append(mat)

# --- Add a ground plane ---
bpy.ops.mesh.primitive_plane_add(size=15, location=(0, 0, 0))
plane = bpy.context.active_object
mat_floor = bpy.data.materials.new(name="Floor")
mat_floor.use_nodes = True
bsdf_floor = mat_floor.node_tree.nodes["Principled BSDF"]
bsdf_floor.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf_floor.inputs["Metallic"].default_value = 1.0
bsdf_floor.inputs["Roughness"].default_value = 0.1
plane.data.materials.append(mat_floor)

# --- Set up camera ---
bpy.ops.object.camera_add(location=(8, -8, 12))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(55), 0, math.radians(45))
bpy.context.scene.camera = cam

# --- Add lighting ---
bpy.ops.object.light_add(type='SUN', location=(5, -5, 15))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.object.light_add(type='POINT', location=(0, 0, 10))
point = bpy.context.active_object
point.data.energy = 500

# --- Switch to Material Preview so you see colors ---
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                break

print("Rainbow spiral tower created!")
