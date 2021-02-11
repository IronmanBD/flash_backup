from marshmallow import Schema, fields, ValidationError, pre_load

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class OpmobItemSchema(Schema):
    xitem = fields.Str(required = True, validate = must_not_be_blank)
    xqty = fields.Int(required = True, validate = must_not_be_blank)

class OpmobSchema(Schema):
    zid = fields.Int(required=True, validate=must_not_be_blank)
    xcus = fields.Str(required = True, validate = must_not_be_blank)
    order = fields.Nested(OpmobItemSchema,only=['xitem','xqty'], many = True)
    xlat = fields.Float(required = True, validate = must_not_be_blank)
    xlong = fields.Float(required = True, validate = must_not_be_blank)

opmobSchemas = OpmobSchema(many=True)