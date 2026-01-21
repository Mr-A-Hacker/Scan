from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "Mr.A HiveSec Server is running."

@app.route("/logs", methods=["POST"])
def upload_logs():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No selected file"}), 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    return jsonify({"status": "success", "message": f"Saved to {save_path}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051)
