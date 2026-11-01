import bpy
import math
from mathutils import Matrix, Vector

PROJECT_ROOT = r"__FAMILY_STUDIO_PROJECT_ROOT__"

# R3 deliverable: a deliberately neutral, unapproved 3D silhouette blockout.
# This is authored and executed in Blender, not in the legacy NumPy renderer.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for collection in list(bpy.data.collections):
    if collection.name.startswith(("DAD — R3 BLOCKOUT", "REFERENCE IMAGES — viewport only")):
        bpy.data.collections.remove(collection)
for datablocks in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)

scene = bpy.context.scene
scene.name = "Dad — R3 gray blockout"
scene["family_studio_stage"] = "R3 blockout — likeness pending approval"
scene["family_studio_costume_override"] = "light crewneck, no hood"
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 360
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.resolution_percentage = 100
scene.render.filepath = "//renders/dad-blockout/"
scene.view_settings.view_transform = "AgX"
scene.world = scene.world or bpy.data.worlds.new("World")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.38, 0.41, 0.46, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.45

# Organize the native Blender scene for later rigging and approved refinements.
root = bpy.data.collections.new("DAD — R3 BLOCKOUT")
scene.collection.children.link(root)
refs = bpy.data.collections.new("REFERENCE IMAGES — viewport only")
scene.collection.children.link(refs)

def move_to_collection(obj, collection=root):
    for collection_old in list(obj.users_collection):
        collection_old.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def make_material(name, color, roughness=0.78):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    return mat

crew = make_material("Crewneck — warm light gray", (0.62, 0.64, 0.67))
pants = make_material("Trousers — mid gray", (0.31, 0.34, 0.39))
skin = make_material("Skin — neutral gray blockout", (0.53, 0.54, 0.55))
hair = make_material("Hair — charcoal gray", (0.16, 0.18, 0.21))
beard = make_material("Beard — dark gray", (0.22, 0.24, 0.27))
shoe_mat = make_material("Shoes — graphite", (0.18, 0.20, 0.23))
eye_white = make_material("Eyes — pale gray", (0.78, 0.80, 0.82), 0.45)
pupil_mat = make_material("Pupils — charcoal", (0.08, 0.09, 0.11), 0.42)
feature_mat = make_material("Face details — medium gray", (0.28, 0.29, 0.31), 0.72)
ground_mat = make_material("Studio floor", (0.24, 0.27, 0.31), 0.88)

def ellipsoid(name, location, scale, material, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + " mesh"
    obj.scale = scale
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.materials.append(material)
    return move_to_collection(obj)

def ellipsoid_between(name, a, b, radius, material, radius_y=None):
    start = Vector(a)
    end = Vector(b)
    direction = end - start
    obj = ellipsoid(name, (start + end) / 2.0, (radius, radius_y or radius, direction.length / 2.0 + radius * 0.55), material)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    return obj

def loft(name, profile, material, segments=48):
    vertices = []
    faces = []
    for z, radius_x, radius_y, center_y in profile:
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            vertices.append((radius_x * math.cos(angle), center_y + radius_y * math.sin(angle), z))
    for ring in range(len(profile) - 1):
        low = ring * segments
        high = (ring + 1) * segments
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((low + index, low + nxt, high + nxt, high + index))
    faces.append(tuple(reversed(range(segments))))
    top = (len(profile) - 1) * segments
    faces.append(tuple(top + index for index in range(segments)))
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    root.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return obj

# Feet, trousers, and a broad relaxed torso. The shapes are proportions-first,
# intentionally not a final anatomical model or a rigged character.
ellipsoid("Shoe.L", (-0.135, -0.045, 0.075), (0.105, 0.19, 0.075), shoe_mat)
ellipsoid("Shoe.R", (0.135, -0.045, 0.075), (0.105, 0.19, 0.075), shoe_mat)
ellipsoid_between("Trouser lower.L", (-0.135, 0.01, 0.42), (-0.135, 0.0, 0.18), 0.095, pants, 0.105)
ellipsoid_between("Trouser lower.R", (0.135, 0.01, 0.42), (0.135, 0.0, 0.18), 0.095, pants, 0.105)
ellipsoid_between("Trouser upper.L", (-0.13, 0.015, 0.79), (-0.135, 0.01, 0.42), 0.115, pants, 0.13)
ellipsoid_between("Trouser upper.R", (0.13, 0.015, 0.79), (0.135, 0.01, 0.42), 0.115, pants, 0.13)
loft("Pelvis", [(0.69, 0.22, 0.15, 0.015), (0.78, 0.27, 0.18, 0.015), (0.91, 0.28, 0.18, 0.015), (0.98, 0.24, 0.16, 0.015)], pants)
loft("Crewneck torso", [
    (0.87, 0.235, 0.15, 0.0),
    (0.98, 0.275, 0.175, 0.0),
    (1.12, 0.305, 0.19, 0.0),
    (1.27, 0.315, 0.185, 0.0),
    (1.39, 0.315, 0.17, 0.0),
    (1.48, 0.27, 0.15, 0.0),
    (1.54, 0.15, 0.13, 0.0),
], crew)

# Arms hang naturally at the sides; separate ellipsoids are placeholders for
# later shoulder/elbow/wrist topology and deformation tests.
for side, sign in (("L", -1), ("R", 1)):
    shoulder = (sign * 0.285, 0.0, 1.405)
    elbow = (sign * 0.345, -0.005, 1.105)
    wrist = (sign * 0.355, -0.02, 0.855)
    ellipsoid_between(f"Sleeve upper.{side}", shoulder, elbow, 0.105, crew, 0.11)
    ellipsoid_between(f"Sleeve lower.{side}", elbow, wrist, 0.085, crew, 0.09)
    ellipsoid(f"Hand.{side}", (sign * 0.355, -0.03, 0.805), (0.065, 0.055, 0.095), skin)
    # A simple thumb mass preserves a readable hand silhouette at blockout scale.
    ellipsoid(f"Thumb.{side}", (sign * 0.31, -0.055, 0.815), (0.03, 0.04, 0.065), skin)

# Neck and head proportions draw on the preserved dad master; face/hair remain
# a blockout and still require likeness review before any rig is approved.
ellipsoid("Neck", (0.0, 0.0, 1.505), (0.115, 0.115, 0.115), skin)
loft("Head", [
    (1.535, 0.035, 0.045, 0.0),
    (1.565, 0.095, 0.095, 0.0),
    (1.625, 0.132, 0.12, 0.0),
    (1.715, 0.142, 0.13, 0.0),
    (1.805, 0.135, 0.125, 0.0),
    (1.865, 0.105, 0.105, 0.0),
    (1.88, 0.055, 0.06, 0.0),
], skin)

# A restrained beard mass, moustache, short sides, and a small swept-up quiff.
ellipsoid("Beard jaw mass", (0.0, -0.025, 1.605), (0.132, 0.116, 0.105), beard)
ellipsoid("Beard chin", (0.0, -0.045, 1.552), (0.102, 0.105, 0.052), beard)
ellipsoid("Moustache.L", (-0.041, -0.132, 1.654), (0.052, 0.038, 0.027), beard)
ellipsoid("Moustache.R", (0.041, -0.132, 1.654), (0.052, 0.038, 0.027), beard)
ellipsoid("Hair cap", (0.0, 0.006, 1.835), (0.139, 0.128, 0.074), hair)
ellipsoid("Hair quiff", (-0.018, -0.072, 1.865), (0.075, 0.071, 0.052), hair)
for side, sign in (("L", -1), ("R", 1)):
    ellipsoid(f"Hair side.{side}", (sign * 0.12, 0.005, 1.77), (0.037, 0.105, 0.095), hair)
    ellipsoid(f"Ear.{side}", (sign * 0.139, -0.005, 1.687), (0.03, 0.034, 0.048), skin)
    ellipsoid(f"Eye white.{side}", (sign * 0.052, -0.117, 1.735), (0.026, 0.016, 0.026), eye_white)
    ellipsoid(f"Pupil.{side}", (sign * 0.052, -0.132, 1.735), (0.011, 0.009, 0.015), pupil_mat)
    brow = ellipsoid(f"Eyebrow.{side}", (sign * 0.052, -0.119, 1.777), (0.039, 0.018, 0.012), hair)
    brow.rotation_euler[1] = math.radians(sign * -7)
ellipsoid("Nose", (0.0, -0.134, 1.688), (0.034, 0.053, 0.052), skin)
ellipsoid("Mouth line", (0.0, -0.151, 1.622), (0.039, 0.012, 0.008), feature_mat)

# Crewneck collar: explicitly no hood, matching the confirmed home-look override.
bpy.ops.mesh.primitive_torus_add(major_radius=0.112, minor_radius=0.018, major_segments=48, minor_segments=12, location=(0.0, 0.0, 1.505))
collar = bpy.context.object
collar.name = "Crewneck collar — no hood"
collar.data.materials.append(crew)
for poly in collar.data.polygons:
    poly.use_smooth = True
move_to_collection(collar)

# Keep the character as one Blender mesh object for a clean handoff, while
# retaining the intentionally disconnected primitive shells of a blockout.
character_meshes = [obj for obj in root.objects if obj.type == "MESH"]
for obj in bpy.context.selected_objects:
    obj.select_set(False)
for obj in character_meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects.get("Crewneck torso")
bpy.ops.object.join()
model = bpy.context.object
model.name = "Dad — R3 gray blockout"
model.data.name = "Dad blockout mesh shells"
model["topology_note"] = "Single mesh object; disconnected primitive shells; not production topology or rig-ready"

# Neutral studio ground.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0.0, 0.0, 0.0))
ground = bpy.context.object
ground.name = "Studio floor"
ground.data.materials.append(ground_mat)
move_to_collection(ground)

# Three native cameras provide comparable orthographic silhouettes.
def add_camera(name, location, target, scale):
    data = bpy.data.cameras.new(name + " data")
    camera = bpy.data.objects.new(name, data)
    root.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    data.type = "ORTHO"
    data.ortho_scale = scale
    data.lens = 52
    return camera

add_camera("CAM_Front", (0.0, -4.5, 1.02), (0.0, 0.0, 0.98), 2.22)
add_camera("CAM_ThreeQuarter", (3.6, -4.8, 1.08), (0.0, 0.0, 0.98), 2.22)
add_camera("CAM_Profile", (4.8, 0.0, 1.02), (0.0, 0.0, 0.98), 2.22)
scene.camera = bpy.data.objects["CAM_Front"]

def add_area(name, location, power, size, target=(0.0, 0.0, 1.0)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    light = bpy.data.objects.new(name, data)
    root.objects.link(light)
    light.location = location
    light.rotation_euler = (Vector(target) - light.location).to_track_quat("-Z", "Y").to_euler()
    return light

add_area("Key softbox", (-3.0, -4.0, 5.0), 430, 4.0)
add_area("Fill softbox", (3.5, -3.0, 2.8), 190, 3.5)
add_area("Rim softbox", (0.8, 2.8, 3.6), 320, 2.6)

# Reference images are packed into the .blend and only shown in the viewport.
# They are never used as render textures or as a substitute for 3D geometry.
def add_reference(filename, name, location, rotation):
    filepath = PROJECT_ROOT + "/references/dad-" + filename
    try:
        image = bpy.data.images.load(filepath, check_existing=True)
    except Exception as error:
        print("Reference not loaded:", filepath, error)
        return None
    empty = bpy.data.objects.new(name, None)
    refs.objects.link(empty)
    empty.empty_display_type = "IMAGE"
    empty.data = image
    empty.empty_display_size = 1.9
    empty.empty_image_offset = (0.5, 0.5)
    empty.location = location
    empty.rotation_euler = rotation
    empty.show_in_front = True
    empty.hide_render = True
    return empty

add_reference("front.png", "REF — Dad front", (0.0, 0.75, 0.98), (math.radians(90), 0.0, 0.0))
add_reference("side.png", "REF — Dad profile", (0.75, 0.0, 0.98), Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))).to_euler())
add_reference("face.png", "REF — Dad face", (0.0, 0.80, 1.72), (math.radians(90), 0.0, 0.0))

# Keep the viewport easy to inspect on opening the .blend.
for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_distance = 3.8
        area.spaces.active.region_3d.view_location = (0.0, 0.0, 0.98)

for image in list(bpy.data.images):
    if image.source == "FILE" and image.packed_file is None:
        try:
            image.pack()
        except Exception as error:
            print("Image packing warning:", image.name, error)

scene.frame_set(1)
bpy.context.view_layer.update()
print("FAMILY_STUDIO_BLOCKOUT_READY: Dad gray 3D blockout built with Blender Python; crewneck/no hood; 3 cameras; Cycles preview ready.")
