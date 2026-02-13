from flask import Flask, request, jsonify, send_file
from supabase import create_client, Client
import os
import tempfile

app = Flask(__name__)

# Load environment variables from Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def home():
    return "Supabase Storage Connected"


# ---------------------------------------------------------
# UPLOAD FILE
# ---------------------------------------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = file.filename

    # Supabase v2 upload syntax
    res = supabase.storage.from_(SUPABASE_BUCKET).upload(
        path=filename,
        file=file.read(),
        file_options={"content-type": "text/plain"}
    )

    # If Supabase returns an error object
    if isinstance(res, dict) and res.get("error"):
        return jsonify({"error": res["error"]}), 500

    # Public URL
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"

    return jsonify({
        "status": "success",
        "filename": filename,
        "url": public_url
    })


# ---------------------------------------------------------
# LIST FILES
# ---------------------------------------------------------
@app.route("/files", methods=["GET"])
def list_files():
    files = supabase.storage.from_(SUPABASE_BUCKET).list()
    return jsonify(files)


# ---------------------------------------------------------
# VIEW FILE
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# DELETE FILE
# ---------------------------------------------------------
@app.route("/delete/<filename>", methods=["DELETE"])
def delete_file(filename):
    res = supabase.storage.from_(SUPABASE_BUCKET).remove(filename)
    return jsonify({"status": "deleted", "filename": filename})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
