import bpy
import math
from mathutils import Vector

# DAD HEAD STUDY V1 — custom mesh study generated in Blender, not a primitive kit.
# Status: unapproved exploratory model; every view must be checked against masters.
# The script uses exploratory custom loft/sweep surfaces and keeps approved source
# images as packed, viewport-only guides. Silhouette CSV samples do not drive this mesh yet;
# it is not represented as a hand sculpt or as a likeness-approved model.
PROJECT_ROOT = r"__FAMILY_STUDIO_PROJECT_ROOT__"

# Clear any prior scene data so the study is reproducible.
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for collection in list(bpy.data.collections):
    if collection.users == 0:
        bpy.data.collections.remove(collection)
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
for curve in list(bpy.data.curves):
    if curve.users == 0:
        bpy.data.curves.remove(curve)

scene = bpy.context.scene
scene.name = "Dad — custom head study v1 (unapproved)"
scene["family_studio_stage"] = "UNAPPROVED detailed head study; likeness review pending"
scene["family_studio_source"] = "Dad approved face/front/three_quarter/side masters"
scene["family_studio_method"] = "Reference-driven custom loft and sweep meshes in Blender Python; not manual sculpt"
scene["family_studio_not_a_blockout"] = True
scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = True
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.render.filepath = "//renders/dad-head-study-v1/"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.world = scene.world or bpy.data.worlds.new("World")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.014, 0.018, 0.027, 1.0)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32

# Render/output collection and non-rendering reference collections.
model_collection = bpy.data.collections.new("DAD — HEAD STUDY V1 — NOT APPROVED")
scene.collection.children.link(model_collection)
reference_collection = bpy.data.collections.new("SOURCE MASTERS — VIEWPORT GUIDES ONLY")
scene.collection.children.link(reference_collection)


def move_to_collection(obj, collection=model_collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def linear_channel(value):
    value = value / 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def hex_rgb(code):
    code = code.lstrip("#")
    return tuple(linear_channel(int(code[i:i + 2], 16)) for i in (0, 2, 4))


def material(name, hex_color, roughness=0.56, subsurface=0.0, metallic=0.0):
    rgb = hex_rgb(hex_color)
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    if "Subsurface Weight" in shader.inputs:
        shader.inputs["Subsurface Weight"].default_value = subsurface
    shader.inputs["Subsurface Radius"].default_value = (0.8, 0.35, 0.18)
    shader.inputs["Metallic"].default_value = metallic
    return mat


skin = material("Skin — warm peach master palette", "E8B48F", 0.48, 0.07)
skin_shadow = material("Skin details — warm shaded peach", "B87961", 0.54, 0.025)
inner_ear = material("Ear interior — warm rose", "C98270", 0.6, 0.025)
hair = material("Hair — dark chestnut master palette", "4A332A", 0.46)
hair_light = material("Hair clumps — chestnut highlight", "694634", 0.43)
hair_dark = material("Hair clumps — deep brown", "35251F", 0.48)
beard_mat = material("Beard — deep chestnut", "493128", 0.56)
beard_light = material("Beard strands — warm chestnut", "604334", 0.52)
beard_dark = material("Beard strands — shadow brown", "35251F", 0.58)
brow_mat = material("Brows — dark chestnut", "3F2A23", 0.54)
white = material("Eyes — warm ivory", "F4EAE1", 0.32, 0.0)
iris = material("Iris — warm brown", "8A552C", 0.28)
iris_dark = material("Iris outer ring — deep brown", "4A2E20", 0.32)
pupil = material("Pupil — near black brown", "1E1714", 0.2)
glint = material("Eye catchlight", "FFF4DB", 0.12)
lip = material("Lips — muted warm rose", "B96F61", 0.5, 0.035)
mouth_dark = material("Mouth line — deep warm brown", "552C25", 0.58)


def smooth_object(obj, mat=None, subdiv=0):
    if mat is not None:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if subdiv:
        modifier = obj.modifiers.new("Surface refinement", "SUBSURF")
        modifier.levels = subdiv
        modifier.render_levels = subdiv
    return obj


def catmull_rom(values, subdivisions=3):
    """Interpolate scalar/vector profile rows without changing end constraints."""
    rows = [tuple(float(value) for value in row) for row in values]
    output = []
    for index in range(len(rows) - 1):
        p0 = rows[max(0, index - 1)]
        p1 = rows[index]
        p2 = rows[index + 1]
        p3 = rows[min(len(rows) - 1, index + 2)]
        for step in range(subdivisions):
            t = step / subdivisions
            t2 = t * t
            t3 = t2 * t
            row = []
            for col in range(len(p1)):
                value = 0.5 * ((2 * p1[col]) + (-p0[col] + p2[col]) * t +
                               (2 * p0[col] - 5 * p1[col] + 4 * p2[col] - p3[col]) * t2 +
                               (-p0[col] + 3 * p1[col] - 3 * p2[col] + p3[col]) * t3)
                row.append(value)
            output.append(tuple(row))
    output.append(rows[-1])
    return output


def make_head_surface(name, profile, mat, segments=96, subdivisions=3, socket_indent=False, beard_shape=False):
    """Continuous custom head surface lofted from measured design cross-sections.

    Profile rows: z, width radius, depth radius, depth center. Front is -Y.
    """
    rows = catmull_rom(profile, subdivisions)
    vertices = []
    faces = []
    for z, rx, ry, cy in rows:
        for index in range(segments):
            angle = 2.0 * math.pi * index / segments
            x = max(0.001, rx) * math.sin(angle)
            front_factor = math.cos(angle)
            y = cy - max(0.001, ry) * front_factor
            if beard_shape and front_factor > 0.0:
                # Raise the sideburn/jaw edge while carving the exposed lower-lip/chin patch.
                side_fraction = min(1.0, abs(x) / max(0.001, rx))
                z += 0.18 * side_fraction ** 1.8
                patch = math.exp(-((x / 0.27) ** 4 + ((z - 0.70) / 0.22) ** 4))
                y += 0.46 * patch * (front_factor ** 3)
            if socket_indent and front_factor > 0.35:
                # Subtle recessed orbital beds; the globe stays seated in the face.
                for eye_x in (-0.36, 0.36):
                    dx = (x - eye_x) / 0.24
                    dz = (z - 1.38) / 0.18
                    y += 0.060 * math.exp(-2.2 * (dx * dx + dz * dz)) * front_factor
            vertices.append((x, y, z))
    for ring in range(len(rows) - 1):
        low = ring * segments
        high = (ring + 1) * segments
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((low + index, low + nxt, high + nxt, high + index))
    bottom = len(vertices)
    top = bottom + 1
    vertices.extend([(0.0, rows[0][3], rows[0][0]), (0.0, rows[-1][3], rows[-1][0])])
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((bottom, nxt, index))
        top_ring = (len(rows) - 1) * segments
        faces.append((top, top_ring + index, top_ring + nxt))
    mesh = bpy.data.meshes.new(name + " — continuous loft mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    model_collection.objects.link(obj)
    smooth_object(obj, mat, 1)
    return obj


def make_ellipsoid(name, location, radii, mat, segments=48, rings=32):
    """Create a smooth, dense custom UV surface for an anatomical sub-form."""
    rx, ry, rz = radii
    vertices = [(location[0], location[1], location[2] - rz)]
    faces = []
    for ring in range(1, rings):
        phi = -math.pi / 2.0 + math.pi * ring / rings
        cp = math.cos(phi)
        sp = math.sin(phi)
        for index in range(segments):
            theta = 2.0 * math.pi * index / segments
            vertices.append((location[0] + rx * cp * math.sin(theta),
                             location[1] - ry * cp * math.cos(theta),
                             location[2] + rz * sp))
    top = len(vertices)
    vertices.append((location[0], location[1], location[2] + rz))
    first_ring = 1
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((0, first_ring + nxt, first_ring + index))
    for ring in range(rings - 2):
        low = first_ring + ring * segments
        high = low + segments
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((low + index, low + nxt, high + nxt, high + index))
    last_ring = first_ring + (rings - 2) * segments
    for index in range(segments):
        nxt = (index + 1) % segments
        faces.append((last_ring + index, last_ring + nxt, top))
    mesh = bpy.data.meshes.new(name + " — shaped surface")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    model_collection.objects.link(obj)
    smooth_object(obj, mat, 1)
    return obj


def make_sweep(name, points, radii, mat, sides=10, samples_per_span=5):
    """Custom tapered sweep mesh used for eyelids, brows, hair and beard clumps."""
    pts = [Vector(p) for p in points]
    samples = []
    for index in range(len(pts) - 1):
        p0 = pts[max(0, index - 1)]
        p1 = pts[index]
        p2 = pts[index + 1]
        p3 = pts[min(len(pts) - 1, index + 2)]
        r1 = radii[index]
        r2 = radii[index + 1]
        for step in range(samples_per_span):
            t = step / samples_per_span
            t2, t3 = t * t, t * t * t
            point = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
            radius = r1 * (1 - t) + r2 * t
            samples.append((point, max(0.001, radius)))
    samples.append((pts[-1], max(0.001, radii[-1])))
    vertices = []
    faces = []
    for index, (point, radius) in enumerate(samples):
        tangent = (samples[min(index + 1, len(samples) - 1)][0] - samples[max(index - 1, 0)][0]).normalized()
        reference = Vector((0.0, 1.0, 0.0))
        if abs(tangent.dot(reference)) > 0.92:
            reference = Vector((1.0, 0.0, 0.0))
        axis_a = tangent.cross(reference).normalized()
        axis_b = tangent.cross(axis_a).normalized()
        for side in range(sides):
            angle = 2.0 * math.pi * side / sides
            offset = axis_a * (math.cos(angle) * radius) + axis_b * (math.sin(angle) * radius * 0.72)
            vertices.append(tuple(point + offset))
    for ring in range(len(samples) - 1):
        low = ring * sides
        high = (ring + 1) * sides
        for index in range(sides):
            nxt = (index + 1) % sides
            faces.append((low + index, low + nxt, high + nxt, high + index))
    mesh = bpy.data.meshes.new(name + " — tapered sweep mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    model_collection.objects.link(obj)
    smooth_object(obj, mat, 1)
    return obj


# Main head and neck: broad cheeks, strong jaw, round skull, custom smooth profile.
head_profile = [
    (0.04, 0.12, 0.13, 0.00),
    (0.10, 0.28, 0.34, 0.02),
    (0.22, 0.43, 0.43, 0.02),
    (0.42, 0.58, 0.49, 0.03),
    (0.66, 0.70, 0.51, 0.03),
    (0.90, 0.77, 0.49, 0.04),
    (1.12, 0.80, 0.47, 0.04),
    (1.34, 0.76, 0.46, 0.04),
    (1.53, 0.78, 0.48, 0.05),
    (1.72, 0.79, 0.49, 0.06),
    (1.91, 0.76, 0.49, 0.07),
    (2.08, 0.68, 0.45, 0.07),
    (2.20, 0.46, 0.34, 0.08),
    (2.26, 0.12, 0.10, 0.08),
]
head = make_head_surface("Head — continuous custom form", head_profile, skin, socket_indent=True)
head["design_note"] = "Main face/head volume; not an ellipsoid primitive"

neck_profile = [
    (-0.38, 0.34, 0.32, 0.08),
    (-0.18, 0.32, 0.31, 0.08),
    (0.08, 0.31, 0.31, 0.08),
    (0.32, 0.38, 0.34, 0.08),
    (0.52, 0.45, 0.35, 0.07),
]
neck = make_head_surface("Neck — tapered custom form", neck_profile, skin, segments=72, subdivisions=3)

# Volumetric full beard: rounded cross-sections wrap around jaw and chin.
beard_profile = [
    (0.025, 0.10, 0.10, -0.18),
    (0.08, 0.28, 0.24, -0.24),
    (0.18, 0.43, 0.32, -0.27),
    (0.34, 0.56, 0.36, -0.28),
    (0.53, 0.65, 0.38, -0.27),
    (0.70, 0.70, 0.39, -0.27),
    (0.84, 0.68, 0.40, -0.28),
    (0.96, 0.62, 0.37, -0.27),
    (1.04, 0.50, 0.30, -0.23),
]
beard_obj = make_head_surface("Beard — volumetric jaw and chin shell", beard_profile, beard_mat,
                               segments=96, subdivisions=4)
beard_obj["design_note"] = "Rounded 3D shell wrapping jaw; preserve reference silhouette"
# The source master has a small exposed skin patch under the lower lip/goatee area.
make_ellipsoid("Exposed chin patch — skin", (0.0, -0.66, 0.70), (0.19, 0.035, 0.18),
               skin, segments=48, rings=32)

# Ears: custom shaped volumes with outer folds and inner concha accents.
for side in (-1, 1):
    x = side * 0.77
    ear = make_ellipsoid("Ear — left custom cartilage" if side < 0 else "Ear — right custom cartilage",
                         (x, -0.02, 1.18), (0.18, 0.15, 0.29), skin, segments=48, rings=32)
    ear.rotation_euler[1] = side * math.radians(-7)
    # Soft inner concha and antihelix, placed slightly inside the ear surface.
    make_ellipsoid("Ear concha — rose", (x - side * 0.015, -0.184, 1.18), (0.105, 0.035, 0.19), inner_ear, segments=36, rings=24)
    make_sweep("Ear antihelix — sculpted fold", [
        (x - side * 0.05, -0.218, 1.02),
        (x - side * 0.01, -0.235, 1.13),
        (x + side * 0.02, -0.235, 1.27),
        (x - side * 0.03, -0.21, 1.34),
    ], [0.025, 0.032, 0.026, 0.008], skin, sides=8)

# Eyes sit in the sculpted sockets with lids wrapping the visible globe.
for side in (-1, 1):
    cx = side * 0.36
    cz = 1.38
    # Set the small globe deep into the socket to avoid a startled/bulging look.
    make_ellipsoid("Eyeball — seated left" if side < 0 else "Eyeball — seated right",
                   (cx, -0.385, cz), (0.165, 0.085, 0.105), white, segments=48, rings=32)
    make_ellipsoid("Iris outer ring", (cx + side * 0.008, -0.485, cz - 0.005), (0.079, 0.028, 0.087), iris_dark, segments=40, rings=28)
    make_ellipsoid("Iris — warm brown", (cx + side * 0.008, -0.505, cz - 0.005), (0.064, 0.023, 0.073), iris, segments=40, rings=28)
    make_ellipsoid("Pupil", (cx + side * 0.008, -0.522, cz - 0.006), (0.031, 0.014, 0.043), pupil, segments=32, rings=24)
    make_ellipsoid("Catchlight", (cx - 0.014, -0.536, cz + 0.028), (0.018, 0.009, 0.019), glint, segments=24, rings=16)

    # Upper and lower lids follow the eye opening; these define the expression.
    make_sweep("Upper eyelid — raised arch", [
        (cx - 0.18, -0.474, cz + 0.005),
        (cx - 0.13, -0.500, cz + 0.083),
        (cx - 0.045, -0.515, cz + 0.115),
        (cx + 0.055, -0.515, cz + 0.112),
        (cx + 0.145, -0.493, cz + 0.070),
        (cx + 0.18, -0.470, cz + 0.005),
    ], [0.010, 0.022, 0.028, 0.027, 0.019, 0.008], skin, sides=10)
    make_sweep("Lower eyelid — soft rim", [
        (cx - 0.18, -0.470, cz + 0.003),
        (cx - 0.11, -0.492, cz - 0.072),
        (cx, -0.503, cz - 0.095),
        (cx + 0.11, -0.492, cz - 0.070),
        (cx + 0.18, -0.470, cz + 0.003),
    ], [0.009, 0.017, 0.021, 0.016, 0.008], skin, sides=10)

    # Dense, tapered brow mass; arch and downward tail match the master.
    brow_points = [
        (cx - 0.20, -0.438, 1.59),
        (cx - 0.12, -0.482, 1.65),
        (cx - 0.015, -0.502, 1.68),
        (cx + 0.095, -0.493, 1.65),
        (cx + 0.20, -0.455, 1.59),
    ]
    make_sweep("Eyebrow — expressive tapered mass", brow_points, [0.015, 0.048, 0.055, 0.043, 0.008], brow_mat, sides=12)

# Nose: bridge-to-tip loft, wider rounded tip and sculpted alae, not a sphere.
nose_profile = [
    (1.10, 0.12, 0.10, -0.51),
    (1.14, 0.18, 0.14, -0.54),
    (1.20, 0.205, 0.16, -0.54),
    (1.27, 0.17, 0.145, -0.50),
    (1.38, 0.13, 0.12, -0.47),
    (1.50, 0.10, 0.09, -0.445),
    (1.61, 0.065, 0.055, -0.42),
    (1.65, 0.025, 0.02, -0.41),
]
nose = make_head_surface("Nose — continuous bridge and rounded tip", nose_profile, skin, segments=56, subdivisions=4)
nose["design_note"] = "Broad stylized bridge and tip, tuned in profile"
for side in (-1, 1):
    make_ellipsoid("Nasal ala — left" if side < 0 else "Nasal ala — right",
                   (side * 0.135, -0.594, 1.16), (0.095, 0.075, 0.072), skin, segments=36, rings=24)
    make_sweep("Nostril crease", [
        (side * 0.075, -0.622, 1.115),
        (side * 0.12, -0.638, 1.105),
        (side * 0.165, -0.61, 1.12),
    ], [0.007, 0.012, 0.004], mouth_dark, sides=8)

# Mouth and a restrained friendly smirk, visible above the beard/moustache.
make_sweep("Upper lip — cupid contour", [
    (-0.25, -0.494, 0.94), (-0.15, -0.515, 0.966), (-0.06, -0.526, 0.954),
    (0.0, -0.529, 0.944), (0.07, -0.526, 0.956), (0.16, -0.512, 0.965), (0.25, -0.491, 0.94),
], [0.006, 0.017, 0.020, 0.012, 0.019, 0.014, 0.004], lip, sides=10)
make_sweep("Mouth line — slight smile", [
    (-0.25, -0.518, 0.927), (-0.15, -0.535, 0.912), (0.0, -0.54, 0.908),
    (0.15, -0.532, 0.917), (0.25, -0.516, 0.936),
], [0.006, 0.009, 0.010, 0.008, 0.004], mouth_dark, sides=8)
make_sweep("Lower lip — soft volume", [
    (-0.16, -0.514, 0.887), (0.0, -0.533, 0.872), (0.16, -0.513, 0.889),
], [0.006, 0.020, 0.005], lip, sides=10)

# Volumetric moustache: two tapered sweeps that follow the reference, not a flat decal.
for side in (-1, 1):
    make_sweep("Moustache — left sculpted half" if side < 0 else "Moustache — right sculpted half", [
        (side * 0.015, -0.568, 0.995),
        (side * 0.09, -0.586, 1.005),
        (side * 0.18, -0.575, 0.986),
        (side * 0.26, -0.535, 0.955),
        (side * 0.30, -0.505, 0.938),
    ], [0.013, 0.061, 0.056, 0.035, 0.005], beard_mat, sides=12)

# Hair cap follows the skull; separate tapered clumps create the raised textured top.
hair_profile = [
    (1.66, 0.64, 0.37, 0.08),
    (1.73, 0.74, 0.43, 0.08),
    (1.84, 0.79, 0.48, 0.08),
    (1.99, 0.77, 0.50, 0.085),
    (2.14, 0.70, 0.47, 0.09),
    (2.27, 0.55, 0.39, 0.09),
    (2.36, 0.32, 0.26, 0.085),
    (2.40, 0.06, 0.06, 0.08),
]
haircap = make_head_surface("Hair — scalp cap and fade mass", hair_profile, hair, segments=80, subdivisions=4)

# Broad sculptural quiff locks sweep up and back, fanning inward rather than hanging over the brow.
for index in range(9):
    x0 = -0.56 + index * 0.14
    side = x0 / 0.56
    width_factor = 1.0 - 0.22 * abs(side)
    z0 = 1.79 + 0.018 * math.cos(index * 0.8)
    y0 = -0.34 + 0.05 * abs(side)
    rise = 0.57 + 0.18 * (0.5 + 0.5 * math.sin(index * 1.3))
    sweep_x = 0.055 * math.sin(index * 0.85)
    clump_mat = hair_light if index in (1, 4, 7) else (hair_dark if index == 0 else hair)
    make_sweep("Quiff lock %02d" % (index + 1), [
        (x0, y0, z0),
        (x0 + sweep_x * 0.35, y0 + 0.02, z0 + rise * 0.36),
        (x0 + sweep_x * 0.72, y0 + 0.14, z0 + rise * 0.74),
        (x0 + sweep_x, y0 + 0.23, z0 + rise),
    ], [0.018 * width_factor, 0.058 * width_factor, 0.042 * width_factor, 0.002], clump_mat, sides=12)

# Hairline and fade guide clumps above the ears and temples.
for side in (-1, 1):
    for strand in range(5):
        z = 1.72 + strand * 0.045
        make_sweep("Temple fade ridge", [
            (side * 0.65, -0.19, z),
            (side * 0.72, -0.10, z + 0.02),
            (side * 0.76, 0.02, z + 0.035),
        ], [0.010, 0.016, 0.003], hair_light if strand == 2 else hair, sides=8)

# Fine tapered growth ridges follow the beard surface; keep them embedded, not floating.
for side in (-1, 1):
    for strand in range(5):
        start_x = side * (0.60 - strand * 0.018)
        end_x = side * (0.10 + strand * 0.038)
        start_z = 0.98 - strand * 0.075
        end_z = 0.12 + strand * 0.045
        clump_mat = beard_light if strand in (1, 3) else (beard_dark if strand == 4 else beard_mat)
        make_sweep("Beard growth ridge", [
            (start_x, -0.40, start_z),
            (side * (0.49 - 0.018 * strand), -0.59, start_z - 0.18),
            (side * (0.29 - 0.010 * strand), -0.66, (start_z + end_z) * 0.47),
            (end_x, -0.51, end_z),
        ], [0.003, 0.012, 0.011, 0.0015], clump_mat, sides=8)

# A small number of restrained contour strands along the moustache and chin.
for index in range(5):
    x = -0.18 + index * 0.09
    make_sweep("Moustache hairline detail", [
        (x, -0.615, 0.998), (x + 0.02, -0.625, 0.972), (x + 0.06, -0.608, 0.952)
    ], [0.004, 0.008, 0.0015], beard_light if index % 2 else beard_dark, sides=6)

# Portrait view cameras: front, true profile, 3/4, and close face.
def look_at(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat("-Z", "Y").to_euler()


def make_camera(name, location, target, ortho_scale):
    data = bpy.data.cameras.new(name + " data")
    cam = bpy.data.objects.new(name, data)
    scene.collection.objects.link(cam)
    cam.location = location
    look_at(cam, target)
    data.type = "ORTHO"
    data.ortho_scale = ortho_scale
    data.lens = 55
    return cam

cam_front = make_camera("CAM_Front", (0.0, -9.0, 1.27), (0.0, 0.0, 1.27), 3.00)
cam_three = make_camera("CAM_ThreeQuarter", (4.4, -8.0, 1.27), (0.0, 0.0, 1.27), 3.00)
cam_profile = make_camera("CAM_Profile", (9.0, 0.0, 1.27), (0.0, 0.0, 1.27), 3.00)
cam_face = make_camera("CAM_FaceCloseup", (0.0, -8.0, 1.36), (0.0, -0.05, 1.36), 2.55)

# Soft three-point studio lighting. No floor plane so the silhouette stays clean.
def area_light(name, location, energy, color, size, target):
    data = bpy.data.lights.new(name + " data", "AREA")
    data.energy = energy
    data.color = color
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    look_at(obj, target)
    return obj

area_light("Key — soft warm", (-4.2, -5.5, 5.0), 620, (1.0, 0.78, 0.62), 4.0, (0, 0, 1.1))
area_light("Fill — soft neutral", (4.0, -4.5, 2.6), 420, (0.66, 0.78, 1.0), 3.2, (0, 0, 1.1))
area_light("Rim — hair separation", (0.5, 2.8, 4.2), 760, (1.0, 0.69, 0.43), 2.8, (0, 0, 1.2))

# Pack reference images into the .blend as viewport-only empties; they never render.
ref_dir = PROJECT_ROOT + "/references/"
for filename, name in [("dad-front.png", "REFERENCE — Dad front"),
                       ("dad-three_quarter.png", "REFERENCE — Dad three-quarter"),
                       ("dad-side.png", "REFERENCE — Dad profile"),
                       ("dad-face.png", "REFERENCE — Dad face master")]:
    try:
        image = bpy.data.images.load(ref_dir + filename, check_existing=True)
        image.pack()
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = "IMAGE"
        empty.data = image
        empty.empty_display_size = 2.5
        empty.empty_image_offset = (0.5, 0.5)
        empty.hide_render = True
        empty.show_in_front = True
        reference_collection.objects.link(empty)
        empty["source_file"] = filename
        empty["role"] = "viewport reference only; not part of the model"
    except Exception as error:
        print("Reference image warning:", filename, error)

# Hide source guides by default to keep render and viewport object selection clean.
reference_collection.hide_render = True

# Open the file focused on the head. The evidence renders use explicit cameras above.
scene.camera = cam_three
for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_distance = 4.2
        area.spaces.active.region_3d.view_location = (0.0, 0.0, 1.15)
        area.spaces.active.region_3d.view_perspective = "PERSP"

scene.frame_set(1)
bpy.context.view_layer.update()
print("DAD_HEAD_STUDY_V1_READY: custom head surfaces, seated eyes, volumetric beard, hair clumps; not approved.")
