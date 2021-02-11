from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import func
import datetime
from flask_jwt_extended import (jwt_required,fresh_jwt_required,get_jwt_claims,get_jwt_identity)
import html

from db import db
from .increment import increment
from models.caitem import CaitemModel
from models.users import UserModel
from models.vbusiness import VbusinessModel
from models.category import CategoryModel
from models.opspprc import OpspprcModel

from app.tasks import receive_from_client_db

from schemas.caitem import categorySchema

class Caitem(Resource):
    @jwt_required
    def get(self, businessId ,productCode):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 21 in Product Resource, You have not been activated by the admin'},400

        product = CaitemModel.find_by_productCode(businessId, productCode)

        if product:
            final_product = [product.json() for product in CaitemModel.find_by_productCode(businessId, productCode)]
            return final_product,200
        return {'message':'Error # 27 in Product Resource, Product not found'},400

class CaitemList(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 34 in Product Resource, You have not been activated by the admin'},400

        current_user = UserModel.find_by_user(get_jwt_identity())

        if not claims['is_superuser']:
            approved_zid_list = VbusinessModel.find_all_business_list()

            business_Id_list = [current_user.businessId]
            if current_user.businessId not in approved_zid_list:
                return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400
        else:
            business_Id_list = VbusinessModel.find_all_business_list()

        category_list = CategoryModel.find_all_category_list()

        all_items = [{'product_Code':item.json()['product_Code'],
                        'product_Name':item.json()['product_Name'],
                        'product_Category':item.json()['product_Category'],
                        'Sales_Price':item.json()['Sales_Price'],
                        'Unit':item.json()['Unit']}
                        for item in CaitemModel.find_by_zid_category(business_Id_list,category_list)]

        all_priceCat = [{'productCatCode':cat.json()['productCatCode'],
                        'sp_priceQty':cat.json()['sp_priceQty'],
                        'discountAmount':cat.json()['discountAmount']}
                        for cat in OpspprcModel.find_by_priceCat_all(business_Id_list)]

        for i in all_items:
            i['sp_priceQty'] = 0
            i['discountAmount'] = 0
            for j in all_priceCat:
                if i['product_Code'] == j['productCatCode']:
                    i['sp_priceQty'] = j['sp_priceQty']
                    i['discountAmount'] = j['discountAmount']

        return all_items,200

class CaitemRowCount(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 34 in Product Resource, You have not been activated by the admin'},400

        current_user = UserModel.find_by_user(get_jwt_identity())

        if not claims['is_superuser']:
            approved_zid_list = VbusinessModel.find_all_business_list()

            business_Id_list = [current_user.businessId]
            if current_user.businessId not in approved_zid_list:
                return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400
        else:
            business_Id_list = VbusinessModel.find_all_business_list()

        category_list = CategoryModel.find_all_category_list()

        all_items = [item.json() for item in CaitemModel.find_by_zid_category(business_Id_list,category_list)]

        product_count = len(all_items)
        return {'rowcount':product_count},200

class CaitemProductCategory(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'admin previlege required'},400

        current_user = UserModel.find_by_user(get_jwt_identity())

        if not claims['is_superuser']:
            approved_zid_list = VbusinessModel.find_all_business_list()

            business_Id_list = [current_user.businessId]
            if current_user.businessId not in approved_zid_list:
                return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400
        else:
            business_Id_list = VbusinessModel.find_all_business_list()

        category_list = CategoryModel.find_all_category_list()
        
        all_category = [{'businessId':category.json()['businessId'],'product_Category':category.json()['product_Category']} for category in CaitemModel.find_product_category(business_Id_list)]
        approved_category = [category.json() for category in CategoryModel.find_all_category()]

        non_approved_category = [i for i in all_category if i not in approved_category]

        return {'all_category':all_category,'approved_category':approved_category,'non_approved_category':non_approved_category},200

class CaitemCelery(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        print(claims)
        if not claims['active']:
            return {'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'},400

        try:
            receive_from_client_db(CaitemModel.__tablename__, CaitemModel.__table__.c.keys())        
        except Exception as e:
            print(e)
        
        return 'product data synced'


class CaitemProductCategoryAdd(Resource):
    @jwt_required
    def post(self, businessId):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'admin previlege required'},400

        approved_zid_list = VbusinessModel.find_all_business_list()

        current_user = UserModel.find_by_user(get_jwt_identity())

        if (current_user.businessId not in approved_zid_list) or (businessId not in approved_zid_list):
            return {'message': 'Error # 180 in Product Resource, You have not been authorized to use this business'},400

        json_data = request.get_json()

        if not json_data:
            return {'message': 'Error # 186 in Product Resource, No input data provided'},400

        try:
            data = categorySchema.load(json_data).data
        except ValidationError as err:
            return err.messages,400

        data['approvedCategory'] = html.unescape(data['approvedCategory'])
        if not CaitemModel.find_by_zid_category([businessId],[data['approvedCategory']]):
            return {'message':'Error # 131 in Product Resources, this category or business ID does not exist in our System'},400

        if CategoryModel.find_by_zid_category(current_user.businessId,data['approvedCategory']):
            return {'message':'Error # 194 in Product Resources, this category has already been approved'},400

        categoryDetail = CategoryModel(
            zid=businessId,
            approvedCategory=data['approvedCategory'],
            xtra1 = None,
            xtra2 = None,
            xtra3 = None,
            xtra4 = None,
            xtra5 = None
        )

        try:
            categoryDetail.save_to_db()
        except Exception as e:
            print(e)
            return {"message":"Error # 205 in Product Resource, An error occured while saving the product category"},400

        return categoryDetail.json(),200

class CaitemProductCategoryDelete(Resource):
    @jwt_required
    def delete (self,businessId,approvedCategory):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Error # 213 in Product Resource, admin prevelige required'},400

        approved_zid_list = VbusinessModel.find_all_business_list()

        current_user = UserModel.find_by_user(get_jwt_identity())

        if (current_user.businessId not in approved_zid_list) or (businessId not in approved_zid_list):
            return {'message': 'Error # 180 in Product Resource, You have not been authorized to use this business'},400

        if not CaitemModel.find_by_zid_category([businessId],[approvedCategory]):
            return {'message':'Error # 131 in Product Resources, this category or business ID does not exist in our System'},400

        categoryDetail = CategoryModel.find_by_zid_category(current_user.businessId, approvedCategory)

        if categoryDetail:
            categoryDetail.delete_from_db()

        return {'message':'Response # 225 in Product Resources, Category has been deleted'},200


class SpecialPrice(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'},400
        try:
            receive_from_client_db(OpspprcModel.__tablename__, OpspprcModel.__table__.c.keys())
        except Exception as e:
            print(e)
        
        return 'special price data synced'

