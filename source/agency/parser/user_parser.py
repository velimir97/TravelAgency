from flask_restful import fields as fld
from agency.models import UserModel
from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema

class UserSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=50), required=True)
    surname = fields.String(validate=validate.Length(min=2, max=50), required=True)
    email = fields.Email(required=True)
    username = fields.String(validate=validate.Length(min=2, max=50), required=True)
    password1 = fields.String(required=True, validate=validate.Length(min=6, max=20))
    password2 = fields.String(required=True, validate=validate.Length(min=6, max=20))
    desired_type = fields.String(required=True, validate=validate.OneOf(['tourist', 'guide', 'admin']))

    @validates('email')
    def validate_email(self, email):
        check_email = UserModel.query.filter_by(email=email).first()
        if check_email:
            raise ValidationError("Email exists ...")

    @validates('username')
    def validate_username(self, username):
        if ' ' in username:
            raise ValidationError('Username is not correct')

        check_username = UserModel.query.filter_by(username=username).first()
        if check_username:
            raise ValidationError('Username exists ...')

    @validates_schema
    def validate_passwords_equal(self, data, **kwargs):
        if data['password1'] != data['password2']:
            raise ValidationError('Passwords are not equal')

class UserUpdateSchema(Schema):
    name = fields.String(validate=validate.Length(min=2, max=50))
    surname = fields.String(validate=validate.Length(min=2, max=50))
    email = fields.Email()
    username = fields.String(validate=validate.Length(min=2, max=50))
    password1 = fields.String(validate=validate.Length(min=6, max=20))
    password2 = fields.String(validate=validate.Length(min=6, max=20))

    @validates('email')
    def validate_email(self, email):
        check_email = UserModel.query.filter_by(email=email).first()
        if check_email:
            raise ValidationError("Email exists ...")

    @validates('username')
    def validate_username(self, username):
        if ' ' in username:
            raise ValidationError('Username is not correct')

        check_username = UserModel.query.filter_by(username=username).first()
        if check_username:
            raise ValidationError('Username exists ...')

    @validates_schema
    def validate_passwords_equal(self, data, **kwargs):
        if 'password1' in data and 'password2' in data:
            if data['password1'] != data['password2']:
                raise ValidationError('Passwords are not equal')
        elif 'password1' in data or 'password2' in data:
            raise ValidationError('Password1 and password2 are required together')


# restriction on user return
user_resource_fields = {
    'id': fld.Integer,
    'username': fld.String,
    'name': fld.String,
    'surname': fld.String,
    'email': fld.String,
    'desired_type': fld.String,
    'current_type': fld.String
}