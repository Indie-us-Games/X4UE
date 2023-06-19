import bpy

from . import x4ue_log, x4ue_utils

if "bpy" in locals():
    import importlib

    if "x4ue_log" in locals():
        importlib.reload(x4ue_log)
    if "x4ue_utils" in locals():
        importlib.reload(x4ue_utils)

from .x4ue_log import debuglog, infolog, warnlog, errorlog

from .x4ue_utils import set_active_object, is_mesh, is_armature


class X4UE_OT_delete_action(bpy.types.Operator):
    """ Delete selected action """

    bl_idname = "x4ue.delete_action"
    bl_label = "The action will be permanently removed from the scene, ok?"
    bl_options = {"UNDO"}

    action_name: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):

        if not self.action_name:
            warnlog("Delete action name is not defined")
            self.report({"ERROR"}, "Delete action name is not defined")
            return {"FINISHED"}

        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:

            if bpy.data.actions.get(self.action_name):
                bpy.data.actions.remove(bpy.data.actions[self.action_name])
                infolog("Delete action:", self.action_name)
                self.report({"INFO"}, "Action [" + self.action_name + "] deleted")

        finally:
            context.preferences.edit.use_global_undo = use_global_undo

        return {"FINISHED"}


class X4UE_PT_delete_action_panel(bpy.types.Panel):
    """ Delete selected action panel """

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "X4UE Tools"
    bl_label = "Delete Action (Experimental)"
    bl_idname = "X4UE_PT_delete_action"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Action list:")

        col = layout.column(align=True)

        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                debuglog("Find action:", action.name)
                _row = col.row(align=True)
                _row.label(text=action.name)
                _op = _row.operator("x4ue.delete_action", text="", icon="X")
                _op.action_name = action.name
        else:
            _row = col.row(align=True)
            _row.label(text="No actions")


class X4UE_OT_unbind_armature(bpy.types.Operator):
    """ Unbind armature """

    bl_idname = "x4ue.unbind_armature"
    bl_label = "Unbind armature, and remove armature mod and vertex groups. Ok?"
    bl_options = {"UNDO"}

    target_armature_name: bpy.props.StringProperty(default="")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):

        if not self.target_armature_name:
            warnlog("Not found target armature")
            self.report({"ERROR"}, "Require set target armature")
            return {"FINISHED"}

        arm_obj = bpy.data.objects[self.target_armature_name]

        if not is_armature(arm_obj):
            warnlog("Target object is not armature, name:", self.target_armature_name)
            self.report({"ERROR"}, "Target object is not ARMATURE")
            return {"FINISHED"}

        for obj in bpy.data.objects:
            if obj.parent == arm_obj and is_mesh(obj):
                debuglog("Find target mesh:", obj.name)

                debuglog("Remove armature modifiers")
                if len(obj.modifiers) > 0:
                    for mod in obj.modifiers:
                        if is_armature(mod):
                            if (
                                mod.object is not None
                                and mod.object.name == self.target_armature_name
                            ):
                                debuglog("Find armature mod, removed. name:", mod.name)
                                obj.modifiers.remove(mod)

                debuglog("Remove all vertex groups")
                obj.vertex_groups.clear()

                debuglog("Unparent object fromm armature")
                obj.parent = None

        self.report({"INFO"}, "Unbind armature. Armature=" + self.target_armature_name)

        return {"FINISHED"}


class X4UE_PT_unbind_armature_panel(bpy.types.Panel):
    """ Unbind armature operation panel """

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "X4UE Tools"
    bl_label = "Unbind Armature (Experimental)"
    bl_idname = "X4UE_PT_unbind_armature"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text="Unbind Armature")

        col = layout.column(align=True)

        target_armature_name = ""
        print("Redraw")

        for obj in bpy.context.selected_objects:
            if is_armature(obj):
                target_armature_name = obj.name
                break

        if target_armature_name:
            _op = col.operator("x4ue.unbind_armature", text="Unbind Armature", icon="X")
            _op.target_armature_name = target_armature_name
        else:
            col.label(text="Select target armature")


class X4UE_OT_popup_message(bpy.types.Operator):
    """ Message popup window """

    bl_label = "FBX Exporter for UE"
    bl_idname = "x4ue.popup_message"

    message = ""
    icon_type = "INFO"

    def draw(self, context):

        layout = self.layout
        message_lines = self.message.split("\n")

        for i, line in enumerate(message_lines):
            if i == 0:
                layout.label(text=line, icon=self.icon_type)
            else:
                layout.label(text=line)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


class X4UE_OT_select_action(bpy.types.Operator):

    """ select action """

    bl_idname = "x4ue.select_action"
    bl_label = "Select action"
    bl_options = {"UNDO"}

    action_name: bpy.props.StringProperty(default="")

    def execute(self, context):

        use_global_undo = context.preferences.edit.use_global_undo
        context.preferences.edit.use_global_undo = False
        try:
            if self.action_name != "":
                act = bpy.data.actions.get(self.action_name)
                if act:
                    found = False
                    if len(act.keys()) > 0:
                        if "x4ue_export" in act.keys():
                            act["x4ue_export"] = not act["x4ue_export"]
                            found = True
                    if not found:
                        act["x4ue_export"] = False
        finally:
            context.preferences.edit.use_global_undo = use_global_undo 

        return {"FINISHED"}


classes = (
    X4UE_OT_delete_action,
    X4UE_PT_delete_action_panel,
    X4UE_OT_unbind_armature,
    X4UE_PT_unbind_armature_panel,
    X4UE_OT_popup_message,
    X4UE_OT_select_action,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
