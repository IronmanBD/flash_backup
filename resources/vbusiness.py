from flask import request
from flask_restful import Resource
from flask_jwt_extended import (jwt_required, fresh_jwt_required,
                                jwt_refresh_token_required,get_jwt_claims, get_jwt_identity)

from marshmallow import ValidationError
import datetime

from models.zbusiness import ZbusinessModel
from models.hierarchy import HierarchyModel
from models.vbusiness import VbusinessModel
from schemas.users import vbusinessSchema


class Vbusiness(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_superuser']:
            return {'message': 'superuser previlege required'},400

        vbusinessDetail = VbusinessModel.find_all_business()

        return [vbusDetail.json() for vbusDetail in vbusinessDetail],200


    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['is_superuser']:
            return {'message': 'superuser previlege required'},400

        json_data = request.get_json()
        print(json_data)

        if not json_data:
            return {'message': 'No input data provided'},400

        try:
            data = vbusinessSchema.load(json_data).data
        except ValidationError as err:
            return {'message':err.messages},400

        if VbusinessModel.find_by_zid(data['business_Id']):
            return {'message':'This Business has already been registered'},400
        
        if not ZbusinessModel.find_by_businessId(data['business_Id']):
            return {'message':'This Business does not exist in your system'},400

        ztime = datetime.datetime.now()

        vbusinessDetail = VbusinessModel(
                                        ztime=ztime,
                                        zid=data['business_Id']
                                        )

        try:
            vbusinessDetail.save_to_db()
        except Exception as e:
            print(e)
            return {"message":"An error occured inserting the customer"},400

        return vbusinessDetail.json(),200

class VbusinessDelete(Resource):
    @jwt_required
    def delete (self, business_Id):
        claims = get_jwt_claims()
        if not claims['is_superuser']:
            return {'message': 'admin previlige required'},400

        vbusinessDetail = VbusinessModel.find_by_zid(business_Id)

        if vbusinessDetail:
            vbusinessDetail.delete_from_db()

        return {'message':'Business has been deleted, Admin/Users cannot access information from these businesses anymore'},200

class VbusinessNonapproved(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_superuser']:
            return {'message': 'superuser previlege required'},400

        zbusinessDetail = [zbusDetail.json() for zbusDetail in ZbusinessModel.find_all_business()]

        vbusinessDetail = [vbusDetail.json() for vbusDetail in VbusinessModel.find_all_business()]

        vbusinessList = [z['business_id'] for z in vbusinessDetail]
        zbusinessDict = [d for d in zbusinessDetail if d['business_id'] not in vbusinessList]


        return zbusinessDict,200

class VbusinessRegular(Resource):
    def get(self):
        vbusinessDetail = VbusinessModel.find_all_business()

        return [vbusDetail.json() for vbusDetail in vbusinessDetail],200
