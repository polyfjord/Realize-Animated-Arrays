import bpy
from mathutils import Matrix

# Blender 4.4 script to realize all instances of an Array modifier using an animated empty as Object Offset.
# This duplicates the object for each array element and bakes world-space transforms into keyframes.

def realize_array_instances():
    context = bpy.context
    scene = context.scene
    original = context.active_object

    if original is None:
        print("Error: No active object selected.")
        return

    # Find the Array modifier
    array_mod = next((m for m in original.modifiers if m.type == 'ARRAY'), None)
    if array_mod is None:
        print("Error: Active object has no Array modifier.")
        return

    count = array_mod.count
    if count < 1:
        print("Error: Array count < 1.")
        return

    offset_obj = array_mod.offset_object
    if offset_obj is None:
        print("Error: Array modifier has no Object Offset set.")
        return

    start = scene.frame_start
    end = scene.frame_end

    # Precompute matrices for each frame and each instance index
    mats = []  # mats[frame_index][instance_index]
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        deps = context.evaluated_depsgraph_get()
        orig_eval = original.evaluated_get(deps)
        offset_eval = offset_obj.evaluated_get(deps)
        orig_mat = orig_eval.matrix_world.copy()
        # Compute offset transform relative to original
        offset_mat = (offset_eval.matrix_world @ orig_mat.inverted()).copy()

        frame_mats = []
        for i in range(count):
            mat = orig_mat.copy()
            for _ in range(i):
                mat = offset_mat @ mat
            frame_mats.append(mat)
        mats.append(frame_mats)

    # Duplicate original into separate instances
    instances = []
    for i in range(count):
        bpy.ops.object.select_all(action='DESELECT')
        original.select_set(True)
        context.view_layer.objects.active = original
        bpy.ops.object.duplicate()
        inst = context.view_layer.objects.active
        # Remove any Array modifiers from the duplicate
        for m in [m for m in inst.modifiers if m.type == 'ARRAY']:
            inst.modifiers.remove(m)
        # Clear parenting to bake world transforms
        inst.parent = None
        instances.append(inst)

    # Delete the original
    bpy.ops.object.select_all(action='DESELECT')
    original.select_set(True)
    bpy.ops.object.delete()

    # Bake keyframes per instance
    for idx, inst in enumerate(instances):
        inst.rotation_mode = 'XYZ'
        for frame_idx, frame in enumerate(range(start, end + 1)):
            inst.matrix_world = mats[frame_idx][idx]
            inst.keyframe_insert(data_path="location", frame=frame)
            inst.keyframe_insert(data_path="rotation_euler", frame=frame)
            inst.keyframe_insert(data_path="scale", frame=frame)

    print(f"Realized {count} instances with baked animation.")

if __name__ == "__main__":
    realize_array_instances()
