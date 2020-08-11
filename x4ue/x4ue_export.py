import bpy
import bmesh
import math
import re
import operator
import os
import difflib
from math import degrees, pi, radians, ceil
from bpy.types import Panel, UIList
import mathutils
from mathutils import Vector, Euler, Matrix
from bpy_extras.io_utils import ExportHelper


if "bpy" in locals():
    import importlib

    if "x4ue_log" in locals():
        importlib.reload(x4ue_log)
    if "x4ue_funcs" in locals():
        importlib.reload(x4ue_funcs)
    if "x4ue_utils" in locals():
        importlib.reload(x4ue_utils)
    if "x4ue_tools" in locals():
        importlib.reload(x4ue_tools)

from . import x4ue_log, x4ue_funcs, x4ue_utils, x4ue_tools
from .x4ue_utils import (
    # Constants
    X4UE_OBJ_SUFFIX,
    X4UE_OBJ_WORK_SUFFIX,
    X4UE_DUMMY_MESH_NAME,
    # Functions
    select_objects,
    set_active_object,
    is_object_hidden,
    is_mesh,
    is_armature,
)
from .x4ue_funcs import (
    set_scale_x100,
    revert_scale_x100,
    create_copy_objects,
    delete_copy_objects,
    rename_objects_for_export,
    revert_object_name,
    set_action_scale_x100,
    revert_action_scale_x100,
    set_scale_x100_no_armature,
)
from .x4ue_log import debuglog, infolog, warnlog, errorlog, set_log_level


class X4UE_OT_export_fbx_panel(bpy.types.Operator, ExportHelper):
    """ Export FBX file format """

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "UE4 FBX Export"
    bl_idname = "id.x4ue_export_fbx_panel"

    filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(default="*.fbx", options={"HIDDEN"})
    message_final = ""
    non_armature_actions = []

    def draw(self, context):
        layout = self.layout
        active_object = context.active_object
        scene = context.scene

        # Buttons
        col = layout.column(align=True)

        # Disable x100 scale property input
        # box = layout.box()
        # box.label(text="Units:")
        # col = box.column(align=True)
        # row = col.row(align=True)
        # row.prop(scene, "x4ue_units_x100")

        box = layout.box()
        box.label(text="Misc:")
        col = box.column(align=True)
        col.prop(scene, "x4ue_global_scale")
        col = box.column(align=True)
        col.prop(scene, "x4ue_mesh_smooth_type")
        col = box.column(align=True)
        col.prop(scene, "x4ue_use_armature_deform_only")
        col = box.column()
        col.label(text="Bones Axes:")
        col.prop(scene, "x4ue_bone_axis_primary_export", text="Primary")
        col.prop(scene, "x4ue_bone_axis_secondary_export", text="Secondary")

        # TODO ActionSelectorを追加する
        box = layout.box()
        box.label(text="Animations:")

        col = box.column(align=True)
        col.label(text="Export Mode:")
        col.prop(scene, "x4ue_mode_export_animations", text="")

        if context.scene.x4ue_mode_export_animations == "SELECT":
            col_anim = box.column(align=True)

            if len(bpy.data.actions):
                for act in bpy.data.actions:
                    act_row = col.row(align=True)
                    act_row.label(text=act.name)
                    icon_name = "CHECKBOX_HLT"
                    if len(act.keys()) > 0:
                        if "x4ue_export" in act.keys():
                            if not act["x4ue_export"]:
                                icon_name = "CHECKBOX_DEHLT"
                    op_select = act_row.operator(
                        "x4ue.select_action", text="", icon=icon_name
                    )
                    op_select.action_name = act.name

            else:
                row = col.row(align=True)
                row.label(text="No actions to export")

    def execute(self, context):
        return X4UE_OT_export_fbx.execute(self, context)


class X4UE_OT_export_fbx(bpy.types.Operator):
    """Export armature in .fbx file format"""

    bl_idname = "id.export_fbx"
    bl_label = "Export .FBX(for UE4)"

    def execute(self, context):

        set_log_level(context.scene.x4ue_log_level)

        # valiables
        self.units_before_export = context.scene.unit_settings.scale_length
        self.arm_scale = None
        self.actions_units_changed = []
        self.actions_x100_changed = []
        self.actions_pushed_changed = []
        self.save_auto_key = context.scene.tool_settings.use_keyframe_insert_auto
        self.saved_collection_vis = [i.hide_viewport for i in bpy.data.collections]
        self.saved_unit_type = context.scene.unit_settings.system
        self.current_selection = None

        self.armature_name = ""
        self.armature_add_name = ""
        self.char_objects = None
        self.message_final = ""
        self.non_armature_actions = []
        self.shape_keys_data = {}

        target_armature_name = ""
        list_target_objects = []
        list_target_actions = []

        no_armature_mode = False

        try:

            # Initial checks

            # Is target armature selected?
            if bpy.context.active_object is None:
                warnlog("Not found selected object")
                self.report({"ERROR"}, "Select the armature to export")
                return {"FINISHED"}

            debuglog("Current selected object:", bpy.context.active_object.name)

            self.current_selection = [
                bpy.context.active_object.name,
                [i.name for i in bpy.context.selected_objects],
            ]

            # Set the armature as active object (if any)
            if not is_armature(bpy.context.active_object):
                for obj in bpy.context.selected_objects:
                    if is_armature(obj):
                        set_active_object(obj.name)
                        break

            if not is_armature(bpy.context.active_object):

                # TODO Need Implemetnt NO ARMATURE mode
                no_armature_mode = True
                debuglog("NO ARMATURE MODE Enabled")

                selected_parent = [
                    obj for obj in bpy.context.selected_objects if obj.parent is None
                ]
                debuglog("Selected parent:", selected_parent)

                if len(selected_parent) == 0:
                    warnlog("No root object")
                    self.report(
                        {"ERROR"},
                        "No root object detected. Plase select target object(s) structure include root.",
                    )
                    return {"FINISHED"}

                if len(selected_parent) > 1:
                    warnlog("Multi root object detected")
                    self.report(
                        {"ERROR"},
                        "Multi root object detected. Please select single structure.",
                    )
                    return {"FINISHED"}

                target_armature_name = selected_parent[0].name

            if no_armature_mode:
                debuglog(
                    "(NO ARMATURE MODE) Target object:", bpy.context.active_object.name
                )
            else:
                debuglog("Target armature: ", bpy.context.active_object.name)

            armature_base_name = bpy.context.active_object.name
            if bpy.context.active_object.proxy:
                armature_base_name = bpy.context.active_object.proxy.name
                debuglog("The armature is a proxy. Real name = ", armature_base_name)

            # Set main target armature name
            target_armature_name = bpy.context.active_object.name

            debuglog("Begin FBX Export")

            # Disable auto-keyframe
            context.scene.tool_settings.use_keyframe_insert_auto = False

            # Create copy objects
            list_target_objects = create_copy_objects(
                target_armature_name, no_armature_mode
            )
            list_target_actions = [a.name for a in bpy.data.actions]

            if no_armature_mode:
                set_scale_x100_no_armature(list_target_objects)
            else:
                set_scale_x100(target_armature_name)

            set_action_scale_x100(list_target_actions)

            # Select exportable only
            select_objects(*list_target_objects)

            rename_objects_for_export(list_target_objects)

            infolog("Begin FBX EXPORT")

            bpy.ops.x4ue_export_scene.fbx(
                filepath=self.filepath,
                use_selection=True,
                # TODO DEBUG
                global_scale=context.scene.x4ue_global_scale,
                use_mesh_modifiers=True,
                use_armature_deform_only=context.scene.x4ue_use_armature_deform_only,
                add_leaf_bones=False,
                apply_unit_scale=True,
                # TODO debug
                # humanoid_actions=context.scene.x4ue_export_h_actions,
                # TODO debug
                # bake_anim_simplify_factor=context.scene.x4ue_simplify_fac,
                mesh_smooth_type=context.scene.x4ue_mesh_smooth_type,
                primary_bone_axis=context.scene.x4ue_bone_axis_primary_export,
                secondary_bone_axis=context.scene.x4ue_bone_axis_secondary_export,
                # TODO debug
                # shape_keys_baked_data=str(self.shape_keys_data)
            )

        finally:
            # Revert changes after export
            revert_object_name(list_target_objects)

            # Revert animation scale
            revert_action_scale_x100(list_target_actions)

            # deleting copies
            delete_copy_objects(list_target_objects)

            # set auto-key if needed
            context.scene.tool_settings.use_keyframe_insert_auto = self.save_auto_key

            # Resotore collections
            for i, vis_value in enumerate(self.saved_collection_vis):
                bpy.data.collections[i].hide_viewport = vis_value

            # restore scene units type
            context.scene.unit_settings.system = self.saved_unit_type

            # restore selection
            set_active_object(self.current_selection[0])
            for i in self.current_selection[1]:
                bpy.data.objects[i].select_set(True)

            bpy.context.evaluated_depsgraph_get().update()

            infolog("Export done")

            # WARNING

        x4ue_tools.X4UE_OT_popup_message.message = "Character exported"
        bpy.ops.x4ue.popup_message("INVOKE_DEFAULT")
        self.report({"INFO"}, "Character Exported")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


classes = (X4UE_OT_export_fbx, X4UE_OT_export_fbx_panel)


def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # properties
    bpy.types.Scene.x4ue_simplify_fac = bpy.props.FloatProperty(
        name="Simplify Factor",
        default=0.05,
        min=0.0,
        max=100,
        description="Simplify factor to compress the animation data size. Lower value = higher quality, higher file size",
    )

    bpy.types.Scene.x4ue_use_armature_deform_only = bpy.props.BoolProperty(
        name="Deform Armature Only",
        description="If True, export only deform (weight-painted) armature",
        default=False,
    )

    bpy.types.Scene.x4ue_global_scale = bpy.props.FloatProperty(
        name="Global Scale", default=1.0, description="Global scale applied"
    )
    bpy.types.Scene.x4ue_mesh_smooth_type = bpy.props.EnumProperty(
        name="Smoothing",
        items=(
            (
                "OFF",
                "Normals Only",
                "Export only normals intstead of writing edge or face smoothing data",
            ),
            ("FACE", "Face", "Write face smoothing"),
            ("EDGE", "Edge", "Write edge smoothing"),
        ),
        description="Export smoothing information (prefer 'Normal Only' option if your target importer understand split normals)",
        default="OFF",
    )
    bpy.types.Scene.x4ue_bone_axis_primary_export = bpy.props.EnumProperty(
        name="Primary Bone Axis",
        items=(
            ("X", "X Axis", ""),
            ("Y", "Y Axis", ""),
            ("Z", "Z Axis", ""),
            ("-X", "-X Axis", ""),
            ("-Y", "-Y Axis", ""),
            ("-Z", "-Z Axis", ""),
        ),
        default="Z",
    )
    bpy.types.Scene.x4ue_bone_axis_secondary_export = bpy.props.EnumProperty(
        name="Secondary Bone Axis",
        items=(
            ("X", "X Axis", ""),
            ("Y", "Y Axis", ""),
            ("Z", "Z Axis", ""),
            ("-X", "-X Axis", ""),
            ("-Y", "-Y Axis", ""),
            ("-Z", "-Z Axis", ""),
        ),
        default="X",
    )

    bpy.types.Scene.x4ue_mode_export_animations = bpy.props.EnumProperty(
        name="Export animation mode",
        items=(
            ("ALL", "All animation export", ""),
            ("SELECT", "Select export animation", ""),
            ("NOT", "No animation export (Armature only)", "")
        ),
        default="ALL"
    )


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.x4ue_simplify_fac
    del bpy.types.Scene.x4ue_global_scale
    del bpy.types.Scene.x4ue_mesh_smooth_type
    del bpy.types.Scene.x4ue_bone_axis_primary_export
    del bpy.types.Scene.x4ue_bone_axis_secondary_export
    del bpy.types.Scene.x4ue_mode_export_animations
