from db import db
import datetime

class OpspprcModel(db.Model):

    __tablename__ = 'opspprc'

    zid = db.Column(db.Integer, primary_key = True)
    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    xpricecat = db.Column(db.String(100),primary_key = True)
    xqty = db.Column(db.Float, primary_key = True)
    xdisc = db.Column(db.Float)
    xqtypur = db.Column(db.Float)

    def myConverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def myConverter2(self,o):
         if isinstance(o, datetime.date):
             return o.__str__()


    def __init__(self,zid,ztime,zutime,xpricecat,xqty,xdisc,xqtypur):
        self.zid = zid
        self.ztime=ztime
        self.zutime=zutime
        self.xpricecat = xpricecat
        self.xqty = xqty
        self.xdisc = xdisc
        self.xqtypur = xqtypur

    def json(self):
        return {
                'businessId':self.zid,
                'Entry_Date':self.myConverter(self.ztime),
                'Update_Date':self.myConverter(self.zutime),
                'productCatCode':self.xpricecat,
                'sp_priceQty':self.xqty,
                'discountAmount':self.xdisc,
                'maxQty':self.xqtypur
                }

    @classmethod
    def find_by_priceCat(cls,zid,xpricecat):
        return cls.query.filter_by(zid=zid).filter_by(xpricecat=xpricecat).first()

    @classmethod
    def find_by_priceCat_all(cls,zid_list):
        return cls.query.filter(cls.zid.in_(zid_list)).all()

    @classmethod
    def find_by_ztime(cls,ztime):
        return cls.query.filter(cls.ztime>ztime).all()

    @classmethod
    def find_count(cls):
        return cls.query.count()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
