from flask_restful import reqparse, fields

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


# restriction on arangement return
arangement_resource_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'destination': fields.String,
    'price': fields.Integer,
    'free_seats': fields.Integer
}