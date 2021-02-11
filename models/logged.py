from db import db
from datetime import datetime
from flask import current_app as app
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import or_

class LoggedModel(db.Model):
    __tablename__ = 'logged'

    id=db.Column(db.Integer, primary_key=True)
    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    username = db.Column(db.String(120),unique=True, nullable = False)
    businessId = db.Column(db.Integer,nullable = False)
    access_token = db.Column(db.String(400),unique=True, nullable = False)
    refresh_token = db.Column(db.String(400),unique=True, nullable = False)
    status = db.Column(db.String(50),nullable = False)

    def myConverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def __init__(self,ztime,zutime,username,businessId,access_token,refresh_token,status):
        self.ztime = ztime
        self.zutime = zutime
        self.username = username
        self.businessId = businessId
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.status = status

    def json(self):
        return {
            'entry_time' : self.myConverter(self.ztime),
            'update_time' : self.myConverter(self.zutime),
            'username' : self.username,
            'businessId' : self.businessId,
            'access_token': self.access_token,
            'refresh_token' : self.refresh_token,
            'status' : self.status
        }

    @classmethod
    def find_by_user(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_user_businessid(cls, username, businessId):
        return cls.query.filter_by(username=username).filter_by(businessId=businessId).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
