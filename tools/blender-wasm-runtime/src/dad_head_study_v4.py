"""Official-base V4 Dad head/bust study. Scripted geometry; not manual sculpting or approved.

Starts from the official Blender Human Base Meshes v1.4.1 stylized head and eyes.
It bakes source transforms, preserves the skull profile, broadens the lower face and neck
as integrated geometry, and shapes the scalp directly (no detached sphere or jagged shell).
"""
import bpy
import json
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def material(name, color, roughness=0.45, specular=0.3, subsurface=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    return mat


def make_curve(name, points, mat, bevel):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = bevel
    curve.bevel_resolution = 4
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for i, (p, radius) in enumerate(points):
        spline.points[i].co = (p.x, p.y, p.z, 1.0)
        spline.points[i].radius = radius
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def uv_sphere(name, location, scale, mat, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat)
    return obj


def world_bake(objects):
    snapshots = [(obj, obj.matrix_world.copy()) for obj in objects]
    for obj, world in snapshots:
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        for vertex in obj.data.vertices:
            vertex.co = world @ vertex.co
        obj.parent = None
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        obj.data.update()


def build_face_shader(skin, skin_light, hair, hair_mid, beard, beard_mid):
    mat = bpy.data.materials.new("DadV4 · continuous stylized face")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.46
    if "Subsurface Weight" in shader.inputs:
        shader.inputs["Subsurface Weight"].default_value = 0.035
    geom = nodes.new("ShaderNodeNewGeometry")
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geom.outputs["Position"], sep.inputs["Vector"])

    def math_node(op, label, a, b=None):
        node = nodes.new("ShaderNodeMath")
        node.operation = op
        node.label = label
        links.new(a, node.inputs[0]) if hasattr(a, "node") else setattr(node.inputs[0], "default_value", a)
        if b is not None:
            links.new(b, node.inputs[1]) if hasattr(b, "node") else setattr(node.inputs[1], "default_value", b)
        return node.outputs[0]

    def range_node(value, start, end, out_start=0.0, out_end=1.0, label=""):
        node = nodes.new("ShaderNodeMapRange")
        node.label = label
        node.interpolation_type = "SMOOTHSTEP"
        node.clamp = True
        node.inputs["From Min"].default_value = start
        node.inputs["From Max"].default_value = end
        node.inputs["To Min"].default_value = out_start
        node.inputs["To Max"].default_value = out_end
        links.new(value, node.inputs["Value"])
        return node.outputs["Result"]

    x = math_node("ABSOLUTE", "Mirror about face", sep.outputs["X"])
    y, z = sep.outputs["Y"], sep.outputs["Z"]
    xshape = range_node(x, 0.0, 0.145, 0.0, 1.0, "Temple taper")
    rear = range_node(y, 0.025, 0.105, 0.0, 1.0, "Rear scalp")
    front_hairline = math_node("SUBTRACT", "Front hairline", 0.414, math_node("MULTIPLY", "Temple fade", xshape, 0.065))
    hairline = math_node("ADD", "Hairline over skull", math_node("MULTIPLY", "Front hairline blend", front_hairline, math_node("SUBTRACT", "One minus rear", 1.0, rear)), math_node("MULTIPLY", "Nape line", 0.235, rear))
    hair_mask = range_node(math_node("SUBTRACT", "Above hairline", z, hairline), -0.003, 0.003, 0.0, 1.0, "Soft hairline")

    beard_upper = math_node("ADD", "Cheek beard line", 0.252, math_node("MULTIPLY", "Sideburn rise", xshape, 0.054))
    beard_top = range_node(math_node("SUBTRACT", "Below cheek line", beard_upper, z), -0.014, 0.014, 0.0, 1.0, "Soft cheek edge")
    front = range_node(y, -0.005, 0.085, 1.0, 0.0, "Front face")
    sides = range_node(x, 0.132, 0.157, 1.0, 0.0, "Jaw not ears")
    chin = range_node(z, 0.174, 0.194, 0.0, 1.0, "Beard under chin")
    no_hair = math_node("SUBTRACT", "Beard below scalp", 1.0, hair_mask)
    beard_mask = math_node("MULTIPLY", "Beard region A", beard_top, front)
    beard_mask = math_node("MULTIPLY", "Beard region B", beard_mask, sides)
    beard_mask = math_node("MULTIPLY", "Beard region C", beard_mask, chin)
    beard_mask = math_node("MULTIPLY", "Beard region D", beard_mask, no_hair)

    moustache_x = range_node(x, 0.064, 0.083, 1.0, 0.0, "Moustache width")
    moustache_low = range_node(z, 0.238, 0.249, 0.0, 1.0, "Moustache lower line")
    moustache_high = range_node(z, 0.271, 0.282, 1.0, 0.0, "Moustache upper line")
    moustache = math_node("MULTIPLY", "Moustache mask A", moustache_x, moustache_low)
    moustache = math_node("MULTIPLY", "Moustache mask B", moustache, moustache_high)
    moustache = math_node("MULTIPLY", "Moustache on face", moustache, front)
    moustache = math_node("MULTIPLY", "Moustache below hair", moustache, 0.0)

    xnorm = math_node("DIVIDE", "Lip opening width", x, 0.034)
    znorm = math_node("DIVIDE", "Lip opening height", math_node("SUBTRACT", "Mouth center", z, 0.235), 0.015)
    radius2 = math_node("ADD", "Mouth oval", math_node("MULTIPLY", "Mouth X squared", xnorm, xnorm), math_node("MULTIPLY", "Mouth Z squared", znorm, znorm))
    mouth = range_node(radius2, 0.74, 1.12, 1.0, 0.0, "Lip opening")
    mouth = math_node("MULTIPLY", "Mouth only on front", mouth, 0.0)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.label = "Short beard grain"
    noise.inputs["Scale"].default_value = 125.0
    noise.inputs["Detail"].default_value = 2.0
    color_breakup = nodes.new("ShaderNodeMixRGB")
    color_breakup.blend_type = "MIX"
    color_breakup.inputs[1].default_value = beard.diffuse_color
    color_breakup.inputs[2].default_value = beard_mid.diffuse_color
    links.new(math_node("MULTIPLY", "Subtle beard variation", noise.outputs["Fac"], 0.20), color_breakup.inputs[0])

    skin_beard = nodes.new("ShaderNodeMixRGB")
    skin_beard.blend_type = "MIX"
    links.new(beard_mask, skin_beard.inputs[0])
    skin_beard.inputs[1].default_value = skin.diffuse_color
    links.new(color_breakup.outputs[0], skin_beard.inputs[2])
    stache_mix = nodes.new("ShaderNodeMixRGB")
    stache_mix.blend_type = "MIX"
    links.new(moustache, stache_mix.inputs[0])
    links.new(skin_beard.outputs[0], stache_mix.inputs[1])
    stache_mix.inputs[2].default_value = beard_mid.diffuse_color
    mouth_mix = nodes.new("ShaderNodeMixRGB")
    mouth_mix.blend_type = "MIX"
    links.new(mouth, mouth_mix.inputs[0])
    links.new(stache_mix.outputs[0], mouth_mix.inputs[1])
    mouth_mix.inputs[2].default_value = skin_light.diffuse_color
    hair_mix = nodes.new("ShaderNodeMixRGB")
    hair_mix.blend_type = "MIX"
    links.new(hair_mask, hair_mix.inputs[0])
    links.new(mouth_mix.outputs[0], hair_mix.inputs[1])
    hair_noise = nodes.new("ShaderNodeTexNoise")
    hair_noise.label = "Soft short-hair texture"
    hair_noise.inputs["Scale"].default_value = 95.0
    hair_noise.inputs["Detail"].default_value = 2.0
    links.new(geom.outputs["Position"], hair_noise.inputs["Vector"])
    hair_tone = math_node("MULTIPLY", "Restrained hair variation", hair_noise.outputs["Fac"], 0.20)
    hair_color = nodes.new("ShaderNodeMixRGB")
    hair_color.blend_type = "MIX"
    links.new(hair_tone, hair_color.inputs[0])
    hair_color.inputs[1].default_value = hair.diffuse_color
    hair_color.inputs[2].default_value = hair_mid.diffuse_color
    links.new(hair_color.outputs[0], hair_mix.inputs[2])
    links.new(hair_mix.outputs[0], shader.inputs["Base Color"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def line_height(theta):
    if theta < 0.65:
        return 0.414
    if theta < 1.45:
        return 0.414 - 0.064 * smoothstep((theta - 0.65) / 0.80)
    return 0.350 - 0.115 * smoothstep((theta - 1.45) / (math.pi - 1.45))


def main():
    scene = bpy.context.scene
    head = bpy.data.objects.get("GEO-head_stylized")
    eyes = [bpy.data.objects.get("GEO-head_stylized.eye.L"), bpy.data.objects.get("GEO-head_stylized.eye.R")]
    if not head or any(obj is None for obj in eyes):
        raise RuntimeError("Official bundle must contain GEO-head_stylized and its two eye meshes")
    source_objects = [head] + eyes
    world_bake(source_objects)
    for obj in list(bpy.data.objects):
        if obj not in source_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    head.name = "DadV4 · official stylized base"
    eyes[0].name = "DadV4 · eye L"
    eyes[1].name = "DadV4 · eye R"

    source = [v.co.copy() for v in head.data.vertices]
    xmin, xmax = min(p.x for p in source), max(p.x for p in source)
    ymin, ymax = min(p.y for p in source), max(p.y for p in source)
    zmin, zmax = min(p.z for p in source), max(p.z for p in source)
    cx, cy = (xmin + xmax) * 0.5, (ymin + ymax) * 0.5
    for obj in source_objects:
        for vertex in obj.data.vertices:
            p = vertex.co
            p.x = (p.x - cx) * 1.08
            p.y = (p.y - cy) * 1.05
            p.z = (p.z - zmin) * 1.06 + 0.12
        obj.data.update()

    # Integrate the hairstyle and beard volume into the official head surface so no
    # detached cap or jagged beard-shell border can read as a sphere/mask.
    for vertex in head.data.vertices:
        p = vertex.co
        theta = abs(math.atan2(p.x, -p.y))
        upper = 0.252 + 0.054 * smoothstep(theta / 1.30)
        front = 1.0 - smoothstep((p.y + 0.015) / 0.105)
        beard_weight = smoothstep((upper + 0.010 - p.z) / 0.050) * smoothstep((p.z - 0.165) / 0.050) * front
        chin_bulge = math.exp(-((p.z - 0.225) / 0.085) ** 2) * math.exp(-(p.x / 0.118) ** 2)
        p.y -= 0.022 * beard_weight * chin_bulge
        p.x *= 1.0 + 0.075 * beard_weight * chin_bulge
        neck = smoothstep((0.285 - p.z) / 0.085) * smoothstep((p.z - 0.12) / 0.035)
        p.x *= 1.0 + 0.16 * neck
        p.y *= 1.0 + 0.06 * neck
        hair_weight = smoothstep((p.z - line_height(theta) + 0.008) / 0.035)
        crown = smoothstep((p.z - 0.385) / 0.095)
        front_crown = math.exp(-((p.x / 0.11) ** 2)) * math.exp(-(((p.y + 0.045) / 0.075) ** 2))
        p.z += 0.014 * hair_weight * crown * (0.35 + 0.65 * front_crown)
    head.data.update()

    skin = material("DadV4 · warm skin", (0.51, 0.255, 0.17), 0.46, subsurface=0.035)
    skin_light = material("DadV4 · lips", (0.61, 0.32, 0.23), 0.43, subsurface=0.02)
    hair = material("DadV4 · dark espresso hair", (0.042, 0.020, 0.014), 0.42, specular=0.34)
    hair_mid = material("DadV4 · hair highlights", (0.075, 0.037, 0.022), 0.40, specular=0.36)
    beard = material("DadV4 · chestnut beard", (0.055, 0.024, 0.016), 0.54, specular=0.22)
    beard_mid = material("DadV4 · brow and facial detail", (0.092, 0.043, 0.026), 0.54, specular=0.22)
    sclera = material("DadV4 · ivory sclera", (0.88, 0.80, 0.70), 0.24, specular=0.5)
    iris = material("DadV4 · hazel iris", (0.30, 0.12, 0.035), 0.27, specular=0.48)
    pupil = material("DadV4 · pupil", (0.012, 0.008, 0.006), 0.18, specular=0.5)
    glint = material("DadV4 · eye glint", (0.98, 0.93, 0.85), 0.13, specular=0.55)

    face_material = build_face_shader(skin, skin_light, hair, hair_mid, beard, beard_mid)
    head.data.materials.clear()
    head.data.materials.append(face_material)
    for poly in head.data.polygons:
        poly.use_smooth = True
        poly.material_index = 0

    # Hair and beard stay continuous with the base head: geometric volume comes from
    # the vertex-level crown/jaw/neck edits above; the shader supplies a soft boundary.

    # Reuse the official fitted eye meshes as sclera, then set true iris and pupil layers.
    for eye in eyes:
        xs = [v.co.x for v in eye.data.vertices]
        ys = [v.co.y for v in eye.data.vertices]
        zs = [v.co.z for v in eye.data.vertices]
        ex = (min(xs) + max(xs)) * 0.5
        ez = (min(zs) + max(zs)) * 0.5
        for vertex in eye.data.vertices:
            vertex.co = Vector((ex, (min(ys) + max(ys)) * 0.5, ez)) + (vertex.co - Vector((ex, (min(ys) + max(ys)) * 0.5, ez))) * 0.68 + Vector((0.0, 0.0060, 0.0))
        eye.data.update()
        eye.data.materials.clear()
        eye.data.materials.append(sclera)
        for poly in eye.data.polygons:
            poly.use_smooth = True
        xs = [v.co.x for v in eye.data.vertices]
        ys = [v.co.y for v in eye.data.vertices]
        zs = [v.co.z for v in eye.data.vertices]
        ex = (min(xs) + max(xs)) * 0.5
        ez = (min(zs) + max(zs)) * 0.5
        front_y = min(ys)
        suffix = "L" if eye.name.endswith("L") else "R"
        uv_sphere("DadV4 · iris " + suffix, (ex, front_y - 0.0015, ez), (0.009, 0.0025, 0.0105), iris, 32, 20)
        uv_sphere("DadV4 · pupil " + suffix, (ex, front_y - 0.0040, ez), (0.0045, 0.0020, 0.0060), pupil, 24, 16)
        uv_sphere("DadV4 · glint " + suffix, (ex - 0.0030, front_y - 0.0062, ez + 0.0040), (0.0016, 0.0008, 0.0016), glint, 16, 10)

    # Subtle brow geometry is ray-seated to the transformed official face.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    face_tree = BVHTree.FromObject(head, depsgraph)
    def on_face(x, z, offset=0.004):
        hit, normal, face_index, distance = face_tree.ray_cast(Vector((x, -0.62, z)), Vector((0.0, 1.0, 0.0)), 1.24)
        if hit is None:
            return Vector((x, -0.14, z))
        return hit + (normal.normalized() if normal and normal.length else Vector((0.0, -1.0, 0.0))) * offset
    # The official sculpt already has modeled orbital rims; keep those, without
    # adding bright concentric overlay curves.
    for side in (-1, 1):
        brow = [(0.020, 0.397, 0.25), (0.035, 0.405, 0.72), (0.052, 0.408, 1.0), (0.070, 0.403, 0.75), (0.084, 0.395, 0.20)]
        make_curve("DadV4 · eyebrow " + str(side), [(on_face(side * x, z, 0.005), r) for x, z, r in brow], beard_mid, 0.0025)

    mouth_line = [(-0.026, 0.239, 0.12), (-0.014, 0.237, 0.55), (0.0, 0.236, 0.7), (0.014, 0.237, 0.55), (0.026, 0.239, 0.12)]
    make_curve("DadV4 · subtle mouth seam", [(on_face(x, z, 0.004), r) for x, z, r in mouth_line], beard, 0.0008)
    # Remove asset-browser cameras and lights; build deterministic review views.
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 40
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 640
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.25
    if scene.world is None:
        scene.world = bpy.data.worlds.new("DadV4 Studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.025, 0.032, 0.040, 1.0)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.18
    target = Vector((0.0, 0.0, 0.34))
    def area(name, offset, energy, size, color):
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy
        light.shape = "DISK"
        light.size = size
        light.color = color
        obj = bpy.data.objects.new(name, light)
        scene.collection.objects.link(obj)
        obj.location = target + Vector(offset)
        obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()
    area("DadV4 · key", (-0.50, -0.72, 0.55), 24, 0.80, (1.0, 0.82, 0.68))
    area("DadV4 · fill", (0.55, -0.55, 0.06), 12, 0.94, (0.72, 0.82, 1.0))
    area("DadV4 · rim", (0.10, 0.45, 0.45), 20, 0.75, (1.0, 0.84, 0.68))
    def camera(name, offset, scale):
        data = bpy.data.cameras.new(name)
        data.type = "ORTHO"
        data.ortho_scale = scale
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = target + Vector(offset)
        obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj
    cameras = [
        ("V4_FRONT", (0.0, -1.65, 0.0), 0.64),
        ("V4_THREE_QUARTER", (0.90, -1.40, 0.0), 0.65),
        ("V4_PROFILE", (1.70, 0.0, 0.0), 0.64),
        ("V4_FACE_CLOSEUP", (0.0, -1.40, 0.0), 0.45),
    ]
    for name, offset, scale in cameras:
        camera(name, offset, scale)
    scene.camera = bpy.data.objects["V4_FRONT"]
    scene["study_status"] = "NOT APPROVED — official base, scripted geometry, review only"
    scene["source"] = "Blender Human Base Meshes v1.4.1 / GEO-head_stylized — CC0"
    print("@@DAD_V4_RESULT " + json.dumps({"source_bounds": [[round(xmin, 5), round(ymin, 5), round(zmin, 5)], [round(xmax, 5), round(ymax, 5), round(zmax, 5)]], "normalized_bounds": [[round(min(v.co.x for v in head.data.vertices), 5), round(min(v.co.y for v in head.data.vertices), 5), round(min(v.co.z for v in head.data.vertices), 5)], [round(max(v.co.x for v in head.data.vertices), 5), round(max(v.co.y for v in head.data.vertices), 5), round(max(v.co.z for v in head.data.vertices), 5)]], "beard_shell_faces": 0, "hair_cap_faces": 0, "geometry_volume": "integrated into official head mesh", "source_mesh_faces": len(head.data.polygons)}))


main()
