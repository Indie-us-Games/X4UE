import bpy

# Constants
X4UE_OBJ_SUFFIX = "_ue4export"
X4UE_OBJ_WORK_SUFFIX = "_ue4baseobject"
X4UE_DUMMY_MESH_NAME = "x4ue_dummy_mesh"

# Utility functions


def select_objects(*object_names):
    # Reset all selection
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    for obj_name in object_names:
        set_active_object(obj_name)


def set_active_object(object_name):
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]
    bpy.data.objects[object_name].select_set(state=True)


def unhide_object(obj):
    obj.hide_set(False)
    obj.hide_viewport = False

def hide_object(obj):
    obj.hide_set(True)
    obj.hide_viewport = True

def hide_object_visual(obj):
    obj.hide_set(True)

def is_object_hidden(obj):
    try:
        if not obj.hide_get() and not obj.hide_viewport:
            return False
        else:
            return True
    except:
        return True


def is_mesh(obj):
    return obj is not None and obj.type == "MESH"


def is_armature(obj):
    return obj is not None and obj.type == "ARMATURE"
