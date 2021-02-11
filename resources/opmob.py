from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import func, not_
import datetime
import ast
from flask_jwt_extended import (jwt_required,fresh_jwt_required,get_jwt_claims,get_jwt_identity)
import datetime

from db import db
from .increment import increment, clean

from models.cacus import CacusModel
from models.caitem import CaitemModel
from models.users import UserModel
from models.opmob import OpmobModel
from models.vbusiness import VbusinessModel
from models.hierarchy import HierarchyModel
from schemas.opmob import opmobSchemas
from models.opspprc import OpspprcModel
from app.tasks import *
from app.tasks import receive_from_client_db


class Opmob(Resource):
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Order Resource, You have not been activated by the admin'},400

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


        for d in data:
            cacusSp = CacusModel.find_by_customerId(d['zid'],d['xcus']).json()
            
            sp_list = [cacusSp['cus_salesman'],cacusSp['cus_salesman1'],cacusSp['cus_salesman2'],cacusSp['cus_salesman3']]

            if len(set(sp_list).intersection(set(final_list))) == 0:
                return {'message':'You are not allowed to place an order for this customer'},400
            

        ztime = datetime.datetime.now()
        xdate = datetime.datetime.now().date()


        xsl = clean(str(OpmobModel.find_last_xsl().xsl))
        if xsl == 'None':
            xsl = 0
        else:
            xsl = int(xsl)

        invoicesl = clean(str(OpmobModel.find_last_invoicesl().invoicesl))
        if invoicesl == 'None':
            invoicesl = 0
        else:
            invoicesl = int(invoicesl)

        mainList = []
        for d in data:
            invoicesl = invoicesl + 1
            xroword = 1
            for i in (d['order']):
                #update all static values
                i['xcus'] = d['xcus']

                try:
                    i['xlat'] = d['xlat']
                except:
                    i['xlat'] = 0

                try:
                    i['xlong'] = d['xlong']
                except:
                    i['xlong'] = 0

                approved_zid_list = VbusinessModel.find_all_business_list()

                if d['zid'] not in approved_zid_list:
                    return {'message': 'Error # 182 in Customer Resource, You have not been authorized to use this business'},400

                i['zid'] = d['zid']
                i['ztime'] = self.myconverter(ztime)
                i['zutime'] = self.myconverter(ztime)
                i['xdate'] = self.myconverter2(xdate)
                i['username'] = username.username
                i['xterminal'] = username.terminal
                i['xroword'] = xroword
                xroword = xroword + 1
                xsl = xsl + 1
                i['xsl'] = xsl
                i['invoicesl'] = invoicesl
                i['invoiceno'] = str(username.terminal) + str(invoicesl)
                # i['xemp'] = [item['xemp'] for item in busIdempCodeList if item.get('zid','') == i['zid']][0]
                i['xemp'] = username.employeeCode
                i['xcusname'] = CacusModel.query.filter_by(zid=i['zid']).filter_by(xcus=i['xcus']).first().xorg
                i['xcusadd'] = CacusModel.query.filter_by(zid=i['zid']).filter_by(xcus=i['xcus']).first().xadd1

                i['xdesc'] = CaitemModel.query.filter_by(zid=i['zid']).filter_by(xitem=i['xitem']).first().xdesc

                xstdprice = CaitemModel.query.filter_by(zid=i['zid']).filter_by(xitem=i['xitem']).first().xstdprice
                xpricecat = CaitemModel.query.filter_by(zid=i['zid']).filter_by(xitem=i['xitem']).first().xpricecat

                print(xstdprice,'xstdprice')
                print(xpricecat,'xpricecat')


                try:
                    xqtycat = OpspprcModel.query.filter_by(zid=i['zid']).filter_by(xpricecat=xpricecat).first().xqty
                except:
                    xqtycat = 0

                try:
                    xdisc = OpspprcModel.query.filter_by(zid=i['zid']).filter_by(xpricecat=xpricecat).first().xdisc
                except:
                    xdisc = 0

                print(xqtycat,'xqtycat')
                print(xdisc,'xdisc')

                if i['xqty']>= xqtycat:
                    i['xprice'] = xstdprice - xdisc
                else:
                    i['xprice'] = xstdprice


                i['xlinetotal'] = i['xprice'] * i['xqty']
                print(i['xprice'],'xprice')
                print(i['xqty'],'xqty')
                print(i['xlinetotal'],'xlinetotal')
                i['xstatusord'] = "New"
                i['xordernum'] = ""
                mainList.append(i)

        #########################################
        orders_json_list = []
        #########################################

        for orders in mainList:
            orderDetail = OpmobModel(
            zid = orders['zid'],
            ztime = orders['ztime'],
            zutime = orders['zutime'],
            invoiceno = orders['invoiceno'],
            invoicesl =orders['invoicesl'],
            username = orders['username'],
            xemp = orders['xemp'],
            xcus = orders['xcus'],
            xcusname = orders['xcusname'],
            xcusadd = orders['xcusadd'],
            xitem = orders['xitem'],
            xdesc = orders['xdesc'],
            xqty = orders['xqty'],
            xprice = orders['xprice'],
            xstatusord = orders['xstatusord'],
            xordernum =orders['xordernum'],
            xroword = orders['xroword'],
            xterminal = orders['xterminal'],
            xdate = orders['xdate'],
            xsl = orders['xsl'],
            xlat = orders['xlat'],
            xlong = orders['xlong'],
            xlinetotal = orders['xlinetotal'],
            xtra1 = None,
            xtra2 = None,
            xtra3 = None,
            xtra4 = None,
            xtra5 = None
            )

            try:
                orderDetail.save_to_db()
                orders_json_list.append(orderDetail.get_json_for_celery_db())
            except Exception as e:
                print(e)
                return {"message":"An error occured inserting the customer"},400
        ####################################
        add_all_rows_to_client_db_by_celery.delay(orderDetail.__tablename__, orders_json_list)
        ####################################
        return mainList,200

    def myconverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def myconverter2(self,o):
        if isinstance(o, datetime.date):
            return o.__str__()

class OpmobDelete(Resource):
    @jwt_required
    def delete(self,invoiceno):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Order Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())

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

        terminal_list = UserModel.find_by_user_list(final_list)
        terminal_list = [term.json()['terminal'] for term in terminal_list]

        if OpmobModel.find_by_invoiceno(invoiceno)[0].xterminal not in terminal_list:
            return {'message':'You are not allowed to delete this order'},400

        orderNum =[ordernum.xordernum for ordernum in OpmobModel.find_by_invoiceno(invoiceno)]

        if '' not in orderNum:
            return {'message':'You cannot delete this Order as it has already been confirmed'},400

        orderDetail = OpmobModel.find_by_invoiceno(invoiceno)
        for orders in orderDetail:
            orders.delete_from_db()
            
        ####################################
        delete_key_value_pair_list = [('invoiceno', invoiceno)]
        ####################################
        delete_from_client_db_with_custom_key_by_celery.delay(OpmobModel.__tablename__, delete_key_value_pair_list)
    
        return {'message':'Your order has been deleted'},200


class OpmobConfirmed(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Order Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())
        ztime = datetime.datetime.now().date()
        ztime_31 = ztime - datetime.timedelta(31)

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

        terminal_list = UserModel.find_by_user_list(final_list)
        terminal_list = [term.json()['terminal'] for term in terminal_list]


        try:
            confirmedOrders = OpmobModel.find_confirmed(terminal_list,ztime_31)
        except Exception as e:
            print(e)
            return {'message':'No orders created under your name'},400

        reOrders = []
        invoice_no = ''

        for orders in confirmedOrders:
            if invoice_no != orders.json()['invoice_no']:
                newOrderDict = {}
                newOrderDict['Entry_Date'] = orders.json()['Entry_Date']
                newOrderDict['employeeCode'] = orders.json()['employeeCode']
                newOrderDict['businessId'] = orders.json()['businessId']
                newOrderDict['invoice_no'] = orders.json()['invoice_no']
                newOrderDict['customerCode'] = orders.json()['customerCode']
                newOrderDict['customerName'] = orders.json()['customerName']

                products = []
                for ordersProduct in OpmobModel.find_by_invoiceno(orders.json()['invoice_no']):
                    invoice_product = {
                                        'productCode':ordersProduct.json()['productCode'],
                                        'productName':ordersProduct.json()['productName'],
                                        'orderQty':ordersProduct.json()['orderQty'],
                                        'orderPrice':ordersProduct.json()['orderPrice'],
                                        'orderLineTotal':ordersProduct.json()['orderLineTotal'],
                                        'orderTotal':ordersProduct.json()['orderTotal']
                                    }
                    products.append(invoice_product)
                newOrderDict['products'] = products

                invoice_no = orders.json()['invoice_no']
                reOrders.append(newOrderDict)
            else:
                continue

        return reOrders,200

class OpmobConfirmedCelery(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        print(claims)
        if not claims['active']:
            return {'message': 'Error # 171 in Customer Resource, You have not been activated by the admin'},400

        try:
            #i think we need to import this
            receive_from_client_db(OpmobModel.__tablename__, OpmobModel.__table__.c.keys())
        except Exception as e:
            print(e)

        return 'customer data synced'

class OpmobConfirmedRowCount(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Order Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())
        ztime = datetime.datetime.now().date()
        ztime_31 = ztime - datetime.timedelta(31)

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

        terminal_list = UserModel.find_by_user_list(final_list)
        terminal_list = [term.json()['terminal'] for term in terminal_list]

        try:
            
            confirmedOrders = OpmobModel.find_confirmed(terminal_list,ztime_31)
        except Exception as e:
            print(e)
            return {'message':'No orders created under your name'},400

        invoice_no = ''
        count = 0
        for orders in confirmedOrders:
            if invoice_no != orders.json()['invoice_no']:
                count += 1
                invoice_no = orders.json()['invoice_no']
            else:
                continue
        
        return {'Number_of_confirmedOrders':count},200


class OpmobNotConfirmed(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Order Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())
        ztime = datetime.datetime.now().date()
        ztime_31 = ztime - datetime.timedelta(31)

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

        terminal_list = UserModel.find_by_user_list(final_list)
        terminal_list = [term.json()['terminal'] for term in terminal_list]

        try:
            notConfirmedOrders = OpmobModel.find_not_confirmed(terminal_list,ztime_31)
        except Exception as e:
            print(e)
            return {'message':'No orders created under your name'},400

        reOrders = []
        invoice_no = ''

        for orders in notConfirmedOrders:
            print(invoice_no)
            if invoice_no != orders.json()['invoice_no']:
                newOrderDict = {}
                newOrderDict['Entry_Date'] = orders.json()['Entry_Date']
                newOrderDict['employeeCode'] = orders.json()['employeeCode']
                newOrderDict['businessId'] = orders.json()['businessId']
                newOrderDict['invoice_no'] = orders.json()['invoice_no']
                newOrderDict['customerCode'] = orders.json()['customerCode']
                newOrderDict['customerName'] = orders.json()['customerName']

                products = []
                orderTotal = 0
                for ordersProduct in OpmobModel.find_by_invoiceno(orders.json()['invoice_no']):
                    orderTotal += ordersProduct.json()['orderLineTotal']
                    invoice_product = {
                                        'productCode':ordersProduct.json()['productCode'],
                                        'productName':ordersProduct.json()['productName'],
                                        'orderQty':ordersProduct.json()['orderQty'],
                                        'orderPrice':ordersProduct.json()['orderPrice'],
                                        'orderLineTotal':ordersProduct.json()['orderLineTotal']
                                    }
                    products.append(invoice_product)
                newOrderDict['orderTotal'] = orderTotal
                newOrderDict['products'] = products

                invoice_no = orders.json()['invoice_no']
                reOrders.append(newOrderDict)
            else:
                continue

        return reOrders,200



class OpmobNotConfirmedRowCount(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Order Resource, You have not been activated by the admin'},400

        username = UserModel.find_by_user(get_jwt_identity())
        ztime = datetime.datetime.now().date()
        ztime_31 = ztime - datetime.timedelta(31)

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

        terminal_list = UserModel.find_by_user_list(final_list)
        terminal_list = [term.json()['terminal'] for term in terminal_list]

        try:
            notConfirmedOrders = OpmobModel.find_not_confirmed(terminal_list,ztime_31)
        except Exception as e:
            print(e)
            return {'message':'No orders created under your name'},400

        invoice_no = ''
        count = 0
        for orders in notConfirmedOrders:
            if invoice_no != orders.json()['invoice_no']:
                count += 1
                invoice_no = orders.json()['invoice_no']
            else:
                continue

        return {'Number_of_confirmedOrders':count},200


