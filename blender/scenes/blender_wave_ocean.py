# © 2026 Mathew. All rights reserved.
import bpy
import math
import colorsys

# --- Clean the scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

# --- Settings ---
grid_size = 20         # 20x20 = 400 pillars
spacing = 0.6
wave_height = 2.5
wave_speed = 0.08
num_frames = 200
pillar_size = 0.4

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = num_frames
scene.render.fps = 30

# --- Create the wave grid ---
pillars = []
for ix in range(grid_size):
    for iy in range(grid_size):
        x = (ix - grid_size / 2) * spacing
        y = (iy - grid_size / 2) * spacing

        bpy.ops.mesh.primitive_cube_add(size=pillar_size, location=(x, y, 0))
        pillar = bpy.context.active_object
        pillar.name = f"Pillar_{ix}_{iy}"

        # Color based on grid position
        hue = ((ix + iy) / (grid_size * 2)) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 1.0)

        mat = bpy.data.materials.new(name=f"Wave_{ix}_{iy}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Emission Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 3.0
        bsdf.inputs["Metallic"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.15
        pillar.data.materials.append(mat)

        # Animate: keyframe Z-scale on every frame
        for frame in range(1, num_frames + 1):
            dist = math.sqrt((ix - grid_size / 2) ** 2 + (iy - grid_size / 2) ** 2)
            wave = math.sin(dist * 0.8 - frame * wave_speed * 2 * math.pi) * 0.5 + 0.5
            sz = 0.3 + wave * wave_height

            pillar.scale = (1, 1, sz)
            pillar.location.z = sz * pillar_size * 0.5
            pillar.keyframe_insert(data_path="scale", index=2, frame=frame)
            pillar.keyframe_insert(data_path="location", index=2, frame=frame)

        pillars.append(pillar)

# --- Dark reflective floor ---
bpy.ops.mesh.primitive_plane_add(size=25, location=(0, 0, -0.1))
plane = bpy.context.active_object
mat_floor = bpy.data.materials.new(name="DarkFloor")
mat_floor.use_nodes = True
bsdf_f = mat_floor.node_tree.nodes["Principled BSDF"]
bsdf_f.inputs["Base Color"].default_value = (0.01, 0.01, 0.02, 1.0)
bsdf_f.inputs["Metallic"].default_value = 1.0
bsdf_f.inputs["Roughness"].default_value = 0.05
plane.data.materials.append(mat_floor)

# --- Camera ---
bpy.ops.object.camera_add(location=(10, -10, 12))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(50), 0, math.radians(45))
cam.data.lens = 35
scene.camera = cam

# --- Lighting ---
bpy.ops.object.light_add(type='SUN', location=(5, -5, 15))
sun = bpy.context.active_object
sun.data.energy = 2.0
sun.rotation_euler = (math.radians(40), 0, math.radians(30))

bpy.ops.object.light_add(type='AREA', location=(0, 0, 10))
area = bpy.context.active_object
area.data.energy = 300
area.data.size = 8

# --- Dark world background ---
world = bpy.data.worlds.get("World")
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.005, 0.005, 0.01, 1.0)
        bg.inputs["Strength"].default_value = 1.0

# --- Material preview mode ---
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
                break

# --- Start playback ---
scene.frame_set(1)
bpy.ops.screen.animation_play()

print("Wave ocean created! 400 animated pillars. Hit Space to pause/play.")
