from agency import app, db, login_manager, mail
from flask_restful import abort, marshal_with, marshal
from agency.models import UserModel, ArangementModel
from flask_login import login_required, login_user, logout_user, current_user
from agency.parser import user_post_args, user_login_args, user_resource_fields, user_type_args
from agency.parser import arangement_resource_fields, arangement_update_args, arangement_post_args
from datetime import datetime, timedelta
from flask import request, json, jsonify
from flask_mail import Message
from datetime import datetime

# route: http://127.0.0.1:5000/singin, method POST
# processing the request for registration of a new user 
@app.route('/signin', methods=['POST'])
@marshal_with(user_resource_fields)
def sign_in():

    # parsing the obtained arguments
    args = user_post_args.parse_args()

    # check if the user(email) is already registered 
    result = UserModel.query.filter_by(email=args['email']).first()
    if result:
        abort(409, message="The email exists ...")

    # check if the user(username) is already registered 
    result = UserModel.query.filter_by(username=args['username']).first()
    if result:
        abort(409, message="The username exists ... ")
    
    # check that both passwords are the same
    if args['password1'] != args['password2']:
        abort(409, message="Passwords is not equal")

    # creating and entering a new user
    user = UserModel(name=args['name'], surname=args['surname'], email=args['email'],
                    username=args['username'], desired_type=args['desired_type'], current_type='tourist'
    )
    user.set_password(args['password1'])
    db.session.add(user)
    db.session.commit()
    return user, 201

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


# route: http://127.0.0.1:5000/add_arangement, method POST
# processing requests to add arangements (admin)
@app.route("/add_arangement", methods = ['POST'])
@login_required
@marshal_with(arangement_resource_fields)
def add_arangement():
    # parsing the obtained arguments
    if current_user.current_type != "admin":
        abort(401, message="This request is not allowed to you")

    args = arangement_post_args.parse_args()
    arangement = ArangementModel(start_date = datetime.fromisoformat(args['start']),
                                end_date = datetime.fromisoformat(args['end']),
                                description = args['description'],
                                destination = args['destination'],
                                number_of_seats = args['number_of_seats'],
                                free_seats = args['number_of_seats'],
                                price = args['price'],
                                admin_id = current_user.id
    )

    db.session.add(arangement)
    db.session.commit()

    return arangement, 201


# route: http://127.0.0.1:5000/update_arangement/arangement_id, method PATCH
# processing requests to update arangements (admin)
@app.route("/update_arangement/<int:arangement_id>", methods = ['PATCH'])
@login_required
@marshal_with(arangement_resource_fields)
def update_arangement(arangement_id):
    print(current_user.username)
    if current_user.current_type != "admin":
        abort(401, message="This request is not allowed to you")

    arangement = ArangementModel.query.filter_by(id=arangement_id).first()
    if not arangement:
        abort(404, message="Arangement is not exists")
    
    time_now = datetime.now()
    if (arangement.start_date - time_now < timedelta(days=5)):
        abort(404, message="Five days until the arrangement")

    args = arangement_update_args.parse_args()
    if args['start'] != None:
        arangement.start_date = datetime.fromisoformat(args['start'])
    if args['end'] != None:
        arangement.end_date = datetime.fromisoformat(args['end'])
    if args['description'] != None:
        arangement.description = args['description']
    if args['destination'] != None:
        arangement.destination = args['destination']
    if args['number_of_seats'] != None:
        arangement.number_of_seats = args['number_of_seats']
    if args['price'] != None:
        arangement.price = args['price']    
    if args['guide_id'] != None:
        user_guide = UserModel.query.filter_by(id=args['guide_id']).first()
        for guide_arangement in user_guide.guide_arangements:
            if ((arangement.start_date > guide_arangement.start_date and arangement.start_date < guide_arangement.end_date) or 
                (arangement.end_date > guide_arangement.start_date and arangement.end_date < guide_arangement.end_date)
            ):
                abort(404, "Guide is reserved.")
        arangement.guide_id = args['guide_id']
    
    db.session.commit()

    return arangement, 201

# route: http://127.0.0.1:5000/delete_arangement/arangement_id, method DELETE
# processing requests to update arangements (admin)
@app.route("/delete_arangement/<int:arangement_id>", methods = ['DELETE'])
@login_required
def delete_arangement(arangement_id):
    if current_user.current_type != "admin":
        abort(401, message="This request is not allowed to you")

    arangement = ArangementModel.query.filter_by(id=arangement_id).first()
    if not arangement:
        abort(404, message="Arangement is not exists")
    
    time_now = datetime.now()
    if (arangement.start_date - time_now < timedelta(days=5)):
        abort(404, message="Five days until the arrangement")

    for tourist in arangement.tourists:
        try:
            msg = Message("The arrangement was canceled.", sender="velimirbicanin@gmail.com", recipients=[tourist.email])
            mail.send(msg)
        except Exception as e:
            print("Mail is not send.")

    db.session.delete(arangement)
    db.session.commit()

    return "Success", 201

# route: http://127.0.0.1:5000/arangements, method GET
# processing requests to get arangements
@app.route("/arangements")
def all_arangements():
    arangements = ArangementModel.query.all()
    arangement_list = [marshal(a.to_json(), arangement_resource_fields) for a in arangements]
    return jsonify(arangement_list), 200

@app.route("/my_arangements")
@login_required
def my_arangements():
    if current_user.current_type == "admin":
        admin_arangements = ArangementModel.query.filter_by(admin_id=current_user.id)
        admin_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in admin_arangements]
        return jsonify(admin_arangements_list), 200

    if current_user.current_type == "tourist":
        user = UserModel.query.filter_by(id=current_user.id).first()
        tourist_arangements = user.tourist_arangements
        tourist_arangements_list = [marshal(t.to_json(), arangement_resource_fields) for t in tourist_arangements]
        return jsonify(tourist_arangements_list), 200

    if current_user.current_type == "guide":
        user = UserModel.query.filter_by(id=current_user.id).first()
        guide_arangements = user.guide_arangements
        guide_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in guide_arangements]
        return jsonify(guide_arangements_list), 200

@app.route('/arangement/<int:arangement_id>')
@login_required
def info_arangement(arangement_id):
    if current_user.current_type != 'admin':
        abort(401, message="This request is not allowed to you")

    arangement = ArangementModel.query.filter_by(id=arangement_id).first()
    return jsonify(arangement.to_json()), 200

@app.route('/type_diff_users')
@login_required
def different_type_users():
    if current_user.current_type != 'admin':
        abort(401, message="This request is not allowed to you")

    user_like_admin1 = UserModel.query.filter_by(desired_type = 'admin', current_type = 'tourist')
    user_like_admin2 = UserModel.query.filter_by(desired_type = 'admin', current_type = 'guide')
    user_like_guide = UserModel.query.filter_by(desired_type = 'guide', current_type = 'tourist')

    list_user_like_admin1 = [marshal(u.to_json(), user_resource_fields) for u in user_like_admin1]
    list_user_like_admin2 = [marshal(u.to_json(), user_resource_fields) for u in user_like_admin2]
    list_user_like_guide = [marshal(u.to_json(), user_resource_fields) for u in user_like_guide]
    return jsonify(list_user_like_admin1 + list_user_like_admin2 + list_user_like_guide), 200

@app.route('/type_diff_users/<int:user_id>', methods = ["POST", "PUT"])
@login_required
def info_user_type(user_id):
    if current_user.current_type != 'admin':
        abort(401, message="This request is not allowed to you")

    if request.method == 'PUT':
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not exists")
        user.current_type = user.desired_type
        db.session.commit()

        try:
            msg = Message("Your request has been accepted", sender=current_user.email, recipients=[user.email])
            mail.send(msg)
        except Exception as e:
            print("Message dont send")

        return "Success", 200
    elif request.method == 'POST':
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            abort(404, message="User not exists")
        user.desired_type = user.current_type
        db.session.commit()

        try:
            msg = Message(request.form['message'], sender=current_user.email, recipients=[user.email])
            mail.send(msg)
        except Exception as e:
            print("Message dont send")

        return "Success", 200

@app.route('/users')
@login_required
def all_users():
    if current_user.current_type != 'admin':
        abort(401, message="This request is not allowed to you")

    users = UserModel.query.all()
    user_list = [marshal(u.to_json(), user_resource_fields) for u in users]
    return jsonify(user_list), 200

@app.route('/users_type')
@login_required
def all_users_by_type():
    if current_user.current_type != 'admin':
        abort(401, message="This request is not allowed to you")

    args = user_type_args.parse_args()

    if args['type'] == 'tourist':
        tourists = UserModel.query.filter_by(current_type=args['type'])
        tourists_with_arangements = []
        for tourist in tourists:
            tourist_arangements = [a.to_json() for a in tourist.tourist_arangements]
            tourist_json = marshal(tourist.to_json(), user_resource_fields)
            tourist_json['tourist_arangements'] = tourist_arangements
            tourists_with_arangements.append(tourist_json)
        
        return jsonify(tourists_with_arangements), 200
    
    if args['type'] == 'guide':
        guides = UserModel.query.filter_by(current_type=args['type'])
        guides_with_arangements = []
        for guide in guides:
            guide_arangements = [a.to_json() for a in guide.guide_arangements if a.end_date > datetime.now()] #  promeni na manje
            guide_json = marshal(guide.to_json(), user_resource_fields)
            guide_json['tourist_arangements'] = guide_arangements
            guides_with_arangements.append(guide_json)
        
        return jsonify(guides_with_arangements), 200
    
    return "Type is wrong", 404

@app.route("/next_arangements")
@login_required
def next_possible_arrangements():
    if current_user.current_type != 'tourist':
        abort(401, message="This request is not allowed to you")

    
