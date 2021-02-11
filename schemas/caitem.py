from marshmallow import Schema, fields, ValidationError, pre_load

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class CategorySchema(Schema):
    approvedCategory = fields.Str(required = True, validate=must_not_be_blank)


categorySchema = CategorySchema()

