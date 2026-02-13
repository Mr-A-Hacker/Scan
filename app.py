import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from b2sdk.v2 import InMemoryAccountInfo, B2Api
from io import BytesIO

app = Flask(__name__)

# ----------------------------------------------------
# Backblaze B2 Client
# ----------------------------------------------------
def get_b2():
    info = InMemoryAccountInfo()
    b2 = B2Api(info)
    b2.authorize_account(
        "production",
        os.getenv("B2_KEY_ID"),
        os.getenv("B2_APPLICATION_KEY")
    )
    return b2


# ----------------------------------------------------
# Home
# ----------------------------------------------------
@app.route("/")
def home():
    return "✅ Backblaze-enabled server is running"


# ----------------------------------------------------
# Upload File to Backblaze
# ----------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "❌ No file part", 400

    file = request.files["file"]

    if file.filename == "":
        return "❌ No selected file", 400

    # Use the filename provided by the client
    filename = secure_filename(file.filename)

    # OPTIONAL: Force filename to be based on client IP
    # client_ip = request.remote_addr.replace(".", "-")
    # filename = f"{client_ip}.txt"

    # Connect to B2
    b2 = get_b2()
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

    # Upload bytes directly
    bucket.upload_bytes(
        file.read(),
        filename
    )

    # Build file URL (private bucket will NOT open directly)
    endpoint = os.getenv("B2_BUCKET_ENDPOINT")
    bucket_name = os.getenv("B2_BUCKET_NAME")
    file_url = f"https://{endpoint}/file/{bucket_name}/{filename}"

    return jsonify({
        "status": "success",
        "filename": filename,
        "url": file_url
    })


# ----------------------------------------------------
# List Files in Backblaze
# ----------------------------------------------------
@app.route("/files")
def list_files():
    b2 = get_b2()
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

    files = [f.file_name for f, _ in bucket.ls()]

    return jsonify(files)


# ----------------------------------------------------
# Get File URL (still private)
# ----------------------------------------------------
@app.route("/files/<filename>")
def get_file(filename):
    endpoint = os.getenv("B2_BUCKET_ENDPOINT")
    bucket_name = os.getenv("B2_BUCKET_NAME")

    file_url = f"https://{endpoint}/file/{bucket_name}/{filename}"

    return jsonify({"url": file_url})


# ----------------------------------------------------
# Download File (works with PRIVATE buckets)
# ----------------------------------------------------
@app.route("/download/<filename>")
def download_file(filename):
    b2 = get_b2()
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

    # Find the file version
    for file_version, _ in bucket.ls():
        if file_version.file_name == filename:
            downloaded = bucket.download_file_by_id(file_version.id_)

            buffer = BytesIO()
            downloaded.save_to(buffer)   # <-- THIS WORKS ON YOUR VERSION
            buffer.seek(0)

            # Show file in browser instead of forcing download
            return send_file(
                buffer,
                mimetype="text/plain",   # or "application/pdf" if PDF
                download_name=filename,
                as_attachment=False      # <-- SHOW IN BROWSER
            )

    return jsonify({"error": "file not found"}), 404





# ----------------------------------------------------
# Delete File from Backblaze
# ----------------------------------------------------
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    b2 = get_b2()
    bucket = b2.get_bucket_by_name(os.getenv("B2_BUCKET_NAME"))

    # Search for the file version
    for file_version, _ in bucket.ls():
        if file_version.file_name == filename:
            bucket.delete_file_version(file_version.id_, file_version.file_name)
            return jsonify({
                "status": "deleted",
                "filename": filename
            })

    return jsonify({"error": "file not found"}), 404


# ----------------------------------------------------
# Run (local only)
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
