from marshmallow import Schema, fields, ValidationError, pre_load

def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')

class UserRegSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required = True)
    email = fields.Str(required = True)
    mobile = fields.Str(required = True)
    businessId = fields.Int(required = True, validate=must_not_be_blank)
    employeeCode = fields.Str(required = True, validate=must_not_be_blank)
    is_admin = fields.Str(required = True)

userRegSchema = UserRegSchema()

class UserLoginSchema(Schema):
    username = fields.Str(required=True, validate=must_not_be_blank)
    password = fields.Str(required = True, validate = must_not_be_blank)

userLogSchema = UserLoginSchema()

class UserFreshSchema(Schema):
    password = fields.Str(required = True, validate = must_not_be_blank)

userFreshSchema = UserFreshSchema()

class UserUpdateSchema(Schema):
    password = fields.Str(required = True)
    email = fields.Str(required = True)
    mobile = fields.Str(required = True)

updateUserSchema = UserUpdateSchema()

class HierarchySchema(Schema):
    username = fields.Str(required=True, validate=must_not_be_blank)
    business_Id = fields.Int(required = True, validate = must_not_be_blank)
    employee_code = fields.Str(required = True, validate = must_not_be_blank)
    employee_name = fields.Str(required = True, validate = must_not_be_blank)
    child_of_code = fields.Str(required = True)
    child_of_name = fields.Str(required = True)

hierarchySchema = HierarchySchema()

class HierarchyUpdateSchema(Schema):
    business_Id = fields.Int(required = True, validate = must_not_be_blank)
    employee_code = fields.Str(required=True, validate=must_not_be_blank)
    child_of_code = fields.Str(required=True)
    child_of_name = fields.Str(required=True)

hierarchyUpdateSchema = HierarchyUpdateSchema()

class VbusinessSchema(Schema):
    business_Id = fields.Int(required=True,validate=must_not_be_blank)

vbusinessSchema = VbusinessSchema()
