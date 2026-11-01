import bpy
import math
from mathutils import Vector, Matrix

PROJECT_ROOT = r"__FAMILY_STUDIO_PROJECT_ROOT__"

# R4 hero-model iteration v1: a complete, colored, static 3D figure built in
# Blender Python from Family Studio's local Dad references. This is not a rigged
# production asset yet; topology and deformation still require their own gates.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for collection in list(bpy.data.collections):
    if collection.name.startswith(("DAD — R4 HERO MODEL", "STUDIO — R4", "REFERENCE IMAGES — viewport only")):
        bpy.data.collections.remove(collection)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)
for material in list(bpy.data.materials):
    bpy.data.materials.remove(material)

scene = bpy.context.scene
scene.name = "Dad — R4 hero model v1"
scene["family_studio_stage"] = "R4 hero model v1 — static; likeness and technical gates pending"
scene["family_studio_costume_override"] = "warm light gray crewneck, no hood"
scene["family_studio_reference"] = "assets/references/character-masters/characters/dad"
scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 512
scene.render.resolution_y = 896
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = "//renders/dad-hero-v1/"
scene.view_settings.view_transform = "AgX"
scene.world = scene.world or bpy.data.worlds.new("Dad R4 studio world")
scene.world.use_nodes = True
world_bg = scene.world.node_tree.nodes.get("Background")
world_bg.inputs["Color"].default_value = (0.12, 0.15, 0.20, 1.0)
world_bg.inputs["Strength"].default_value = 0.24

root = bpy.data.collections.new("DAD — R4 HERO MODEL v1")
scene.collection.children.link(root)
studio = bpy.data.collections.new("STUDIO — R4 presentation")
scene.collection.children.link(studio)
refs = bpy.data.collections.new("REFERENCE IMAGES — viewport only")
scene.collection.children.link(refs)


def move_to(obj, collection=root):
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def set_active(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def material(name, color, roughness=0.5, metallic=0.0, subsurface=0.0, texture=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    shader = nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if "Specular IOR Level" in shader.inputs:
        shader.inputs["Specular IOR Level"].default_value = 0.28
    if "Subsurface Weight" in shader.inputs:
        shader.inputs["Subsurface Weight"].default_value = subsurface
    if texture:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = texture[0]
        noise.inputs["Detail"].default_value = 2.0
        noise.inputs["Roughness"].default_value = 0.62
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = texture[1]
        bump.inputs["Distance"].default_value = texture[2]
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    return mat


skin = material("Skin · warm peach", (0.58, 0.31, 0.18), 0.48, subsurface=0.055, texture=(185.0, 0.055, 0.012))
skin_light = material("Skin · highlight", (0.67, 0.39, 0.25), 0.46, subsurface=0.045)
skin_shadow = material("Ear / nostril · warm shadow", (0.31, 0.12, 0.085), 0.62)
hair = material("Hair · deep chestnut", (0.045, 0.017, 0.008), 0.62, texture=(110.0, 0.045, 0.004))
hair_hi = material("Hair locks · warm chestnut", (0.072, 0.028, 0.012), 0.60)
beard = material("Beard · dark chestnut", (0.048, 0.018, 0.009), 0.68, texture=(155.0, 0.05, 0.004))
beard_hi = material("Beard texture · chestnut", (0.085, 0.032, 0.014), 0.66)
white = material("Eyes · warm ivory", (0.88, 0.79, 0.66), 0.25)
iris = material("Eyes · warm brown iris", (0.24, 0.105, 0.045), 0.28)
iris_inner = material("Eyes · amber iris", (0.43, 0.22, 0.075), 0.31)
pupil = material("Eyes · pupil", (0.022, 0.014, 0.012), 0.18)
glint = material("Eyes · catchlight", (1.0, 0.94, 0.78), 0.12)
crew = material("Crewneck · warm light gray", (0.42, 0.41, 0.38), 0.78, texture=(235.0, 0.14, 0.009))
crew_rib = material("Crewneck · rib knit", (0.35, 0.34, 0.31), 0.84, texture=(260.0, 0.12, 0.006))
thread = material("Garment stitching · warm gray", (0.55, 0.52, 0.46), 0.76)
denim = material("Jeans · deep indigo charcoal", (0.047, 0.061, 0.086), 0.78, texture=(185.0, 0.20, 0.012))
denim_hi = material("Jeans seams · slate blue", (0.13, 0.16, 0.19), 0.75)
leather = material("Sneakers · dark warm brown leather", (0.16, 0.082, 0.043), 0.48, texture=(125.0, 0.09, 0.008))
sole_mat = material("Sneaker soles · dark rubber", (0.055, 0.047, 0.042), 0.77)
metal = material("Eyelets · antique brass", (0.38, 0.24, 0.10), 0.3, metallic=0.65)
backdrop_mat = material("Studio backdrop · midnight blue", (0.038, 0.052, 0.075), 0.9)


def uv(name, loc, scale, mat, segments=40, rings=28, collection=root):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return move_to(obj, collection)


def loft_z(name, profile, mat, center_x=0.0, segments=48, collection=root):
    # profile rows: (z, radius_x, radius_y, center_y); clean, regular rings.
    verts = []
    faces = []
    for z, rx, ry, cy in profile:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            verts.append((center_x + rx * math.cos(a), cy + ry * math.sin(a), z))
    for row in range(len(profile) - 1):
        lo, hi = row * segments, (row + 1) * segments
        for i in range(segments):
            nxt = (i + 1) % segments
            faces.append((lo + i, lo + nxt, hi + nxt, hi + i))
    faces.append(tuple(reversed(tuple(range(segments)))))
    top = (len(profile) - 1) * segments
    faces.append(tuple(top + i for i in range(segments)))
    mesh = bpy.data.meshes.new(name + " · quad rings")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return obj


def loft_y(name, profile, mat, center_x=0.0, segments=40, collection=root):
    # Cross-sections along the foot depth: (y, radius_x, center_z, radius_z).
    verts = []
    faces = []
    for y, rx, cz, rz in profile:
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            verts.append((center_x + rx * math.cos(a), y, cz + rz * math.sin(a)))
    for row in range(len(profile) - 1):
        lo, hi = row * segments, (row + 1) * segments
        for i in range(segments):
            nxt = (i + 1) % segments
            faces.append((lo + i, lo + nxt, hi + nxt, hi + i))
    faces.append(tuple(reversed(tuple(range(segments)))))
    top = (len(profile) - 1) * segments
    faces.append(tuple(top + i for i in range(segments)))
    mesh = bpy.data.meshes.new(name + " · quad rings")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return obj


def tube_mesh(name, points, radii, mat, sides=12, collection=root, elliptical=None):
    # Swept, capped tube following a centerline; radii taper smoothly between samples.
    points = [Vector(p) for p in points]
    if len(points) < 2:
        raise ValueError("tube_mesh needs at least two points")
    if isinstance(radii, (int, float)):
        radii = [float(radii)] * len(points)
    if len(radii) != len(points):
        raise ValueError("tube_mesh radius count must match point count")
    verts = []
    faces = []
    for idx, point in enumerate(points):
        if idx == 0:
            tangent = (points[1] - point).normalized()
        elif idx == len(points) - 1:
            tangent = (point - points[idx - 1]).normalized()
        else:
            tangent = (points[idx + 1] - points[idx - 1]).normalized()
        guide = Vector((0.0, 1.0, 0.0))
        if abs(tangent.dot(guide)) > 0.93:
            guide = Vector((1.0, 0.0, 0.0))
        axis_a = tangent.cross(guide).normalized()
        axis_b = tangent.cross(axis_a).normalized()
        rx, ry = (radii[idx], radii[idx]) if elliptical is None else elliptical[idx]
        for side in range(sides):
            angle = 2.0 * math.pi * side / sides
            p = point + axis_a * (math.cos(angle) * rx) + axis_b * (math.sin(angle) * ry)
            verts.append(tuple(p))
    for row in range(len(points) - 1):
        lo, hi = row * sides, (row + 1) * sides
        for j in range(sides):
            nxt = (j + 1) % sides
            faces.append((lo + j, lo + nxt, hi + nxt, hi + j))
    faces.append(tuple(reversed(tuple(range(sides)))))
    top = (len(points) - 1) * sides
    faces.append(tuple(top + j for j in range(sides)))
    mesh = bpy.data.meshes.new(name + " · swept surface")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    for poly in mesh.polygons:
        poly.use_smooth = len(poly.vertices) == 4
    return obj


def line(name, points, radius, mat, sides=8, collection=root):
    return tube_mesh(name, points, radius, mat, sides=sides, collection=collection)


def smooth_subdivision(obj, levels=1):
    modifier = obj.modifiers.new("Smooth surface refinement", "SUBSURF")
    modifier.subdivision_type = "CATMULL_CLARK"
    modifier.levels = levels
    modifier.render_levels = levels
    return obj


def elliptical_ring(name, center, rx, ry, tube_radius, mat, plane="XY", steps=64, collection=root):
    points = []
    for i in range(steps):
        a = 2.0 * math.pi * i / steps
        if plane == "XY":
            points.append((center[0] + rx * math.cos(a), center[1] + ry * math.sin(a), center[2]))
        elif plane == "XZ":
            points.append((center[0] + rx * math.cos(a), center[1], center[2] + ry * math.sin(a)))
        else:
            points.append((center[0], center[1] + rx * math.cos(a), center[2] + ry * math.sin(a)))
    radii = [tube_radius] * (steps + 1)
    return tube_mesh(name, points + [points[0]], radii, mat, sides=8, collection=collection)


def make_material_detail_noise(mat, scale, strength, distance):
    nodes = mat.node_tree.nodes
    shader = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 2.0
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    mat.node_tree.links.new(bump.outputs["Normal"], shader.inputs["Normal"])


# ---- Head and identity ----------------------------------------------------
# Mature, softly squared jaw and wide friendly cheeks; face points toward -Y.
head_profile = [
    (1.535, 0.065, 0.078, 0.004),
    (1.565, 0.105, 0.105, 0.002),
    (1.610, 0.137, 0.129, 0.000),
    (1.675, 0.155, 0.143, 0.000),
    (1.755, 0.164, 0.145, 0.002),
    (1.830, 0.158, 0.139, 0.006),
    (1.890, 0.137, 0.123, 0.010),
    (1.925, 0.094, 0.089, 0.012),
    (1.936, 0.018, 0.022, 0.012),
]
head = loft_z("Head · shaped base", head_profile, skin, segments=64)
smooth_subdivision(head, levels=2)
head["surface_note"] = "Profile-built stylized head base; facial parts are separate for later rigging"

# Ears: broad shells with warm inner concha; left/right are mirrored in the relaxed pose.
for side, sign in (("L", -1), ("R", 1)):
    uv("Ear shell." + side, (sign * 0.158, -0.002, 1.724), (0.052, 0.041, 0.073), skin)
    uv("Ear concha." + side, (sign * 0.180, -0.036, 1.724), (0.023, 0.012, 0.043), skin_shadow, segments=28, rings=20)
    line("Ear helix." + side, [
        (sign * 0.181, -0.042, 1.756), (sign * 0.194, -0.046, 1.740),
        (sign * 0.190, -0.047, 1.712), (sign * 0.176, -0.044, 1.702),
    ], 0.005, skin_light, sides=8)

# Beard: a surface patch sampled directly from the head profile so it hugs the jaw.
# It wraps from the chin across the cheeks and rises toward the sideburns.
def head_radii_at(z):
    if z <= head_profile[0][0]:
        return head_profile[0][1], head_profile[0][2], head_profile[0][3]
    if z >= head_profile[-1][0]:
        return head_profile[-1][1], head_profile[-1][2], head_profile[-1][3]
    for a, b in zip(head_profile[:-1], head_profile[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return (a[1] + (b[1] - a[1]) * t,
                    a[2] + (b[2] - a[2]) * t,
                    a[3] + (b[3] - a[3]) * t)
    return head_profile[-1][1], head_profile[-1][2], head_profile[-1][3]

beard_verts, beard_faces = [], []
lon_steps, lat_steps = 64, 24
for j in range(lat_steps + 1):
    v = j / lat_steps
    for i in range(lon_steps + 1):
        u = i / lon_steps
        norm_x = u * 2.0 - 1.0
        lon = norm_x * 1.72
        side = abs(norm_x)
        z_bottom = 1.555 + 0.022 * side
        z_top = 1.660 + 0.112 * (side ** 1.35)
        z = z_bottom + (z_top - z_bottom) * v
        rx, ry, cy = head_radii_at(z)
        x = (rx + 0.003) * math.sin(lon)
        y = cy - (ry + 0.004) * math.cos(lon)
        beard_verts.append((x, y, z))
for j in range(lat_steps):
    for i in range(lon_steps):
        a = j * (lon_steps + 1) + i
        b = a + 1
        c = b + lon_steps + 1
        d = a + lon_steps + 1
        beard_faces.append((a, b, c, d))
beard_mesh = bpy.data.meshes.new("Beard · face-conforming shell mesh")
beard_mesh.from_pydata(beard_verts, [], beard_faces)
beard_mesh.materials.append(beard)
beard_mesh.update()
beard_obj = bpy.data.objects.new("Beard · shaped full coverage", beard_mesh)
root.objects.link(beard_obj)
for poly in beard_mesh.polygons:
    poly.use_smooth = True
solid = beard_obj.modifiers.new("Beard shell thickness", "SOLIDIFY")
solid.thickness = 0.006
solid.offset = 0.0

# Sideburn extensions blend the beard mass into the short fade.
for side, sign in (("L", -1), ("R", 1)):
    loft_z("Sideburn." + side, [
        (1.661, 0.018, 0.022, -0.005),
        (1.700, 0.026, 0.025, -0.002),
        (1.758, 0.022, 0.022, 0.003),
    ], beard, center_x=sign * 0.142, segments=24)

# Eyes: layered sclera, brown iris, dark pupil and soft catchlights.
for side, sign in (("L", -1), ("R", 1)):
    cx, cz = sign * 0.058, 1.783
    uv("Eye socket." + side, (cx, -0.124, cz), (0.044, 0.019, 0.033), skin)
    uv("Eyeball." + side, (cx, -0.136, cz), (0.034, 0.019, 0.025), white)
    uv("Iris." + side, (cx + sign * 0.001, -0.152, cz), (0.016, 0.008, 0.017), iris)
    uv("Iris inner." + side, (cx + sign * 0.001, -0.158, cz), (0.010, 0.005, 0.012), iris_inner)
    uv("Pupil." + side, (cx + sign * 0.001, -0.162, cz), (0.0065, 0.003, 0.010), pupil)
    uv("Catchlight." + side, (cx - 0.004, -0.165, cz + 0.007), (0.0038, 0.002, 0.0038), glint, segments=20, rings=12)
    # Upper/lower eyelid arcs frame the eyeball; proper deformable lids are a later rig gate.
    line("Upper eyelid." + side, [
        (cx - 0.035, -0.140, cz), (cx - 0.022, -0.151, cz + 0.019),
        (cx, -0.153, cz + 0.025), (cx + 0.022, -0.151, cz + 0.019),
        (cx + 0.035, -0.140, cz),
    ], 0.0045, skin_light)
    line("Lower eyelid." + side, [
        (cx - 0.035, -0.140, cz), (cx - 0.021, -0.148, cz - 0.015),
        (cx, -0.149, cz - 0.018), (cx + 0.021, -0.148, cz - 0.015),
        (cx + 0.035, -0.140, cz),
    ], 0.0032, skin_light)
    line("Eyebrow." + side, [
        (cx - 0.045, -0.145, 1.838), (cx - 0.026, -0.158, 1.851),
        (cx, -0.160, 1.855), (cx + 0.028, -0.157, 1.848),
        (cx + 0.045, -0.145, 1.837),
    ], 0.011, hair, sides=10)

# Nose bridge, tip, alae and restrained nostril accents.
uv("Nose bridge", (0.0, -0.142, 1.748), (0.019, 0.029, 0.067), skin_light)
uv("Nose tip", (0.0, -0.166, 1.704), (0.032, 0.026, 0.024), skin)
for side, sign in (("L", -1), ("R", 1)):
    uv("Nasal ala." + side, (sign * 0.024, -0.158, 1.697), (0.015, 0.017, 0.012), skin)
    uv("Nostril." + side, (sign * 0.018, -0.174, 1.689), (0.0055, 0.0025, 0.0035), skin_shadow, segments=20, rings=12)

# Moustache shape above the mouth; a soft smile line remains visible beneath it.
for side, sign in (("L", -1), ("R", 1)):
    tube_mesh("Moustache lobe." + side, [
        (sign * 0.006, -0.174, 1.674), (sign * 0.024, -0.185, 1.682),
        (sign * 0.046, -0.173, 1.675), (sign * 0.061, -0.157, 1.661),
    ], [0.007, 0.012, 0.011, 0.004], beard_hi, sides=12)
line("Smile crease", [(-0.048, -0.163, 1.653), (-0.025, -0.176, 1.648), (0.0, -0.180, 1.646), (0.025, -0.176, 1.648), (0.048, -0.163, 1.653)], 0.0035, skin_shadow)
uv("Lower lip", (0.0, -0.170, 1.641), (0.028, 0.010, 0.008), skin_light, segments=28, rings=16)

# Hair cap follows the skull; tapered swept clumps make the quiff three-dimensional.
uv("Hair cap · short fade base", (0.0, 0.012, 1.887), (0.151, 0.137, 0.091), hair, segments=48, rings=32)
for side, sign in (("L", -1), ("R", 1)):
    loft_z("Fade temple." + side, [
        (1.805, 0.018, 0.038, 0.012),
        (1.845, 0.027, 0.043, 0.012),
        (1.884, 0.031, 0.045, 0.012),
    ], hair, center_x=sign * 0.132, segments=24)
# Swept locks rise at the hairline and flow toward the crown/back, with restrained chestnut highlights.
for idx, x in enumerate([-0.118, -0.088, -0.058, -0.029, 0.0, 0.029, 0.058, 0.088, 0.118]):
    t = abs(x) / 0.118
    base_y = -0.090 + 0.018 * t
    base_z = 1.884 - 0.010 * t
    points = [
        (x, base_y, base_z),
        (x * 0.88, base_y - 0.015, 1.919 + 0.008 * (1.0 - t)),
        (x * 0.62, -0.018, 1.958 + 0.012 * (1.0 - t)),
        (x * 0.38, 0.028, 1.975 + 0.012 * (1.0 - t)),
    ]
    radii = [0.023 - 0.005 * t, 0.029 - 0.005 * t, 0.020 - 0.003 * t, 0.002]
    lock = tube_mesh("Swept quiff lock %02d" % idx, points, radii, hair_hi if idx % 3 == 1 else hair, sides=14)
    smooth_subdivision(lock, 1)
# Short side locks keep the fade readable in profile and three-quarter views.
for side, sign in (("L", -1), ("R", 1)):
    for i in range(3):
        x = sign * (0.118 + 0.012 * i)
        tube_mesh("Temple lock %s %d" % (side, i), [
            (x, -0.066 + 0.012 * i, 1.888 - 0.012 * i),
            (x * 1.04, -0.035 + 0.01 * i, 1.915 - 0.009 * i),
            (x * 0.96, 0.010 + 0.012 * i, 1.922 - 0.008 * i),
        ], [0.014, 0.016, 0.0015], hair_hi if i == 1 else hair, sides=10)
        smooth_subdivision(bpy.data.objects["Temple lock %s %d" % (side, i)], 1)

# ---- Body, clothing and shoes --------------------------------------------
# Neck sits naturally inside the ribbed crewneck opening.
loft_z("Neck", [
    (1.455, 0.075, 0.080, 0.006),
    (1.515, 0.083, 0.082, 0.006),
    (1.585, 0.078, 0.078, 0.006),
], skin, segments=40)

# Broad torso with relaxed abdomen and sloped shoulders, tailored as one garment shell.
torso = loft_z("Crewneck torso · relaxed fit", [
    (0.865, 0.224, 0.145, 0.008),
    (0.900, 0.258, 0.163, 0.008),
    (0.980, 0.274, 0.174, 0.008),
    (1.085, 0.291, 0.184, 0.006),
    (1.205, 0.300, 0.184, 0.004),
    (1.325, 0.310, 0.175, 0.003),
    (1.405, 0.300, 0.160, 0.004),
    (1.462, 0.248, 0.138, 0.005),
    (1.495, 0.147, 0.105, 0.006),
], crew, segments=64)
smooth_subdivision(torso, levels=1)
# Bottom band is a separate, slightly thicker rib-knit garment piece.
loft_z("Crewneck hem band", [
    (0.875, 0.234, 0.152, 0.008),
    (0.888, 0.270, 0.169, 0.008),
    (0.927, 0.270, 0.169, 0.008),
    (0.940, 0.261, 0.166, 0.008),
], crew_rib, segments=64)
elliptical_ring("Hem seam · upper", (0.0, 0.008, 0.930), 0.270, 0.169, 0.0022, thread)

# Crewneck collar: soft ribbed roll; the shape is explicitly hood-free.
elliptical_ring("Crewneck rib collar", (0.0, 0.006, 1.492), 0.117, 0.103, 0.016, crew_rib)
elliptical_ring("Crewneck collar seam", (0.0, 0.006, 1.475), 0.132, 0.113, 0.003, thread)

# Arms are separate, smoothly swept sleeves; elbows hang in a calm relaxed pose.
for side, sign in (("L", -1), ("R", 1)):
    shoulder = (sign * 0.175, 0.004, 1.365)
    elbow = (sign * 0.333, -0.006, 1.165)
    forearm = (sign * 0.352, -0.018, 0.980)
    wrist = (sign * 0.356, -0.026, 0.900)
    tube_mesh("Crewneck sleeve." + side, [shoulder, (sign * 0.267, 0.001, 1.330), elbow, forearm, wrist], [0.112, 0.111, 0.098, 0.083, 0.078], crew, sides=32, elliptical=[(0.115,0.130),(0.110,0.124),(0.100,0.113),(0.088,0.098),(0.080,0.090)])
    tube_mesh("Rib cuff." + side, [
        (sign * 0.355, -0.022, 0.925), (sign * 0.356, -0.024, 0.900),
        (sign * 0.357, -0.025, 0.879),
    ], [0.080, 0.084, 0.079], crew_rib, sides=28, elliptical=[(0.082,0.094),(0.086,0.097),(0.081,0.092)])
    line("Sleeve seam." + side, [
        (sign * 0.300, -0.101, 1.334), (sign * 0.328, -0.095, 1.255),
        (sign * 0.344, -0.090, 1.170), (sign * 0.351, -0.085, 1.085),
        (sign * 0.354, -0.078, 0.985),
    ], 0.0022, crew_rib)

# Hands: palms, articulated finger segments and thumbs. Five digits per hand.
for side, sign in (("L", -1), ("R", 1)):
    uv("Palm." + side, (sign * 0.359, -0.030, 0.810), (0.063, 0.047, 0.086), skin)
    finger_x = [0.322, 0.346, 0.369, 0.391]
    finger_lengths = [0.094, 0.111, 0.105, 0.081]
    finger_radii = [0.014, 0.015, 0.014, 0.012]
    for i, (fx, length, radius) in enumerate(zip(finger_x, finger_lengths, finger_radii)):
        x = sign * fx
        root_z = 0.766 + (0.009 if i in (0, 3) else 0.0)
        mid_z = root_z - length * 0.53
        tip_z = root_z - length
        tube_mesh("Finger %s %d" % (side, i + 1), [
            (x, -0.042, root_z), (x + sign * 0.003, -0.050, mid_z),
            (x + sign * 0.004, -0.046, tip_z),
        ], [radius, radius * 0.88, radius * 0.58], skin, sides=10)
        uv("Knuckle %s %d" % (side, i + 1), (x, -0.048, root_z - 0.009), (radius * 1.02, radius * 0.78, radius * 0.86), skin, segments=20, rings=12)
    tube_mesh("Thumb." + side, [
        (sign * 0.315, -0.036, 0.831), (sign * 0.293, -0.052, 0.800),
        (sign * 0.289, -0.057, 0.765),
    ], [0.022, 0.019, 0.012], skin, sides=12)

# Dark straight jeans: a relaxed waist/hip and separate shaped legs.
loft_z("Jeans · waist and seat", [
    (0.728, 0.216, 0.135, 0.012),
    (0.770, 0.252, 0.158, 0.010),
    (0.838, 0.263, 0.166, 0.008),
    (0.886, 0.249, 0.159, 0.008),
], denim, segments=56)
for side, sign in (("L", -1), ("R", 1)):
    cx = sign * 0.132
    loft_z("Jeans leg." + side, [
        (0.115, 0.083, 0.093, 0.010),
        (0.150, 0.086, 0.095, 0.010),
        (0.235, 0.089, 0.097, 0.011),
        (0.340, 0.092, 0.103, 0.011),
        (0.440, 0.101, 0.112, 0.012),
        (0.535, 0.108, 0.119, 0.012),
        (0.620, 0.112, 0.123, 0.011),
        (0.710, 0.119, 0.130, 0.010),
        (0.795, 0.128, 0.136, 0.008),
        (0.842, 0.126, 0.131, 0.008),
    ], denim, center_x=cx, segments=40)
    # Bottom turn-up and top-stitching catch light subtly without changing the silhouette.
    elliptical_ring("Jeans hem seam." + side, (cx, 0.010, 0.157), 0.087, 0.096, 0.0024, denim_hi)
    line("Jeans outer seam." + side, [
        (cx + sign * 0.081, -0.015, 0.175), (cx + sign * 0.089, -0.021, 0.310),
        (cx + sign * 0.101, -0.025, 0.470), (cx + sign * 0.111, -0.029, 0.640),
        (cx + sign * 0.121, -0.025, 0.795),
    ], 0.0022, denim_hi)
# Waistline, fly and simplified front pocket stitch outlines.
line("Jeans fly seam", [(0.0, -0.159, 0.862), (0.0, -0.166, 0.830), (0.004, -0.168, 0.790), (0.0, -0.164, 0.762)], 0.0025, denim_hi)
for side, sign in (("L", -1), ("R", 1)):
    line("Jeans pocket seam." + side, [
        (sign * 0.050, -0.157, 0.866), (sign * 0.095, -0.162, 0.851),
        (sign * 0.172, -0.142, 0.810), (sign * 0.188, -0.130, 0.776),
    ], 0.0024, denim_hi)

# Brown low-top sneakers: shaped toe/heel profile, rubber outsole and restrained eyelets.
for side, sign in (("L", -1), ("R", 1)):
    cx = sign * 0.132
    sole = loft_y("Sneaker rubber outsole." + side, [
        (-0.225, 0.034, 0.052, 0.022),
        (-0.208, 0.074, 0.052, 0.026),
        (-0.160, 0.090, 0.052, 0.027),
        (-0.060, 0.087, 0.052, 0.027),
        (0.060, 0.081, 0.052, 0.027),
        (0.132, 0.050, 0.052, 0.026),
    ], sole_mat, center_x=cx, segments=40)
    smooth_subdivision(sole, 1)
    upper = loft_y("Sneaker leather upper." + side, [
        (-0.214, 0.028, 0.112, 0.018),
        (-0.196, 0.064, 0.113, 0.042),
        (-0.156, 0.083, 0.119, 0.056),
        (-0.092, 0.090, 0.127, 0.067),
        (-0.018, 0.085, 0.140, 0.076),
        (0.060, 0.077, 0.151, 0.087),
        (0.117, 0.055, 0.156, 0.088),
        (0.137, 0.034, 0.153, 0.066),
    ], leather, center_x=cx, segments=40)
    smooth_subdivision(upper, 1)
    uv("Sneaker tongue." + side, (cx, -0.071, 0.171), (0.043, 0.068, 0.017), leather)
    line("Sneaker welt." + side, [
        (cx - 0.080, -0.042, 0.078), (cx - 0.070, -0.157, 0.078),
        (cx, -0.204, 0.078), (cx + 0.070, -0.157, 0.078),
        (cx + 0.080, -0.042, 0.078),
    ], 0.0025, sole_mat)
    for j in range(3):
        z = 0.145 + j * 0.014
        y = -0.112 + j * 0.030
        uv("Sneaker eyelet %s %d" % (side, j), (cx + sign * 0.040, y, z), (0.005, 0.003, 0.005), metal, segments=16, rings=10)
    line("Sneaker lace." + side, [(cx - 0.027, -0.140, 0.169), (cx + 0.027, -0.120, 0.169), (cx - 0.027, -0.100, 0.169), (cx + 0.027, -0.080, 0.169)], 0.0022, thread)

# ---- Presentation, cameras and packed reference images -------------------
# Large seamless cyclorama floor/backdrop, kept separate from the character.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0.0, 0.0, 0.0))
floor = bpy.context.object
floor.name = "Studio floor"
floor.data.materials.append(backdrop_mat)
move_to(floor, studio)


def add_camera(name, location, target, scale):
    data = bpy.data.cameras.new(name + " data")
    camera = bpy.data.objects.new(name, data)
    studio.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    data.type = "ORTHO"
    data.ortho_scale = scale
    data.lens = 55
    return camera

add_camera("CAM_Front", (0.0, -5.4, 1.02), (0.0, 0.0, 1.00), 2.16)
add_camera("CAM_ThreeQuarter", (3.6, -5.3, 1.08), (0.0, 0.0, 1.00), 2.16)
add_camera("CAM_Profile", (5.4, 0.0, 1.02), (0.0, 0.0, 1.00), 2.16)
add_camera("CAM_Back", (0.0, 5.4, 1.02), (0.0, 0.0, 1.00), 2.16)
add_camera("CAM_FaceCloseup", (0.0, -4.6, 1.745), (0.0, 0.0, 1.745), 0.57)
scene.camera = bpy.data.objects["CAM_Front"]


def area(name, location, power, size, target=(0.0, 0.0, 1.05), color=(1.0, 1.0, 1.0)):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    studio.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj

area("Key · warm softbox", (-3.2, -4.2, 4.8), 300, 3.3, color=(1.0, 0.86, 0.74))
area("Fill · cool softbox", (3.0, -3.5, 2.7), 175, 3.2, color=(0.78, 0.86, 1.0))
area("Rim · warm edge", (0.8, 2.5, 3.4), 360, 2.0, color=(1.0, 0.78, 0.58))
area("Face · soft bounce", (-0.5, -3.2, 1.8), 65, 2.6, target=(0.0, 0.0, 1.72), color=(1.0, 0.94, 0.86))


def add_reference(filename, name, location, rotation, size=1.9):
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
    empty.empty_display_size = size
    empty.empty_image_offset = (0.5, 0.5)
    empty.location = location
    empty.rotation_euler = rotation
    empty.show_in_front = True
    empty.hide_render = True
    return empty

add_reference("front.png", "REF — Dad front", (0.0, 0.68, 0.97), (math.radians(90), 0.0, 0.0))
add_reference("side.png", "REF — Dad profile", (0.72, 0.0, 0.97), Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))).to_euler())
add_reference("face.png", "REF — Dad face", (0.0, 0.72, 1.73), (math.radians(90), 0.0, 0.0), size=0.62)

# Viewport opens on the full character and organized collections.
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        if area_ui.type == "VIEW_3D":
            area_ui.spaces.active.region_3d.view_distance = 3.7
            area_ui.spaces.active.region_3d.view_location = (0.0, 0.0, 1.0)

for image in list(bpy.data.images):
    if image.source == "FILE" and image.packed_file is None:
        try:
            image.pack()
        except Exception as error:
            print("Reference packing warning:", image.name, error)

scene.frame_set(1)
bpy.context.view_layer.update()
print("FAMILY_STUDIO_HERO_MODEL_READY: Dad R4 hero model v1 created with full body, identity details, light crewneck, dark jeans and brown sneakers; static, clean topology and rig gates still pending.")
