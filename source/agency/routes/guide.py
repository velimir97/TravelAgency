from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.models import UserModel, ArangementModel
from agency.parser.arangement_parser import arangement_resource_fields


def is_guide(user):
    if user.current_type != "guide":
        abort(401, message="This request is not allowed to you")

# route: http://127.0.0.1:5000/update_description/<int:arangement_id>
# PUT: updates the description of the arrangement
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

            # check if the arrangement is mine
            my_arangements = [a.id for a in current_user.guide_arangements]
            if arangement_id not in my_arangements:
                return jsonify({"message" : "You are not the guide on this arrangement"}), 409

            # memorizing a new description
            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            arangement.description = guide_description
            db.session.commit()
            return jsonify({"message": "Description is update!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/guide/update_type
# POST: sends a request for promotion
@app.route("/guide/update_type", methods=["POST"])
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
# GET: processes the request for retrieval of its arrangements
@app.route("/guide/my_arangements")
@login_required
def guides_arangements():
    is_guide(current_user)

    try:
        user = UserModel.query.filter_by(id=3).first()
        guide_arangements = user.guide_arangements
        guide_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in guide_arangements]
        return jsonify(guide_arangements_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500