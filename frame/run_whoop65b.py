"""在 Mac 上由 Blender --background 调用：建模 → 存 .blend → 渲染设计图 → 导出 STL。"""

import bpy
import sys
from pathlib import Path

frame_dir = Path.home() / "mini-drone-65mm" / "frame"
sys.path.insert(0, str(frame_dir))
renders = frame_dir / "renders"
renders.mkdir(parents=True, exist_ok=True)

import whoop65b_blender  # noqa: E402

whoop65b_blender.build()

blend_path = frame_dir / "Whoop65B_Frame.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

scene = bpy.context.scene
# Workbench：清晰工程图风格（灰底白件 + 线框轮廓）
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.light = "STUDIO"
scene.display.shading.color_type = "SINGLE"
scene.display.shading.single_color = (0.82, 0.84, 0.86)
scene.display.shading.show_object_outline = True
scene.display.shading.object_outline_color = (0.05, 0.05, 0.05)
scene.display.shading.show_cavity = True
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.22, 0.23, 0.25, 1.0)
    bg.inputs[1].default_value = 1.0

cam_top = bpy.data.objects.get("Whoop65B_Top")
if cam_top:
    scene.camera = cam_top
    if cam_top.data:
        cam_top.data.ortho_scale = 95.0
    scene.render.filepath = str(renders / "whoop65b_top.png")
    bpy.ops.render.render(write_still=True)

cam_iso = bpy.data.objects.get("Whoop65B_Iso")
if cam_iso:
    scene.camera = cam_iso
    scene.render.filepath = str(renders / "whoop65b_iso.png")
    bpy.ops.render.render(write_still=True)

stl_path = frame_dir / "Whoop65B_Frame.stl"
frame = bpy.data.objects.get("Whoop65B_Frame")
if frame:
    bpy.ops.object.select_all(action="DESELECT")
    frame.select_set(True)
    bpy.context.view_layer.objects.active = frame
    try:
        bpy.ops.wm.stl_export(filepath=str(stl_path), export_selected_objects=True)
    except Exception:
        # Blender 3.x
        bpy.ops.export_mesh.stl(filepath=str(stl_path), use_selection=True)

print("SAVED", blend_path)
print("RENDERED", sorted(p.name for p in renders.glob("*.png")))
print("STL", stl_path if stl_path.exists() else "missing")
