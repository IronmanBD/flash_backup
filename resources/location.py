from flask import request
from flask_restful import Resource
from flask_jwt_extended import (jwt_required, fresh_jwt_required,jwt_refresh_token_required,
                                get_jwt_claims,get_jwt_identity)
from models.location import LocationModel
from models.vbusiness import VbusinessModel
from schemas.location import LocationSchema

class LocationUpdate(Resource):
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Location Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())
        approved_zid_list = VbusinessModel.find_all_business_list()

        if username.businessId not in approved_zid_list:
            return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400
        
        json_data = request.get_json()

        if not json_data:
            return {'message': 'No input data provided'},400

        try:
            data = opmobSchemas.load(json_data).data
        except ValidationError as err:
            return err.messages,400

        locationDetail = LocationModel(
            ztime = data['ztime'],
            zid = username.businessId,
            xemp = username.employeeCode,
            xlat = data['xlat'],
            xlong = data['xlong']
        )

        try:
            locationDetail.save_to_db()
            return {'message':'Location Saved'},200
        except:
            return {'message':'Something went wrong'},400

# class LocationList(Resource):
#     @jwt_required
#     def get(self):
#         claims = get_jwt_claims()
#         if not claims['active']:
#             return {'message': 'Error # 25 in Location Resource, You have not been activated by the admin'})

#         locationList = [location.json() for location in LocationModel.find_by_xemp()]

#         return [business.json() for business in ZbusinessModel.find_all_business()])
