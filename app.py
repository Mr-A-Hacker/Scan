from flask import Flask, request, jsonify, send_file
from supabase import create_client, Client
import os
import tempfile

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def home():
    return "Supabase Storage Connected"


# -----------------------------
# UPLOAD FILE
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = file.filename

    # Upload to Supabase
    res = supabase.storage.from_(SUPABASE_BUCKET).upload(filename, file.read(), {
        "content-type": "text/plain"
    })

    if "error" in str(res).lower():
        return jsonify({"error": "Upload failed", "details": str(res)}), 500

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"

    return jsonify({
        "status": "success",
        "filename": filename,
        "url": public_url
    })


# -----------------------------
# LIST FILES
# -----------------------------
@app.route("/files", methods=["GET"])
def list_files():
    files = supabase.storage.from_(SUPABASE_BUCKET).list()
    return jsonify(files)


# -----------------------------
# VIEW FILE
# -----------------------------
@app.route("/view/<filename>", methods=["GET"])
def view_file(filename):
    data = supabase.storage.from_(SUPABASE_BUCKET).download(filename)

    if data is None:
        return "File not found", 404

    # Save temporarily to send
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(data)
    tmp.close()

    return send_file(tmp.name, mimetype="text/plain")


# -----------------------------
# DELETE FILE
# -----------------------------
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    res = supabase.storage.from_(SUPABASE_BUCKET).remove(filename)
    return jsonify({"status": "deleted", "filename": filename})
