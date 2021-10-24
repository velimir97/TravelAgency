from agency import app, db, mail
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from agency.parser.arangement_parser import arangement_args, arangement_resource_fields, arangement_update_args, check_arangement_data
from agency.parser.user_parser import user_type_args, user_resource_fields
from agency.models import ArangementModel, UserModel
from datetime import datetime, timedelta
from flask_mail import Message
from flask import jsonify, request
from math import ceil


def is_admin(user):
    if user.current_type != "admin":
        abort(401, message="This request is not allowed to you")


# route: http://127.0.0.1:5000/admin/add_arangement
# POST: processing requests to add arangements
@app.route("/admin/add_arangement", methods = ['POST'])
@login_required
def create_new_arangement():
    is_admin(current_user)

    # parsing the obtained arguments
    args = arangement_args.parse_args()

    try:
        # check the args data is correct
        check_result, check_message = check_arangement_data(args)
        if not check_result:
            return jsonify({"message" : check_message}), 409

        # creating and entering a new arangement
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
        return jsonify({"message" : "Successful create arangement"}), 201
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/admin/update_arangement/<int:arangement_id>
# PATCH: processing requests to update arangement by id
# DELETE: processing requests to delete arangement by id
# GET: processing request to retrieve the arangement by id
@app.route("/admin/arangement/<int:arangement_id>", methods = ['PATCH', 'DELETE', 'GET'])
@login_required
def process_arangement_by_id(arangement_id):
    is_admin(current_user)

    if request.method == "PATCH":
        try:
            # check if the arangement exists
            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            if not arangement:
                return jsonify({"message" : "Arangement does't not exist"}), 404
            
            # check if the arangement starts in five days
            time_now = datetime.now()
            if (arangement.start_date - time_now < timedelta(days=5)):
                return jsonify({"message" : "Five days until the arangement"}), 404
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

        # parsing the obtained arguments
        args = arangement_update_args.parse_args()

        try:
            # check if the args data is correct
            check_result, check_message = check_arangement_data(args)
            if not check_result:
                return jsonify({"message" : check_message}), 409
            
            # updating the values
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
                # updating the guide values
                user_guide = UserModel.query.filter_by(id=args['guide_id']).first()
                if not user_guide or user_guide.current_type != 'guide':
                    return jsonify({"message" : "Guide is not found"}), 404
                for guide_arangement in user_guide.guide_arangements:
                    # check if the guide is available at the required time
                    if ((arangement.start_date > guide_arangement.start_date and arangement.start_date < guide_arangement.end_date) or 
                        (arangement.end_date > guide_arangement.start_date and arangement.end_date < guide_arangement.end_date)
                    ):
                        return jsonify({"message": "Guide is reserved."}), 409
                arangement.guide_id = args['guide_id']
            
            db.session.commit()
            return jsonify({"message" : "Arangement is updated"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    
    if request.method == "DELETE":
        try:
            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            if not arangement:
                return jsonify({"message" : "Arangement does't exist"}), 404

            # check if the arangement starts in five days
            time_now = datetime.now()
            if (arangement.start_date - time_now < timedelta(days=5)):
                return jsonify({"message" : "Five days until the arangement"}), 404
                
            # an email is sent to users
            for tourist in arangement.tourists:
                try:
                    msg = Message("The arangement was canceled.", sender=app.config.get("MAIL_USERNAME") , recipients=[tourist.email])
                    mail.send(msg)
                except Exception as e:
                    print(e)
                    return jsonify({"message" : "Mails not sent"}), 500

            db.session.delete(arangement)
            db.session.commit()
            return jsonify({"message" : "Arangement has been deleted"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    if request.method == "GET":
        try:
            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            if not arangement:
                return jsonify({"message" : "Arangement not found"}), 404
            return jsonify(arangement.to_json()), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    return jsonify({"message" : "Method not found"}), 404

# route: http://127.0.0.1:5000/admin/users_reqs
# GET: handles the retrieval request of users who want to upgrade the type
@app.route('/admin/users_reqs')
@login_required
def get_users_requirement():
    is_admin(current_user)

    try:
        # search users who want upgrade
        tourist_req_admin = UserModel.query.filter_by(desired_type = 'admin', current_type = 'tourist')
        guide_req_admin = UserModel.query.filter_by(desired_type = 'admin', current_type = 'guide')
        tourist_req_guide = UserModel.query.filter_by(desired_type = 'guide', current_type = 'tourist')

        list_tourist_req_admin = [marshal(u.to_json(), user_resource_fields) for u in tourist_req_admin]
        list_guide_req_admin = [marshal(u.to_json(), user_resource_fields) for u in guide_req_admin]
        list_tourist_req_guide = [marshal(u.to_json(), user_resource_fields) for u in tourist_req_guide]
        return jsonify(list_tourist_req_admin + list_guide_req_admin + list_tourist_req_guide), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/admin/response_type
# PUT: accepts the request for upgrade
# POST: does not accept the request for upgrade
@app.route('/admin/response_type/<int:user_id>', methods = ["PUT", "POST"])
@login_required
def process_user_requirement(user_id):
    is_admin(current_user)

    if request.method == 'PUT':
        try :
            # check the user exist
            user = UserModel.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"message" : "User not exists"}), 404

            # sending an email to the user
            try:
                msg = Message("Your request has been accepted", sender=app.config.get("MAIL_USERNAME"), recipients=[user.email])
                mail.send(msg)
            except Exception as e:
                print(e)
                return jsonify({"message" : "Mail not sent"}), 500
            
            # user type upgrade
            user.current_type = user.desired_type
            db.session.commit()
            
            return jsonify({"message" : "Success"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    elif request.method == 'POST':
        msg = request.args.get("message", "", type=str)
        try:
            if msg == "":
                return jsonify({"message" : "Message is require"}), 409
            # check the user exist
            user = UserModel.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"message" : "User not exists"}), 404

            # user type not upgrade
            user.desired_type = user.current_type
            db.session.commit()

            # sending an email to the user
            try:
                msg = Message(msg, sender=app.config.get("MAIL_USERNAME"), recipients=[user.email])
                mail.send(msg)
            except Exception as e:
                print(e)
                return jsonify({"message" : "Mail not sent"}), 500

            return jsonify({"message" : "Success"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
        

# route: http://127.0.0.1:5000/users, method GET
# processing requests to get all users or get user by type
@app.route('/admin/users')
@login_required
def all_users_by_type():
    is_admin(current_user)

    # parsing the obtained arguments
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    sort = request.args.get('sort', 'id', type=str)
    users_type = request.args.get("type", "all", type=str)

    if users_type == "all":
        # getting all users
        try:
            users = UserModel.query.filter_by()
            if page > ceil(users.count()/per_page):
                return jsonify({"message": "Page is not found"}), 404

            users = users.order_by(sort).paginate(page=page, per_page=per_page)
            user_list = [marshal(u.to_json(), user_resource_fields) for u in users.items]
            return jsonify(user_list), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif users_type == "tourist":
        # getting tourist users
        try:
            tourists = UserModel.query.filter_by(current_type="tourist")
            tourists_with_arangements = []
            for tourist in tourists:
                tourist_arangements = [a.to_json() for a in tourist.tourist_arangements]
                tourist_json = marshal(tourist.to_json(), user_resource_fields)
                tourist_json['tourist_arangements'] = tourist_arangements
                tourists_with_arangements.append(tourist_json)
            
            return jsonify(tourists_with_arangements), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif users_type == "guide":
        # getting guide users
        try:
            guides = UserModel.query.filter_by(current_type="guide")
            guides_with_arangements = []
            for guide in guides:
                guide_arangements = [a.to_json() for a in guide.guide_arangements if a.end_date < datetime.now()]
                guide_json = marshal(guide.to_json(), user_resource_fields)
                guide_json['guide_arangements'] = guide_arangements
                guides_with_arangements.append(guide_json)
            
            return jsonify(guides_with_arangements), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    
    return jsonify({"message" : "Type not found"}), 404


# route: http://127.0.0.1:5000/my_arangements
# GET: processes the request for retrieval of its arangements
@app.route("/admin/my_arangements")
@login_required
def admins_arangements():
    is_admin(current_user)
    try:
        admin_arangements = ArangementModel.query.filter_by(admin_id = current_user.id)
        admin_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in admin_arangements]
        return jsonify(admin_arangements_list), 200
    except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500