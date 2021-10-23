from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.parser.user import user_resource_fields, user_reserve_args, user_update_args, user_update_type_args
from agency.parser.arangement import arangement_resource_fields, arangement_search_args
from agency.models import UserMixin, ArangementModel
from datetime import datetime, timedelta


# route: http://127.0.0.1:5000/next_arangements, methods GET, POST
# GET: takes all arrangements that the user can reserve (tourist)
# POST: reserve arrangement (tourist)
@app.route("/next_arangements", methods = ["GET", "POST"])
@login_required
def next_possible_arrangements():
    if current_user.current_type != 'tourist':
        abort(401, message="This request is not allowed to you")

    if request.method == "GET":
        tourist = UserModel.query.filter_by(id = current_user.id).first()
        my_arangements = [a.id for a in tourist.tourist_arangements]

        all_arangements = ArangementModel.query.all()
        return jsonify([marshal(a.to_json(), arangement_resource_fields) for a in all_arangements 
                        if a.start_date > datetime.now() + timedelta(days=5) 
                            and a.id not in my_arangements]), 200
    
    elif request.method == "POST":
        args = user_reserve_args.parse_args()
        user = UserModel.query.filter_by(id=current_user.id).first()

        arangement = ArangementModel.query.filter_by(id=args['arangement_id']).first()
        if arangement.start_date < datetime.now() + timedelta(days=5):
            return "You are late for this arrangement", 200
        if args['number_of_persons'] > arangement.free_seats:
            return "The arrangement is full", 200
        
        arangement.free_seats -= args['number_of_persons']
        arangement.tourists.append(user)

        db.session.commit()

        price = args['number_of_persons'] * arangement.price
        if args['number_of_persons'] > 3:
            price -= (args['number_of_persons'] - 3) * 0.1 * arangement.price

        return f"Success! Price of arrangement is {price}", 200

# route: http://127.0.0.1:5000/search_arangements, method GET
# takes arrangements by date and destination (tourist)
@app.route("/search_arangements")
@login_required
def search_arangements():
    if current_user.current_type != 'tourist':
        abort(401, message="This request is not allowed to you")

    args = arangement_search_args.parse_args()
    arangements = ArangementModel.query.filter_by(destination=args['destination'])
    list_arangements = [a.to_json() for a in arangements if a.start_date > args['start'] and a.end_date < args['end']]
    return jsonify(list_arangements), 200

# route: http://127.0.0.1:5000/my_profile, methods GET, PUT, POST (tourist)
# GET: retrieves tourist profile information
# PUT: update tourist profile
# POST: sends a request for promotion
@app.route("/my_profile", methods = ["GET", "PUT","POST"])
@login_required
def update_my_profile():
    if current_user.current_type != 'tourist':
        abort(401, message="This request is not allowed to you")

    if request.method == "GET":
        return marshal(UserModel.query.filter_by(id=current_user.id).first(), user_resource_fields), 200

    if request.method == "PUT":
        args = user_update_args.parse_args()
        
        tourist = UserModel.query.filter_by(id=current_user.id).first()
        if args['name']:
            tourist.name = args['name']
        if args['surname']:
            tourist.surname = args['surname']
        if args['email']:
             # check if the user(email) is already registered 
            result = UserModel.query.filter_by(email=args['email']).first()
            if result:
                abort(409, message="The email exists ...")

            tourist.email = args['email']
        if args['username']:
            # check if the user(username) is already registered 
            result = UserModel.query.filter_by(username=args['username']).first()
            if result:
                abort(409, message="The username exists ... ")
            tourist.username = args['username']
        if args['password1'] and args['password2'] and args['password1'] == args['password2']:
            tourist.password = args['password1']
        
        db.session.commit()
        return jsonify({"message": "Success!"}), 200

    if request.method == "POST":
        args = user_update_type_args.parse_args()
        tourist = UserModel.query.filter_by(id=current_user.id).first()
        tourist.desired_type = args['type']
        db.session.commit()
        return jsonify({"message": "Success!"}), 200


# route: http://127.0.0.1:5000/my_arangements, method GET
# processes the request for retrieval of its arrangements
@app.route("/tourist/my_arangements")
@login_required
def my_tourist_arangements():
    if current_user.current_type != 'tourist':
        abort(401, message="This request is not allowed to you")

    user = UserModel.query.filter_by(id=current_user.id).first()
    tourist_arangements = user.tourist_arangements
    tourist_arangements_list = [marshal(t.to_json(), arangement_resource_fields) for t in tourist_arangements]
    return jsonify(tourist_arangements_list), 200