"""
Whoop-65B 机架 — Blender 参数化建模脚本
在 MacBook Pro 上：安装 Blender → 打开本脚本 → 运行 → 另存为 .blend / 导出 STL

尺寸与 frame/README.md 一致（单位：mm，场景按 1 BU = 1 mm）。
"""

import bpy
import math
from mathutils import Vector

# ---------- 关键尺寸（mm）----------
MOTOR_SQUARE = 46.0          # 相邻电机中心距
DIAGONAL = 65.0              # 对角电机中心距（校验用）
BASE_XY = 70.0
BASE_Z = 1.2
DUCT_ID = 33.5
DUCT_WALL = 1.0
DUCT_H = 15.0
MOTOR_BORE = 7.2
MOTOR_BORE_DEPTH = 10.0
BATTERY_L, BATTERY_W, BATTERY_H = 20.0, 12.0, 8.0
CORNER_R = 6.0


def clear_mesh_objects():
    bpy.ops.object.select_all(action="DESELECT")
    for obj in list(bpy.context.scene.objects):
        if obj.type == "MESH":
            obj.select_set(True)
    bpy.ops.object.delete()


def set_mm_units():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.001  # 1 Blender Unit = 1 mm
    scene.unit_settings.length_unit = "MILLIMETERS"


def motor_centers():
    """正方形四角：俯视 M4-M2 / M3-M1，对角线 ≈ 65 mm。"""
    half = MOTOR_SQUARE / 2.0
    # 前左、前右、后左、后右 → 对应 README 的 M4,M2,M3,M1
    return [
        Vector((-half, half, 0)),
        Vector((half, half, 0)),
        Vector((-half, -half, 0)),
        Vector((half, -half, 0)),
    ]


def add_rounded_plate(name, size_xy, thick, radius):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size_xy, size_xy, thick)
    bpy.ops.object.transform_apply(scale=True)
    obj.location.z = thick / 2.0

    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = radius
    mod.segments = 6
    mod.limit_method = "ANGLE"
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def add_duct(center, name):
    od = DUCT_ID + 2.0 * DUCT_WALL
    bpy.ops.mesh.primitive_cylinder_add(
        radius=od / 2.0,
        depth=DUCT_H,
        vertices=64,
        location=(center.x, center.y, BASE_Z + DUCT_H / 2.0),
    )
    outer = bpy.context.active_object
    outer.name = name + "_outer"

    bpy.ops.mesh.primitive_cylinder_add(
        radius=DUCT_ID / 2.0,
        depth=DUCT_H + 2.0,
        vertices=64,
        location=(center.x, center.y, BASE_Z + DUCT_H / 2.0),
    )
    inner = bpy.context.active_object
    inner.name = name + "_inner"

    bool_mod = outer.modifiers.new("CutDuct", "BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.object = inner
    bpy.context.view_layer.objects.active = outer
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    return outer


def cut_motor_bore(plate, center):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=MOTOR_BORE / 2.0,
        depth=MOTOR_BORE_DEPTH + 2.0,
        vertices=48,
        location=(center.x, center.y, BASE_Z / 2.0),
    )
    cutter = bpy.context.active_object
    cutter.name = "tmp_motor_bore"

    bool_mod = plate.modifiers.new("CutMotor", "BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.object = cutter
    bpy.context.view_layer.objects.active = plate
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def cut_battery_pocket(plate):
    bpy.ops.mesh.primitive_cube_add(size=1)
    pocket = bpy.context.active_object
    pocket.name = "tmp_battery"
    pocket.scale = (BATTERY_L, BATTERY_W, BATTERY_H)
    bpy.ops.object.transform_apply(scale=True)
    pocket.location = (0, 0, -BATTERY_H / 2.0 + 0.2)

    bool_mod = plate.modifiers.new("CutBatt", "BOOLEAN")
    bool_mod.operation = "DIFFERENCE"
    bool_mod.object = pocket
    bpy.context.view_layer.objects.active = plate
    bpy.ops.object.modifier_apply(modifier=bool_mod.name)
    bpy.data.objects.remove(pocket, do_unlink=True)


def join_objects(objects, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    objects[0].name = name
    return objects[0]


def add_dimension_empties(centers):
    """空物体标注关键点，便于出图时量尺寸。"""
    for i, c in enumerate(centers, start=1):
        empty = bpy.data.objects.new(f"M{i}_center", None)
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 3.0
        empty.location = (c.x, c.y, BASE_Z + DUCT_H)
        bpy.context.collection.objects.link(empty)


def setup_camera_top():
    cam_data = bpy.data.cameras.new("Whoop65B_Top")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 90.0
    cam = bpy.data.objects.new("Whoop65B_Top", cam_data)
    cam.location = (0, 0, 120)
    cam.rotation_euler = (0, 0, 0)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def setup_camera_iso():
    cam_data = bpy.data.cameras.new("Whoop65B_Iso")
    cam = bpy.data.objects.new("Whoop65B_Iso", cam_data)
    cam.location = (80, -80, 70)
    cam.rotation_euler = (math.radians(55), 0, math.radians(45))
    bpy.context.collection.objects.link(cam)


def setup_light():
    light_data = bpy.data.lights.new("Key", type="AREA")
    light_data.energy = 200
    light_data.size = 80
    light = bpy.data.objects.new("Key", light_data)
    light.location = (40, -40, 80)
    bpy.context.collection.objects.link(light)


def build():
    clear_mesh_objects()
    set_mm_units()

    centers = motor_centers()
    diag = (centers[0] - centers[3]).length
    print(f"[Whoop-65B] motor diagonal = {diag:.2f} mm (target {DIAGONAL})")

    plate = add_rounded_plate("base_plate", BASE_XY, BASE_Z, CORNER_R)
    for c in centers:
        cut_motor_bore(plate, c)
    cut_battery_pocket(plate)

    ducts = [add_duct(c, f"duct_{i}") for i, c in enumerate(centers, start=1)]
    frame = join_objects([plate] + ducts, "Whoop65B_Frame")

    # 浅灰塑料感
    mat = bpy.data.materials.new("PETG_Grey")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.55, 0.57, 0.6, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.45
    if frame.data.materials:
        frame.data.materials[0] = mat
    else:
        frame.data.materials.append(mat)

    add_dimension_empties(centers)
    setup_camera_top()
    setup_camera_iso()
    setup_light()

    # 俯视正交，适合「设计图」截图
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.region_3d.view_perspective = "ORTHO"
                    space.region_3d.view_rotation = (1, 0, 0, 0)
            break

    print("[Whoop-65B] 完成：另存为 Whoop65B_Frame.blend；可导出 STL 打印。")
    print("  俯视相机: Whoop65B_Top | 轴测相机: Whoop65B_Iso")


if __name__ == "__main__":
    build()
