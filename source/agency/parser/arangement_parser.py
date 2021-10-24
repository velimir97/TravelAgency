from flask_restful import reqparse, fields
from datetime import datetime, timedelta


# defining a parser for entering arangements
arangement_args = reqparse.RequestParser()
arangement_args.add_argument("start", help="Date of start arangement is required", required=True)
arangement_args.add_argument("end", help="Date of end arangement is required", required=True)
arangement_args.add_argument("description", type=str, help="Description is required", required=True)
arangement_args.add_argument("destination", type=str, help="Destination is required", required=True)
arangement_args.add_argument("number_of_seats", type=int, help="Number of seats is required", required=True)
arangement_args.add_argument("price", type=int, help="Price is required", required=True)

def check_arangement_data(args):
    if args['start'] and args['end']:
        try:
            datetime.fromisoformat(args['start'])
            datetime.fromisoformat(args['end'])
        except ValueError:
            return False, "Date is not correct"

        if datetime.fromisoformat(args['start']) < datetime.now() + timedelta(days=5):
            return False, "Start date is not correct"

        if datetime.fromisoformat(args['end']) < datetime.now() + timedelta(days=5) or datetime.fromisoformat(args['end']) < datetime.fromisoformat(args['start']):
            return False, "End date is not corrent"
    elif args['start'] or args['end']:
        return False, "Both dates must be entered"

    if args['description'] != None and len(args['description']) < 10:
        return False, "Description is not correct"

    if args['destination'] != None and (len(args['destination']) < 2 or len(args['destination']) > 50):
        return False, "Destination is not corrent"

    if args['number_of_seats'] != None and args['number_of_seats'] == 0:
        return False, "Number of seats is not correct"
    
    return True, "Data is correct"

arangement_update_args = reqparse.RequestParser()
arangement_update_args.add_argument("start")
arangement_update_args.add_argument("end")
arangement_update_args.add_argument("description", type=str)
arangement_update_args.add_argument("destination", type=str)
arangement_update_args.add_argument("number_of_seats", type=int)
arangement_update_args.add_argument("price", type=int)
arangement_update_args.add_argument("guide_id", type=int)

arangement_search_args = reqparse.RequestParser()
arangement_search_args.add_argument("start", help="Start date is required")
arangement_search_args.add_argument("end", help="End date is required")
arangement_search_args.add_argument("destination", type=str, help="Destination is required")

# restriction on arangement return
arangement_resource_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'destination': fields.String,
    'price': fields.Integer,
}