import bpy
from mathutils import Matrix, Quaternion

# Blender 4.4 script to realize all instances of an Array modifier using an animated empty as Object Offset.
# This duplicates the object for each array element and bakes world-space transforms into keyframes,
# ensuring quaternion continuity to avoid flipping artifacts.

def realize_array_instances():
    context = bpy.context
    scene = context.scene
    original = context.active_object

    if not original:
        print("Error: No active object selected.")
        return

    # Find the Array modifier
    array_mod = next((m for m in original.modifiers if m.type == 'ARRAY'), None)
    if not array_mod:
        print("Error: Active object has no Array modifier.")
        return

    count = array_mod.count
    if count < 1:
        print("Error: Array count < 1.")
        return

    offset_obj = array_mod.offset_object
    if not offset_obj:
        print("Error: Array modifier has no Object Offset set.")
        return

    start, end = scene.frame_start, scene.frame_end

    # Precompute world matrices for each frame and instance
    mats = []  # mats[frame_index][instance_index]
    for frame in range(start, end + 1):
        scene.frame_set(frame)
        deps = context.evaluated_depsgraph_get()
        orig_eval = original.evaluated_get(deps)
        offset_eval = offset_obj.evaluated_get(deps)
        base_mat = orig_eval.matrix_world.copy()
        delta_mat = offset_eval.matrix_world @ base_mat.inverted()

        frame_mats = []
        for i in range(count):
            mat = base_mat.copy()
            for _ in range(i):
                mat = delta_mat @ mat
            frame_mats.append(mat)
        mats.append(frame_mats)

    # Duplicate and un-parent instances
    instances = []
    for _ in range(count):
        bpy.ops.object.select_all(action='DESELECT')
        original.select_set(True)
        context.view_layer.objects.active = original
        bpy.ops.object.duplicate()
        inst = context.view_layer.objects.active
        # Remove any Array modifiers
        for m in inst.modifiers:
            if m.type == 'ARRAY':
                inst.modifiers.remove(m)
        inst.parent = None
        inst.rotation_mode = 'QUATERNION'
        instances.append(inst)

    # Delete the original
    bpy.ops.object.select_all(action='DESELECT')
    original.select_set(True)
    bpy.ops.object.delete()

    # Bake transforms frame-by-frame, ensuring quaternion continuity
    prev_quats = [None] * count
    for frame_idx, frame in enumerate(range(start, end + 1)):
        for idx, inst in enumerate(instances):
            mat = mats[frame_idx][idx]
            loc, rot, scale = mat.decompose()  # returns (Vector, Quaternion, Vector)
            # Flip quaternion if needed for continuity
            if prev_quats[idx] and prev_quats[idx].dot(rot) < 0:
                rot = -rot
            prev_quats[idx] = rot.copy()

            # Assign transforms
            inst.location = loc
            inst.rotation_quaternion = rot
            inst.scale = scale
            # Insert keyframes
            inst.keyframe_insert(data_path="location", frame=frame)
            inst.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            inst.keyframe_insert(data_path="scale", frame=frame)

    print(f"Realized {count} instances with baked quaternion animation and continuity.")

if __name__ == "__main__":
    realize_array_instances()
