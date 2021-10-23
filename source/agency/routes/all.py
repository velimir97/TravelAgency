from agency import app, db
from flask_restful import abort, marshal_with, marshal
from agency.parser.user import user_resource_fields, user_registration_args, user_login_args, chack_registration_data
from agency.parser.arangement import arangement_resource_fields
from agency.models import UserModel, ArangementModel
from flask_login import login_user, logout_user, login_required
from flask import jsonify


# route: http://127.0.0.1:5000/sing_in, method POST
# processing the request for registration of a new user 
@app.route('/sign_in', methods=['POST'])
def user_registration():

    try:
        # parsing the obtained arguments
        args = user_registration_args.parse_args()

        chack_result, chack_message = chack_registration_data(args)
        if not chack_result:
            return {"message" : chack_message}, 409

        # creating and entering a new user
        user = UserModel(name=args['name'], surname=args['surname'], email=args['email'],
                        username=args['username'], desired_type=args['desired_type'], current_type='tourist'
        )
        user.set_password(args['password1'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message" : "Successful registration"}), 201
    except Exception as e:
        return jsonify({"message" : "Internal server error"}), 500

# route: http://127.0.0.1:5000/login, method POST
# processing user login requests
@app.route("/login", methods = ["POST"])
@marshal_with(user_resource_fields)
def login():
    # parsing the obtained arguments
    args = user_login_args.parse_args()

    # checking that the user exists and that the password is correct
    user = UserModel.query.filter_by(username=args['username']).first()
    if user:
        if user.check_password_hash(args['password']):
            # memory of the logged-in user
            login_user(user)
            return user, 200
        else:
            abort(401, message="Password is wrong")

    abort(401, message="This user is not registered. Please register.")

# route: http://127.0.0.1:5000/logout, method POST
# processing user logout requests 
@app.route("/logout", methods = ["POST"])
@login_required
def logout():
    logout_user()
    return "Success", 201

# route: http://127.0.0.1:5000/arangements, method GET
# processing requests to get all arangements
@app.route("/arangements")
def all_arangements():
    arangements = ArangementModel.query.all()
    arangement_list = [marshal(a.to_json(), arangement_resource_fields) for a in arangements]
    return jsonify(arangement_list), 200