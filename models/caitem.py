from db import db
import datetime


class CaitemModel(db.Model):

    __tablename__ = 'caitem'

    zid = db.Column(db.Integer, primary_key = True)
    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    xitem = db.Column(db.String(100),primary_key = True)
    xdesc = db.Column(db.String(250))
    xgitem = db.Column(db.String(100))
    xstdprice = db.Column(db.Float)
    xpricecat = db.Column(db.String(50))
    xunitstk=db.Column(db.String(100))
    xdateeff=db.Column(db.Date)
    xdateexp=db.Column(db.Date)
    xcatful = db.Column(db.String(12))

    def myConverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def myConverter2(self,o):
         if isinstance(o, datetime.date):
             return o.__str__()

    def __init__(self,zid,ztime,zutime,xitem,xdesc,xgitem,xstdprice,xpricecat,xunitstk,xdateeff,xdateexp,xcatful):
        self.zid=zid
        self.ztime=ztime
        self.zutime=zutime
        self.xitem=xitem
        self.xdesc=xdesc
        self.xgitem=xgitem
        self.xstdprice=xstdprice
        self.xpricecat=xpricecat
        self.xunitstk=xunitstk
        self.xdateeff=xdateeff
        self.xdateexp=xdateexp
        self.xcatful=xcatful

    def json(self):
        return {
                'businessId':self.zid,
                'Entry_Date':self.myConverter(self.ztime),
                'Update_Date':self.myConverter(self.zutime),
                'product_Code':self.xitem,
                'product_Name':self.xdesc,
                'product_Category':self.xgitem,
                'Sales_Price':self.xstdprice,
                'Price_Category':self.xpricecat,
                'Unit':self.xunitstk,
                'Eff_Date':self.myConverter2(self.xdateeff),
                'Exp_Date':self.myConverter2(self.xdateexp),
                'xcatful':self.xcatful
                }

    @classmethod
    def find_by_productCode(cls,zid,xitem):
        return cls.query.filter_by(zid=zid).filter_by(xitem=xitem).all()

    @classmethod
    def find_by_zid_category(cls,zid_list,category_list):
        return cls.query.filter(cls.zid.in_(zid_list)).filter(cls.xgitem.in_(category_list)).all()
    
    @classmethod
    def find_product_category(cls,zid_list):
        return cls.query.filter(cls.zid.in_(zid_list)).distinct(cls.xgitem)

    @classmethod
    def find_count(cls, zid_list):
        return cls.query.filter(cls.zid.in_(zid_list)).count()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()