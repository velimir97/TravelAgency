from flask_restful import fields as fld
from datetime import datetime, timedelta
from marshmallow import Schema, fields, validate, validates_schema, ValidationError

class ArrangementSchema(Schema):
    start_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S', required=True)
    end_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S', required=True)
    destination = fields.String(validate=validate.Length(min=2, max=50), required=True)
    description = fields.String(validate=validate.Length(min=10), required=True)
    number_of_seats = fields.Integer(validate=validate.Range(min=1), required=True)
    price = fields.Integer(required=True, validate=validate.Range(min=1))

    @validates_schema
    def validate_date(self, data, **kwargs):
        if data['start_date'] < datetime.now() + timedelta(days=5):
            raise ValidationError("Start date is not correct")

        if data['end_date'] < data['start_date']:
            raise ValidationError("End date is not correct")

class ArrangementUpdateSchema(Schema):
    start_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    end_date = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
    destination = fields.String(validate=validate.Length(min=2, max=50))
    description = fields.String(validate=validate.Length(min=10))
    number_of_seats = fields.Integer(validate=validate.Range(min=1))
    price = fields.Integer(validate=validate.Range(min=1))
    guide_id = fields.Integer(validate=validate.Range(min=1))

    @validates_schema
    def validate_date(self, data, **kwargs):
        if 'start_date' in data and 'end_date' in data:    
            if data['start_date'] < datetime.now() + timedelta(days=5):
                raise ValidationError("Start date is not correct")

            if data['end_date'] < data['start_date']:
                raise ValidationError("End date is not correct")
        elif 'start_date' in data or 'end_date' in data:
            raise ValidationError("Start date and end date are required together")


# restriction on arrangement return
arrangement_resource_fields = {
    'id': fld.Integer,
    'start_date': fld.DateTime(),
    'end_date': fld.DateTime,
    'destination': fld.String,
    'price': fld.Integer,
}