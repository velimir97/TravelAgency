from agency import app, db
from flask_restful import abort, marshal_with, marshal
from agency.parser.user import user_resource_fields, user_registration_args, user_login_args, chack_registration_data
from agency.parser.arangement import arangement_resource_fields
from agency.models import UserModel, ArangementModel
from flask_login import login_user, logout_user, login_required
from flask import jsonify, request


# route: http://127.0.0.1:5000/singin, method POST
# processing the request for registration of a new user 
@app.route('/signin', methods=['POST'])
def user_registration():
    # parsing the obtained arguments
    args = user_registration_args.parse_args()
    try:
        # check the args data is correct
        chack_result, chack_message = chack_registration_data(args)
        if not chack_result:
            return jsonify({"message" : chack_message}), 409

        # creating and entering a new user
        user = UserModel(name=args['name'], surname=args['surname'], email=args['email'],
                        username=args['username'], desired_type=args['desired_type'], current_type='tourist'
        )
        user.set_password(args['password1'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message" : "Successful registration"}), 201
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/login, method POST
# processing user login requests
@app.route("/login", methods = ["POST"])
def login():
    # parsing the obtained arguments
    args = user_login_args.parse_args()
    try:
        # checking that the user exists and that the password is correct
        user = UserModel.query.filter_by(username=args['username']).first()
        if not user:
            return jsonify({"message" : "Username dont exist. Please register."}), 409
        if not user.check_password_hash(args['password']):
            return jsonify({"message" : "Username dont exist"}), 409
        
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


# route: http://127.0.0.1:5000/arangements, method GET
# processing requests to get all arangements
@app.route("/arangements")
def all_arangements():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        sort = request.args.get('sort', 'id', type=str)

        arangements = ArangementModel.query.filter_by().order_by(sort).paginate(page=page, per_page=per_page)
        arangement_list = [marshal(a.to_json(), arangement_resource_fields) for a in arangements.items]
        return jsonify(arangement_list), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500