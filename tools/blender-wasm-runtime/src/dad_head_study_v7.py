"""Official-base V7 Dad head/bust study. Scripted geometry; not manual sculpting or approved.

Starts from the official Blender Human Base Meshes v1.4.1 stylized head and eyes.
It bakes source transforms, preserves the skull profile, broadens the lower face and neck,
and builds separate surface-conforming scalp/beard meshes rather than spherical overlays.
"""
import bpy
import bmesh
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


def build_beard_shell_material(beard, name="DadV7 · feathered volumetric beard", uv_name="BeardShellUV", fade_width_u=0.095, fade_width_v=0.17):
    """Give a mesh edge a soft UV-driven fade so it blends into the face, not a mask."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    uv = nodes.new("ShaderNodeUVMap")
    uv.uv_map = uv_name
    separate = nodes.new("ShaderNodeSeparateXYZ")
    links.new(uv.outputs["UV"], separate.inputs["Vector"])

    def math_node(operation, a, b=None):
        node = nodes.new("ShaderNodeMath")
        node.operation = operation
        if hasattr(a, "node"):
            links.new(a, node.inputs[0])
        else:
            node.inputs[0].default_value = a
        if b is not None:
            if hasattr(b, "node"):
                links.new(b, node.inputs[1])
            else:
                node.inputs[1].default_value = b
        return node.outputs[0]

    def fade(value, width, label):
        node = nodes.new("ShaderNodeMapRange")
        node.label = label
        node.interpolation_type = "SMOOTHSTEP"
        node.clamp = True
        node.inputs["From Min"].default_value = 0.0
        node.inputs["From Max"].default_value = width
        node.inputs["To Min"].default_value = 0.0
        node.inputs["To Max"].default_value = 1.0
        links.new(value, node.inputs["Value"])
        return node.outputs["Result"]

    u, v = separate.outputs["X"], separate.outputs["Y"]
    u_edge = math_node("MINIMUM", u, math_node("SUBTRACT", 1.0, u))
    v_edge = math_node("MINIMUM", v, math_node("SUBTRACT", 1.0, v))
    fade_u = fade(u_edge, fade_width_u, "Fade at sideburn ends")
    fade_v = fade(v_edge, fade_width_v, "Fade at cheek and jaw edges")
    opacity = math_node("MULTIPLY", fade_u, fade_v)

    pigment = nodes.new("ShaderNodeBsdfPrincipled")
    pigment.inputs["Base Color"].default_value = beard.diffuse_color
    pigment.inputs["Roughness"].default_value = 0.57
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links.new(opacity, mix.inputs[0])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(pigment.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])
    return mat


def line_height(theta):
    # Clear the ears, keep a short temple fade, and finish above the rounded nape.
    if theta < 0.65:
        return 0.438
    if theta < 1.45:
        return 0.438 - 0.043 * smoothstep((theta - 0.65) / 0.80)
    return 0.395 - 0.055 * smoothstep((theta - 1.45) / (math.pi - 1.45))


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
    head.name = "DadV7 · official stylized base"
    eyes[0].name = "DadV7 · eye L"
    eyes[1].name = "DadV7 · eye R"

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

    # Shape the jaw/neck and nose on the official mesh; hair and beard are separate geometry.
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
        bridge = math.exp(-((p.x / 0.026) ** 2)) * math.exp(-(((p.z - 0.352) / 0.060) ** 2))
        tip = math.exp(-((p.x / 0.031) ** 2)) * math.exp(-(((p.z - 0.305) / 0.026) ** 2))
        p.y -= 0.012 * bridge + 0.018 * tip
        p.x *= 1.0 + 0.045 * tip
    head.data.update()

    skin = material("DadV7 · warm skin", (0.51, 0.255, 0.17), 0.46, subsurface=0.035)
    skin_light = material("DadV7 · lips", (0.61, 0.32, 0.23), 0.43, subsurface=0.02)
    hair = material("DadV7 · dark espresso hair", (0.042, 0.020, 0.014), 0.56, specular=0.24)
    hair_mid = material("DadV7 · hair highlights", (0.065, 0.031, 0.019), 0.52, specular=0.26)
    beard = material("DadV7 · chestnut beard", (0.078, 0.024, 0.010), 0.62, specular=0.16)
    beard_mid = material("DadV7 · brow and facial detail", (0.092, 0.043, 0.026), 0.54, specular=0.22)
    sclera = material("DadV7 · ivory sclera", (0.88, 0.80, 0.70), 0.24, specular=0.5)
    iris = material("DadV7 · hazel iris", (0.30, 0.12, 0.035), 0.27, specular=0.48)
    pupil = material("DadV7 · pupil", (0.012, 0.008, 0.006), 0.18, specular=0.5)
    glint = material("DadV7 · eye glint", (0.98, 0.93, 0.85), 0.13, specular=0.55)

    face_material = skin  # No painted hair/beard mask: those regions are represented by separate geometry.
    beard_shell_material = build_beard_shell_material(beard, fade_width_u=0.12, fade_width_v=0.24)
    mustache_material = build_beard_shell_material(
        beard, "DadV7 · softly blended raised moustache", "MustacheUV", 0.20, 0.36
    )
    head.data.materials.clear()
    head.data.materials.append(face_material)
    for poly in head.data.polygons:
        poly.use_smooth = True
        poly.material_index = 0

    # Separate scalp-cap mesh, duplicated from the official scalp surface. Smooth only its
    # open hairline boundary, then add a compact front quiff by lifting cap vertices.
    cap_bm = bmesh.new()
    cap_bm.from_mesh(head.data)
    cap_bm.normal_update()
    cap_bm.faces.ensure_lookup_table()
    cap_faces_bm = []
    for face in cap_bm.faces:
        center = face.calc_center_median()
        theta = abs(math.atan2(center.x, -center.y))
        if center.z >= line_height(theta):
            cap_faces_bm.append(face)
    cap_source_verts = sorted({v for face in cap_faces_bm for v in face.verts}, key=lambda v: v.index)
    cap_index = {v: i for i, v in enumerate(cap_source_verts)}
    hair_verts = [tuple(vertex.co) for vertex in cap_source_verts]
    hair_faces = [tuple(cap_index[v] for v in face.verts) for face in cap_faces_bm]
    cap_bm.free()
    hair_mesh = bpy.data.meshes.new("DadV7SeparateScalpCapMesh")
    hair_mesh.from_pydata(hair_verts, [], hair_faces)
    hair_mesh.materials.append(hair)
    hair_mesh.update()
    cap_smooth = bmesh.new()
    cap_smooth.from_mesh(hair_mesh)
    cap_smooth.verts.ensure_lookup_table()
    cap_smooth.verts.index_update()
    border = {v for edge in cap_smooth.edges if edge.is_boundary for v in edge.verts}
    for _ in range(12):
        previous = {v: v.co.copy() for v in border}
        for vertex in border:
            neighbors = [edge.other_vert(vertex) for edge in vertex.link_edges if edge.is_boundary and edge.other_vert(vertex) in border]
            if neighbors:
                average = sum((previous[n] for n in neighbors), Vector()) / len(neighbors)
                vertex.co = previous[vertex].lerp(average, 0.32)
    # Add enough surface samples for broad, smooth carved hair flow without pointy strands.
    bmesh.ops.subdivide_edges(cap_smooth, edges=list(cap_smooth.edges), cuts=2, use_grid_fill=True)
    cap_smooth.verts.ensure_lookup_table()
    border = {v for edge in cap_smooth.edges if edge.is_boundary for v in edge.verts}
    distance_to_border = {v: 0 for v in border}
    queue = list(border)
    cursor = 0
    while cursor < len(queue):
        vertex = queue[cursor]
        cursor += 1
        if distance_to_border[vertex] >= 8:
            continue
        for edge in vertex.link_edges:
            other = edge.other_vert(vertex)
            if other not in distance_to_border:
                distance_to_border[other] = distance_to_border[vertex] + 1
                queue.append(other)
    cap_smooth.normal_update()
    for vertex in cap_smooth.verts:
        p = vertex.co
        quiff = math.exp(-(((p.x - 0.012) / 0.075) ** 2)) * math.exp(-(((p.y + 0.088) / 0.055) ** 2)) * smoothstep((p.z - 0.385) / 0.060)
        flow_t = max(0.0, min(1.0, (p.y + 0.135) / 0.225))
        flow = smoothstep(flow_t / 0.16) * (1.0 - smoothstep((flow_t - 0.83) / 0.17)) * smoothstep((p.z - 0.390) / 0.060)
        lock_ridge = 0.0
        for lane in range(-2, 3):
            center_x = lane * 0.031 + 0.018 * flow_t + 0.004 * math.sin(math.pi * flow_t)
            lock_ridge += 0.009 * math.exp(-(((p.x - center_x) / 0.020) ** 2))
        fringe = 0.0
        for lane in range(-2, 3):
            center_x = lane * 0.030 + 0.016 * flow_t
            fringe += 0.014 * math.exp(-(((p.x - center_x) / 0.022) ** 2))
        fringe *= math.exp(-(((p.y + 0.074) / 0.048) ** 2)) * smoothstep((p.z - 0.390) / 0.060)
        border_fade = smoothstep(distance_to_border.get(vertex, 8) / 8.0)
        normal = vertex.normal.normalized() if vertex.normal.length else Vector((0.0, 0.0, 1.0))
        surface_grain = 0.0008 * math.sin(p.x * 280.0 + p.y * 170.0) * math.sin(p.y * 245.0 + p.z * 180.0)
        vertex.co += normal * (0.0015 + lock_ridge * flow + surface_grain * flow) * border_fade
        vertex.co.z += (0.030 * quiff + fringe) * border_fade
    cap_smooth.to_mesh(hair_mesh)
    cap_smooth.free()
    hair_mesh.update()
    hair_obj = bpy.data.objects.new("DadV7 · separate raised hair cap", hair_mesh)
    bpy.context.collection.objects.link(hair_obj)
    for poly in hair_mesh.polygons:
        poly.use_smooth = True
    hair_smooth = hair_obj.modifiers.new("Hairline and nape smoothing", "SUBSURF")
    hair_smooth.subdivision_type = "CATMULL_CLARK"
    hair_smooth.levels = 2
    hair_smooth.render_levels = 2
    hair_thickness = hair_obj.modifiers.new("Hair cap inner wall", "SOLIDIFY")
    hair_thickness.thickness = 0.006
    hair_thickness.offset = -1.0

    # A quad grid is ray-seated to the lower official face. It is a distinct beard object,
    # offset outward from the surface and closed with a thin inner wall; no painted-only patch.
    surface = BVHTree.FromObject(head, bpy.context.evaluated_depsgraph_get())
    angle_steps, row_steps, beard_angle = 145, 61, 0.86
    beard_grid = [[None for _ in range(row_steps)] for _ in range(angle_steps)]
    beard_verts, beard_faces, beard_uv = [], [], {}
    def beard_upper(theta):
        # Raised central moustache line blends continuously into high cheek beard.
        return 0.268 + 0.024 * smoothstep(abs(theta) / beard_angle)
    def beard_lower(theta):
        return 0.174 + 0.015 * smoothstep(abs(theta) / beard_angle)
    for i in range(angle_steps):
        theta = -beard_angle + 2.0 * beard_angle * i / (angle_steps - 1)
        radial = Vector((math.sin(theta), -math.cos(theta), 0.0))
        upper, lower = beard_upper(theta), beard_lower(theta)
        angular_fade = smoothstep(min(i, angle_steps - 1 - i) / 9.0)
        for j in range(row_steps):
            t = j / (row_steps - 1)
            z = upper * (1.0 - t) + lower * t
            origin = Vector((0.0, 0.0, z)) + radial * 0.62
            hit, normal, face_index, distance = surface.ray_cast(origin, -radial, 1.24)
            if hit is None:
                continue
            vertical_fade = smoothstep(min(t, 1.0 - t) / 0.14)
            mustache_lift = 0.0035 * math.exp(-((theta / 0.38) ** 2)) * math.exp(-(((z - 0.266) / 0.018) ** 2))
            grain = 0.00012 * math.sin(hit.x * 490.0 + hit.z * 830.0 + hit.y * 130.0) * math.sin(hit.z * 610.0 - hit.x * 330.0)
            push = 0.014 * angular_fade * vertical_fade + mustache_lift + grain * angular_fade * vertical_fade
            beard_grid[i][j] = len(beard_verts)
            beard_uv[len(beard_verts)] = (i / (angle_steps - 1), t)
            beard_verts.append(tuple(hit + radial * push))
    for i in range(angle_steps - 1):
        theta_mid = -beard_angle + 2.0 * beard_angle * (i + 0.5) / (angle_steps - 1)
        for j in range(row_steps - 1):
            indices = (beard_grid[i][j], beard_grid[i + 1][j], beard_grid[i + 1][j + 1], beard_grid[i][j + 1])
            if any(index is None for index in indices):
                continue
            beard_faces.append(indices)
    beard_mesh = bpy.data.meshes.new("DadV7SeparateBeardShellMesh")
    beard_mesh.from_pydata(beard_verts, [], beard_faces)
    beard_mesh.materials.append(beard_shell_material)
    beard_mesh.update()
    uv_layer = beard_mesh.uv_layers.new(name="BeardShellUV")
    for polygon in beard_mesh.polygons:
        for loop_index in polygon.loop_indices:
            vertex_index = beard_mesh.loops[loop_index].vertex_index
            uv_layer.data[loop_index].uv = beard_uv[vertex_index]
    beard_bm = bmesh.new()
    beard_bm.from_mesh(beard_mesh)
    bmesh.ops.recalc_face_normals(beard_bm, faces=list(beard_bm.faces))
    beard_bm.to_mesh(beard_mesh)
    beard_bm.free()
    beard_obj = bpy.data.objects.new("DadV7 · separate volumetric beard shell", beard_mesh)
    bpy.context.collection.objects.link(beard_obj)
    for poly in beard_mesh.polygons:
        poly.use_smooth = True
    beard_smooth = beard_obj.modifiers.new("Soft beard silhouette and lip opening", "SUBSURF")
    beard_smooth.subdivision_type = "CATMULL_CLARK"
    beard_smooth.levels = 2
    beard_smooth.render_levels = 2
    beard_wall = beard_obj.modifiers.new("Beard inner wall", "SOLIDIFY")
    beard_wall.thickness = 0.012
    beard_wall.offset = -1.0
    beard_face_count = len(beard_mesh.polygons)

    # Reuse the official eye meshes as smaller, deeper sclerae, then set fitted iris/pupil layers.
    eye_specs = []
    for eye in eyes:
        xs = [v.co.x for v in eye.data.vertices]
        ys = [v.co.y for v in eye.data.vertices]
        zs = [v.co.z for v in eye.data.vertices]
        ex = (min(xs) + max(xs)) * 0.5
        ez = (min(zs) + max(zs)) * 0.5
        for vertex in eye.data.vertices:
            center = Vector((ex, (min(ys) + max(ys)) * 0.5, ez))
            # 30% smaller than V6 and shifted deeper into the orbital socket.
            vertex.co = center + (vertex.co - center) * 0.476 + Vector((0.0, -0.0100, 0.0))
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
        eye_specs.append((ex, ez, max(xs) - min(xs), max(zs) - min(zs), suffix))
        uv_sphere("DadV7 · iris " + suffix, (ex, front_y - 0.0012, ez), (0.0063, 0.0020, 0.0074), iris, 32, 20)
        uv_sphere("DadV7 · pupil " + suffix, (ex, front_y - 0.0032, ez), (0.0032, 0.0016, 0.0042), pupil, 24, 16)
        uv_sphere("DadV7 · glint " + suffix, (ex - 0.0020, front_y - 0.0048, ez + 0.0028), (0.0012, 0.0007, 0.0012), glint, 16, 10)

    # Subtle brow geometry is ray-seated to the transformed official face.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    face_tree = BVHTree.FromObject(head, depsgraph)
    def on_face(x, z, offset=0.004):
        hit, normal, face_index, distance = face_tree.ray_cast(Vector((x, -0.62, z)), Vector((0.0, 1.0, 0.0)), 1.24)
        if hit is None:
            return Vector((x, -0.14, z))
        return hit + (normal.normalized() if normal and normal.length else Vector((0.0, -1.0, 0.0))) * offset

    # Two broad, tapered surface patches form a soft raised moustache, rather than crossed wires.
    for side in (-1, 1):
        u_steps, v_steps = 33, 13
        patch_verts, patch_faces, patch_uv = [], [], []
        for i in range(u_steps):
            u = i / (u_steps - 1)
            x = 0.008 + 0.044 * u
            center_z = 0.266 - 0.008 * u + 0.002 * math.sin(math.pi * u)
            half_height = 0.001 + 0.0045 * (math.sin(math.pi * u) ** 0.7)
            for j in range(v_steps):
                v = j / (v_steps - 1)
                z = center_z + (2.0 * v - 1.0) * half_height
                dome = math.sin(math.pi * u) * math.sin(math.pi * v)
                patch_verts.append(tuple(on_face(side * x, z, 0.009 + 0.002 * dome)))
                patch_uv.append((u, v))
        for i in range(u_steps - 1):
            for j in range(v_steps - 1):
                a = i * v_steps + j
                patch_faces.append((a, a + v_steps, a + v_steps + 1, a + 1))
        patch_mesh = bpy.data.meshes.new("DadV7RaisedMoustacheSurface")
        patch_mesh.from_pydata(patch_verts, [], patch_faces)
        patch_mesh.materials.append(mustache_material)
        patch_mesh.update()
        uv_layer = patch_mesh.uv_layers.new(name="MustacheUV")
        for polygon in patch_mesh.polygons:
            for loop_index in polygon.loop_indices:
                uv_layer.data[loop_index].uv = patch_uv[patch_mesh.loops[loop_index].vertex_index]
        patch_bm = bmesh.new()
        patch_bm.from_mesh(patch_mesh)
        bmesh.ops.recalc_face_normals(patch_bm, faces=list(patch_bm.faces))
        patch_bm.to_mesh(patch_mesh)
        patch_bm.free()
        patch_obj = bpy.data.objects.new("DadV7 · volumetric moustache " + str(side), patch_mesh)
        bpy.context.collection.objects.link(patch_obj)
        for poly in patch_mesh.polygons:
            poly.use_smooth = True
        patch_smooth = patch_obj.modifiers.new("Soft rounded moustache form", "SUBSURF")
        patch_smooth.subdivision_type = "CATMULL_CLARK"
        patch_smooth.levels = 2
        patch_smooth.render_levels = 2
        patch_wall = patch_obj.modifiers.new("Moustache inner wall", "SOLIDIFY")
        patch_wall.thickness = 0.003
        patch_wall.offset = -1.0

    # The official sculpt already has modeled orbital rims; keep those, without
    # adding bright concentric overlay curves.
    for side in (-1, 1):
        brow = [(0.020, 0.397, 0.25), (0.035, 0.405, 0.72), (0.052, 0.408, 1.0), (0.070, 0.403, 0.75), (0.084, 0.395, 0.20)]
        make_curve("DadV7 · eyebrow " + str(side), [(on_face(side * x, z, 0.005), r) for x, z, r in brow], beard_mid, 0.0025)
    beard_tree = BVHTree.FromObject(beard_obj, bpy.context.evaluated_depsgraph_get())
    def on_beard(x, z, offset=0.003):
        hit, normal, face_index, distance = beard_tree.ray_cast(Vector((x, -0.65, z)), Vector((0.0, 1.0, 0.0)), 1.3)
        if hit is None:
            return on_face(x, z, offset + 0.008)
        return hit + (normal.normalized() if normal and normal.length else Vector((0.0, -1.0, 0.0))) * offset
    mouth_line = [(-0.024, 0.239, 0.12), (-0.012, 0.237, 0.55), (0.0, 0.236, 0.7), (0.012, 0.237, 0.55), (0.024, 0.239, 0.12)]
    make_curve("DadV7 · mouth seam", [(on_beard(x, z, 0.002), r) for x, z, r in mouth_line], beard_mid, 0.0009)
    # A shared studio-rig module keeps framing, exposure, and lights consistent for
    # future characters instead of hard-coding this study's camera placements.
    subject_objects = [obj for obj in bpy.data.objects if obj.type in {"MESH", "CURVE"}]
    setup_studio_review_rig(
        scene, subject_objects, prefix="V7", resolution=(640, 800), samples=40, frame_margin=1.32
    )
    scene["study_status"] = "NOT APPROVED — official base, separate hair/beard geometry, review only"
    scene["source"] = "Blender Human Base Meshes v1.4.1 / GEO-head_stylized — CC0"
    print("@@DAD_V7_RESULT " + json.dumps({"source_bounds": [[round(xmin, 5), round(ymin, 5), round(zmin, 5)], [round(xmax, 5), round(ymax, 5), round(zmax, 5)]], "normalized_bounds": [[round(min(v.co.x for v in head.data.vertices), 5), round(min(v.co.y for v in head.data.vertices), 5), round(min(v.co.z for v in head.data.vertices), 5)], [round(max(v.co.x for v in head.data.vertices), 5), round(max(v.co.y for v in head.data.vertices), 5), round(max(v.co.z for v in head.data.vertices), 5)]], "beard_shell_faces": len(beard_faces), "hair_cap_faces": len(hair_faces), "geometry_volume": "separate scalp/beard/moustache meshes", "source_mesh_faces": len(head.data.polygons)}))


main()
