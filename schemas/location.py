from marshmallow import Schema, fields, ValidationError, pre_load

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class LocationSchema(Schema):
    ztime = fields.DateTime(required = True, validate = must_not_be_blank)
    xlat = fields.Float(required = True, validate = must_not_be_blank)
    xlong = fields.Float(required = True, validate = must_not_be_blank)