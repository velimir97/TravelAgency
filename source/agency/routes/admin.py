from agency import app, db, mail
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from agency.parser.arangement_parser import arangement_create_args, arangement_resource_fields, arangement_update_args, chack_create_arangement_data
from agency.parser.user_parser import user_type_args, user_resource_fields
from agency.models import ArangementModel, UserModel
from datetime import datetime, timedelta
from flask_mail import Message
from flask import jsonify, request


def chack_user_is_admin(user):
    if user.current_type != "admin":
        abort(401, message="This request is not allowed to you")


# route: http://127.0.0.1:5000/admin/add_arangement, method POST
# processing requests to add arangements
@app.route("/admin/add_arangement", methods = ['POST'])
@login_required
def create_new_arangement():
    chack_user_is_admin(current_user)

    # parsing the obtained arguments
    args = arangement_create_args.parse_args()

    try:
        # check the args data is correct
        chack_result, chack_message = chack_create_arangement_data(args)
        if not chack_result:
            return jsonify({"message" : chack_message}), 409

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
# GET: processes the request to retrieve the arrangement by id
@app.route("/admin/arangement/<int:arangement_id>", methods = ['PATCH', 'DELETE', 'GET'])
@login_required
def update_arangement(arangement_id):
    chack_user_is_admin(current_user)

    if request.method == "PATCH":
        try:
            # checking that the arangement exists
            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            if not arangement:
                return jsonify({"message" : "Arangement is not exists"}), 404
            
            # check if the arrangement starts in five days
            time_now = datetime.now()
            if (arangement.start_date - time_now < timedelta(days=5)):
                return jsonify({"message" : "Five days until the arrangement"}), 404
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

        args = arangement_update_args.parse_args()

        try:
            chack_result, chack_message = chack_create_arangement_data(args)
            if not chack_result:
                return jsonify({"message" : chack_message}), 409

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
                for guide_arangement in user_guide.guide_arangements:
                    # check if the guide is available at the required time
                    if ((arangement.start_date > guide_arangement.start_date and arangement.start_date < guide_arangement.end_date) or 
                        (arangement.end_date > guide_arangement.start_date and arangement.end_date < guide_arangement.end_date)
                    ):
                        return jsonify({"message": "Guide is reserved."}), 409
                arangement.guide_id = args['guide_id']
            
            db.session.commit()
            return jsonify({"message" : "Arangement is update"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    
    if request.method == "DELETE":
        try:
            arangement = ArangementModel.query.filter_by(id=arangement_id).first()
            if not arangement:
                return jsonify({"message" : "Arangement is not exists"}), 404

            # check if the arrangement starts in five days
            time_now = datetime.now()
            if (arangement.start_date - time_now < timedelta(days=5)):
                return jsonify({"message" : "Five days until the arrangement"}), 404
                
            # an email is sent to users
            for tourist in arangement.tourists:
                try:
                    msg = Message("The arrangement was canceled.", sender="velimirbicanin@gmail.com", recipients=[tourist.email])
                    mail.send(msg)
                except Exception as e:
                    print(e)
                    return jsonify({"message" : "Internal server error"}), 500

            db.session.delete(arangement)
            db.session.commit()
            return jsonify({"message" : "Arrangement has been deleted"}), 200
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

# route: http://127.0.0.1:5000/admin/list_users_req, method GET
# handles the retrieval request of users who want to upgrade the type
@app.route('/admin/list_users_req')
@login_required
def different_type_users():
    chack_user_is_admin(current_user)

    try:
        # search users who want upgrade
        user_like_admin1 = UserModel.query.filter_by(desired_type = 'admin', current_type = 'tourist')
        user_like_admin2 = UserModel.query.filter_by(desired_type = 'admin', current_type = 'guide')
        user_like_guide = UserModel.query.filter_by(desired_type = 'guide', current_type = 'tourist')

        list_user_like_admin1 = [marshal(u.to_json(), user_resource_fields) for u in user_like_admin1]
        list_user_like_admin2 = [marshal(u.to_json(), user_resource_fields) for u in user_like_admin2]
        list_user_like_guide = [marshal(u.to_json(), user_resource_fields) for u in user_like_guide]
        return jsonify(list_user_like_admin1 + list_user_like_admin2 + list_user_like_guide), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/admin/upgrade_type
# PUT: accepts the request for upgrade
# POST: does not accept the request for upgrade
@app.route('/admin/upgrade_type/<int:user_id>', methods = ["PUT", "POST"])
@login_required
def upgrade_user_current_type(user_id):
    chack_user_is_admin(current_user)

    if request.method == 'PUT':
        try :
            user = UserModel.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"message" : "User not exists"}), 404

            user.current_type = user.desired_type
            db.session.commit()
            
            try:
                msg = Message("Your request has been accepted", sender=current_user.email, recipients=[user.email])
                mail.send(msg)
            except Exception as e:
                print(e)
                return jsonify({"message" : "Mail not sent"}), 500
            
            return jsonify({"message" : "Success"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    elif request.method == 'POST':
        try:
            user = UserModel.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"message" : "User not exists"}), 404

            user.desired_type = user.current_type
            db.session.commit()

            try:
                msg = Message(request.form['message'], sender=current_user.email, recipients=[user.email])
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
    chack_user_is_admin(current_user)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    sort = request.args.get('sort', 'id', type=str)
    users_type = request.args.get("type", "all", type=str)

    if users_type == "all":
        try:
            users = UserModel.query.filter_by().order_by(sort).paginate(page=page, per_page=per_page)
            user_list = [marshal(u.to_json(), user_resource_fields) for u in users.items]
            return jsonify(user_list), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif users_type == "tourist":
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
        try:
            guides = UserModel.query.filter_by(current_type="guide")
            guides_with_arangements = []
            for guide in guides:
                guide_arangements = [a.to_json() for a in guide.guide_arangements if a.end_date < datetime.now()]
                guide_json = marshal(guide.to_json(), user_resource_fields)
                guide_json['tourist_arangements'] = guide_arangements
                guides_with_arangements.append(guide_json)
            
            return jsonify(guides_with_arangements), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    
    return jsonify({"message" : "Type not found"}), 404


# route: http://127.0.0.1:5000/my_arangements, method GET
# processes the request for retrieval of its arrangements
@app.route("/admin/my_arangements")
@login_required
def my_arangements():
    chack_user_is_admin(current_user)
    try:
        admin_arangements = ArangementModel.query.filter_by(admin_id = current_user.id)
        admin_arangements_list = [marshal(a.to_json(), arangement_resource_fields) for a in admin_arangements]
        return jsonify(admin_arangements_list), 200
    except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500