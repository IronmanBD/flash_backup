from db import db
from datetime import datetime
from flask import current_app as app
from sqlalchemy import or_

class HierarchyModel(db.Model):
    __tablename__ = 'userHierarchy'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable = False)
    business_Id = db.Column(db.Integer)
    employee_code = db.Column(db.String(100))
    employee_name = db.Column(db.String(120), nullable = False)
    child_of_code = db.Column(db.String(100))
    child_of_name = db.Column(db.String(100))


    def __init__(self,username,business_Id,employee_code,employee_name,child_of_code,child_of_name):
        self.username = username
        self.business_Id = business_Id
        self.employee_code = employee_code
        self.employee_name = employee_name
        self.child_of_code = child_of_code
        self.child_of_name = child_of_name

    def json(self):
        return {
            'username':self.username,
            'business_id':self.business_Id,
            'employee_code':self.employee_code,
            'employee_name':self.employee_name,
            'child_of_code':self.child_of_code,
            'child_of_name':self.child_of_name
        }

    @classmethod
    def find_by_employee_code(cls, employee_code):
        return cls.query.filter_by(employee_code=employee_code).first()

    @classmethod
    def find_by_employee_code_zid(cls, zid, employee_code):
        return cls.query.filter_by(zid=zid).filter_by(employee_code=employee_code).first()

    @classmethod
    def find_by_child_of_code(cls, child_of_code):
        return cls.query.filter(cls.child_of_code.in_(child_of_code)).all()

    @classmethod
    def find_by_child_of_code_single_user(cls, current_employee_code):
        return cls.query.filter_by(child_of_code=current_employee_code).all()

    @classmethod
    def find_by_hierarchy(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_all_hierarchy(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
