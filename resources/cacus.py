from flask import request
from marshmallow import ValidationError
from flask_restful import Resource, reqparse
from sqlalchemy import func
import datetime
import ast
from flask_jwt_extended import (jwt_required,fresh_jwt_required,get_jwt_claims,get_jwt_identity)

from db import db

from .increment import increment
from models.cacus import CacusModel
from models.users import UserModel
from models.vbusiness import VbusinessModel
from models.hierarchy import HierarchyModel
from models.hrmst import HrmstModel
from schemas.cacus import cacusSchema,cacusUpdateSchema

from app.tasks import receive_from_client_db



class Cacus(Resource):
    @jwt_required
    def get(self,businessId,customerId):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 21 in Customer Resource, You have not been activated by the admin'},400

        approved_zid_list = VbusinessModel.find_all_business_list()

        if businessId not in approved_zid_list:
            return {'message': 'Error # 24 in Customer Resource, You have not been authorized to use this business'},400

        customer = CacusModel.find_by_customerId(businessId,customerId)

        if customer:
            return customer.json(),200
        return {'message':'Response # 30 in Customer Resource, Customer not found'},400

    @jwt_required
    def post(self, businessId, customerId):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Error # 41 in Customer Resource, admin previlege required'},400

        approved_zid_list = VbusinessModel.find_all_business_list()

        if businessId not in approved_zid_list:
            return {'message': 'Error # 46 in Customer Resource, You have not been authorized to use this business'},400

        customerId = str(db.session.query(func.max(CacusModel.xcus)).filter_by(zid=businessId).first())

        customerId = increment(customerId)

        if CacusModel.find_by_customerId(businessId, customerId):
            return {'message':"Error # 54 in Customer Resource, An item with name '{}' already exists.".format(customerId)},400

        json_data = request.get_json()

        if not json_data:
            return {'message': 'Error # 59 in Customer Resource, No input data provided'},400

        try:
            data = cacusSchema.load(json_data).data
        except ValidationError as err:
            return err.messages,400

        ztime = datetime.datetime.now()
        zutime = datetime.datetime.now()
        xdate = datetime.datetime.today()

        customerDetail = CacusModel(
                                    zid=businessId,
                                    ztime=ztime,
                                    zutime=zutime,
                                    xcus=customerId,
                                    xshort=data['xshort'],
                                    xadd1=data['xadd1'],
                                    xadd2=data['xadd2'],
                                    xcity=data['xcity'],
                                    xmobile=data['xmobile'],
                                    xsp=data['xsp']
                                    )

        try:
            customerDetail.save_to_db()

        except Exception as e:
            print(e)
            return {"message":"Error # 86 in Customer Resource, An error occured inserting the customer"},400

        return customerDetail.json(),200

    @jwt_required
    def put (self, businessId ,customerId):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Error # 94 in Customer Resource, admin previlige required'},400

        approved_zid_list = VbusinessModel.find_all_business_list()

        if businessId not in approved_zid_list:
            return {'message': 'Error # 99 in Customer Resource, You have not been authorized to use this business'},400

        json_data = request.get_json()

        if not json_data:
            return {'message': 'Error # 104 in Customer Resource, No input data provided'},400

        try:
            data = cacusUpdateSchema.load(json_data).data
        except ValidationError as err:
            return {'message': 'Error # 109 in Customer Resource, Validation error in Schemas'},400

        ztime = datetime.datetime.now()
        zutime = datetime.datetime.now()
        xdate = datetime.datetime.now()

        customerDetail = CacusModel.find_by_customerId(businessId,customerId)

        if customerDetail is None:
            customerDetail = CacusModel(
                                        zid=businessId,
                                        ztime=ztime,
                                        zutime=zutime,
                                        xcus=customerId,
                                        xshort=data['xshort'],
                                        xadd1=data['xadd1'],
                                        xadd2=data['xadd2'],
                                        xcity=data['xcity'],
                                        xmobile=data['xmobile'],
                                        xsp = data['xsp']
                                        )
        else:
            customerDetail.zid=businessId
            customerDetail.zutime=zutime
            customerDetail.xdate=xdate
            customerDetail.xcus=customerId
            customerDetail.xshort=data['xshort']
            customerDetail.xadd1=data['xadd1']
            customerDetail.xadd2=data['xadd2']
            customerDetail.xcity=data['xcity']
            customerDetail.xmobile=data['xmobile']
            customerDetail.xsp = data['xsp']

        try:
            customerDetail.save_to_db()
        except Exception as e:
            print (e)
            return {"message":"Error # 145 in Customer Resource, An error update the customer"},400

        return customerDetail.json(),200

    @jwt_required
    def delete (self, businessId, customerId):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Error # 151 in Customer Resource, admin previlige required'},400

        approved_zid_list = VbusinessModel.find_all_business_list()

        if businessId not in approved_zid_list:
            return {'message': 'Error # 156 in Customer Resource, You have not been authorized to use this business'},400

        customerDetail = CacusModel.find_by_customerId(businessId,customerId)

        if customerDetail:
            customerDetail.delete_from_db()

        return {'message':'Response # 163 in Customer Resources, Customer has been deleted'},200


class CacusList(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())

        if not claims['is_superuser']:
            approved_zid_list = VbusinessModel.find_all_business_list()

            if username.businessId not in approved_zid_list:
                return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400
        else:
            employee_code_list = HrmstModel.find_all_employee_list()
            return [cus.json() for cus in CacusModel.find_customers_by_sp(employee_code_list)],200

        try:
            child_list = HierarchyModel.find_by_child_of_code_single_user(username.employeeCode)
            child_list = [hier.json()['employee_code'] for hier in child_list]
        except Exception as e:
            print(e)

        if len(child_list) == 0:
            final_list = [username.employeeCode]
        else:
            try:
                full_list = HierarchyModel.find_all_hierarchy()
                full_list = [{'child':hier.json()['employee_code'],'parent':hier.json()['child_of_code']} for hier in full_list]
            except Exception as e:
                print(e)

            final_list = [username.employeeCode]
            for i in final_list:
                for j in full_list:
                    if i == j['parent']:
                        final_list.append(j['child'])
        
        return [cus.json() for cus in CacusModel.find_customers_by_sp(final_list)],200

class CacusCelery(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        print(claims)
        if not claims['active']:
            return {'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'},400
        try:
            receive_from_client_db(CacusModel.__tablename__, CacusModel.__table__.c.keys())
        except Exception as e:
            print(e)
        
        return 'customer data synced'



class CacusRowCount(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())

        if not claims['is_superuser']:
            approved_zid_list = VbusinessModel.find_all_business_list()

            if username.businessId not in approved_zid_list:
                return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400
        else:
            employee_code_list = HrmstModel.find_all_employee_list()
            return {'Number of Customers':len([cus.json() for cus in CacusModel.find_customers_by_sp(employee_code_list)])},200

        try:
            child_list = HierarchyModel.find_by_child_of_code_single_user(username.employeeCode)
            child_list = [hier.json()['employee_code'] for hier in child_list]
        except Exception as e:
            print(e)

        if len(child_list) == 0:
            final_list = [username.employeeCode]
        else:
            try:
                full_list = HierarchyModel.find_all_hierarchy()
                full_list = [{'child':hier.json()['employee_code'],'parent':hier.json()['child_of_code']} for hier in full_list]
            except Exception as e:
                print(e)

            final_list = [username.employeeCode]
            for i in final_list:
                for j in full_list:
                    if i == j['parent']:
                        final_list.append(j['child'])

        return {'Number of Customers':len([cus.json() for cus in CacusModel.find_customers_by_sp(final_list)])},200


# class CacusList(Resource):
#     @jwt_required
#     def get(self):
#         claims = get_jwt_claims()
#         if not claims['active']:
#             return jsonify({'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'})

#         current_user = UserModel.find_by_user(get_jwt_identity())

#         if not claims['is_superuser']:
#             approved_zid_list = VbusinessModel.find_all_business_list()

#             if current_user.businessId not in approved_zid_list:
#                 return jsonify({'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'})
#         else:
#             employee_code_list = HrmstModel.find_all_employee_list()
#             return jsonify([cus.json() for cus in CacusModel.find_customers_by_sp(employee_code_list)])

#         child_list = [child.employee_code for child in HierarchyModel.find_by_child_of_code_single_user(current_user.employeeCode)]

#         if len(child_list) == 0:
#             child_list = [current_user.employeeCode]

#         return jsonify([cus.json() for cus in CacusModel.find_customers_by_sp(child_list)])
