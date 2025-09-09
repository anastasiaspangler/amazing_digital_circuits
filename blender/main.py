#!/usr/bin/env python3
"""
Remote Blender Control - Main Script
====================================

This script demonstrates how to control Blender remotely via WebSocket.
Make sure Blender is running with the remote control addon installed and connected.

Usage:
    python3 main.py

Requirements:
    - Blender running with the remote control addon
    - WebSocket connection established (ws://127.0.0.1:8765)
"""

import time
from blender_session import BlenderSession


def main():
    """Main demonstration of remote Blender control."""
    print("Remote Blender Control Demo")
    print("=" * 40)
    glb_file = "examples/trash_can.glb"
    
    try:
        # Connect to Blender
        print("Connecting to Blender...")
        blender = BlenderSession("ws://127.0.0.1:8765")
        
        # Wait a moment for connection to stabilize
        time.sleep(1)
        
        print("\n1. Creating test objects...")
        blender.create_cube(0, 0, 0)
        time.sleep(0.5)
        blender.create_sphere(3, 0, 0)
        time.sleep(0.5)
        
        print("\n2. Adjusting camera...")
        blender.set_camera_position(5, -5, 3)
        blender.rotate_camera(1.1, 0, 0.785)
        time.sleep(0.5)
        
        print("\n3. Focusing on cube...")
        blender.focus_on("Cube")
        time.sleep(0.5)
        blender.focus_on("Sphere")
        time.sleep(0.5)
        blender.focus_on("Cube")
        
        print("\n4. Adjusting lighting...")
        blender.set_light_intensity("Light", 5.0)
        blender.set_light_color("Light", 1.0, 0.9, 0.8)
        time.sleep(0.5)
        
        print("\n5. Scaling objects...")
        blender.set_object_scale("Cube", 1.5)
        blender.set_object_scale("Sphere", 0.8)
        time.sleep(0.5)
        
        print("\n6. Rotating objects...")
        blender.set_object_rotation("Cube", 0, 0, 0.5)
        blender.set_object_rotation("Sphere", 0.3, 0, 0)
        time.sleep(0.5)
        
        print("\n7. Testing GLB import...")
        blender.add_glb(glb_file)
        time.sleep(1)
        
        print("\n8. Listing scene objects...")
        objects = blender.list_objects()
        
        print("\nDemo completed successfully!")
        print("Check your Blender viewport to see the changes.")
        
        # Keep connection alive for a moment
        time.sleep(2)
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. Blender is running")
        print("2. The remote control addon is installed and enabled")
        print("3. The WebSocket connection is established")
        print("4. The addon is connected to ws://127.0.0.1:8765")
    
    finally:
        try:
            blender.close()
            print("Connection closed.")
        except:
            pass


if __name__ == '__main__':
    main()
