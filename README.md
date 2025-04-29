# Realize Array Instances

A Blender 4.4 Python script to convert Array modifier instances (using an animated Empty as Object Offset) into real, keyframed objects. This tool duplicates your active object for each element in the Array modifier, computes the correct world‑space transforms per frame, bakes the animation (location, rotation, scale), and cleans up the original.

## Installation

1. Open Blender and switch to the **Scripting** workspace.
2. Click **New** in the Text Editor panel.
3. Copy the contents of `realize_array_instances.py` into the editor.
4. Run script

## Usage

1. In the 3D Viewport, select the object that has the Array modifier you want to realize.
2. Ensure the Array modifier uses an Empty object for **Object Offset** and that the Empty has animation.
3. In the Text Editor, click **Run Script** (or press **Alt+P**).
4. The script will:
   - Duplicate the original object for each element in the array.
   - Remove the Array modifier from all duplicates.
   - Clear parenting to isolate world transforms.
   - Compute and bake keyframes (location, rotation, scale) from frame start to end.
   - Delete the original object.
5. After completion, you’ll have separate objects with baked keyframe data in your scene.


## Troubleshooting

- **All instances share the same transform**: Make sure your Array modifier’s **Object Offset** is set to a unique Empty and that the Empty is animated.
- **No Array modifier found**: Confirm you have the active object selected and that it has an Array modifier.
- **Script errors**: Check the system console for error messages (`Window → Toggle System Console`).
