from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)


@api.get("/health")
def health():
    return jsonify(status="ok")


@api.post("/hello")
def hello():
    data = request.get_json(silent=True)
    name = data.get("name") if isinstance(data, dict) else None

    if not isinstance(name, str) or not name.strip():
        return jsonify(error="Send a non-empty 'name' in the JSON body."), 400

    return jsonify(message=f"Hello, {name.strip()}!")
