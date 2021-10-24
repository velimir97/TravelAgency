from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.models import UserModel, ArangementModel
from agency.parser.arangement_parser import arangement_resource_fields
from datetime import datetime, timedelta


def is_guide(user):
    if user.current_type != "guide":
        abort(401, message="This request is not allowed to you")

# route: http://127.0.0.1:5000/update_description/<int:arangement_id>
# PUT: updates the description of the arangement
@app.route("/guide/update_description/<int:arangement_id>", methods=["PUT"])
@login_required
def update_description(arangement_id):
    is_guide(current_user)

    if request.method == "PUT":
        try:
            # parsing the obtained argument
            guide_description = request.args.get("description", "none", type=str)

            # check the description is valid
            if guide_description == "none" or len(guide_description) < 10:
                return jsonify({"message" : "Description is wrong"}), 409
            
            # check if the arangement is mine
            my_arangements = [a.id for a in current_user.guide_arangements]
            if arangement_id not in my_arangements:
                return jsonify({"message" : "You are not the guide of this arangement"}), 409

            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            if arangement.start_date < datetime.now() + timedelta(days=5):
                return jsonify({"message" : "Start date is wrong"}), 409

            # memorizing a new description
            arangement.description = guide_description
            db.session.commit()
            return jsonify({"message": "Description is updated!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/guide/type_req
# POST: send a request for promotion
@app.route("/guide/type_req", methods=["POST"])
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


# route: http://127.0.0.1:5000/guide/my_arangements
# GET: processes the request for retrieval of its arangements
@app.route("/guide/my_arangements")
@login_required
def guides_arangements():
    is_guide(current_user)

    try:
        user = UserModel.query.filter_by(id=current_user.id).first()
        guide_arangements = user.guide_arangements
        guide_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in guide_arangements]
        return jsonify(guide_arangements_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500