import bpy
from math import tau  # 2*pi

def spin_object(obj_name, axis='Z', frames=120, start=1, loop=True):
  obj = bpy.data.objects.get(obj_name)
  if obj is None:
    raise ValueError(f"Object '{obj_name}' not found")

  # reset and keyframe start
  obj.rotation_euler = (0.0, 0.0, 0.0)
  obj.keyframe_insert(data_path="rotation_euler", frame=start)

  # set end rotation
  rot = [0.0, 0.0, 0.0]
  idx = {'X':0, 'Y':1, 'Z':2}[axis.upper()]
  rot[idx] = tau
  obj.rotation_euler = rot
  obj.keyframe_insert(data_path="rotation_euler", frame=start+frames)

  # ensure animation data exists
  obj.animation_data_create()
  act = obj.animation_data.action
  if act is None:
    act = bpy.data.actions.new(name=f"{obj.name}_Spin")
    obj.animation_data.action = act

  # set extrapolation on the object's rotation curves
  for fc in act.fcurves:
    if fc.data_path == "rotation_euler":
      fc.extrapolation = 'LINEAR' if loop else 'CONSTANT'

  # optional: set scene range
  bpy.context.scene.frame_start = start
  bpy.context.scene.frame_end = start + frames


def spin_via_parent(obj_name, axis='Z', frames=120, start=1, loop=True):
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError(f"Object '{obj_name}' not found")

    # make or reuse a parent empty
    parent_name = f"{obj.name}_SpinEmpty"
    empty = bpy.data.objects.get(parent_name)
    if not empty:
        empty = bpy.data.objects.new(parent_name, None)
        bpy.context.scene.collection.objects.link(empty)
        empty.location = obj.matrix_world.translation

    # parent without moving
    obj.parent = empty
    obj.matrix_parent_inverse = empty.matrix_world.inverted()

    # keyframe the empty
    empty.animation_data_clear()
    empty.rotation_euler = (0,0,0)
    empty.keyframe_insert("rotation_euler", frame=start)

    idx = {'X':0,'Y':1,'Z':2}[axis.upper()]
    rot = list(empty.rotation_euler)
    rot[idx] += tau
    empty.rotation_euler = rot
    empty.keyframe_insert("rotation_euler", frame=start+frames)

    # loop
    empty.animation_data_create()
    act = empty.animation_data.action
    for fc in act.fcurves:
        if fc.data_path == "rotation_euler":
            fc.extrapolation = 'LINEAR' if loop else 'CONSTANT'



