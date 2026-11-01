"""Reusable, reference-friendly Blender studio rig for character review renders.

Designed for Blender Python, including the WebAssembly runtime. Call
``setup_studio_review_rig(scene, subject_objects, prefix='CHAR', ...)`` after model
geometry is ready; it returns the standard named orthographic review cameras.
This module configures rendering only and does not alter character geometry/materials.
"""
import math
import bpy
from mathutils import Vector


def _world_bounds(subject_objects):
    points = []
    for obj in subject_objects:
        if obj is None or obj.type not in {"MESH", "CURVE", "SURFACE", "FONT", "META"}:
            continue
        local_points = []
        if obj.type == "MESH" and hasattr(obj.data, "vertices"):
            local_points = [vertex.co.copy() for vertex in obj.data.vertices]
        elif obj.type == "CURVE":
            for spline in obj.data.splines:
                if spline.type == "BEZIER":
                    local_points.extend(point.co.copy() for point in spline.bezier_points)
                else:
                    local_points.extend(Vector(point.co[:3]) for point in spline.points)
        if not local_points:
            local_points = [Vector(corner) for corner in obj.bound_box]
        points.extend(obj.matrix_world @ point for point in local_points)
    if not points:
        raise ValueError("The studio rig needs at least one renderable subject object")
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def _aim_at(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_studio_review_rig(
    scene,
    subject_objects,
    prefix="CHAR",
    resolution=(640, 800),
    samples=64,
    frame_margin=1.28,
    world_color=(0.025, 0.032, 0.040),
    key_color=(1.0, 0.84, 0.72),
    fill_color=(0.84, 0.88, 0.95),
    rim_color=(1.0, 0.86, 0.72),
):
    """Configure consistent lights and a named front/3-4/profile/back/closeup rig.

    Camera framing derives from world-space subject bounds and the requested aspect
    ratio; lights scale with the subject, so the same call works for heads or full-body
    figures. Camera suffixes are `_FRONT`, `_THREE_QUARTER`, `_PROFILE`, `_BACK`, and
    `_FACE_CLOSEUP` to keep harnesses and render batches predictable.
    """
    objects = list(subject_objects)
    minimum, maximum = _world_bounds(objects)
    bounds = maximum - minimum
    target = (minimum + maximum) * 0.5
    width_px, height_px = resolution
    aspect = width_px / height_px
    subject_width = max(bounds.x, bounds.y)
    frame_width = max(subject_width, bounds.z * aspect) * frame_margin
    frame_width = max(frame_width, 0.05)
    radius = max(bounds.length * 0.5, frame_width * 0.5)
    camera_distance = max(radius * 4.0, frame_width * 2.4)

    # Remove only objects created by this helper, leaving all character geometry intact.
    for obj in list(bpy.data.objects):
        if obj.get("studio_render_role") in {"camera", "light"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = int(width_px)
    scene.render.resolution_y = int(height_px)
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.25
    if scene.world is None:
        scene.world = bpy.data.worlds.new("Studio Review World")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (*world_color, 1.0)
    background.inputs["Strength"].default_value = 0.18

    rig_collection = bpy.data.collections.get("Studio Review Rig")
    if rig_collection is None:
        rig_collection = bpy.data.collections.new("Studio Review Rig")
        scene.collection.children.link(rig_collection)

    def area(name, offset, energy_factor, color, size_factor=1.25):
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy_factor * (frame_width / 0.64) ** 2
        light.shape = "DISK"
        light.size = frame_width * size_factor
        light.color = color
        obj = bpy.data.objects.new(name, light)
        rig_collection.objects.link(obj)
        obj["studio_render_role"] = "light"
        obj.location = target + Vector(offset) * radius
        _aim_at(obj, target)
        return obj

    area("Studio Render · key", (-0.95, -1.35, 1.0), 24.0, key_color, 1.15)
    area("Studio Render · fill", (1.05, -0.85, 0.12), 8.0, fill_color, 1.45)
    area("Studio Render · rim", (0.10, 1.15, 0.85), 20.0, rim_color, 1.15)

    # Horizontal and vertical coverage are both respected for landscape and portrait rigs.
    camera_scale = frame_width
    closeup_scale = max(camera_scale * 0.72, 0.05)
    views = {
        "FRONT": (Vector((0.0, -1.0, 0.0)), camera_scale),
        "THREE_QUARTER": (Vector((0.62, -1.0, 0.0)), camera_scale),
        "PROFILE": (Vector((1.0, 0.0, 0.0)), camera_scale),
        "BACK": (Vector((0.0, 1.0, 0.0)), camera_scale),
        "FACE_CLOSEUP": (Vector((0.0, -1.0, 0.0)), closeup_scale),
    }
    cameras = {}
    for suffix, (direction, scale) in views.items():
        name = f"{prefix}_{suffix}"
        data = bpy.data.cameras.new(name)
        data.type = "ORTHO"
        data.ortho_scale = scale
        obj = bpy.data.objects.new(name, data)
        rig_collection.objects.link(obj)
        obj["studio_render_role"] = "camera"
        obj.location = target + direction.normalized() * camera_distance
        _aim_at(obj, target)
        cameras[suffix] = obj
    scene.camera = cameras["FRONT"]
    return {
        "cameras": cameras,
        "target": target,
        "bounds_min": minimum,
        "bounds_max": maximum,
        "frame_width": frame_width,
        "camera_distance": camera_distance,
    }
