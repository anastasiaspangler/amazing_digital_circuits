import sys, subprocess, ensurepip

ensurepip.bootstrap()
subprocess.check_call([sys.executable, "-m", "pip", "install", "websocket-client"])

# !/usr/bin/env python3
"""
Safe Blender script to set up a test scene WITHOUT deleting the camera
Run this in Blender's Scripting workspace
"""

import bpy

def create_test_scene_safe():
    """Create a test scene with objects but keep the default camera"""

    # Add a cube at the origin
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    # Add a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 0))
    sphere = bpy.context.active_object
    sphere.name = "TestSphere"

    # Get the default camera and position it to look at the scene
    camera = bpy.data.objects.get("Camera")
    if camera:
        camera.location = (5, -5, 3)
        camera.rotation_euler = (1.1, 0, 0.785)  # Look at origin
        print(f"Camera positioned at {camera.location}")
    else:
        # If no camera exists, create one
        bpy.ops.object.camera_add(location=(5, -5, 3))
        camera = bpy.context.active_object
        camera.rotation_euler = (1.1, 0, 0.785)
        print("New camera created and positioned")

    # Add some lighting
    bpy.ops.object.light_add(type='SUN', location=(2, 2, 5))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3

    # Set camera as active camera
    bpy.context.scene.camera = camera

    # Set viewport to camera view
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    break

    print("Test scene created!")
    print("Camera positioned to look at cube and sphere")
    print("Now connect the WebSocket addon and test remote control!")


if __name__ == "__main__":
    create_test_scene_safe()
