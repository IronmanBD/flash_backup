from marshmallow import Schema, fields, ValidationError, pre_load

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class CacusSchema(Schema):
    xshort = fields.Str(required = True, validate=must_not_be_blank)
    xadd1 = fields.Str(required = True, validate = must_not_be_blank)
    xadd2 = fields.Str(required = True, validate = must_not_be_blank)
    xcity = fields.Str(required = True, validate = must_not_be_blank)
    xmobile = fields.Str(required = True, validate = must_not_be_blank)
    xsp = fields.Str(required = True, validate = must_not_be_blank)

cacusSchema = CacusSchema()

class CacusUpdateSchema(Schema):
    xshort = fields.Str(required = True)
    xadd1 = fields.Str(required = True)
    xadd2 = fields.Str(required = True)
    xcity = fields.Str(required = True)
    xmobile = fields.Str(required = True)
    xsp = fields.Str(required = True)
    
cacusUpdateSchema = CacusUpdateSchema()