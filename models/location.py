from db import db
import datetime
from flask import current_app as app
from passlib.hash import pbkdf2_sha256 as sha256

class LocationModel(db.Model):

    __tablename__ = 'userLocation'

    id = db.Column(db.Integer, primary_key=True)
    ztime = db.Column(db.DateTime)
    zid = db.Column(db.Integer, nullable = False)
    xemp = db.Column(db.String(100),nullable = False)
    xlat = db.Column(db.Float)
    xlong = db.Column(db.Float)


    def myconverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def __init__(self,ztime,zid,xemp,xlat,xlong):
        self.ztime = ztime
        self.zid = zid
        self.xemp = xemp
        self.xlat = xlat
        self.xlong = xlong


    def json(self):
        return {
            'entry_datetime':self.myconverter(self.ztime),
            'business_id':self.zid,
            'xemp':self.xemp,
            'xlat':self.xlat,
            'xlong':self.xlong
        }

    @classmethod
    def find_by_xemp(cls):
        return cls.query.filter_by(zid=zid).filter_by(xemp).all()

    @classmethod
    def find_by_zid(cls, zid):
        return cls.query.filter_by(zid=zid).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
