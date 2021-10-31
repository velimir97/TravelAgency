from agency import app, db
from flask_restful import abort, marshal
from agency.parser.user_parser import user_resource_fields, UserSchema
from agency.parser.arrangement_parser import arrangement_resource_fields
from agency.models import UserModel, ArrangementModel
from flask_login import login_user, logout_user, login_required
from flask import jsonify, request
from math import ceil
from marshmallow import ValidationError


# route: http://127.0.0.1:5000/singin
# POST: processing the request for registration of a new user 
@app.route('/signin', methods=['POST'])
def user_registration():
    try:
        # check the form data is correct
        schema = UserSchema()
        try:
            schema.load(request.form)
        except ValidationError as e:
            print(e)
            return jsonify(e.messages), 409
        
        # creating and entering a new user
        user = UserModel(name=request.form['name'], surname=request.form['surname'], email=request.form['email'],
                        username=request.form['username'], desired_type=request.form['desired_type'], current_type='tourist'
        )
        user.set_password(request.form['password1'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message" : "Successful registration"}), 201
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/login
# POST: processing user login requests
@app.route("/login", methods = ["POST"])
def login():
    try:
        username = request.form.get("username", "", type=str)
        if username == "":
            return jsonify({"message" : "Username is required"}), 404
        password = request.form.get("password", "", type=str)
        if password == "":
            return jsonify({"message" : "Password is required"}), 404

        # checking that the user exists and that the password is correct
        user = UserModel.query.filter_by(username=username).first()
        if not user:
            return jsonify({"message" : "Username does't exist. Please register."}), 409
        if not user.check_password(password):
            return jsonify({"message" : "Password is wrong"}), 409
        
        login_user(user)
        return jsonify({"message" : "Successful login"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/logout, method POST
# processing user logout requests 
@app.route("/logout", methods = ["POST"])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message" : "Successful logout"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/arrangements
# GET :processing requests to get all arrangements
@app.route("/arrangements")
def all_arrangements():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        sort = request.args.get('sort', 'id', type=str)

        # check that the page is correct
        arrangements = ArrangementModel.query.filter_by()
        if page > ceil(arrangements.count()/per_page):
            return jsonify({"message": "Page is not found"}), 404

        res = {"count" : arrangements.count()}
        
        arrangements = arrangements.order_by(sort).paginate(page=page, per_page=per_page)
        arrangement_list = [marshal(a.to_json(), arrangement_resource_fields) for a in arrangements.items]
        res['arrangements'] = arrangement_list
        
        res['page'] = page
        res['per_page'] = per_page
        
        return jsonify(res), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500