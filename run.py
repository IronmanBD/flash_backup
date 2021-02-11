from app import factory
import app

from flask import g
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager #new
import time
import datetime

from blacklist import BLACKLIST
from resources.cacus import Cacus, CacusList, CacusRowCount, CacusCelery
from resources.caitem import Caitem, CaitemList, CaitemRowCount, CaitemProductCategory, CaitemProductCategoryAdd, CaitemProductCategoryDelete, SpecialPrice, CaitemCelery
from resources.opmob import Opmob,OpmobDelete, OpmobConfirmed, OpmobNotConfirmed, OpmobNotConfirmedRowCount, OpmobConfirmedRowCount, OpmobConfirmedCelery
from resources.users import UserRegistration,UserLogout,UserLogin,TokenRefresh,AccessFreshToken,UpdateUser,UserStatusActive,UserStatusInactive, EmployeeCodeList, HrmstList, UserDelete
from resources.vbusiness import Vbusiness,VbusinessNonapproved, VbusinessRegular, VbusinessDelete
from resources.zbusiness import ZbusinessList
from resources.hierarchy import Hierarchy,HierarchyDelete, HierarchyNonparent, HierarchyParent
from resources.location import LocationUpdate


# from resources.opcdt import OpcdtListTime
# from resources.opcrn import OpcrnListTime
# from resources.opdor import OpdorListTime
# from resources.opord import OpordListTime
# from resources.opodt import OpodtListTime
# from resources.opddt import OpddtListTime

from models.users import UserModel
from models.vbusiness import VbusinessModel
from resources.weather import WeatherCity

#main app config
app = factory.create_app(celery=app.celery)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

#SQL config
app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:postgres@localhost:5432/da'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
api = Api(app)

#JWT config
app.config['JWT_SECRET_KEY'] = '!jk168b$ana36na'
app.config['JWT_SUPERUSER_SECRET_KEY'] = 'AnilSaddat19%!'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access','refresh']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)
jwt = JWTManager(app) #not creating a /auth end point

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if UserModel.find_by_user(identity).is_admin == 'is_admin':  # instead of hard-coding, we should read from a config file to get a list of admins instead
        return {'is_admin': True,'active':True,'is_superuser':False}
    elif UserModel.find_by_user(identity).is_admin == 'is_superuser':
        return {'is_superuser': True,'is_admin':True,'active':True}
    elif UserModel.find_by_user(identity).status == 'active':
        return {'active': True,'is_admin':False,'is_superuser':False}
    return {'is_admin': False,'is_superuser':False,'active':False}

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

@app.before_request
def before_request():
   g.request_start_time = time.time()
   g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)


#resources for super user function
api.add_resource(Vbusiness,'/validate_business')
api.add_resource(VbusinessDelete,'/delete_business/<int:business_Id>')
api.add_resource(VbusinessNonapproved,'/nonapprovedbusiness')
api.add_resource(ZbusinessList,'/businessId')

#resources for admin function
api.add_resource(Hierarchy,'/hierarchy')
api.add_resource(HierarchyDelete,'/hierarchyDelete/<string:username>')
api.add_resource(HierarchyNonparent,'/hierarchynonparent')
api.add_resource(HierarchyParent,'/hierarchyparent')

#resources for location function
api.add_resource(LocationUpdate,'/location')

#resources for customer function
api.add_resource(Cacus,'/customer/<int:businessId>/<string:customerId>')
api.add_resource(CacusList,'/customers')
api.add_resource(CacusRowCount,'/customerowcount')
api.add_resource(CacusCelery,'/customers_sync')


#resources for product function
api.add_resource(Caitem,'/product/<int:businessId>/<string:productCode>')
api.add_resource(CaitemList,'/products')
api.add_resource(CaitemRowCount,'/itemrowcount')
api.add_resource(CaitemProductCategory,'/itemcategory')
api.add_resource(CaitemProductCategoryAdd,'/itemcategoryadd/<int:businessId>')
api.add_resource(CaitemProductCategoryDelete,'/itemcategorydelete/<int:businessId>/<string:approvedCategory>')
api.add_resource(SpecialPrice,'/specialPrice')
api.add_resource(CaitemCelery,'/products_sync')

#resources for mobile orders
api.add_resource(Opmob,'/order') #this uses request.json in order to accept lists
api.add_resource(OpmobDelete,'/orderdelete/<string:invoiceno>')
api.add_resource(OpmobConfirmed,'/orderconfirmed')
api.add_resource(OpmobConfirmedCelery,'/orderconfirmed_sync')
api.add_resource(OpmobConfirmedRowCount,'/orderconfirmedrowcount')
api.add_resource(OpmobNotConfirmed, '/ordernotconfirmed')
api.add_resource(OpmobNotConfirmedRowCount,'/ordernotconfirmedrowcount')
# api.add_resource(OpmobDate,'/orderdate/<string:fromDate>/<string:toDate>')
# api.add_resource(OpmobCustomer,'/customerOrder/<int:zid>/<string:xcus>')

# api.add_resource(OpcdtListTime,'/opcdttime/<string:ztime>')
# api.add_resource(OpcrnListTime,'/opcrntime/<string:ztime>')
# api.add_resource(OpdorListTime,'/opdortime/<string:ztime>')
# api.add_resource(OpddtListTime,'/opddttime/<string:ztime>')
# api.add_resource(OpordListTime,'/opordtime/<string:ztime>')
# api.add_resource(OpodtListTime,'/opodttime/<string:ztime>')

#resources for user registration and login function
api.add_resource(UserRegistration,'/registration')
api.add_resource(UserLogin,'/login')
api.add_resource(UserLogout,'/logout')
api.add_resource(TokenRefresh,'/token/refresh')
api.add_resource(AccessFreshToken,'/token/fresh')
api.add_resource(UpdateUser,'/updateuser')
api.add_resource(EmployeeCodeList,'/employeeCode/<int:businessId>')
api.add_resource(VbusinessRegular,'/validate_business_regular')
api.add_resource(UserDelete, '/userdelete/<string:username>')
api.add_resource(HrmstList,'/hr')

#user according to status
api.add_resource(UserStatusActive,'/userstatusactive')
api.add_resource(UserStatusInactive,'/userstatusinactive')

#weather data
api.add_resource(WeatherCity,'/weather/<string:city>')

from db import db
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
