from agency import app, db
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from flask import request, jsonify
from agency.parser.user_parser import user_resource_fields, UserUpdateSchema
from agency.parser.arrangement_parser import arrangement_resource_fields
from agency.models import UserModel, ArrangementModel
from datetime import datetime, timedelta
from marshmallow import ValidationError


def is_tourist(user):
    if user.current_type != "tourist":
        abort(401, message="This request is not allowed to you")


# route: http://127.0.0.1:5000/tourist/reserve_arrangement
# GET: takes all arrangements that the user can reserve
# POST: reserve arrangement
@app.route("/tourist/reserve_arrangement", methods = ["GET", "POST"])
@login_required
def next_possible_arrangements():
    is_tourist(current_user)

    if request.method == "GET":
        try:
            tourist = UserModel.query.filter_by(id = current_user.id).first()
            my_arrangements = [a.id for a in tourist.tourist_arrangements]

            next_arrangements = ArrangementModel.query.filter(ArrangementModel.start_date > datetime.now() + timedelta(days=5), ArrangementModel.id.not_in(my_arrangements)).all()
            return jsonify([marshal(a.to_json(), arrangement_resource_fields) for a in next_arrangements])
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif request.method == "POST":
        try:
            arrangement_id = request.form.get("arrangement_id", None, type=int)
            number_of_persons = request.form.get("number_of_persons", None, type=int)

            if arrangement_id == None:
                return jsonify({"message" : "Arrangement id is required"}), 409

            if number_of_persons == None:
                return jsonify({"message" : "Number of persons is required"}), 409

            if number_of_persons < 1:
                return jsonify({"message" : "Invalid number of persons"}), 409

            user = UserModel.query.filter_by(id=current_user.id).first()
            user_arrangements = [a.id for a in user.tourist_arrangements]
            if arrangement_id in user_arrangements:
                return jsonify({"message" : "Arrangement is already reserved"}), 409

            arrangement = ArrangementModel.query.filter_by(id=arrangement_id).first()
            if not arrangement:
                return jsonify({"message" : "Arrangement not found"}), 404
            # check to see if it's too late
            if arrangement.start_date < datetime.now() + timedelta(days=5):
                return jsonify({"message" : "You are late for this arrangement"}), 400
            # check for seats
            if number_of_persons > arrangement.free_seats:
                return jsonify({"message" : "The arrangement is full"}), 400
            
            # update free_seats
            arrangement.free_seats -= number_of_persons
            arrangement.tourists.append(user)

            db.session.commit()

            # price calculation
            price = number_of_persons * arrangement.price
            if number_of_persons > 3:
                price -= (number_of_persons - 3) * 0.1 * arrangement.price

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

    start_date = request.form.get('start_date', None)
    end_date = request.form.get('end_date', None)
    destination = request.form.get('destination', None, type=str)

    try:
        arrangements = ArrangementModel.query

        # check args
        if start_date:
            try:
                datetime.fromisoformat(start_date)
            except ValueError:
                return jsonify({"message" : "Start date is wrong"}), 409
            arrangements = arrangements.filter(ArrangementModel.start_date > datetime.fromisoformat(start_date))
        if end_date:
            try:
                datetime.fromisoformat(end_date)
            except ValueError:
                return jsonify({"message" : "End date is wrong"}), 409
            arrangements = arrangements.filter(ArrangementModel.end_date < datetime.fromisoformat(end_date))
        if destination:
            arrangements = arrangements.filter(ArrangementModel.destination == destination)

        arrangements = arrangements.all()
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
        try:
            schema = UserUpdateSchema()
            try:
                schema.load(request.form)
            except ValidationError as e:
                print(e)
                return jsonify(e.messages), 409

            name = request.form.get('name', None, type=str)
            surname = request.form.get('surname', None, type=str)
            email = request.form.get('email', None, type=str)
            username = request.form.get('username', None, type=str)
            password = request.form.get('password1', None, type=str)

            tourist = UserModel.query.filter_by(id=current_user.id).first()
            if name:
                tourist.name = name
            if surname:
                tourist.surname = surname
            if email:
                tourist.email = email
            if username:
                tourist.username = username
            if password:
                tourist.password = password
            
            db.session.commit()
            return jsonify({"message": "Profile is updated!"}), 200
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
    is_tourist(current_user)
    try:
        user = UserModel.query.filter_by(id=current_user.id).first()
        tourist_arrangements = user.tourist_arrangements
        tourist_arrangements_list = [marshal(a.to_json(), arrangement_resource_fields) for a in tourist_arrangements]
        return jsonify(tourist_arrangements_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500
