from db import db
import datetime

class HrmstModel(db.Model):

    __tablename__ = 'prmst'


    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    zid = db.Column(db.Integer, primary_key = True)
    xemp = db.Column(db.String(100), primary_key = True)
    xname = db.Column(db.String(100))
    zemail = db.Column(db.String(100))
    xmobile =db.Column(db.String(40))
    xdiv = db.Column(db.String(50))
    xsec = db.Column(db.String(50))
    xdesig =db.Column(db.String(100))
    xdept = db.Column(db.String(100))


    def myConverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def myConverter2(self,o):
        if isinstance(o, datetime.date):
            return o.__str__()



    def __init__():
        self.ztime=ztime
        self.zutime=zutime
        self.zid=zid
        self.xemp=xemp
        self.xname=xname
        self.zemail=zemail
        self.xmobile=xmobile
        self.xdiv=xdiv
        self.xsec=xsec
        self.xdesig=xdesig
        self.xdept=xdept




    def json(self):
        return {
               'entry_date':self.myConverter(self.ztime),
               'update_date':self.myConverter(self.zutime),
               'businessId':self.zid,
               'emp_Code':self.xemp,
               'emp_FirstName':self.xname,
               'emp_Email':self.zemail,
               'emp_PhoneNum':self.xmobile,
               'emp_place':self.xdiv,
               'emp_status':self.xsec,
               'emp_designation':self.xdesig,
               'emp_department':self.xdept
                }

    @classmethod
    def find_by_EmployeeDetail(cls,businessId, employeeId):
        return cls.query.filter_by(zid=businessId).filter_by(xemp=employeeId).first()

    @classmethod
    def find_by_zid(cls,businessId):
        return cls.query.filter_by(zid=businessId).all()

    @classmethod
    def find_by_zid_list(cls,zid_list):
        return cls.query.filter(cls.zid.in_(zid_list)).all()

    @classmethod
    def find_by_ztime(cls,ztime):
        return cls.query.filter(cls.ztime>ztime).all()

    @classmethod
    def find_count(cls):
        return cls.query.count()

    @classmethod
    def find_all_employee_list(cls):
        employee_model = cls.query.all()
        employee_list = []
        for eid in employee_model:
            employee_list.append(eid.xemp)

        return employee_list

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
