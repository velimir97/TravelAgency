from flask_restful import reqparse, fields
import datetime

def chack_user_type(user, allowed_type):
    return user.current_type == allowed_type

# defining a registration parser 
user_post_args = reqparse.RequestParser()
user_post_args.add_argument("name", type=str, help="Name is required", required=True)
user_post_args.add_argument("surname", type=str, help="Surname is required", required=True)
user_post_args.add_argument("email", type=str, help="Email is required", required=True)
user_post_args.add_argument("username", type=str, help="Username is required", required=True)
user_post_args.add_argument("password1", type=str, help="Password is required", required=True)
user_post_args.add_argument("password2", type=str, help="Password is required", required=True)
user_post_args.add_argument("desired_type", type=str, help="Desired type is required", required=True)

user_update_args = reqparse.RequestParser()
user_update_args.add_argument("name", type=str)
user_update_args.add_argument("surname", type=str)
user_update_args.add_argument("email", type=str)
user_update_args.add_argument("username", type=str)
user_update_args.add_argument("password1", type=str)
user_update_args.add_argument("password2", type=str)

user_update_type_args = reqparse.RequestParser()
user_update_type_args.add_argument("type", type=str, help="Type is required", required=True)

# define a login parser 
user_login_args = reqparse.RequestParser()
user_login_args.add_argument("username", type=str, help="Username is required", required=True)
user_login_args.add_argument("password", type=str, help="Password is required", required=True)

user_type_args = reqparse.RequestParser()
user_type_args.add_argument("type", type=str, help="Type is required", required=True)

user_reserve_args = reqparse.RequestParser()
user_reserve_args.add_argument("arangement_id", type=int, help="Id is required", required=True)
user_reserve_args.add_argument("number_of_persons", type=int, help="Number of persons is required", required=True)

# defining a parser for entering arrangements 
arangement_post_args = reqparse.RequestParser()
arangement_post_args.add_argument("start", help="Date of start arangement is required", required=True)
arangement_post_args.add_argument("end", help="Date of end arangement is required", required=True)
arangement_post_args.add_argument("description", type=str, help="Description is required", required=True)
arangement_post_args.add_argument("destination", type=str, help="Destination is required", required=True)
arangement_post_args.add_argument("number_of_seats", type=int, help="Number of seats is required", required=True)
arangement_post_args.add_argument("price", type=int, help="Price is required", required=True)

arangement_update_args = reqparse.RequestParser()
arangement_update_args.add_argument("start")
arangement_update_args.add_argument("end")
arangement_update_args.add_argument("description", type=str)
arangement_update_args.add_argument("destination", type=str)
arangement_update_args.add_argument("number_of_seats", type=int)
arangement_update_args.add_argument("price", type=int)
arangement_update_args.add_argument("guide_id", type=int)

arangement_search_args = reqparse.RequestParser()
arangement_search_args.add_argument("start", help="Date of start arangement is required", required=True)
arangement_search_args.add_argument("end", help="Date of end arangement is required", required=True)
arangement_search_args.add_argument("destination", type=str, help="Destination is required", required=True)

arangement_update_desc_args = reqparse.RequestParser()
arangement_update_desc_args.add_argument("description", help="Description is required", required=True)

# restriction on user return
user_resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'email': fields.String,
    'desired_type': fields.String,
    'current_type': fields.String,
}

# restriction on arangement return
arangement_resource_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'destination': fields.String,
    'price': fields.Integer,
    'free_seats': fields.Integer
}