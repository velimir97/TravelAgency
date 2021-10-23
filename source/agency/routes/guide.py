from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.models import UserModel, ArangementModel
from agency.parser.arangement import arangement_update_desc_args


# route: http://127.0.0.1:5000/update_description/<int:arangement_id>, method PUT (guide)
# updates the description of the arrangement
@app.route("/update_description/<int:arangement_id>", methods=["PUT"])
@login_required
def update_description(arangement_id):
    if current_user.current_type != 'guide':
        abort(401, message="This request is not allowed to you")

    if request.method == "PUT":
        my_arangements = [a.id for a in current_user.guide_arangements]
        if arangement_id not in my_arangements:
            return abort(404, message="You are not the guide on this arrangement")

        args = arangement_update_desc_args.parse_args()
        arangement = ArangementModel.query.filter_by(id=arangement_id).first()
        arangement.description = args['description']
        db.session.commit()
        return jsonify({"message": "Success!"}), 200


# route: http://127.0.0.1:5000/update_type, methods POST (guide)
# sends a request for promotion
@app.route("/update_type", methods=["POST"])
@login_required
def guide_update_type():
    if current_user.current_type != 'guide':
        abort(401, message="This request is not allowed to you")

    if request.method == "POST":
        guide = UserModel.query.filter_by(id=current_user.id).first()
        guide.desired_type = 'admin'
        db.session.commit()
        return jsonify({"message": "Success!"}), 200 

# route: http://127.0.0.1:5000/my_arangements, method GET
# processes the request for retrieval of its arrangements
@app.route("/guide/my_arangements")
@login_required
def my_guide_arangements():
    if current_user.current_type != 'guide':
        abort(401, message="This request is not allowed to you")

    user = UserModel.query.filter_by(id=current_user.id).first()
    guide_arangements = user.guide_arangements
    guide_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in guide_arangements]
    return jsonify(guide_arangements_list), 200