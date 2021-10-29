from agency import app, db, mail
from flask_login import login_required, current_user
from flask_restful import abort, marshal_with, marshal
from agency.parser.arrangement_parser import arrangement_args, arrangement_resource_fields, arrangement_update_args, check_arrangement_data
from agency.parser.user_parser import user_type_args, user_resource_fields
from agency.models import ArrangementModel, UserModel
from datetime import datetime, timedelta
from flask_mail import Message
from flask import jsonify, request
from math import ceil


def is_admin(user):
    if user.current_type != "admin":
        abort(401, message="This request is not allowed to you")


# route: http://127.0.0.1:5000/admin/add_arrangement
# POST: processing requests to add arrangements
@app.route("/admin/add_arrangement", methods = ['POST'])
@login_required
def create_new_arrangement():
    is_admin(current_user)

    # parsing the obtained arguments
    args = arrangement_args.parse_args()

    try:
        # check the args data is correct
        check_result, check_message = check_arrangement_data(args)
        if not check_result:
            return jsonify({"message" : check_message}), 409

        # creating and entering a new arrangement
        arrangement = ArrangementModel(start_date = datetime.fromisoformat(args['start']),
                                    end_date = datetime.fromisoformat(args['end']),
                                    description = args['description'],
                                    destination = args['destination'],
                                    number_of_seats = args['number_of_seats'],
                                    free_seats = args['number_of_seats'],
                                    price = args['price'],
                                    admin_id = current_user.id
        )

        db.session.add(arrangement)
        db.session.commit()
        return jsonify({"message" : "Successful create arrangement"}), 201
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/admin/free_guides/<int:arrangement_id>
# GET: processing request to retrieving free guides at the time of the arrangement
@app.route("/admin/free_guides/<int:arrangement_id>")
@login_required
def free_guides(arrangement_id):
    is_admin(current_user)

    try:
        # check if the arrangement exists
        arrangement = ArrangementModel.query.filter_by(id=arrangement_id).first()
        if not arrangement:
            return jsonify({"message" : "Arrangement does't not exist"}), 404

        # check if this arrangement is from the current admin
        if arrangement.admin_id != 7:
            return jsonify({"message" : "This arrangement is not from the current admin"})

        list_free_guides = []
        guides = UserModel.query.filter_by(current_type='guide')
        for guide in guides:
            reserved = False
            for guide_arrangement in guide.guide_arrangements:
                if ((arrangement.start_date > guide_arrangement.start_date and arrangement.start_date < guide_arrangement.end_date) or 
                        (arrangement.end_date > guide_arrangement.start_date and arrangement.end_date < guide_arrangement.end_date) or
                        (arrangement.start_date < guide_arrangement.start_date and arrangement.end_date > guide_arrangement.end_date)
                    ):
                    reserved = True
            if not reserved:
                list_free_guides.append(guide)

        return jsonify([marshal(g.to_json(), user_resource_fields) for g in list_free_guides]), 200
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500
            



# route: http://127.0.0.1:5000/admin/arrangement/<int:arrangement_id>
# PATCH: processing requests to update arrangement by id
# DELETE: processing requests to delete arrangement by id
# GET: processing request to retrieve the arrangement by id
@app.route("/admin/arrangement/<int:arrangement_id>", methods = ['PATCH', 'DELETE', 'GET'])
@login_required
def process_arrangement_by_id(arrangement_id):
    is_admin(current_user)

    if request.method == "PATCH":
        try:
            # check if the arrangement exists
            arrangement = ArrangementModel.query.filter_by(id=arrangement_id).first()
            if not arrangement:
                return jsonify({"message" : "Arrangement does't not exist"}), 404
            
            # check if this arrangement is from the current admin
            if arrangement.admin_id != current_user.id:
                return jsonify({"message" : "This arrangement is not from the current admin"})

            # check if the arrangement starts in five days
            time_now = datetime.now()
            if (arrangement.start_date - time_now < timedelta(days=5)):
                return jsonify({"message" : "Five days until the arrangement"}), 404
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

        # parsing the obtained arguments
        args = arrangement_update_args.parse_args()

        try:
            # check if the args data is correct
            check_result, check_message = check_arrangement_data(args)
            if not check_result:
                return jsonify({"message" : check_message}), 409
            
            # updating the values
            if args['start'] != None:
                arrangement.start_date = datetime.fromisoformat(args['start'])
            if args['end'] != None:
                arrangement.end_date = datetime.fromisoformat(args['end'])
            if args['description'] != None:
                arrangement.description = args['description']
            if args['destination'] != None:
                arrangement.destination = args['destination']
            if args['number_of_seats'] != None:
                arrangement.number_of_seats = args['number_of_seats']
            if args['price'] != None:
                arrangement.price = args['price']    
            if args['guide_id'] != None:
                # updating the guide values
                user_guide = UserModel.query.filter_by(id=args['guide_id']).first()
                if not user_guide or user_guide.current_type != 'guide':
                    return jsonify({"message" : "Guide is not found"}), 404
                for guide_arrangement in user_guide.guide_arrangements:
                    # check if the guide is available at the required time
                    if ((arrangement.start_date > guide_arrangement.start_date and arrangement.start_date < guide_arrangement.end_date) or 
                        (arrangement.end_date > guide_arrangement.start_date and arrangement.end_date < guide_arrangement.end_date) or
                        (arrangement.start_date < guide_arrangement.start_date and arrangement.end_date > guide_arrangement.end_date)
                    ):
                        return jsonify({"message": "Guide is reserved."}), 409
                arrangement.guide_id = args['guide_id']
            
            db.session.commit()
            return jsonify({"message" : "Arrangement is updated"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    
    if request.method == "DELETE":
        try:
            arrangement = ArrangementModel.query.filter_by(id=arrangement_id).first()
            if not arrangement:
                return jsonify({"message" : "Arrangement does't exist"}), 404

            # check if the arrangement starts in five days
            time_now = datetime.now()
            if (arrangement.start_date - time_now < timedelta(days=5)):
                return jsonify({"message" : "Five days until the arrangement"}), 404
                
            # an email is sent to users
            for tourist in arrangement.tourists:
                try:
                    msg = Message("The arrangement was canceled.", sender=app.config.get("MAIL_USERNAME") , recipients=[tourist.email])
                    mail.send(msg)
                except Exception as e:
                    print(e)
                    return jsonify({"message" : "Mails not sent"}), 500

            db.session.delete(arrangement)
            db.session.commit()
            return jsonify({"message" : "Arrangement has been deleted"}), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    if request.method == "GET":
        try:
            arrangement = ArrangementModel.query.filter_by(id=arrangement_id).first()
            if not arrangement:
                return jsonify({"message" : "Arrangement not found"}), 404
            return jsonify(arrangement.to_json()), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500

    return jsonify({"message" : "Method not found"}), 404

# route: http://127.0.0.1:5000/admin/users_reqs
# GET: handles the retrieval request of users who want to upgrade the type
@app.route('/admin/users_reqs')
#@login_required
def get_users_requirement():
    #is_admin(current_user)

    try:
        # search users who want upgrade
        user_reqs = db.session.query(UserModel).filter(UserModel.desired_type != UserModel.current_type).all()
        return jsonify([marshal(u.to_json(), user_resource_fields) for u in user_reqs])
    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500


# route: http://127.0.0.1:5000/admin/response_type
# PATCH: accepting or rejecting user requests for upgrade type
@app.route('/admin/response_type/<int:user_id>', methods = ["PATCH"])
#@login_required
def process_user_requirement(user_id):
    #is_admin(current_user)

    try :
        new_type = request.form.get("new_type", "none", type=str)
        if new_type not in ['tourist', 'guide', 'admin']:
            return jsonify({"message" : "New type is require"}), 409

        # check the user exist
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message" : "User not exists"}), 404

        if new_type == user.desired_type:
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
        elif new_type == user.current_type:
            msg = request.form.get("message", "", type=str)
            if msg == "":
                return jsonify({"message" : "Message is require"}), 409

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
        else:
            return jsonify({"message" : "The new type is not correct"}), 409

    except Exception as e:
        print(e)
        return jsonify({"message" : "Internal server error"}), 500

# route: http://127.0.0.1:5000/users, method GET
# processing requests to get all users or get user by type
@app.route('/admin/users')
#@login_required
def all_users_by_type():
    #is_admin(current_user)

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
            tourists_with_arrangements = []
            for tourist in tourists:
                tourist_arrangements = [a.to_json() for a in tourist.tourist_arrangements]
                tourist_json = marshal(tourist.to_json(), user_resource_fields)
                tourist_json['tourist_arrangements'] = tourist_arrangements
                tourists_with_arrangements.append(tourist_json)
            
            return jsonify(tourists_with_arrangements), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    elif users_type == "guide":
        # getting guide users
        try:
            guides = UserModel.query.filter_by(current_type="guide")
            guides_with_arrangements = []
            for guide in guides:
                guide_arrangements = [a.to_json() for a in guide.guide_arrangements if a.end_date < datetime.now()]
                guide_json = marshal(guide.to_json(), user_resource_fields)
                guide_json['guide_arrangements'] = guide_arrangements
                guides_with_arrangements.append(guide_json)
            
            return jsonify(guides_with_arrangements), 200
        except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500
    
    return jsonify({"message" : "Type not found"}), 404


# route: http://127.0.0.1:5000/my_arrangements
# GET: processes the request for retrieval of its arrangements
@app.route("/admin/my_arrangements")
@login_required
def admins_arrangements():
    is_admin(current_user)
    try:
        admin_arrangements = ArrangementModel.query.filter_by(admin_id = current_user.id)
        admin_arrangements_list = [marshal(a.to_json(), arrangement_resource_fields) for a in admin_arrangements]
        return jsonify(admin_arrangements_list), 200
    except Exception as e:
            print(e)
            return jsonify({"message" : "Internal server error"}), 500