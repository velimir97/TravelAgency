from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.parser.user import user_resource_fields, user_reserve_args, user_update_args, chack_registration_data
from agency.parser.arangement import arangement_resource_fields, arangement_search_args, chack_create_arangement_data
from agency.models import UserModel, ArangementModel
from datetime import datetime, timedelta


def chack_user_is_tourist(user):
    if user.current_type != "tourist":
        abort(401, message="This request is not allowed to you")


# route: http://127.0.0.1:5000/tourist/reserve_arangement
# GET: takes all arrangements that the user can reserve (tourist)
# POST: reserve arrangement (tourist)
@app.route("/tourist/reserve_arangement", methods = ["GET", "POST"])
@login_required
def next_possible_arrangements():
    chack_user_is_tourist(current_user)

    if request.method == "GET":
        try:
            tourist = UserModel.query.filter_by(id = current_user.id).first()
            my_arangements = [a.id for a in tourist.tourist_arangements]

            all_arangements = ArangementModel.query.all()
            return jsonify([marshal(a.to_json(), arangement_resource_fields) for a in all_arangements 
                            if a.start_date > datetime.now() + timedelta(days=5) 
                                and a.id not in my_arangements]), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif request.method == "POST":
        args = user_reserve_args.parse_args()

        try:
            user = UserModel.query.filter_by(id=current_user.id).first()

            arangement = ArangementModel.query.filter_by(id=args['arangement_id']).first()
            if arangement.start_date < datetime.now() + timedelta(days=5):
                return jsonify({"message" : "You are late for this arrangement"}), 400
            if args['number_of_persons'] > arangement.free_seats:
                return jsonify({"message" : "The arrangement is full"}), 400
            
            arangement.free_seats -= args['number_of_persons']
            arangement.tourists.append(user)

            db.session.commit()

            price = args['number_of_persons'] * arangement.price
            if args['number_of_persons'] > 3:
                price -= (args['number_of_persons'] - 3) * 0.1 * arangement.price

            msg = "Success! Price of arrangement is " + str(price)
            return jsonify({"message" : msg}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/tourist/search_arangements
# GET: takes arrangements by date and destination
@app.route("/tourist/search_arangements")
@login_required
def search_arangements():
    chack_user_is_tourist(current_user)

    args = arangement_search_args.parse_args()
    
    try:
        arangements = ArangementModel.query.all()
        if args['start']:
            try:
                datetime.fromisoformat(args['start'])
            except ValueError:
                return jsonify({"message" : "Start date is wrong"}), 409
            arangements = [a for a in arangements if a.start_date > datetime.fromisoformat(args['start'])]
        if args['end']:
            try:
                datetime.fromisoformat(args['end'])
            except ValueError:
                return jsonify({"message" : "End date is wrong"}), 409
            arangements = [a for a in arangements if a.end_date < datetime.fromisoformat(args['end'])]
        if args['destination']:
            arangements = [a for a in arangements if a.destination == args['destination']]

        return jsonify([marshal(a.to_json(), arangement_resource_fields) for a in arangements]), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/tourist/my_profile
# GET: retrieves tourist profile information
# PUT: update tourist profile
# POST: sends a request for promotion
@app.route("/tourist/my_profile", methods = ["GET", "PUT","POST"])
@login_required
def update_my_profile():
    chack_user_is_tourist(current_user)

    if request.method == "GET":
        try:
            return jsonify(marshal(UserModel.query.filter_by(id=current_user.id).first(), user_resource_fields)), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    if request.method == "PUT":
        args = user_update_args.parse_args()
        try:
            # set the args['desired_type'] so that the function chack_registration_data can be called
            args['desired_type'] = "tourist"
            chack_res, chack_msg = chack_registration_data(args)
            if not chack_res:
                return jsonify({"message" : chack_msg}), 409

            tourist = UserModel.query.filter_by(id=current_user.id).first()
            if args['name']:
                tourist.name = args['name']
            if args['surname']:
                tourist.surname = args['surname']
            if args['email']:
                tourist.email = args['email']
            if args['username']:
                tourist.username = args['username']
            if args['password1']:
                tourist.password = args['password1']
            
            db.session.commit()
            return jsonify({"message": "Profil is update!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    if request.method == "POST":
        upgrade_type = request.args.get("type", "none", type=str)
        try:
            if upgrade_type not in ['guide', 'admin']:
                return jsonify({"message" : "Type is wrong"}), 409
                
            tourist = UserModel.query.filter_by(id=current_user.id).first()
            tourist.desired_type = upgrade_type
            db.session.commit()
            return jsonify({"message": "Request is send!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/tourist/my_arangements
# GET: processes the request for retrieval of its arrangements
@app.route("/tourist/my_arangements")
@login_required
def my_tourist_arangements():
    chack_user_is_tourist()
    try:
        user = UserModel.query.filter_by(id=current_user.id).first()
        tourist_arangements = user.tourist_arangements
        tourist_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in tourist_arangements]
        return jsonify(tourist_arangements_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500
