"""Isolated MPFB2 beard-pair fit probe, run only with explicit AGPL3 asset permission.

This modifies only the active workspace copy of V8. It does not edit the source blend
or the main V9 scene. Outputs are diagnostic, not approved character assets.
"""
import bpy
import os
import sys

workspace = os.getcwd()
addon_root = os.path.join(workspace, "addons")
extension_root = os.path.join(addon_root, "bl_ext")
user_extension_root = os.path.join(extension_root, "user_default")
print("MPFB_PATH_CHECK", addon_root, os.path.exists(addon_root), os.listdir(addon_root) if os.path.exists(addon_root) else None)
print("MPFB_PACKAGE_CHECK", os.path.join(user_extension_root, "mpfb", "__init__.py"), os.path.exists(os.path.join(user_extension_root, "mpfb", "__init__.py")))
sys.path.insert(0, addon_root)
# Blender 5.2 exposes a bare `bl_ext` module in this WASM build. Register the
# extension namespace explicitly so the pinned MPFB2 package can be imported.
import types
bl_ext = sys.modules.get("bl_ext")
if bl_ext is None:
    bl_ext = types.ModuleType("bl_ext")
    sys.modules["bl_ext"] = bl_ext
bl_ext.__path__ = [extension_root]
user_default = types.ModuleType("bl_ext.user_default")
user_default.__path__ = [user_extension_root]
sys.modules["bl_ext.user_default"] = user_default
import bl_ext.user_default.mpfb as mpfb
mpfb.get_preference = lambda name: None
mpfb.register()
from bl_ext.user_default.mpfb.services.humanservice import HumanService

human = bpy.data.objects.get("Human")
if human is None or human.type != "MESH":
    raise RuntimeError("V8 base mesh Human was not found")

# Replace only the body skin shader on this disposable copy to avoid the known
# BodySectionsRouter closure warning in Cycles; preserve the separate V8 eyes/hair/clothes.
skin = bpy.data.materials.new("Diagnostic skin · simple Principled")
skin.diffuse_color = (0.50, 0.28, 0.18, 1.0)
skin.use_nodes = True
skin_bsdf = skin.node_tree.nodes.get("Principled BSDF")
skin_bsdf.inputs["Base Color"].default_value = (0.50, 0.28, 0.18, 1.0)
skin_bsdf.inputs["Roughness"].default_value = 0.62
if "Subsurface Weight" in skin_bsdf.inputs:
    skin_bsdf.inputs["Subsurface Weight"].default_value = 0.035
human.data.materials.clear()
human.data.materials.append(skin)
for poly in human.data.polygons:
    poly.material_index = 0


def add_asset(label, directory, mhclo_name, texture_name):
    workspace_asset_dir = os.path.join(workspace, "candidates", "beards", directory)
    repo_root = os.path.abspath(os.path.join(workspace, "..", "..", ".."))
    tracked_asset_dir = os.path.join(repo_root, "assets", "models", "dad", "diagnostics", "beard-pair-agpl3", "source", directory)
    asset_dir = workspace_asset_dir if os.path.exists(os.path.join(workspace_asset_dir, mhclo_name)) else tracked_asset_dir
    mhclo_path = os.path.join(asset_dir, mhclo_name)
    texture_path = os.path.join(asset_dir, texture_name)
    obj = HumanService.add_mhclo_asset(
        mhclo_path,
        human,
        asset_type="Hair",  # MHCLO facial-hair assets are clothes proxies in MPFB2.
        subdiv_levels=0,
        material_type="NONE",
        set_up_rigging=False,
        interpolate_weights=False,
        import_subrig=False,
        import_weights=False,
    )
    obj.name = "AGPL3." + label
    obj.data.name = obj.name + "Mesh"

    mat = bpy.data.materials.new("AGPL3 diagnostic · " + label)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = 0.92
    image = bpy.data.images.load(texture_path, check_existing=True)
    image.alpha_mode = "STRAIGHT"
    image.pack()
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.interpolation = "Linear"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if "Alpha" in bsdf.inputs:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "HASHED"
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj["diagnostic_license"] = "AGPL-3.0-only (conservative interpretation)"
    obj["source_author"] = "grinsegold"
    obj["source_asset"] = mhclo_name
    return obj


beard = add_asset("Full_beard", "Full_beard", "grinsegold_full_beard.mhclo", "Full_beard_black_diff.png")
moustache = add_asset("Moustache", "grinsegold_moustache", "grinsegold_moustache.mhclo", "Moustache_black_diff.png")

# Preserve a readable test description inside the file itself.
scene = bpy.context.scene
scene["diagnostic_title"] = "Full_beard + grinsegold_moustache — isolated AGPL3 fit test, NOT approved"
scene["diagnostic_source"] = "grinsegold MHCLO assets; source snapshot 01e848fdb85cd270228027bf7e1bb8eb85ac47d4"
scene["diagnostic_license"] = "AGPL-3.0-only, conservative interpretation; see accompanying ATTRIBUTION.md and LICENSE-AGPL-3.0.txt"

print("BEARD_PAIR_OBJECTS", beard.name, len(beard.data.vertices), len(beard.data.polygons), moustache.name, len(moustache.data.vertices), len(moustache.data.polygons))
print("BEARD_PAIR_CWD", workspace)
print("BEARD_PAIR_CAMERAS", [obj.name for obj in bpy.data.objects if obj.type == "CAMERA"])
bpy.ops.file.pack_all()
bpy.ops.wm.save_mainfile()
print("BEARD_PAIR_SAVED", bpy.data.filepath)
