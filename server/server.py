import os
from flask import Flask, request, jsonify, send_from_directory

import util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "UI"))

app = Flask(__name__, static_folder=None)


def api_response(payload, status=200):
    response = jsonify(payload)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, status


@app.route("/")
def index():
    return send_from_directory(UI_DIR, "app.html")


@app.route("/<path:filename>")
def ui_static(filename):
    return send_from_directory(UI_DIR, filename)


@app.route("/classify_image", methods=["POST"])
def classify_image():
    image_data = request.form.get("image_data")
    if not image_data and request.is_json:
        payload = request.get_json(silent=True) or {}
        image_data = payload.get("image_data")

    if not image_data:
        return api_response({
            "error": "Missing image_data. Upload an image and try again."
        }, 400)

    try:
        result = util.classify_image(image_data)
    except Exception as exc:
        return api_response({
            "error": f"Classification failed: {exc}"
        }, 500)

    if not result:
        return api_response({
            "error": "Could not read that image. Try another JPG or PNG photo."
        }, 422)

    return api_response(result)


# Load model when the app/worker starts (needed for Gunicorn on Render).
util.load_saved_artifacts()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("Starting Python Flask Server For Sports Celebrity Image Classification")
    print(f"UI available at http://0.0.0.0:{port}/")
    app.run(host="0.0.0.0", port=port)
