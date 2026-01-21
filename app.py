from flask import Flask, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Render Flask Server Running"

@app.route("/logs", methods=["POST"])
def upload_log():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({"success": True, "filename": filename}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051)
