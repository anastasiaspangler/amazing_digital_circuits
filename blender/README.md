# Remote Blender Control

A Python library for controlling Blender remotely via WebSocket connection. This allows you to manipulate Blender objects, cameras, lighting, and more from external Python scripts.

## Features

- **Camera Control**: Position, rotate, and focus cameras
- **Object Manipulation**: Create, move, scale, and rotate objects
- **Lighting Control**: Adjust light intensity, color, and position
- **Scene Management**: List objects and import GLB files
- **Real-time Control**: Direct property manipulation via WebSocket

## Requirements

- Python 3.8 or higher
- Blender 3.0 or higher
- WebSocket connection capability

## Installation

### 1. Install Python Dependencies

```bash
# Clone or download this repository
cd remote_blender

# Install Python dependencies
python3 -m pip install -r requirements.txt

# Or install as a package
python3 -m pip install -e .
```

### 2. Install Blender Addon

1. Open Blender
2. Go to **Edit > Preferences > Add-ons**
3. Click **Install...** and select `blender_setup/add_on.py`
4. Enable the "Blender Remote Control" addon
5. The addon will appear in the 3D Viewport's N-panel under "Remote Control"

### 3. Setup Test Scene (Optional)

Run the test scene setup script in Blender's Scripting workspace:

```python
# In Blender's Scripting workspace, run:
exec(open("blender_setup/setup_test_scene.py").read())
```

## Usage

### Basic Setup

1. **Start Blender** with the remote control addon enabled
2. **Connect the addon**:
   - Open the N-panel in 3D Viewport
   - Go to "Remote Control" tab
   - Click "Connect" (default URL: `ws://127.0.0.1:8765`)

3. **Run the Python script**:
   ```bash
   python3 main.py
   ```

### Example Usage

```python
from blender_session import BlenderSession
import time

# Connect to Blender
blender = BlenderSession("ws://127.0.0.1:8765")

# Create objects
blender.create_cube(0, 0, 0)
blender.create_sphere(3, 0, 0)

# Control camera
blender.set_camera_position(5, -5, 3)
blender.rotate_camera(1.1, 0, 0.785)
blender.focus_on("Cube")

# Adjust lighting
blender.set_light_intensity("Light", 5.0)
blender.set_light_color("Light", 1.0, 0.9, 0.8)

# Manipulate objects
blender.set_object_scale("Cube", 1.5)
blender.set_object_rotation("Cube", 0, 0, 0.5)

# Close connection
blender.close()
```

### Available Methods

#### Camera Control
- `set_camera_position(x, y, z)` - Set camera location
- `rotate_camera(x, y, z)` - Set camera rotation
- `focus_on(object_name)` - Point camera at object
- `set_camera_zoom(distance)` - Set camera distance

#### Object Control
- `create_cube(x, y, z)` - Create a cube
- `create_sphere(x, y, z)` - Create a sphere
- `set_object_position(name, x, y, z)` - Move object
- `set_object_rotation(name, x, y, z)` - Rotate object
- `set_object_scale(name, scale)` - Scale object
- `list_objects()` - Get list of scene objects
- `add_glb(filename)` - Import GLB file

#### Lighting Control
- `set_light_intensity(name, intensity)` - Set light energy
- `set_light_color(name, r, g, b)` - Set light color
- `set_light_position(name, x, y, z)` - Move light

## Project Structure

```
remote_blender/
├── main.py                 # Main demonstration script
├── blender_session.py      # WebSocket client for Blender control
├── blender_setup/
│   ├── add_on.py          # Blender addon (install this in Blender)
│   └── setup_test_scene.py # Script to create test scene
├── requirements.txt        # Python dependencies
├── setup.py               # Package installation script
└── README.md              # This file
```

## Troubleshooting

### Connection Issues

1. **"Connection refused"**: Make sure Blender is running and the addon is connected
2. **"Object not found"**: Verify object names exist in the scene
3. **"WebSocket error"**: Check that the URL matches in both client and addon

### Common Solutions

1. **Restart Blender** if the addon stops responding
2. **Check the console** in Blender for error messages
3. **Verify WebSocket URL** matches between client and addon
4. **Ensure objects exist** before trying to manipulate them

### Debug Mode

Enable debug output by checking Blender's console window for detailed WebSocket communication logs.

## Development

### Running Tests

```bash
# Install development dependencies
python3 -m pip install -e ".[dev]"

# Run tests (when available)
python3 -m pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Blender
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Blender's console for error messages
3. Ensure all dependencies are properly installed
4. Verify WebSocket connection is established

## Changelog

### Version 1.0.0
- Initial release
- Basic WebSocket communication
- Camera, object, and lighting controls
- Blender addon integration
