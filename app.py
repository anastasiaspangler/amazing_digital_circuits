from flask import Flask, render_template, request, render_template_string, send_from_directory, abort, url_for, jsonify
from flask_socketio import SocketIO
import os, sys
from replicate_utils.capture_station import capture_and_process

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# -------------------------------------------------------
# Puppetry routes (6DOF Pose)
# -------------------------------------------------------
@app.route('/puppetry/')
def index():
    return render_template("index.html")

@app.post("/puppetry/pose")
def pose():
    data = request.json
    print(f"Received pose data: {data}")
    # Broadcast to all connected WebSocket clients
    socketio.emit('pose_data', data)
    return {"ok": True}

# -------------------------------------------------------
# Replicate routes (Generative Assets)
# -------------------------------------------------------
@app.route('/genassets/replicate_hello')
def replicate_hello():
    return 'Hello World!'

# View 3D Asset
@app.route("/genassets/viewer/<object_name>")
def viewer(object_name):
    return render_template("viewer.html", object_name=object_name)

@app.route("/genassets/models/<object_name>")
def models(object_name):
    base = f"/files/{object_name}/replicate_predictions/{object_name}_output"
    data = {
        "name": object_name,
        "glb": f"{base}.glb",
        "images": [
            f"/files/{object_name}/img_a1.png",
            f"/files/{object_name}/img_a2.png",
            f"/files/{object_name}/img_b1.png",
            f"/files/{object_name}/img_b2.png",
        ],
    }
    return jsonify(data)

@app.route("/genassets/files/<path:filename>")
def files(filename):
    directory = "replicate_utils/local_storage/"
    fpath = directory + filename
    if not os.path.isfile(fpath):
        abort(404, description=f"File not found: {fpath}")
    return send_from_directory(directory, filename)

@app.route('/genassets/replicate', methods=['POST'])
def post_replicate():
    from replicate_utils.replicate_helper import send_to_replicate
    data = request.form.to_dict()
    name = data["name"]
    abs_paths = [data["path_a"], data["path_b"], data["path_c"], data["path_d"]]
    api_response = send_to_replicate(name, abs_paths)
    if api_response:
        return jsonify({
            "received": data,
            "status": "pass",
            "preview": str(f"http://127.0.0.1:5000/viewer/{name}")
        })
    return jsonify({"status": "fail"})

@app.route("/genassets/test_image/<object_name>")
def test_image(object_name):
    img_rel = f"{object_name}/img_a1.png"
    if not os.path.isfile(img_rel):
        return f"Test image not found at {img_rel}", 404

    html = """
    <!doctype html>
    <html>
      <head><meta charset="utf-8"><title>Test Image - {{ object_name }}</title></head>
      <body>
        <h3>Test image for {{ object_name }}</h3>
        <p>If this is blank, open the image URL directly:</p>
        <pre>{{ files_url }}</pre>
        <img src="{{ files_url }}" alt="test image" style="max-width:600px; display:block; margin-top:10px;">
      </body>
    </html>
    """
    files_url = url_for('files', filename=img_rel)
    return render_template_string(html, object_name=object_name, files_url=files_url)

# API trigger for capture station
# Assumes two webcameras are set up and object is in place
@app.route('/genassets/capturestation', methods=['POST'])
def capturestation():
    """Capture station endpoint that captures from webcams and runs replicate_utils automatically"""
    name = request.form.get('name')
    
    if not name:
        return jsonify({
            "status": "error",
            "message": "Name parameter is required"
        }), 400
    
    result = capture_and_process(name)
    
    if result["success"]:
        return jsonify({
            "status": "success",
            "name": result["name"],
            "preview": f"http://127.0.0.1:5000/viewer/{result['name']}",
            "model_data": f"http://127.0.0.1:5000/models/{result['name']}"
        })
    else:
        return jsonify({
            "status": "error", 
            "message": result.get("error", "Unknown error")
        }), 500

# Run functions
def run_puppetry_app():
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)

def run_replicate_app():
    app.run(debug=True)

if __name__ == '__main__':
    # Default to puppetry app
    run_puppetry_app()
