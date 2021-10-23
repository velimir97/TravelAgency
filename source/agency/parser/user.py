from flask_restful import reqparse, fields

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

# restriction on user return
user_resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'surname': fields.String,
    'email': fields.String,
    'desired_type': fields.String,
    'current_type': fields.String,
}