from db import db
from datetime import datetime
from flask import current_app as app
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import or_

class UserModel(db.Model):
    __tablename__ = 'apiUsers'
    __table_args__ = (
        db.UniqueConstraint('username', 'businessId','employeeCode', name='unique_user_per_business'),
    )

    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),unique=True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    employee_name = db.Column(db.String(120), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    mobile = db.Column(db.String(120), nullable = False)
    businessId = db.Column(db.Integer,nullable = False)
    employeeCode = db.Column(db.String(120),nullable = False)
    terminal = db.Column(db.String(120))
    is_admin = db.Column(db.String(120))
    status = db.Column(db.String(50),nullable = False)


    def __init__(self,username,password,employee_name,email,mobile,businessId,employeeCode,terminal,is_admin,status):
        self.username = username
        self.password = password
        self.employee_name = employee_name
        self.email = email
        self.mobile = mobile
        self.businessId = businessId
        self.employeeCode = employeeCode
        self.terminal = terminal
        self.is_admin = is_admin
        self.status = status

    def json(self):
        return {
                    'username':self.username,
                    'password':self.generate_hash(self.password),
                    'employee_name':self.employee_name,
                    'email':self.email,
                    'mobile':self.mobile,
                    'businessId':self.businessId,
                    'employeeCode':self.employeeCode,
                    'terminal':self.terminal,
                    'is_admin':self.is_admin,
                    'status':self.status
                }


    @classmethod
    def find_by_user(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_busIdempCode(cls, username, businessId, employeeCode):
        return cls.query.filter_by(username=username).filter_by(businessId=businessId).filter_by(employeeCode=employeeCode).all()

    @classmethod
    def find_by_user_list(cls, employee_list):
        return cls.query.filter(cls.employeeCode.in_(employee_list)).all()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @staticmethod
    def verify_secret_key(secret_key_data):
        if secret_key_data == app.config['JWT_SECRET_KEY']:
            return 'is_admin'
        elif secret_key_data == app.config['JWT_SUPERUSER_SECRET_KEY']:
            return 'is_superuser'
        else:
            return 'None'

    @staticmethod
    def verify_active_user(secret_key_data):
        if secret_key_data == app.config['JWT_SECRET_KEY']:
            return 'active'
        elif secret_key_data == app.config['JWT_SUPERUSER_SECRET_KEY']:
            return 'active'
        else:
            return 'inactive'

    @classmethod
    def find_by_status(cls,businessId,status):
        return cls.query.filter(cls.username != 'Superuser').filter_by(businessId=businessId).filter_by(status=status).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
