from db import db
import datetime
from flask import current_app as app
from passlib.hash import pbkdf2_sha256 as sha256

class VbusinessModel(db.Model):

    __tablename__ = 'vbusiness'

    id = db.Column(db.Integer, primary_key=True)
    ztime = db.Column(db.DateTime) 
    zid = db.Column(db.Integer, unique = True,nullable = False)
    

    def myconverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def __init__(self,ztime,zid):
        self.ztime = ztime
        self.zid = zid
        
    
    def json(self):
        return {
            'entry_datetime':self.myconverter(self.ztime),
            'business_id':self.zid,
        }

    @classmethod
    def find_all_business(cls):
        return cls.query.all()

    @classmethod
    def find_all_business_list(cls):
        business_model = cls.query.all()
        business_list = []
        for bid in business_model:
            business_list.append(bid.zid) 
        
        return business_list

    @classmethod
    def find_by_zid(cls, zid):
        return cls.query.filter_by(zid=zid).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

