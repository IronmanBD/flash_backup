from db import db
import datetime
from sqlalchemy import or_

class CacusModel(db.Model):

    __tablename__ = 'cacus'

    zid = db.Column(db.Integer, primary_key = True)
    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    xcus= db.Column(db.String(100), primary_key = True)
    xorg = db.Column(db.String)
    xadd1 = db.Column(db.String(100))
    xadd2 = db.Column(db.String)
    xcity = db.Column(db.String)
    xmobile = db.Column(db.String)
    xsp = db.Column(db.String)
    xsp1 = db.Column(db.String)
    xsp2 = db.Column(db.String)
    xsp3 = db.Column(db.String)


    def myconverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()



    def __init__(self,zid,ztime,zutime,xcus,xorg,xadd1,xadd2,xcity,xmobile,xsp,xsp1,xsp2,xsp3):
        self.zid=zid
        self.ztime=ztime
        self.zutime=zutime
        self.xcus=xcus
        self.xorg=xorg
        self.xadd1=xadd1
        self.xadd2=xadd2
        self.xcity=xcity
        self.xmobile=xmobile
        self.xsp = xsp
        self.xsp1 = xsp1
        self.xsp2 = xsp2
        self.xsp3 = xsp3


    def json(self):
        return {
                'businessId':self.zid,
                # 'Entry_time':self.myconverter(self.ztime),
                # 'Update_time':self.myconverter(self.zutime),
                'cus_Code':self.xcus,
                'cus_Name':self.xorg,
                'cus_Add':self.xadd1,
                'cus_Area':self.xadd2,
                'cus_Sub_area':self.xcity,
                'cus_Mobile':self.xmobile,
                'cus_salesman':self.xsp,
                'cus_salesman1':self.xsp1,
                'cus_salesman2':self.xsp2,
                'cus_salesman3':self.xsp3
                }

    @classmethod
    def find_by_customerId(cls, zid ,xcus):
        return cls.query.filter_by(zid=zid).filter_by(xcus=xcus).first()

    @classmethod
    def find_customers_by_sp(cls, xsp_list):
        return cls.query.filter(
            or_(cls.xsp.in_(xsp_list),
            cls.xsp1.in_(xsp_list),
            cls.xsp2.in_(xsp_list),
            cls.xsp3.in_(xsp_list))).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
