from db import db
import datetime

class ZbusinessModel(db.Model):

    __tablename__ = 'zbusiness'

    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    zid = db.Column(db.Integer, primary_key = True)
    xshort = db.Column(db.String(100))
    zorg = db.Column(db.String(50))

    def myconverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def __init__(self,ztime,zutime,zid,xshort,zorg):
        self.ztime=ztime
        self.zutime=zutime
        self.zid=zid
        self.xhort = xshort
        self.zorg = zorg

    def json(self):
        return {
                'entry_datetime':self.myconverter(self.ztime),
                'update_datetime':self.myconverter(self.zutime),
                'business_id':self.zid,
                'business_short_name':self.xshort,
                'business_org_name':self.zorg
                }

    @classmethod
    def find_by_businessId(cls, zid):
        return cls.query.filter_by(zid=zid).first()

    @classmethod
    def find_all_business(cls):
        return cls.query.all()

    @classmethod
    def find_count(cls):
        return cls.query.count()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
