import bpy

from .x4ue_log import (
    debuglog, infolog, warnlog, errorlog
)

from .x4ue_utils import (
    # Constants
    X4UE_OBJ_SUFFIX, X4UE_OBJ_WORK_SUFFIX, X4UE_DUMMY_MESH_NAME,
    # Functions
    is_object_hidden,
    set_active_object, unhide_object,
    is_mesh, is_armature, is_emptyobject,
    get_object_relation_depth
)


def create_copy_objects(armature_name, no_armature_mode=False):

    debuglog("Begin create copies")

    copy_armature_name = armature_name + X4UE_OBJ_SUFFIX

    list_stored_actions = [action.name for action in bpy.data.actions]
    if no_armature_mode:
        list_char_objects = [obj.name for obj in bpy.context.selected_objects]
    else:
        list_char_objects = get_char_objects(armature_name)

    list_copy_objects = []

    set_active_object(armature_name)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    debuglog("Duplicate objects.", "Target:", list_char_objects)
    for obj_name in list_char_objects:
        unhide_object(bpy.data.objects[obj_name])
        selectable_state = bpy.data.objects[obj_name].hide_select
        bpy.data.objects[obj_name].hide_select = False

        bpy.context.evaluated_depsgraph_get().update()
        set_active_object(obj_name)

        bpy.ops.object.mode_set(mode="OBJECT")

        # Duplicate and rename
        current_obj_in_scene = [o.name for o in bpy.data.objects]
        bpy.ops.object.duplicate(linked=False, mode="TRANSLATION")

        for o in bpy.data.objects:
            if o.name not in current_obj_in_scene:
                unhide_object(o)
                set_active_object(o.name)

        # Set duplicated object name
        copy_object_name = obj_name + X4UE_OBJ_SUFFIX

        bpy.context.active_object.name = copy_object_name
        debuglog("Duplicated object name:", copy_object_name)

        bpy.ops.object.select_all(action="DESELECT")

        # Restore selectable state
        bpy.data.objects[obj_name].hide_select = selectable_state

        # add to list
        list_copy_objects.append(copy_object_name)

    if no_armature_mode:
        # Reparent duplicate objects
        for obj_name in list_copy_objects:
            copy_obj = bpy.data.objects[obj_name]
            if copy_obj.parent is not None:
                reparent_name = copy_obj.parent.name + X4UE_OBJ_SUFFIX
                debuglog("Reparent mesh to duplicated mesh.",
                         obj_name, "->", reparent_name)
                copy_obj_mat = copy_obj.matrix_world.copy()
                copy_obj.parent = bpy.data.objects[reparent_name]
                copy_obj.matrix_world = copy_obj_mat

    else:
        # Reparent meshes to armature
        for obj_name in list_copy_objects:
            copy_obj = bpy.data.objects[obj_name]
            if is_mesh(copy_obj):
                debuglog("Reparent mesh to armature.",
                         obj_name, "->", copy_armature_name)
                copy_obj_mat = copy_obj.matrix_world.copy()
                copy_obj.parent = bpy.data.objects[copy_armature_name]
                copy_obj.matrix_world = copy_obj_mat

        # Reset armature target object
        for obj_name in list_copy_objects:
            copy_obj = bpy.data.objects[obj_name]
            if is_mesh(copy_obj):
                if len(copy_obj.modifiers) > 0:
                    for mod in copy_obj.modifiers:
                        if is_armature(mod):
                            if mod.object is not None:
                                if mod.object.name == armature_name:
                                    mod.object = bpy.data.objects[copy_armature_name]

    for action in bpy.data.actions:
        if not action.name in list_stored_actions:
            debuglog("Remove duplicated action:", action.name)
            bpy.data.actions.remove(action, do_unlink=True)

    return list_copy_objects


def delete_copy_objects(list_target_objects):
    arm_data = None
    for obj_name in list_target_objects:
        obj = bpy.data.objects[obj_name]

        if is_armature(obj):
            arm_data = bpy.data.armatures.get(obj.data.name)

        debuglog("Remove object:", obj.name)
        bpy.data.objects.remove(obj, do_unlink=True)

        try:
            debuglog("Remove armature:", arm_data.name)
            bpy.data.armatures.remove(arm_data, do_unlink=True)
        except:
            pass

    for mesh in bpy.data.meshes:
        if X4UE_DUMMY_MESH_NAME in mesh.name:
            debuglog("Remove dummy mesh:", mesh.name)
            bpy.data.meshes.remove(mesh, do_unlink=True)


def rename_objects_for_export(list_target_objects):

    debuglog("Targets:", list_target_objects)

    for obj_name in list_target_objects:
        origin_obj_name = obj_name.replace(X4UE_OBJ_SUFFIX, "")
        if bpy.data.objects.get(origin_obj_name):
            debuglog("Rename exists object:", origin_obj_name,
                     "->", origin_obj_name + X4UE_OBJ_WORK_SUFFIX)
            bpy.data.objects[origin_obj_name].name = origin_obj_name + \
                X4UE_OBJ_WORK_SUFFIX

            debuglog("Rename target object:", obj_name, "->", origin_obj_name)
            bpy.data.objects[obj_name].name = origin_obj_name


def revert_object_name(list_target_objects):

    for obj_name in list_target_objects:
        origin_obj_name = obj_name.replace(X4UE_OBJ_SUFFIX, "")
        base_obj_name = origin_obj_name + X4UE_OBJ_WORK_SUFFIX

        if bpy.data.objects.get(origin_obj_name):
            debuglog("Revert target object:", origin_obj_name, "->", obj_name)
            bpy.data.objects[origin_obj_name].name = obj_name

        if bpy.data.objects.get(base_obj_name):
            debuglog("Revert origin object:",
                     base_obj_name, "->", origin_obj_name)
            bpy.data.objects[base_obj_name].name = origin_obj_name


def get_char_objects(armature_name):

    list_char_objects = []

    # Append armature
    debuglog("Add armature object:", armature_name)
    list_char_objects.append(armature_name)

    for obj in bpy.data.objects:

        debuglog("object:", obj.name)

        if is_mesh(obj) and not is_object_hidden(obj):
            debuglog("check target:", obj.name)
            # if obj.parent:
            #     debuglog("object has parent", obj.name)
            #     if obj.parent.name == armature_name and obj.parent_type == "BONE":
            #         if obj.parent_bone != "":
            #             debuglog("Add char object:", obj.name)
            #             list_char_objects.append(obj.name)

            if len(obj.modifiers) > 0:
                debuglog("check object modifiers. obj:", obj.name,
                         ", mod_count:", len(obj.modifiers))
                for mod in obj.modifiers:
                    if is_armature(mod) and mod.show_viewport:
                        if mod.object is not None:
                            if mod.object.name == armature_name:
                                debuglog(
                                    "Add armature_target object:", obj.name)
                                list_char_objects.append(obj.name)
                                break

    if len(list_char_objects) == 1:
        infolog("Create dummy mesh")
        dummy_obj = _create_dummy_mesh()
        new_mod = dummy_obj.modifiers.new(type="ARMATURE", name="rig")
        new_mod.object = bpy.data.objects[armature_name]
        list_char_objects.append(dummy_obj.name)

    debuglog("list_char_objects:", list_char_objects)

    return list_char_objects


def _create_dummy_mesh(name=X4UE_DUMMY_MESH_NAME):
    debuglog("Create dummy mesh")
    # Create dummy mesh
    dummy_mesh = bpy.data.meshes.new(name)
    dummy_obj = bpy.data.objects.new(name, dummy_mesh)
    # Link to collection
    bpy.context.scene.collection.objects.link(dummy_obj)

    return dummy_obj


def set_scale_x100(armature_name):
    scene = bpy.context.scene

    rig_arm = bpy.data.objects[armature_name + X4UE_OBJ_SUFFIX]

    meshes = []

    for obj in bpy.data.objects:
        if is_mesh(obj):
            if len(obj.modifiers) > 0:
                for mod in obj.modifiers:
                    if is_armature(mod):
                        if mod.object == rig_arm:
                            debuglog("Add target mesh.", obj.name)
                            meshes.append(obj)

    debuglog("Begin modifire scale. target=", rig_arm.name)

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    set_active_object(rig_arm.name)
    rig_arm.scale *= 100
    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )
    bpy.context.evaluated_depsgraph_get().update()

    rig_arm.scale *= 0.01
    bpy.ops.object.select_all(action="DESELECT")

    debuglog("Armature scale:", rig_arm.scale)

    for mesh in meshes:
        set_active_object(mesh.name)

    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )
    bpy.context.evaluated_depsgraph_get().update()

    bpy.ops.object.select_all(action="DESELECT")

    debuglog("Armature:", rig_arm.name)
    debuglog("Meshes:", [m.name for m in meshes])

    infolog("Mesh scale applied")


def set_scale_x100_no_armature(target_meshes):

    relation = []

    # FIX: create relation list
    for mesh in target_meshes:
        mesh_obj = bpy.data.objects[mesh]
        relation.append({
            "name": mesh_obj.name,
            "parent_name": mesh_obj.parent.name if mesh_obj.parent is not None else "",
            "depth": get_object_relation_depth(mesh_obj)
        })

    for mesh in [x["name"] for x in sorted(relation, key=lambda i: i["depth"], reverse=True)]:
        mesh_obj = bpy.data.objects[mesh]

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")

        debuglog("Modify mesh scale:", mesh_obj.name)
        set_active_object(mesh_obj.name)
        # to x100
        mesh_obj.scale *= 100
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True
        )

        mesh_obj.scale *= 0.01
        bpy.context.evaluated_depsgraph_get().update()

        debuglog("Mesh:", mesh_obj.name, ", Scale:", mesh_obj.scale)

    infolog("Mesh scale applied")


def set_action_scale_x100(list_target_actions):
    for action_name in list_target_actions:
        debuglog("Set action x100 scale. action_name:", action_name)
        action = bpy.data.actions[action_name]
        for fcurve in action.fcurves:
            if 'location' in fcurve.data_path:
                for point in fcurve.keyframe_points:
                    point.co[1] *= 100
                    point.handle_left[1] *= 100
                    point.handle_right[1] *= 100


def revert_action_scale_x100(list_target_actions):
    for action_name in list_target_actions:
        debuglog("Revert action x100 scale. action_name:", action_name)
        action = bpy.data.actions[action_name]
        for fcurve in action.fcurves:
            if 'location' in fcurve.data_path:
                for point in fcurve.keyframe_points:
                    point.co[1] *= 0.01
                    point.handle_left[1] *= 0.01
                    point.handle_right[1] *= 0.01


def revert_scale_x100(armature_name):
    """ Revert armature scales """

    rig_arm = bpy.data.objects[armature_name + X4UE_OBJ_SUFFIX]

    meshes = []

    for obj in bpy.data.objects:
        if is_mesh(obj):
            if len(obj.modifiers) > 0:
                for mod in obj.modifiers:
                    if mod.type == "ARMATURE":
                        if mod.object == rig_arm:
                            meshes.append(obj)

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    set_active_object(rig_arm.name)
    rig_arm.scale *= 100

    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )

    bpy.ops.object.select_all(action="DESELECT")

    for mesh in meshes:
        set_active_object(mesh.name)
        mesh.scale *= 0.01

    bpy.ops.object.transform_apply(
        location=False, rotation=False, scale=True
    )

    bpy.ops.object.select_all(action="DESELECT")

    # TODO revert animation curves
