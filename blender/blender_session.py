"""
Bare-bones Blender Remote Control
=================================

Ultra-simple Blender control via WebSocket.
No error checking, no robustness - just the essentials.
"""

import json
from typing import List, Dict, Any
import websocket._core as websocket


class BlenderSession:
    """Simple Blender remote control session."""

    def __init__(self, blender_url: str = "ws://127.0.0.1:8765"):
        """Initialize connection to Blender."""
        self.url = blender_url
        self.ws = None
        self.connected = False
        self._connect()

    def _connect(self):
        """Connect to Blender WebSocket."""
        print(f"Connecting to Blender at {self.url}")
        try:
            self.ws = websocket.create_connection(self.url, timeout=5)
            self.connected = True
            print("Connected to Blender")
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.connected = False
            raise

    def _send(self, data: Dict[str, Any]):
        """Send JSON data to Blender."""
        if not self.connected:
            self._connect()
        message = json.dumps(data)
        self.ws.send(message)
        print(f"Sent: {message}")

    def _set_property(self, target: str, data_path: str, value: Any, index: int = -1):
        """Set Blender object property directly."""
        self._send({
            "type": "set_property",
            "target": target,
            "data_path": data_path,
            "value": value,
            "index": index
        })

    # Camera Controls
    def rotate_camera(self, x: float = 0, y: float = 0, z: float = 0):
        """Set camera rotation directly."""
        if x != 0:
            self._set_property("Camera", "rotation_euler", x, 0)
        if y != 0:
            self._set_property("Camera", "rotation_euler", y, 1)
        if z != 0:
            self._set_property("Camera", "rotation_euler", z, 2)
        print(f"Camera rotation set to ({x}, {y}, {z})")

    def focus_on(self, object_name: str):
        """Focus camera on specific object."""
        self._send({
            "type": "focus_on",
            "target": object_name
        })
        print(f"Camera focusing on: {object_name}")

    def set_camera_position(self, x: float, y: float, z: float):
        """Set camera position directly."""
        self._set_property("Camera", "location", [x, y, z])
        print(f"Camera position set to ({x}, {y}, {z})")

    def set_camera_zoom(self, distance: float):
        """Set camera distance from origin."""
        self._set_property("Camera", "location", distance, 2)
        print(f"Camera zoom set to {distance}")

    # Object Controls
    def list_objects(self) -> List[str]:
        """List all objects in scene."""
        self._send({"type": "list_objects"})
        objects = ["Cube", "Sphere", "Camera", "Light"]  # Placeholder
        print(f"Scene objects: {objects}")
        return objects

    def create_cube(self, x: float = 0, y: float = 0, z: float = 0):
        """Create a cube at specified position."""
        self._send({
            "type": "create_object",
            "object_type": "cube",
            "location": [x, y, z]
        })
        print(f"Creating cube at ({x}, {y}, {z})")

    def create_sphere(self, x: float = 0, y: float = 0, z: float = 0):
        """Create a sphere at specified position."""
        self._send({
            "type": "create_object",
            "object_type": "sphere",
            "location": [x, y, z]
        })
        print(f"Creating sphere at ({x}, {y}, {z})")

    def add_glb(self, filename: str):
        """Import GLB file into the scene."""
        self._send({
            "type": "import_glb",
            "filename": filename
        })
        print(f"Importing GLB file: {filename}")

    def set_object_scale(self, object_name: str, scale: float):
        """Set object scale directly."""
        self._set_property(object_name, "scale", [scale, scale, scale])
        print(f"{object_name} scale set to {scale}")

    def set_object_rotation(self, object_name: str, x: float = 0, y: float = 0, z: float = 0):
        """Set object rotation directly."""
        if x != 0 or y != 0 or z != 0:
            self._set_property(object_name, "rotation_euler", [x, y, z])
            print(f"{object_name} rotation set to ({x}, {y}, {z})")

    def set_object_position(self, object_name: str, x: float, y: float, z: float):
        """Set object position directly."""
        self._set_property(object_name, "location", [x, y, z])
        print(f"{object_name} position set to ({x}, {y}, {z})")

    # Lighting Controls
    def set_light_intensity(self, light_name: str, intensity: float):
        """Set light intensity directly."""
        self._set_property(light_name, "data.energy", intensity)
        print(f"{light_name} intensity set to {intensity}")

    def set_light_color(self, light_name: str, r: float, g: float, b: float):
        """Set light color directly."""
        self._set_property(light_name, "data.color", [r, g, b])
        print(f"{light_name} color set to ({r}, {g}, {b})")

    def set_light_position(self, light_name: str, x: float, y: float, z: float):
        """Set light position directly."""
        self._set_property(light_name, "location", [x, y, z])
        print(f"{light_name} position set to ({x}, {y}, {z})")

    def close(self):
        """Close connection to Blender."""
        if self.ws:
            self.ws.close()
            self.connected = False
            print("Disconnected from Blender")
