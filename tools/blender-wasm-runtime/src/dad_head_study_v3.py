"""Reference-driven Dad head/bust study V3.  Exploratory; not manually sculpted or approved.

Starts from the accessible Dan Ulrich (dan2) neutral sculpting head source. The script
applies a restrained cross-section fit to measured orthographic front/profile alpha
silhouettes, then adds stylized hair, beard, brows and eye materials for a reviewable
head study. It is a scripted Blender adaptation, not manual sculpting.
"""
import bpy
import csv
import json
import math
import os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

PROJECT_ROOT = "__FAMILY_STUDIO_PROJECT_ROOT__"
PROFILE_CSV = os.path.join(PROJECT_ROOT, "references", "dad-silhouette-profiles.csv")

# Reference design anchors are intentionally restrained; render comparisons decide
# whether further movement is warranted.
HEADS_IN_BODY = 5.9
HAIR_HEIGHT = 0.095
FRONT_FIT_STRENGTH = 0.55
PROFILE_FIT_STRENGTH = 0.35


def material(name, color, roughness=0.48, metallic=0.0, subsurface=0.0, specular=0.32):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    return mat


def smoothstep(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def build_face_material(skin, skin_light, hair, beard, beard_mid):
    """Blend groom/skin regions from world position for a continuous hairline and beard edge."""
    mat = bpy.data.materials.new("DadV3 · continuous skin, hair and beard")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.47
    if "Subsurface Weight" in shader.inputs:
        shader.inputs["Subsurface Weight"].default_value = 0.035
    geometry = nodes.new("ShaderNodeNewGeometry")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    links.new(geometry.outputs["Position"], separate.inputs["Vector"])

    def math_node(operation, name, first, second=None):
        node = nodes.new("ShaderNodeMath")
        node.operation = operation
        node.label = name
        if hasattr(first, "node"):
            links.new(first, node.inputs[0])
        else:
            node.inputs[0].default_value = first
        if second is not None:
            if hasattr(second, "node"):
                links.new(second, node.inputs[1])
            else:
                node.inputs[1].default_value = second
        return node.outputs[0]

    def smooth_range(value, start, end, out_start=0.0, out_end=1.0, label=""):
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

    x_abs = math_node("ABSOLUTE", "Mirror across face midline", separate.outputs["X"])
    z = separate.outputs["Z"]
    y = separate.outputs["Y"]
    x_shape = smooth_range(x_abs, 0.0, 0.14, 0.0, 1.0, "Temple taper")
    back_weight = smooth_range(y, 0.08, 0.20, 0.0, 1.0, "Rear scalp transition")
    front_hairline = math_node("SUBTRACT", "Front hairline height", 0.365, math_node("MULTIPLY", "Temple lowering", x_shape, 0.05))
    hairline = math_node("ADD", "Hairline around skull", math_node("MULTIPLY", "Front", front_hairline, math_node("SUBTRACT", "One minus rear", 1.0, back_weight)), math_node("MULTIPLY", "Rear nape hairline", 0.205, back_weight))
    hair_delta = math_node("SUBTRACT", "Above hairline", z, hairline)
    hair_mask = smooth_range(hair_delta, -0.003, 0.003, 0.0, 1.0, "Soft hairline")

    beard_upper = math_node("ADD", "Cheek line height", 0.248, math_node("MULTIPLY", "Sideburn lift", x_shape, 0.040))
    beard_delta = math_node("SUBTRACT", "Below beard line", beard_upper, z)
    beard_top = smooth_range(beard_delta, -0.003, 0.003, 0.0, 1.0, "Soft cheek line")
    front_face = smooth_range(y, 0.015, 0.13, 1.0, 0.0, "Front face only")
    cheek_limit = smooth_range(x_abs, 0.132, 0.151, 1.0, 0.0, "Exclude ears")
    chin_mask = smooth_range(z, 0.174, 0.190, 0.0, 1.0, "End beard under chin")
    no_hair = math_node("SUBTRACT", "Keep beard below hair", 1.0, hair_mask)
    beard_mask = math_node("MULTIPLY", "Beard region", math_node("MULTIPLY", "Beard line and front", beard_top, front_face), math_node("MULTIPLY", "Cheek and chin limits", cheek_limit, chin_mask))
    beard_mask = math_node("MULTIPLY", "Avoid hair overlap", beard_mask, no_hair)

    mustache_width = smooth_range(x_abs, 0.072, 0.090, 1.0, 0.0, "Moustache width")
    mustache_low = smooth_range(z, 0.228, 0.239, 0.0, 1.0, "Moustache lower edge")
    mustache_high = smooth_range(z, 0.260, 0.272, 1.0, 0.0, "Moustache upper edge")
    moustache_front = math_node("MULTIPLY", "Front moustache", math_node("MULTIPLY", "Width and lower edge", mustache_width, mustache_low), math_node("MULTIPLY", "Upper edge and front", mustache_high, front_face))
    mustache_mask = math_node("MULTIPLY", "Visible moustache", moustache_front, no_hair)

    x_norm = math_node("DIVIDE", "Mouth horizontal radius", x_abs, 0.034)
    z_offset = math_node("SUBTRACT", "Mouth vertical center", z, 0.232)
    z_norm = math_node("DIVIDE", "Mouth vertical radius", z_offset, 0.015)
    radius2 = math_node("ADD", "Rounded mouth opening", math_node("ADD", "Mouth ellipse X", math_node("MULTIPLY", "X squared", x_norm, x_norm), math_node("MULTIPLY", "Z squared", z_norm, z_norm)), 0.0)
    mouth_oval = smooth_range(radius2, 0.72, 1.08, 1.0, 0.0, "Soft oval lip opening")
    mouth_mask = math_node("MULTIPLY", "Front mouth only", mouth_oval, front_face)

    beard_noise = nodes.new("ShaderNodeTexNoise")
    beard_noise.label = "Fine beard grain"
    beard_noise.inputs["Scale"].default_value = 115.0
    beard_noise.inputs["Detail"].default_value = 2.0
    beard_variation = nodes.new("ShaderNodeMixRGB")
    beard_variation.blend_type = "MIX"
    beard_variation.inputs[1].default_value = beard.diffuse_color
    beard_variation.inputs[2].default_value = beard_mid.diffuse_color
    grain_mix = math_node("MULTIPLY", "Subtle hair value breakup", beard_noise.outputs["Fac"], 0.24)
    links.new(grain_mix, beard_variation.inputs[0])
    skin_beard = nodes.new("ShaderNodeMixRGB")
    skin_beard.blend_type = "MIX"
    links.new(beard_mask, skin_beard.inputs[0])
    skin_beard.inputs[1].default_value = skin.diffuse_color
    links.new(beard_variation.outputs[0], skin_beard.inputs[2])
    moustache_mix = nodes.new("ShaderNodeMixRGB")
    moustache_mix.blend_type = "MIX"
    links.new(mustache_mask, moustache_mix.inputs[0])
    links.new(skin_beard.outputs[0], moustache_mix.inputs[1])
    moustache_mix.inputs[2].default_value = beard_mid.diffuse_color
    mouth_mix = nodes.new("ShaderNodeMixRGB")
    mouth_mix.blend_type = "MIX"
    links.new(mouth_mask, mouth_mix.inputs[0])
    links.new(moustache_mix.outputs[0], mouth_mix.inputs[1])
    mouth_mix.inputs[2].default_value = skin_light.diffuse_color
    hair_mix = nodes.new("ShaderNodeMixRGB")
    hair_mix.blend_type = "MIX"
    links.new(hair_mask, hair_mix.inputs[0])
    links.new(mouth_mix.outputs[0], hair_mix.inputs[1])
    hair_mix.inputs[2].default_value = hair.diffuse_color
    links.new(hair_mix.outputs[0], shader.inputs["Base Color"])
    links.new(shader.outputs["BSDF"], output.inputs["Surface"])
    return mat


def load_silhouettes():
    profiles = {"front": [], "side": []}
    with open(PROFILE_CSV, "r", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["view"] not in profiles:
                continue
            profiles[row["view"]].append((
                float(row["z_fraction_from_ground"]),
                float(row["width_fraction_of_canvas_height"]),
                float(row["center_offset_fraction_of_canvas_height"]),
            ))
    for rows in profiles.values():
        rows.sort(key=lambda item: item[0])
    return profiles


def sample_profile(rows, z_fraction):
    if z_fraction <= rows[0][0]:
        return rows[0][1]
    if z_fraction >= rows[-1][0]:
        return rows[-1][1]
    for left, right in zip(rows, rows[1:]):
        if left[0] <= z_fraction <= right[0]:
            span = max(1e-8, right[0] - left[0])
            t = (z_fraction - left[0]) / span
            return left[1] * (1.0 - t) + right[1] * t
    return rows[-1][1]


def sample_table(rows, z):
    if z <= rows[0][0]:
        return rows[0][1]
    if z >= rows[-1][0]:
        return rows[-1][1]
    for left, right in zip(rows, rows[1:]):
        if left[0] <= z <= right[0]:
            t = (z - left[0]) / max(1e-8, right[0] - left[0])
            return left[1] * (1.0 - t) + right[1] * t
    return rows[-1][1]


def make_spline(name, points, mat, bevel_depth, cyclic=False):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 4
    spline = curve.splines.new("POLY")
    spline.points.add(max(0, len(points) - 1))
    for i, item in enumerate(points):
        point, radius = item
        spline.points[i].co = (point.x, point.y, point.z, 1.0)
        spline.points[i].radius = radius
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def make_uv_sphere(name, location, scale, mat, segments=32, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat)
    return obj


def bake_mesh_objects_to_world():
    """Resolve the source file's parent/scaling transforms before any measured edits."""
    for obj in list(bpy.data.objects):
        if obj.type != "MESH":
            continue
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        world = obj.matrix_world.copy()
        for vertex in obj.data.vertices:
            vertex.co = world @ vertex.co
        obj.parent = None
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        obj.data.update()


def fit_head_to_profiles(head, profiles):
    mesh = head.data
    coords = [v.co.copy() for v in mesh.vertices]
    # Locate the front chin and scalp from actual source vertices (front is -Y).
    chin_candidates = [v.co.z for v in mesh.vertices if v.co.y < -0.085 and abs(v.co.x) < 0.035 and v.co.z < 0.19]
    chin_z = min(chin_candidates) if chin_candidates else 0.085
    top_z = max(v.co.z for v in mesh.vertices)
    hair_top_z = top_z + HAIR_HEIGHT
    head_height = hair_top_z - chin_z
    body_height = head_height * HEADS_IN_BODY

    front_rows = profiles["front"]
    side_rows = profiles["side"]
    bins = 56
    z0 = chin_z - 0.025
    z1 = top_z + 0.005
    width_table = []
    depth_table = []
    applied = []
    for i in range(bins + 1):
        z = z0 + (z1 - z0) * i / bins
        band = max(0.008, (z1 - z0) / bins * 1.7)
        slice_coords = [p for p in coords if abs(p.z - z) <= band]
        if len(slice_coords) < 8:
            slice_coords = [p for p in coords if abs(p.z - z) <= band * 2.5]
        if len(slice_coords) < 8:
            continue
        current_width = max(p.x for p in slice_coords) - min(p.x for p in slice_coords)
        current_depth = max(p.y for p in slice_coords) - min(p.y for p in slice_coords)
        t = max(0.0, min(1.0, (z - chin_z) / max(1e-6, head_height)))
        z_fraction = 1.0 - (1.0 - t) / HEADS_IN_BODY
        target_width = sample_profile(front_rows, z_fraction) * body_height
        target_depth = sample_profile(side_rows, z_fraction) * body_height
        raw_x = target_width / max(current_width, 1e-6)
        raw_y = target_depth / max(current_depth, 1e-6)
        # Match the measured outline conservatively so the source's recognizable anatomy
        # remains; overshooting the alpha-derived profile is explicitly avoided.
        fx = max(0.88, min(1.18, 1.0 + FRONT_FIT_STRENGTH * (raw_x - 1.0)))
        fy = max(0.90, min(1.16, 1.0 + PROFILE_FIT_STRENGTH * (raw_y - 1.0)))
        width_table.append((z, fx))
        depth_table.append((z, fy))
        if i % 7 == 0:
            applied.append({"z": round(z, 4), "z_fraction": round(z_fraction, 5), "target_width": round(target_width, 4), "source_width": round(current_width, 4), "x_scale": round(fx, 4), "y_scale": round(fy, 4)})

    def at(table, z):
        return sample_table(table, z)

    # Blend correction smoothly from chin through crown; preserve the lower cut bust.
    for vertex in mesh.vertices:
        p = vertex.co
        weight = smoothstep((p.z - (chin_z - 0.025)) / 0.09)
        fx = 1.0 + (at(width_table, p.z) - 1.0) * weight
        fy = 1.0 + (at(depth_table, p.z) - 1.0) * weight
        p.x *= fx
        p.y = 0.0133 + (p.y - 0.0133) * fy
        # A subtle cheek fullness cue below the eye line, symmetric about the midline.
        cheek = math.exp(-((p.z - 0.255) / 0.065) ** 2) * math.exp(-((abs(p.x) - 0.078) / 0.055) ** 2)
        p.y -= 0.0045 * cheek
    mesh.update()
    # Preserve eye seating and spacing while the head cross-sections are fitted.
    for obj in bpy.data.objects:
        if obj == head or obj.type != "MESH" or not (obj.name.startswith("iris_") or obj.name.startswith("sclera_")):
            continue
        for vertex in obj.data.vertices:
            p = vertex.co
            weight = smoothstep((p.z - (chin_z - 0.025)) / 0.09)
            fx = 1.0 + (at(width_table, p.z) - 1.0) * weight
            fy = 1.0 + (at(depth_table, p.z) - 1.0) * weight
            p.x *= fx
            p.y = 0.0133 + (p.y - 0.0133) * fy
        obj.data.update()
    return {"chin_z": round(chin_z, 5), "source_top_z": round(top_z, 5), "hair_top_z": round(hair_top_z, 5), "head_height": round(head_height, 5), "body_height_from_5_9_heads": round(body_height, 5), "samples_used": {k: len(v) for k, v in profiles.items()}, "fit_rows": applied}


def main():
    scene = bpy.context.scene
    head = bpy.data.objects.get("neutral_head")
    if not head or head.type != "MESH":
        raise RuntimeError("Expected the source scene's neutral_head mesh")
    bake_mesh_objects_to_world()
    profiles = load_silhouettes()
    fit_report = fit_head_to_profiles(head, profiles)

    skin = material("Skin · warm stylized", (0.46, 0.205, 0.12), 0.46, subsurface=0.045, specular=0.25)
    skin_light = material("Skin · eyelid/lip highlights", (0.56, 0.265, 0.17), 0.46, subsurface=0.03, specular=0.24)
    hair = material("Hair · espresso brown", (0.060, 0.029, 0.019), 0.42, specular=0.34)
    hair_mid = material("Hair · warm brown lock", (0.085, 0.039, 0.024), 0.4, specular=0.36)
    beard = material("Beard · dark chestnut", (0.068, 0.030, 0.019), 0.56, specular=0.2)
    beard_mid = material("Beard · moustache warmth", (0.11, 0.052, 0.032), 0.58, specular=0.18)
    sclera = material("Eyes · warm ivory", (0.83, 0.75, 0.65), 0.24, subsurface=0.015, specular=0.46)
    iris = material("Eyes · hazel brown", (0.24, 0.095, 0.028), 0.27, specular=0.48)
    pupil = material("Eyes · pupil", (0.014, 0.009, 0.007), 0.19, specular=0.5)
    catchlight = material("Eyes · catchlight", (0.96, 0.91, 0.82), 0.13, specular=0.55)

    # Keep the source's neutral head topology intact; position-driven shading gives clean
    # continuous hairline, cheek and moustache boundaries without polygon-edge stair steps.
    mesh = head.data
    face_material = build_face_material(skin, skin_light, hair, beard, beard_mid)
    mesh.materials.clear()
    mesh.materials.append(face_material)
    for poly in mesh.polygons:
        poly.use_smooth = True
        poly.material_index = 0

    # Ray queries anchor continuous grooming surfaces to the source head.

    depsgraph = bpy.context.evaluated_depsgraph_get()
    surface_tree = BVHTree.FromObject(head, depsgraph)

    def on_face(x, z, offset=0.004):
        hit, normal, face_index, distance = surface_tree.ray_cast(Vector((x, -0.65, z)), Vector((0.0, 1.0, 0.0)), 1.3)
        if hit is None:
            return Vector((x, -0.15, z))
        if normal is None or normal.length == 0:
            normal = Vector((0.0, -1.0, 0.0))
        return hit + normal.normalized() * offset

    # The beard is shaded on the fitted head surface; this keeps its cheek silhouette
    # clean while the source topology remains the single continuous face.

    # Thick, softly arched brows match the graphic reference without protruding like tubes.
    for side in (-1, 1):
        brow_profile = [
            (0.022, 0.334, 0.30), (0.035, 0.345, 0.78), (0.052, 0.349, 1.0),
            (0.069, 0.345, 0.86), (0.083, 0.337, 0.34),
        ]
        points = [(on_face(side * x, z, 0.006), radius) for x, z, radius in brow_profile]
        make_spline("DadV3 · expressive brow " + str(side), points, hair, 0.0058)

    # A small natural mouth seam and soft lower lip sit inside the moustache/beard gap.
    mouth_line = [(-0.030, 0.232, 0.15), (-0.016, 0.229, 0.65), (0.0, 0.228, 0.8), (0.016, 0.229, 0.65), (0.030, 0.232, 0.15)]
    make_spline("DadV3 · mouth seam", [(on_face(x, z, 0.003), r) for x, z, r in mouth_line], beard, 0.00115)
    lower_lip = [(-0.026, 0.223, 0.12), (-0.014, 0.220, 0.60), (0.0, 0.219, 0.75), (0.014, 0.220, 0.60), (0.026, 0.223, 0.12)]
    make_spline("DadV3 · lower lip", [(on_face(x, z, 0.004), r) for x, z, r in lower_lip], skin_light, 0.0016)

    # Bring the source iris disks onto the visible front of the fitted sclera, then add pupils.
    for obj in bpy.data.objects:
        if obj.name.startswith("sclera_"):
            obj.data.materials.clear()
            obj.data.materials.append(sclera)
        elif obj.name.startswith("iris_"):
            obj.data.materials.clear()
            obj.data.materials.append(iris)
            if obj.data.vertices:
                center_eye = sum((v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
                for vertex in obj.data.vertices:
                    vertex.co.y -= 0.017
                x, y, z = center_eye.x, center_eye.y - 0.017, center_eye.z
            else:
                x, y, z = 0.035, -0.126, 0.31
            make_uv_sphere("DadV3 · pupil " + obj.name, (x, y - 0.0035, z), (0.0052, 0.0022, 0.0062), pupil, 24, 16)
            make_uv_sphere("DadV3 · catchlight " + obj.name, (x - 0.0016, y - 0.006, z + 0.0022), (0.0017, 0.0009, 0.0017), catchlight, 16, 10)

    # A fine, restrained procedural bump suggests short beard grain without raised wires.
    beard_bsdf = beard.node_tree.nodes.get("Principled BSDF")
    beard_noise = beard.node_tree.nodes.new("ShaderNodeTexNoise")
    beard_noise.inputs["Scale"].default_value = 58.0
    beard_noise.inputs["Detail"].default_value = 2.0
    beard_bump = beard.node_tree.nodes.new("ShaderNodeBump")
    beard_bump.inputs["Strength"].default_value = 0.11
    beard_bump.inputs["Distance"].default_value = 0.0012
    beard.node_tree.links.new(beard_noise.outputs["Fac"], beard_bump.inputs["Height"])
    beard.node_tree.links.new(beard_bump.outputs["Normal"], beard_bsdf.inputs["Normal"])

    # A shallow swept quiff sits into the scalp; subtle grooves follow its surface rather
    # than standing proud as separate comb teeth.
    quiff_center = Vector((0.0, 0.060, 0.448))
    rx, ry, rz = 0.108, 0.138, 0.072
    make_uv_sphere("DadV3 · swept quiff mass", tuple(quiff_center), (rx, ry, rz), hair, 64, 40)
    for i in range(5):
        u = -0.70 + 1.40 * i / 4.0
        root = math.sqrt(1.0 - u * u)
        flow = []
        for k in range(21):
            t = k / 20.0
            v = -0.78 + 1.58 * t
            zcurve = math.sqrt(max(0.001, 1.0 - u * u - (v * root) ** 2))
            point = Vector((quiff_center.x + u * rx, quiff_center.y + v * ry * root, quiff_center.z + rz * zcurve + 0.0008))
            flow.append((point, 0.15 + 0.38 * math.sin(math.pi * t) ** 0.45))
        make_spline("DadV3 · swept hair flow %02d" % i, flow, hair_mid if i in {1, 3} else hair, 0.00065)

    # Remove source cameras/lights so render framing is deterministic.
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"} and not obj.name.startswith("DadV3"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Neutral studio setup, matching stylized reference colors without copying its green screen.
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 640
    scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.40
    if scene.world is None:
        scene.world = bpy.data.worlds.new("DadV3 Studio World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.033, 0.043, 0.052, 1.0)
    bg.inputs["Strength"].default_value = 0.18

    center = Vector((0.0, 0.0, 0.315))
    def add_area(name, offset, energy, size, color):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = center + Vector(offset)
        obj.rotation_euler = (center - obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj
    add_area("DadV3 · soft key", (-0.52, -0.72, 0.56), 24, 0.82, (1.0, 0.82, 0.68))
    add_area("DadV3 · fill", (0.55, -0.62, 0.10), 11, 0.92, (0.72, 0.81, 1.0))
    add_area("DadV3 · rim", (0.12, 0.45, 0.52), 24, 0.72, (1.0, 0.84, 0.70))

    def add_camera(name, offset, target, ortho):
        data = bpy.data.cameras.new(name)
        data.type = "ORTHO"
        data.ortho_scale = ortho
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
        obj.location = Vector(target) + Vector(offset)
        obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj
    cameras = [
        ("V3_FRONT", (0.0, -1.65, 0.0), (0.0, 0.0, 0.36), 0.62),
        ("V3_THREE_QUARTER", (0.92, -1.35, 0.0), (0.0, 0.0, 0.36), 0.63),
        ("V3_PROFILE", (1.75, 0.0, 0.0), (0.0, 0.0, 0.36), 0.62),
        ("V3_FACE_CLOSEUP", (0.0, -1.4, 0.0), (0.0, 0.0, 0.325), 0.48),
    ]
    for name, offset, target, scale in cameras:
        add_camera(name, offset, target, scale)

    # Keep the uncluttered source scene visible in the outliner; camera selection is explicit.
    scene.camera = bpy.data.objects["V3_FRONT"]
    scene.render.filepath = "//dad-head-study-v3-front.png"
    scene["study_status"] = "NOT APPROVED — scripted reference-driven study; not manual sculpt"
    scene["source"] = "Dan Ulrich (dan2), neutral sculpting head contribution, 2023; see assets/models/dad/sources/SOURCE.md"
    scene["measured_silhouette_fit"] = json.dumps(fit_report, sort_keys=True)
    print("@@DAD_V3_FIT " + json.dumps(fit_report, sort_keys=True))
    print("@@DAD_V3_READY head_object=%s beard_surface=material-mask quiff=deformed-volume" % head.name)
    return fit_report


main()
