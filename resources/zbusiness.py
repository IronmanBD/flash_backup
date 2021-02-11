from flask import request
from flask_restful import Resource
from flask_jwt_extended import (jwt_required, fresh_jwt_required,jwt_refresh_token_required,
                                get_jwt_claims,get_jwt_identity)
from models.zbusiness import ZbusinessModel

from app.tasks import receive_from_client_db

class ZbusinessList(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_superuser']:
            print(claims)
            return {'message': 'Error # 28, zbusiness page, You are not authorized to see the business id list'},400
        try:
            print("******************************************Call Received in Zbusiness*************************************") 
            receive_from_client_db(ZbusinessModel.__tablename__, ZbusinessModel.__table__.c.keys())
        except Exception as e:
            print(e)
        
        return 'Business List Synced'
