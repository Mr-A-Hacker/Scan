import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ----------------------------------------------------
# Ensure uploads folder exists
# ----------------------------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------------------------------
# Home
# ----------------------------------------------------
@app.route("/")
def home():
    return "✅ Local-storage server is running"


# ----------------------------------------------------
# Upload File (Saves Locally)
# ----------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "❌ No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "❌ No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    return jsonify({
        "status": "success",
        "filename": filename,
        "path": filepath
    })


# ----------------------------------------------------
# List Files
# ----------------------------------------------------
@app.route("/files")
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)


# ----------------------------------------------------
# View File in Browser
# ----------------------------------------------------
@app.route("/view/<filename>")
def view_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return "File not found", 404

    with open(filepath, "r", errors="ignore") as f:
        content = f.read()

    return f"<pre>{content}</pre>"


# ----------------------------------------------------
# Download File
# ----------------------------------------------------
@app.route("/download/<filename>")
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "file not found"}), 404

    return send_file(filepath, as_attachment=True)


# ----------------------------------------------------
# Delete File
# ----------------------------------------------------
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "file not found"}), 404

    os.remove(filepath)
    return jsonify({"status": "deleted", "filename": filename})


# ----------------------------------------------------
# Run (local only)
# ----------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

