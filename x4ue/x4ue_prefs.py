import bpy



class X4UE_MT_addon_preferences(bpy.types.AddonPreferences):

    bl_idname = __package__

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene, "x4ue_log_level")
    

def register():
    
    bpy.utils.register_class(X4UE_MT_addon_preferences)

    bpy.types.Scene.x4ue_log_level = bpy.props.EnumProperty(
        name="Log Level",
        items=(
            ("ALL", "All", "Print All level logs"),
            ("INFO", "Info", "Print INFO level logs"),
            ("WARN", "Warn/Error", "Print Warning and Error logs"),
        ),
        default="ALL"
    )

def unregister():

    bpy.utils.unregister_class(X4UE_MT_addon_preferences)

    del bpy.types.Scene.x4ue_log_level