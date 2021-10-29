from flask_restful import reqparse, fields
from datetime import datetime, timedelta


# defining a parser for entering arrangements
arrangement_args = reqparse.RequestParser()
arrangement_args.add_argument("start", help="Date of start arrangement is required", required=True)
arrangement_args.add_argument("end", help="Date of end arrangement is required", required=True)
arrangement_args.add_argument("description", type=str, help="Description is required", required=True)
arrangement_args.add_argument("destination", type=str, help="Destination is required", required=True)
arrangement_args.add_argument("number_of_seats", type=int, help="Number of seats is required", required=True)
arrangement_args.add_argument("price", type=int, help="Price is required", required=True)

def check_arrangement_data(args):
    if args['start'] and args['end']:
        try:
            datetime.fromisoformat(args['start'])
            datetime.fromisoformat(args['end'])
        except ValueError:
            return False, "Date is not correct"

        if datetime.fromisoformat(args['start']) < datetime.now() + timedelta(days=5):
            return False, "Start date is not correct"

        if datetime.fromisoformat(args['end']) < datetime.now() + timedelta(days=5) or datetime.fromisoformat(args['end']) < datetime.fromisoformat(args['start']):
            return False, "End date is not correct"
    elif args['start'] or args['end']:
        return False, "Both dates must be entered"

    if args['description'] != None and len(args['description']) < 10:
        return False, "Description is not correct"

    if args['destination'] != None and (len(args['destination']) < 2 or len(args['destination']) > 50):
        return False, "Destination is not correct"

    if args['number_of_seats'] != None and args['number_of_seats'] == 0:
        return False, "Number of seats is not correct"
    
    return True, "Data is correct"

arrangement_update_args = reqparse.RequestParser()
arrangement_update_args.add_argument("start")
arrangement_update_args.add_argument("end")
arrangement_update_args.add_argument("description", type=str)
arrangement_update_args.add_argument("destination", type=str)
arrangement_update_args.add_argument("number_of_seats", type=int)
arrangement_update_args.add_argument("price", type=int)
arrangement_update_args.add_argument("guide_id", type=int)

arrangement_search_args = reqparse.RequestParser()
arrangement_search_args.add_argument("start", help="Start date is required")
arrangement_search_args.add_argument("end", help="End date is required")
arrangement_search_args.add_argument("destination", type=str, help="Destination is required")

# restriction on arrangement return
arrangement_resource_fields = {
    'id': fields.Integer,
    'start_date': fields.DateTime,
    'end_date': fields.DateTime,
    'destination': fields.String,
    'price': fields.Integer,
}