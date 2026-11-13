from datetime import time

from flask import jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from main import app
from main.extensions import db, bcrypt
from main.models import Club, ClubEvents, ClubMembership, ClubRegularMeeting, SavedClub, User
import re
import datetime

# <------------------------------------ Status Check ------------------------------------>
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

    # Gaurd against improper inserts
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

# <--------------------------------------- Saved Clubs --------------------------------------->

@app.route("/saved-clubs", methods=["GET"])
@jwt_required()
def get_saved_clubs():
    #User specific function
    #Check only if user exists and clubs saved clubs are empty
    user_id = int(get_jwt_identity())
    if db.session.get(User, user_id) is None:
        return jsonify({"error": "user not found"}), 401

    clubs = db.session.execute(
        db.select(Club)
        .join(SavedClub, SavedClub.club_id == Club.club_id)
        .where(SavedClub.user_id == user_id)
    ).scalars().all()
    return jsonify([{
        "club_id": club.club_id,
        "club_name": club.club_name,
        "description": club.description,
    } for club in clubs]), 200


@app.route("/saved-clubs/<int:club_id>", methods=["POST"])
@jwt_required()
def save_club(club_id):
    #User specific function
    #Check only if user exists and club is in their saved list
    user_id = int(get_jwt_identity())
    if db.session.get(User, user_id) is None:
        return jsonify({"error": "user not found"}), 401
    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404

    existing_saved_club = db.session.get(SavedClub, (user_id, club_id))
    if existing_saved_club is not None:
        return jsonify({"error": "club already saved"}), 409

    saved_club = SavedClub(user_id=user_id, club_id=club_id)
    db.session.add(saved_club)
    db.session.commit()
    return jsonify({"user_id": user_id, "club_id": club_id}), 200


@app.route("/saved-clubs/<int:club_id>", methods=["DELETE"])
@jwt_required()
def unsave_club(club_id):
    #User specific function
    #Check only if user exists and club is in their saved list
    user_id = int(get_jwt_identity())
    if db.session.get(User, user_id) is None:
        return jsonify({"error": "user not found"}), 401
    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404

    saved_club = db.session.get(SavedClub, (user_id, club_id))
    if saved_club is None:
        return jsonify({"error": "club is not saved"}), 404

    db.session.delete(saved_club)
    db.session.commit()
    return jsonify({"status": "club unsaved"}), 200

# <--------------------------------------- Regular Meetings --------------------------------------->

def _regular_meeting_json(meeting):
    #Payload, not a route
    return {
        "meeting_id": meeting.meeting_id,
        "club_id": meeting.club_id,
        "start_time": meeting.start_time.isoformat(),
        "end_time": meeting.end_time.isoformat(),
        "day": meeting.day,
        "meeting_interval": meeting.meeting_interval,
    }

def _validate_club_access(club_id):
    #Reusable function to check permissions
    #It also checks if the user and club exists
    user_id = int(get_jwt_identity())

    if db.session.get(User, user_id) is None:
        return jsonify({"error": "user not found"}), 401

    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404

    membership = db.session.execute(
        db.select(ClubMembership).where(
            ClubMembership.user_id == user_id,
            ClubMembership.club_id == club_id,
            ClubMembership.role == "leader",
        )
    ).scalar_one_or_none()

    if membership is None:
        return jsonify({"error": "not authorized; club leader access required"}), 403

    return None


@app.route("/clubs/<int:club_id>/regular-meetings", methods=["GET"])
def get_club_regular_meetings(club_id):
    #General function, no permission needed
    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404

    meetings = db.session.execute(
        db.select(ClubRegularMeeting).where(ClubRegularMeeting.club_id == club_id)
    ).scalars().all()
    return jsonify([_regular_meeting_json(meeting) for meeting in meetings]), 200


@app.route("/clubs/<int:club_id>/regular-meetings/<int:meeting_id>", methods=["GET"])
def get_club_regular_meeting(club_id, meeting_id):
    #General function, no permission needed
    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404

    meeting = db.session.execute(
        db.select(ClubRegularMeeting).where(
            ClubRegularMeeting.club_id == club_id,
            ClubRegularMeeting.meeting_id == meeting_id,
        )
    ).scalar_one_or_none()
    if meeting is None:
        return jsonify({"error": "regular meeting not found"}), 404

    return jsonify(_regular_meeting_json(meeting)), 200


@app.route("/clubs/<int:club_id>/regular-meetings", methods=["POST"])
@jwt_required()
def create_club_regular_meeting(club_id):
    #Permission needed
    #Route only callable by Club Leader with matching club_id
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    incoming_data = request.get_json()
    meeting = ClubRegularMeeting(
        club_id=club_id,
        start_time=time.fromisoformat(incoming_data["start_time"]),
        end_time=time.fromisoformat(incoming_data["end_time"]),
        day=incoming_data["day"],
        meeting_interval=incoming_data.get("meeting_interval"),
    )
    db.session.add(meeting)
    db.session.commit()
    return jsonify(_regular_meeting_json(meeting)), 200


@app.route("/clubs/<int:club_id>/regular-meetings/<int:meeting_id>", methods=["PATCH"])
@jwt_required()
def update_club_regular_meeting(club_id, meeting_id):
    #Permission needed
    #Route only callable by Club Leader with matching club_id
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    meeting = db.session.execute(
        db.select(ClubRegularMeeting).where(
            ClubRegularMeeting.club_id == club_id,
            ClubRegularMeeting.meeting_id == meeting_id,
        )
    ).scalar_one_or_none()
    if meeting is None:
        return jsonify({"error": "regular meeting not found"}), 404

    incoming_data = request.get_json()
    if "start_time" in incoming_data:
        meeting.start_time = time.fromisoformat(incoming_data["start_time"])
    if "end_time" in incoming_data:
        meeting.end_time = time.fromisoformat(incoming_data["end_time"])
    if "day" in incoming_data:
        meeting.day = incoming_data["day"]
    if "meeting_interval" in incoming_data:
        meeting.meeting_interval = incoming_data["meeting_interval"]

    db.session.commit()
    return jsonify(_regular_meeting_json(meeting)), 200


@app.route("/clubs/<int:club_id>/regular-meetings/<int:meeting_id>", methods=["DELETE"])
@jwt_required()
def delete_club_regular_meeting(club_id, meeting_id):
    #Permission needed
    #Route only callable by Club Leader with matching club_id
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    meeting = db.session.execute(
        db.select(ClubRegularMeeting).where(
            ClubRegularMeeting.club_id == club_id,
            ClubRegularMeeting.meeting_id == meeting_id,
        )
    ).scalar_one_or_none()
    if meeting is None:
        return jsonify({"error": "regular meeting not found"}), 404

    db.session.delete(meeting)
    db.session.commit()
    return jsonify({"status": "regular meeting deleted"}), 200

# <------------------------------------- Clubs ------------------------------------------>
@app.route("/clubs", methods=["GET"])
def get_clubs():
    #General function, no perms needed
    clubs = db.session.execute(db.select(Club)).scalars().all()
    return jsonify([{
        "club_id": club.club_id,
        "club_name": club.club_name,
        "description": club.description,
    } for club in clubs]), 200


@app.route("/clubs/<int:club_id>", methods=["GET"])
def get_club(club_id):
    #No permissions needed, general function
    club = db.session.get(Club, club_id)
    if club is None:
        return jsonify({"error": "club not found"}), 404

    return jsonify({
        "club_id": club.club_id,
        "club_name": club.club_name,
        "description": club.description,
    }), 200


@app.route("/clubs", methods=["POST"])
def create_club():
    #No permissions needed?
    incoming_data = request.get_json()
    club = Club(
        club_name=incoming_data["club_name"],
        description=incoming_data.get("description"),
    )
    db.session.add(club)
    db.session.commit()
    return jsonify({
        "club_id": club.club_id,
        "club_name": club.club_name,
        "description": club.description,
    }), 200


@app.route("/clubs/<int:club_id>", methods=["PATCH"])
@jwt_required()
def update_club(club_id):
    #Club leaders who match club id only access
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    club = db.session.get(Club, club_id)
    incoming_data = request.get_json()
    if "club_name" in incoming_data:
        club.club_name = incoming_data["club_name"]
    if "description" in incoming_data:
        club.description = incoming_data["description"]

    db.session.commit()
    return jsonify({
        "club_id": club.club_id,
        "club_name": club.club_name,
        "description": club.description,
    }), 200


@app.route("/clubs/<int:club_id>", methods=["DELETE"])
@jwt_required()
def delete_club(club_id):
    #I assume club leader with specific club id only
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    club = db.session.get(Club, club_id)
    db.session.delete(club)
    db.session.commit()
    return jsonify({"status": "club deleted"}), 200

# <------------------------------------- ClubEvents ------------------------------------->

# TODO: Create Event Name Column

# Retrieve 1 specific event
@app.route("/event/select/<int:event_id>", methods=["GET"])
def select_event(event_id):
    # event lookup
    #No permissions needed
    event = db.session.get(ClubEvents, event_id)

    # Confirm event exists
    if event is None:
        return jsonify({"error": "event not found"}), 404

    # Return
    return jsonify(event.to_dict())

# Retrieve all events a club has to offer
@app.route("/event/<int:club_id>/select_all", methods=["GET"])
def select_club_events(club_id):
    # Gaurd against invalid club
    #No permissions needed

    if (db.session.get(Club, club_id) == None):
        return jsonify({"error": "club not found"}), 404

    # Lookup events
    stmt    = db.select(ClubEvents).filter_by(club_id=club_id)
    events  = db.session.execute(stmt).scalars().all()

    # return
    return jsonify([e.to_dict() for e in events]), 200

# Create a Club Event
@app.route("/event/create/<int:club_id>", methods=["POST"])
@jwt_required()
def create_event(club_id):
    #Club leaders who match club id only
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    data = request.get_json(silent=True) or {}

    start_time_raw = data.get("start_time")
    end_time_raw = data.get("end_time")
    date_raw = data.get("date")
    description = data.get("description")

    if not (start_time_raw and end_time_raw and date_raw):
        return jsonify({"error": "start_time, end_time, and date are required"}), 400

    # Parse and validate formats
    try:
        start_time = datetime.time.fromisoformat(start_time_raw)  # "14:30" or "14:30:00"
        end_time = datetime.time.fromisoformat(end_time_raw)
        date = datetime.date.fromisoformat(date_raw)              # "2026-11-04"
    except (ValueError, TypeError):
        return jsonify({"error": "invalid date or time format (use YYYY-MM-DD and HH:MM)"}), 400

    if end_time <= start_time:
        return jsonify({"error": "end_time must be after start_time"}), 400

    club_event = ClubEvents(
        club_id=club_id,
        start_time=start_time,
        end_time=end_time,
        date=date,
        description=description,
    )

    try:
        db.session.add(club_event)
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to create event")
        return jsonify({"error": "failed to create event"}), 500

    return jsonify(club_event.to_dict()), 201

@app.route("/event/delete/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id):
    #Club leaders who match club id only

    event = db.session.get(ClubEvents, event_id)
    if event is None:
        return jsonify({"error": "event not found"}), 404

    denial = _validate_club_access(event.club_id)
    if denial is not None:
        return denial

    try:
        db.session.delete(event)
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to delete event %s", event_id)
        return jsonify({"error": "failed to delete event"}), 500

    return jsonify({"status": f"deleted event with id: {event_id}"}), 200

@app.route("/event/update/<int:event_id>", methods=["PATCH"])
@jwt_required()
def update_event(event_id):
    #Club leaders who match club id only

    event = db.session.get(ClubEvents, event_id)
    if event is None:
        return jsonify({"error": "event not found"}), 404

    denial = _validate_club_access(event.club_id)
    if denial is not None:
        return denial

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data:
        return jsonify({"error": "request body must be a non-empty JSON object"}), 400

    allowed = {"date", "start_time", "end_time", "description"}
    unknown = set(data) - allowed
    if unknown:
        return jsonify({"error": f"unknown field(s): {', '.join(sorted(unknown))}"}), 400

    # Start from the current values, then override whatever was sent.
    # Nothing is written to `event` until everything validates.
    new_date = event.date
    new_start = event.start_time
    new_end = event.end_time
    new_description = event.description

    try:
        if "date" in data:
            new_date = datetime.date.fromisoformat(data["date"])
        if "start_time" in data:
            new_start = datetime.time.fromisoformat(data["start_time"])
        if "end_time" in data:
            new_end = datetime.time.fromisoformat(data["end_time"])
    except (ValueError, TypeError):
        return jsonify({"error": "invalid date or time format (use YYYY-MM-DD and HH:MM)"}), 400

    if "description" in data:
        desc = data["description"]
        if desc is not None and not isinstance(desc, str):
            return jsonify({"error": "description must be a string or null"}), 400
        new_description = desc.strip() or None if desc is not None else None

    if new_end <= new_start:
        return jsonify({"error": "end_time must be after start_time"}), 400

    event.date = new_date
    event.start_time = new_start
    event.end_time = new_end
    event.description = new_description

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        app.logger.exception("Failed to update event %s", event_id)
        return jsonify({"error": "failed to update event"}), 500

    return jsonify(event.to_dict()), 200

# <------------------------------------- ClubMembers ------------------------------------->

# All current roles, new roles requires modifying this list only
VALID_ROLES = {"member", "leader"}

def _membership_json(membership, user):
    return {
        "user_id": membership.user_id,
        "club_id": membership.club_id,
        "role": membership.role,
        "username": user.username,
    }

#Checks how many leaders are in the club
def _leader_count(club_id):
    return db.session.scalar(
        db.select(db.func.count()).select_from(ClubMembership).where(
            ClubMembership.club_id == club_id,
            ClubMembership.role == "leader",
        )
    )


# Gets all members of the club
@app.route("/clubs/<int:club_id>/members", methods=["GET"])
def get_club_members(club_id):

    #Club existence check
    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404

    rows = db.session.execute(
        db.select(ClubMembership, User)
        .join(User, User.user_id == ClubMembership.user_id)
        .where(ClubMembership.club_id == club_id)
    ).all()
    return jsonify([_membership_json(m, u) for m, u in rows]), 200


#New member joins club, defaulted to member
@app.route("/clubs/<int:club_id>/members", methods=["POST"])
@jwt_required()
def join_club(club_id):
    user_id = int(get_jwt_identity())

    #Error checks before committing to db
    if db.session.get(User, user_id) is None:
        return jsonify({"error": "user not found"}), 401
    if db.session.get(Club, club_id) is None:
        return jsonify({"error": "club not found"}), 404
    if db.session.get(ClubMembership, (user_id, club_id)) is not None:
        return jsonify({"error": "already a member"}), 409

    membership = ClubMembership(user_id=user_id, club_id=club_id, role="member")
    try:
        db.session.add(membership)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "already a member"}), 409

    return jsonify({"user_id": user_id, "club_id": club_id, "role": "member"}), 201


#A member leaves club
@app.route("/clubs/<int:club_id>/members/me", methods=["DELETE"])
@jwt_required()
def leave_club(club_id):
    user_id = int(get_jwt_identity())
    membership = db.session.get(ClubMembership, (user_id, club_id))
    if membership is None:
        return jsonify({"error": "not a member of this club"}), 404

    #Makes sure atleast one member (leader) is in club
    if membership.role == "leader" and _leader_count(club_id) <= 1:
        return jsonify({"error": "last leader cannot leave; promote someone first"}), 409

    db.session.delete(membership)
    db.session.commit()
    return jsonify({"status": "left club"}), 200


# Change someone's role (Leader only)
@app.route("/clubs/<int:club_id>/members/<int:target_user_id>", methods=["PATCH"])
@jwt_required()
def update_member_role(club_id, target_user_id):
    #Checks for leader access
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    membership = db.session.get(ClubMembership, (target_user_id, club_id))
    if membership is None:
        return jsonify({"error": "member not found"}), 404

    #Makes sure role change is only within what exists
    data = request.get_json(silent=True) or {}
    new_role = data.get("role")
    if new_role not in VALID_ROLES:
        return jsonify({"error": f"role must be one of: {', '.join(sorted(VALID_ROLES))}"}), 400

    if membership.role == "leader" and new_role != "leader" and _leader_count(club_id) <= 1:
        return jsonify({"error": "cannot demote the last leader"}), 409

    membership.role = new_role
    db.session.commit()
    user = db.session.get(User, target_user_id)
    return jsonify(_membership_json(membership, user)), 200


#Remove a member from club (leaders only)
@app.route("/clubs/<int:club_id>/members/<int:target_user_id>", methods=["DELETE"])
@jwt_required()
def remove_member(club_id, target_user_id):
    #Checks leader access
    denial = _validate_club_access(club_id)
    if denial is not None:
        return denial

    membership = db.session.get(ClubMembership, (target_user_id, club_id))
    if membership is None:
        return jsonify({"error": "member not found"}), 404

    #Makes sure not last member being removed
    if membership.role == "leader" and _leader_count(club_id) <= 1:
        return jsonify({"error": "cannot remove the last leader"}), 409

    db.session.delete(membership)
    db.session.commit()
    return jsonify({"status": "member removed"}), 200