from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from main import app
from main.extensions import db, bcrypt
from main.models import User
import re


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.post("/api/hello")
def hello():
    data = request.get_json(silent=True)
    name = data.get("name") if isinstance(data, dict) else None

    if not isinstance(name, str) or not name.strip():
        return jsonify(error="Send a non-empty 'name' in the JSON body."), 400

    return jsonify(message=f"Hello, {name.strip()}!")

# <----------------------------------- Authentication ----------------------------------->
@app.route("/register", methods=["POST"])
def register():
    # Retrieve request data
    incoming_data = request.get_json()

    # Extract information
    username = incoming_data["username"]
    password = incoming_data["password"]
    description = incoming_data.get("description", None)

    # Optional: Check if Password is strong enough
    if not re.search(r'(?=.*\d)(?=.*[A-Z]).{8,}', password):
        return jsonify({"error": "Password must be 8+ characters with an uppercase letter and digit"}), 409

    # Hash password
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Create The User
    user = User (
        username=username,
        password=password_hash,
        description=description
    )

    # Try inserting the User to the DB
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username already taken"}), 409
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to create user")
        return jsonify({"error": "Internal server error"}), 500

    return jsonify({"status": "received"}), 201

@app.route("/login", methods=["POST"])
def log_in():
    # Retrieve the data
    incoming_data = request.get_json()

    # Extract user info
    username = incoming_data["username"]
    password = incoming_data["password"]

    # Search the db
    stmt = db.select(User).filter_by(username=username)         # Holds SQL code
    user = db.session.execute(stmt).scalar_one_or_none()        # Executes SQL code

    # Assert everything is correct
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Create the JWT — identity should be a unique, stable value (usually the user's id)
    access_token = create_access_token(identity=str(user.user_id))

    # Return JWT
    return jsonify(
        {
            "access_token": access_token,
            "user": {
                "username": user.username,
                "description": user.description
            }
        }
    ), 200

@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    # retrieve logged in user
    user_id = int(get_jwt_identity())

    # db look up
    user = db.session.get(User, user_id)

    # Confirm user is present
    if user is None:
        return jsonify({"error": "User not found"}), 401

    # Return all this good stuff :)
    return jsonify(
        user_id=user.user_id,
        username=user.username,
        operator=user.operator,
        description=user.description,
    )

# <----------------------------------- ########### ----------------------------------->
