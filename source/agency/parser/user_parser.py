from flask_restful import reqparse, fields
import re
from agency.models import UserModel

# defining a registration parser 
user_registration_args = reqparse.RequestParser()
user_registration_args.add_argument("name", type=str, help="Name is required", required=True)
user_registration_args.add_argument("surname", type=str, help="Surname is required", required=True)
user_registration_args.add_argument("email", type=str, help="Email is required", required=True)
user_registration_args.add_argument("username", type=str, help="Username is required", required=True)
user_registration_args.add_argument("password1", type=str, help="Password is required", required=True)
user_registration_args.add_argument("password2", type=str, help="Password is required", required=True)
user_registration_args.add_argument("desired_type", type=str, help="Desired type is required", required=True)

def check_user_data(args):
    if args['name'] != None and (len(args['name']) > 50 or len(args['name']) < 2):
        return False, "Name is not correct"
    
    if args['surname'] != None and (len(args['surname']) > 50 or len(args['surname']) < 2):
        return False, "Surname is not correct"

    if args['email']:
        regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Z|a-z]{2,}'
        if not re.fullmatch(regex, args['email']) or len(args['email']) > 50:
            return False, "Email is not correct"

        # check if the user(email) is already registered 
        check_email = UserModel.query.filter_by(email=args['email']).first()
        if check_email:
            return False, "Email exists ..."

    if args['username']:
        if len(args['username']) > 50 or ' ' in args['username']:
            return False, "Username is not correct"

        # check if the user(username) is already registered 
        check_username = UserModel.query.filter_by(username=args['username']).first()
        if check_username:
            return False, "Username exists ..."

    # check that both passwords are the same
    if args['password1'] != None and args['password2'] != None and (args['password1'] != args['password2'] or len(args['password1']) < 4):
        return False, "Passwords are not equal"
    
    if args['desired_type'] != None and args['desired_type'] not in ['admin', 'tourist', 'guide']:
        return False, "Desired type is not correct"

    return True, "Data is fine"


user_update_args = reqparse.RequestParser()
user_update_args.add_argument("name", type=str)
user_update_args.add_argument("surname", type=str)
user_update_args.add_argument("email", type=str)
user_update_args.add_argument("username", type=str)
user_update_args.add_argument("password1", type=str)
user_update_args.add_argument("password2", type=str)

# define a login parser 
user_login_args = reqparse.RequestParser()
user_login_args.add_argument("username", type=str, help="Username is required", required=True)
user_login_args.add_argument("password", type=str, help="Password is required", required=True)

user_type_args = reqparse.RequestParser()
user_type_args.add_argument("type", type=str, help="Type is required", required=True)

user_reserve_args = reqparse.RequestParser()
user_reserve_args.add_argument("arangement_id", type=int, help="Id is required", required=True)
user_reserve_args.add_argument("number_of_persons", type=int, help="Number of persons is required", required=True)

# restriction on user return
user_resource_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'name': fields.String,
    'surname': fields.String,
    'email': fields.String,
    'desired_type': fields.String,
    'current_type': fields.String,
}