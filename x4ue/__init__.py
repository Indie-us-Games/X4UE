bl_info = {
    "name": "X4UE: Exporter for Unreal Engine",
    "author": "T_Sumisaki",
    "version": (0, 1, 8),
    "blender": (4, 2, 0),
    "location": "File > Import-Export",
    "description": "Custom FBX exporter and tools for UnrealEngine",
    "category": "Import-Export",
    "warning": "This plugin is alpha development version."
}


import bpy
from x4ue import x4ue_export, x4ue_log, x4ue_funcs, x4ue_utils, x4ue_prefs, x4ue_tools
from x4ue.fbx_export import x4ue_fbx_init

if "bpy" in locals():
    import importlib
    if "x4ue_export" in locals():
        importlib.reload(x4ue_export)
    if "x4ue_fbx_init" in locals():
        importlib.reload(x4ue_fbx_init)
    if "x4ue_log" in locals():
        importlib.reload(x4ue_log)
    if "x4ue_funcs" in locals():
        importlib.reload(x4ue_funcs)
    if "x4ue_utils" in locals():
        importlib.reload(x4ue_utils)
    if "x4ue_tools" in locals():
        importlib.reload(x4ue_tools)
    if "x4ue_prefs" in locals():
        importlib.reload(x4ue_prefs)



# Export Menu
def menu_func_export(self, context):
    self.layout.operator(
        x4ue_export.X4UE_OT_export_fbx_panel.bl_idname,
        text="FBX for UE (.fbx)"
    )	


def register():
    x4ue_prefs.register()
    x4ue_export.register()
    x4ue_fbx_init.register()
    x4ue_tools.register()
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    x4ue_prefs.unregister()
    x4ue_export.unregister()
    x4ue_fbx_init.unregister()
    x4ue_tools.unregister()
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
