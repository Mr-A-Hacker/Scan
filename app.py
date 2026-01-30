import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from b2sdk.v2 import InMemoryAccountInfo, B2Api

app = Flask(__name__)

# -----------------------------
# Backblaze B2 Client
# -----------------------------
def get_b2():
    info = InMemoryAccountInfo()
    b2 = B2Api(info)
    b2.authorize_account(
        "production",
        os.getenv("B2_KEY_ID"),
        os.getenv("B2_APPLICATION_KEY")
    )
    return b2

# -----------------------------
# Home
# -----------------------------
@app.route("/")
def home():
    return "✅ Backblaze-enabled server is running"

# -----------------------------
# Upload File to Backblaze
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "❌ No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "❌ No selected file", 400

    filename = secure_filename(file.filename)

    # Connect to B2
    b2 = get_b2()
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

    # Upload bytes directly
    bucket.upload_bytes(
        file.read(),
        filename
    )

    # Build public or private URL
    endpoint = os.getenv("B2_BUCKET_ENDPOINT")
    bucket_name = os.getenv("B2_BUCKET_NAME")
    file_url = f"https://{endpoint}/file/{bucket_name}/{filename}"

    return jsonify({
        "status": "success",
        "filename": filename,
        "url": file_url
    })

# -----------------------------
# List Files in Backblaze
# -----------------------------
@app.route("/files")
def list_files():
    b2 = get_b2()
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

    files = [f.file_name for f, _ in bucket.ls()]

    return jsonify(files)

# -----------------------------
# Get File URL
# -----------------------------
@app.route("/files/<filename>")
def get_file(filename):
    endpoint = os.getenv("B2_BUCKET_ENDPOINT")
    bucket_name = os.getenv("B2_BUCKET_NAME")

    file_url = f"https://{endpoint}/file/{bucket_name}/{filename}"

    return jsonify({"url": file_url})
