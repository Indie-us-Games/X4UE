"""Minimal headless smoke test for the X4UE FBX exporter.

Run with Blender 4.2+: blender --background --python tests/blender_45_smoke.py
"""
import os
import sys
import tempfile

import bpy


REPOSITORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPOSITORY)

import x4ue


def main():
    x4ue.register()
    try:
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        bpy.ops.object.shade_smooth()

        mesh = cube.data
        mesh.uv_layers.new(name="UVMap")
        mesh.color_attributes.new(name="Color", type='FLOAT_COLOR', domain='CORNER')

        bpy.ops.object.armature_add(enter_editmode=True)
        armature = bpy.context.active_object
        armature.data.edit_bones[0].name = "root"
        bpy.ops.object.mode_set(mode='POSE')
        bone = armature.pose.bones["root"]
        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = (0.0, 0.0, 0.0)
        bone.keyframe_insert(data_path="rotation_euler", frame=1)
        bone.rotation_euler = (0.0, 0.0, 0.5)
        bone.keyframe_insert(data_path="rotation_euler", frame=10)
        bpy.ops.object.mode_set(mode='OBJECT')
        modifier = cube.modifiers.new(name="Armature", type='ARMATURE')
        modifier.object = armature
        cube.select_set(True)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature

        output = os.path.join(tempfile.gettempdir(), "x4ue_blender_45_smoke.fbx")
        result = bpy.ops.x4ue_export_scene.fbx(
            filepath=output,
            use_selection=True,
            use_tspace=True,
            bake_anim=True,
        )
        assert result == {'FINISHED'}, result
        assert os.path.isfile(output) and os.path.getsize(output) > 0
        with open(output, "rb") as exported:
            assert b"AnimationStack" in exported.read()
        os.remove(output)
    finally:
        x4ue.unregister()


if __name__ == "__main__":
    main()
