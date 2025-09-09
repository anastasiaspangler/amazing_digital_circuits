bl_info = {
    "name": "Blender Remote Control",
    "author": "Remote Control Library",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "3D Viewport > N-panel > Remote Control",
    "description": "Receive JSON over WebSocket to control Blender objects directly.",
    "category": "System",
}

import bpy
import json
import math
import threading
import queue
import time
import os

# External lib
try:
    import websocket  # from websocket-client
    import socket
    import threading
    import base64
    import hashlib
except Exception as e:
    raise RuntimeError("Please install 'websocket-client' inside Blender's Python.") from e

# --- Runtime ---
_WS_THREAD = None
_WS_RUNNING = False
_WS_RX = queue.Queue()
_WS_TX = queue.Queue()


def _set_property(target_name: str, data_path: str, value, index: int = -1):
    """Set Blender object property directly."""
    obj = bpy.data.objects.get(target_name)
    if obj is None:
        print(f"Object '{target_name}' not found")
        return False

    # Resolve the property owner (object vs object.data)
    owner = obj
    if data_path.startswith("data."):
        if not hasattr(obj, "data") or obj.data is None:
            print(f"Object '{target_name}' has no data")
            return False
        owner = obj.data
        dp = data_path[len("data."):]
    else:
        dp = data_path

    # Get/set the property
    try:
        if index == -1:
            setattr(owner, dp, value)
        else:
            # vector-like property
            prop = getattr(owner, dp)
            tmp = list(prop)
            if index < 0 or index >= len(tmp):
                print(f"Index {index} out of range for property {dp}")
                return False
            tmp[index] = value
            setattr(owner, dp, tmp)
        print(f"Set {target_name}.{dp} = {value}")
        return True
    except Exception as e:
        print(f"Failed to set property: {e}")
        return False


def _create_object(object_type: str, location: list):
    """Create a new object in the scene."""
    try:
        if object_type == "cube":
            bpy.ops.mesh.primitive_cube_add(location=location)
        elif object_type == "sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(location=location)
        else:
            print(f"Unknown object type: {object_type}")
            return False
        print(f"Created {object_type} at {location}")
        return True
    except Exception as e:
        print(f"Failed to create object: {e}")
        return False


def _import_glb(filename: str):
    """Import GLB file into the scene."""
    try:
        # Check if file exists
        if not os.path.exists(filename):
            print(f"GLB file not found: {filename}")
            return False

        # Import GLB file
        bpy.ops.import_scene.gltf(filepath=filename)
        print(f"Imported GLB file: {filename}")
        return True
    except Exception as e:
        print(f"Failed to import GLB: {e}")
        return False


def _focus_on(target_name: str):
    """Focus camera on specific object."""
    try:
        obj = bpy.data.objects.get(target_name)
        if obj is None:
            print(f"Object '{target_name}' not found")
            return False

        camera = bpy.data.objects.get("Camera")
        if camera is None:
            print("No camera found in scene")
            return False

        # Simple focus: point camera at object
        direction = obj.location - camera.location
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        print(f"Camera focused on {target_name}")
        return True
    except Exception as e:
        print(f"Failed to focus camera: {e}")
        return False


def _list_objects():
    """List all objects in the scene."""
    objects = [obj.name for obj in bpy.data.objects]
    print(f"Scene objects: {objects}")
    return objects


def _timer_step():
    global _WS_RUNNING
    if not _WS_RUNNING:
        return None

    drained = 0
    try:
        while True:
            msg = _WS_RX.get_nowait()
            drained += 1
            try:
                data = json.loads(msg)
            except Exception:
                continue

            msg_type = data.get("type")

            if msg_type == "set_property":
                target = data.get("target")
                data_path = data.get("data_path")
                value = data.get("value")
                index = data.get("index", -1)
                _set_property(target, data_path, value, index)

            elif msg_type == "create_object":
                object_type = data.get("object_type")
                location = data.get("location", [0, 0, 0])
                _create_object(object_type, location)

            elif msg_type == "import_glb":
                filename = data.get("filename")
                _import_glb(filename)

            elif msg_type == "focus_on":
                target = data.get("target")
                _focus_on(target)

            elif msg_type == "list_objects":
                _list_objects()

            elif msg_type == "ping":
                _WS_TX.put(json.dumps({"type": "pong", "ok": True}))

            else:
                print(f"Unknown message type: {msg_type}")

    except queue.Empty:
        pass

    # Send any queued outbound messages back to client
    if _WS_THREAD and _WS_THREAD.client_socket:
        try:
            while True:
                out = _WS_TX.get_nowait()
                _WS_THREAD._websocket_send(_WS_THREAD.client_socket, out)
        except queue.Empty:
            pass

    return 1 / 60 if drained > 0 else 0.05


class _WSServerThread(threading.Thread):
    def __init__(self, port: int):
        super().__init__(daemon=True)
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()
        try:
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
        except Exception:
            pass

    def _websocket_handshake(self, client_socket):
        """Perform WebSocket handshake."""
        request = client_socket.recv(1024).decode('utf-8')
        if 'Sec-WebSocket-Key:' in request:
            key_line = [line for line in request.split('\r\n') if 'Sec-WebSocket-Key:' in line][0]
            key = key_line.split(': ')[1]
            
            # Generate accept key
            accept_key = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
            
            response = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_key}\r\n"
                "\r\n"
            )
            client_socket.send(response.encode())
            return True
        return False

    def _websocket_send(self, client_socket, message):
        """Send WebSocket frame."""
        try:
            payload = message.encode('utf-8')
            payload_len = len(payload)
            
            if payload_len < 126:
                header = bytes([0x81, payload_len])
            elif payload_len < 65536:
                header = bytes([0x81, 126]) + payload_len.to_bytes(2, 'big')
            else:
                header = bytes([0x81, 127]) + payload_len.to_bytes(8, 'big')
            
            client_socket.send(header + payload)
        except Exception:
            pass

    def _websocket_recv(self, client_socket):
        """Receive WebSocket frame."""
        try:
            data = client_socket.recv(2)
            if len(data) < 2:
                return None
            
            fin = (data[0] & 0x80) != 0
            opcode = data[0] & 0x0F
            masked = (data[1] & 0x80) != 0
            payload_len = data[1] & 0x7F
            
            if payload_len == 126:
                data = client_socket.recv(2)
                payload_len = int.from_bytes(data, 'big')
            elif payload_len == 127:
                data = client_socket.recv(8)
                payload_len = int.from_bytes(data, 'big')
            
            if masked:
                mask = client_socket.recv(4)
                payload = client_socket.recv(payload_len)
                payload = bytes(payload[i] ^ mask[i % 4] for i in range(len(payload)))
            else:
                payload = client_socket.recv(payload_len)
            
            if opcode == 1:  # Text frame
                return payload.decode('utf-8')
            elif opcode == 8:  # Close frame
                return None
            return payload
        except Exception:
            return None

    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("127.0.0.1", self.port))
            self.server_socket.listen(1)
            print(f"WebSocket server listening on port {self.port}")
            
            while not self._stop.is_set():
                try:
                    self.client_socket, addr = self.server_socket.accept()
                    print("Client connected")
                    
                    if self._websocket_handshake(self.client_socket):
                        while not self._stop.is_set():
                            try:
                                msg = self._websocket_recv(self.client_socket)
                                if msg is None:
                                    break
                                _WS_RX.put(msg)
                            except Exception:
                                break
                except Exception:
                    if not self._stop.is_set():
                        time.sleep(0.1)
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            try:
                if self.client_socket:
                    self.client_socket.close()
                if self.server_socket:
                    self.server_socket.close()
            except Exception:
                pass


# --- UI ---
class REMOTE_PT_panel(bpy.types.Panel):
    bl_label = "Remote Control"
    bl_idname = "REMOTE_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Remote Control"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(context.scene, "remote_port")
        if _WS_RUNNING:
            col.operator("remote.stop", text="Stop Server", icon="CANCEL")
        else:
            col.operator("remote.start", text="Start Server", icon="PLAY")


class REMOTE_OT_start(bpy.types.Operator):
    bl_idname = "remote.start"
    bl_label = "Start WebSocket Server"

    def execute(self, context):
        global _WS_THREAD, _WS_RUNNING
        if _WS_RUNNING:
            self.report({'INFO'}, "Server already running")
            return {'CANCELLED'}

        port = context.scene.remote_port
        _WS_RUNNING = True
        _WS_THREAD = _WSServerThread(port)
        _WS_THREAD.start()
        bpy.app.timers.register(_timer_step)
        self.report({'INFO'}, f"Server started on port {port}")
        return {'FINISHED'}


class REMOTE_OT_stop(bpy.types.Operator):
    bl_idname = "remote.stop"
    bl_label = "Stop WebSocket Server"

    def execute(self, context):
        global _WS_THREAD, _WS_RUNNING
        if not _WS_RUNNING:
            self.report({'INFO'}, "Server not running")
            return {'CANCELLED'}
        _WS_RUNNING = False
        if _WS_THREAD:
            _WS_THREAD.stop()
            _WS_THREAD.join(timeout=1.0)
        self.report({'INFO'}, "Server stopped")
        return {'FINISHED'}


def _add_props():
    bpy.types.Scene.remote_port = bpy.props.IntProperty(
        name="Port", default=8765, min=1024, max=65535)


def _remove_props():
    if hasattr(bpy.types.Scene, "remote_port"):
        delattr(bpy.types.Scene, "remote_port")


classes = (REMOTE_PT_panel, REMOTE_OT_start, REMOTE_OT_stop)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    _add_props()


def unregister():
    global _WS_THREAD
    try:
        bpy.app.timers.unregister(_timer_step)
    except Exception:
        pass
    if _WS_THREAD:
        try:
            _WS_THREAD.stop()
            _WS_THREAD.join(timeout=0.5)
        except Exception:
            pass
    _remove_props()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
