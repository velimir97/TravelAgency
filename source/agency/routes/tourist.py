from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.parser.user_parser import user_resource_fields, user_reserve_args, user_update_args, check_user_data
from agency.parser.arrangement_parser import arrangement_resource_fields, arrangement_search_args, check_arrangement_data
from agency.models import UserModel, ArrangementModel
from datetime import datetime, timedelta


def is_tourist(user):
    if user.current_type != "tourist":
        abort(401, message="This request is not allowed to you")


# route: http://127.0.0.1:5000/tourist/reserve_arrangement
# GET: takes all arrangements that the user can reserve (tourist)
# POST: reserve arrangement (tourist)
@app.route("/tourist/reserve_arrangement", methods = ["GET", "POST"])
@login_required
def next_possible_arrangements():
    is_tourist(current_user)

    if request.method == "GET":
        try:
            tourist = UserModel.query.filter_by(id = current_user.id).first()
            my_arrangements = [a.id for a in tourist.tourist_arrangements]

            all_arrangements = ArrangementModel.query.all()
            return jsonify([marshal(a.to_json(), arrangement_resource_fields) for a in all_arrangements 
                            if a.start_date > datetime.now() + timedelta(days=5) 
                                and a.id not in my_arrangements]), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif request.method == "POST":
        args = user_reserve_args.parse_args()

        try:
            user = UserModel.query.filter_by(id=current_user.id).first()

            arrangement = ArrangementModel.query.filter_by(id=args['arrangement_id']).first()
            # check to see if it's too late
            if arrangement.start_date < datetime.now() + timedelta(days=5):
                return jsonify({"message" : "You are late for this arrangement"}), 400
            # check for seats
            if args['number_of_persons'] > arrangement.free_seats:
                return jsonify({"message" : "The arrangement is full"}), 400
            
            # update free_seats
            arrangement.free_seats -= args['number_of_persons']
            arrangement.tourists.append(user)

            db.session.commit()

            # price calculation
            price = args['number_of_persons'] * arrangement.price
            if args['number_of_persons'] > 3:
                price -= (args['number_of_persons'] - 3) * 0.1 * arrangement.price

            msg = "Success! Price of arrangement is " + str(price)
            return jsonify({"message" : msg}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/tourist/search_arrangements
# GET: takes arrangements by date and destination
@app.route("/tourist/search_arrangements")
@login_required
def search_arrangements():
    is_tourist(current_user)

    # parsing the obtained argument
    args = arrangement_search_args.parse_args()
    
    try:
        arrangements = ArrangementModel.query.all()

        # check args
        if args['start']:
            try:
                datetime.fromisoformat(args['start'])
            except ValueError:
                return jsonify({"message" : "Start date is wrong"}), 409
            arrangements = [a for a in arrangements if a.start_date > datetime.fromisoformat(args['start'])]
        if args['end']:
            try:
                datetime.fromisoformat(args['end'])
            except ValueError:
                return jsonify({"message" : "End date is wrong"}), 409
            arrangements = [a for a in arrangements if a.end_date < datetime.fromisoformat(args['end'])]
        if args['destination']:
            arrangements = [a for a in arrangements if a.destination == args['destination']]

        return jsonify([marshal(a.to_json(), arrangement_resource_fields) for a in arrangements]), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/tourist/my_profile
# GET: retrieves tourist profile information
# PUT: update tourist profile
# PATCH: sends a request for promotion
@app.route("/tourist/my_profile", methods = ["GET", "PUT","PATCH"])
@login_required
def update_my_profile():
    is_tourist(current_user)

    if request.method == "GET":
        try:
            return jsonify(marshal(UserModel.query.filter_by(id=current_user.id).first(), user_resource_fields)), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    if request.method == "PUT":
        args = user_update_args.parse_args()
        try:
            # set the args['desired_type'] so that the function check_registration_data can be called
            args['desired_type'] = "tourist"
            check_res, check_msg = check_user_data(args)
            if not check_res:
                return jsonify({"message" : check_msg}), 409

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

    if request.method == "PATCH":
        upgrade_type = request.form.get("type", "none", type=str)
        try:
            if upgrade_type not in ['guide', 'admin']:
                return jsonify({"message" : "Type is wrong"}), 409
                
            tourist = UserModel.query.filter_by(id=current_user.id).first()
            tourist.desired_type = upgrade_type
            db.session.commit()
            return jsonify({"message": "Request is sent!"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/tourist/my_arrangements
# GET: processes the request for retrieval of its arrangements
@app.route("/tourist/my_arrangements")
@login_required
def tourists_arrangements():
    is_tourist()
    try:
        user = UserModel.query.filter_by(id=current_user.id).first()
        tourist_arrangements = user.tourist_arrangements
        tourist_arrangements_list = [marshal(a.to_json(), arrangement_resource_fields) for a in tourist_arrangements]
        return jsonify(tourist_arrangements_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500
