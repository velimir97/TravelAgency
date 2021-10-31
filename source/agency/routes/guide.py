from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.models import UserModel, ArrangementModel
from agency.parser.arrangement_parser import arrangement_resource_fields
from datetime import datetime, timedelta


def is_guide(user):
    if user.current_type != "guide":
        abort(401, message="This request is not allowed to you")

# route: http://127.0.0.1:5000/update_description/<int:arrangement_id>
# PUT: updates the description of the arrangement
@app.route("/guide/update_description/<int:arrangement_id>", methods=["PUT"])
@login_required
def update_description(arrangement_id):
    is_guide(current_user)

    if request.method == "PUT":
        try:
            # parsing the obtained argument
            guide_description = request.form.get("description", None, type=str)

            # check the description is valid
            if guide_description == None or len(guide_description) < 10:
                return jsonify({"message" : "Description is wrong"}), 409
            
            # check if the arrangement is mine
            my_arrangements = [a.id for a in current_user.guide_arrangements]
            if arrangement_id not in my_arrangements:
                return jsonify({"message" : "You are not the guide of this arrangement"}), 409

            arrangement = ArrangementModel.query.filter_by(id=arrangement_id).first()
            if arrangement.start_date < datetime.now() + timedelta(days=5):
                return jsonify({"message" : "Start date is wrong"}), 409

            # memorizing a new description
            arrangement.description = guide_description
            db.session.commit()
            return jsonify({"message": "Description is updated!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/guide/type_request
# POST: send a request for promotion
@app.route("/guide/type_request", methods=["POST"])
@login_required
def requirement_upgrade():
    is_guide(current_user)

    if request.method == "POST":
        try:
            guide = UserModel.query.filter_by(id=current_user.id).first()
            guide.desired_type = 'admin'
            db.session.commit()
            return jsonify({"message": "Success!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/guide/my_arrangements
# GET: processes the request for retrieval of its arrangements
@app.route("/guide/my_arrangements")
@login_required
def guides_arrangements():
    is_guide(current_user)

    try:
        user = UserModel.query.filter_by(id=current_user.id).first()
        guide_arrangements = user.guide_arrangements
        guide_arrangements_list = [marshal(a.to_json(), arrangement_resource_fields) for a in guide_arrangements]
        return jsonify(guide_arrangements_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500