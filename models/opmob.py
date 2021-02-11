from db import db
import datetime
from sqlalchemy import and_, or_
from sqlalchemy import func, and_, or_

class OpmobModel(db.Model):

    __tablename__ = 'opmob'

    zid = db.Column(db.Integer)
    ztime = db.Column(db.DateTime)
    zutime = db.Column(db.DateTime)
    invoiceno = db.Column(db.String(100))
    invoicesl = db.Column(db.Integer)
    username = db.Column(db.String(100))
    xemp = db.Column(db.String(100))
    xcus = db.Column(db.String(100))
    xcusname = db.Column(db.String(100))
    xcusadd = db.Column(db.String(100))
    xitem = db.Column(db.String(100))
    xdesc = db.Column(db.String(250))
    xqty = db.Column(db.Integer)
    xprice = db.Column(db.Float)
    xstatusord = db.Column(db.String(100))
    xordernum = db.Column(db.String(100))
    xroword = db.Column(db.Integer)
    xterminal = db.Column(db.String(10))
    xdate = db.Column(db.Date)
    xsl = db.Column(db.Integer,primary_key=True)
    xlat = db.Column(db.Float)
    xlong = db.Column(db.Float)
    xlinetotal = db.Column(db.Integer)
    xtra1 = db.Column(db.Integer, nullable=True)
    xtra2 = db.Column(db.Float, nullable=True)
    xtra3 = db.Column(db.String, nullable=True)
    xtra4 = db.Column(db.String, nullable=True)
    xtra5 = db.Column(db.String, nullable=True)

    def myConverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def myConverter2(self,o):
         if isinstance(o, datetime.date):
             return o.__str__()

    def __init__(self,zid,ztime,zutime,invoiceno,invoicesl,username,xemp,xcus,xcusname,xcusadd,xitem,xdesc,xqty,xprice,xstatusord,xordernum,xroword,xterminal,xdate,xsl,xlat,xlong,xlinetotal,xtra1,xtra2,xtra3,xtra4,xtra5):
        self.zid = zid
        self.ztime  = ztime
        self.zutime  = zutime
        self.invoiceno = invoiceno
        self.invoicesl = invoicesl
        self.username  = username
        self.xemp = xemp
        self.xcus = xcus
        self.xcusname = xcusname
        self.xcusadd  = xcusadd
        self.xitem = xitem
        self.xdesc = xdesc
        self.xqty = xqty
        self.xprice = xprice
        self.xstatusord = xstatusord
        self.xordernum = xordernum
        self.xroword = xroword
        self.xterminal = xterminal
        self.xdate = xdate
        self.xsl = xsl
        self.xlat = xlat
        self.xlong = xlong
        self.xlinetotal = xlinetotal
        self.xtra1 = xtra1
        self.xtra2 = xtra2
        self.xtra3 = xtra3
        self.xtra4 = xtra4
        self.xtra5 = xtra5


    def json(self):
        return {
                'businessId':self.zid,
                'Entry_Date':self.myConverter(self.ztime),
                'Update_Date':self.myConverter(self.zutime),
                'invoice_no':self.invoiceno,
                'invoice_sl':self.invoicesl,
                'username':self.username,
                'employeeCode':self.xemp,
                'customerCode':self.xcus,
                'customerName':self.xcusname,
                'customerAdd':self.xcusadd,
                'productCode':self.xitem,
                'productName':self.xdesc,
                'orderQty':self.xqty,
                'orderPrice':self.xprice,
                'orderStatus':self.xstatusord,
                'orderNumber':self.xordernum,
                'orderRow':self.xroword,
                'orderTerminal':self.xterminal,
                'orderDate':self.myConverter2(self.xdate),
                'orderSerial':self.xsl,
                'order_latitude':self.xlat,
                'order_longitute':self.xlong,
                'orderLineTotal':self.xlinetotal,
                'orderTotal':self.xtra2
                }
    
    def get_json_for_celery_db(self):
        return {
            'zid':self.zid,
            'ztime': self.ztime,
            'zutime': self.zutime,
            'invoiceno': self.invoiceno,
            'invoicesl': self.invoicesl,
            'username': self.username,
            'xemp': self.xemp,
            'xcus': self.xcus,
            'xcusname': self.xcusname,
            'xcusadd': self.xcusadd,
            'xitem': self.xitem,
            'xdesc': self.xdesc,
            'xqty': self.xqty,
            'xprice': self.xprice,
            'xstatusord': self.xstatusord,
            'xordernum': self.xordernum,
            'xroword': self.xroword,
            'xterminal': self.xterminal,
            'xdate': self.xdate,
            'xsl': self.xsl,
            'xlat': self.xlat,
            'xlong': self.xlong,
            'xlinetotal': self.xlinetotal,
            'xtra1': self.xtra1,
            'xtra2': self.xtra2,
            'xtra3': self.xtra3,
            'xtra4': self.xtra4,
            'xtra5': self.xtra5
        }

    @classmethod
    def find_by_invoiceno(cls,invoiceno):
        return cls.query.filter_by(invoiceno=invoiceno).all()

    @classmethod
    def find_by_customerId(cls,zid,xcus):
        return cls.query.filter_by(zid = zid).filter_by(xcus = xcus).all()

    @classmethod
    def find_by_confirmed(cls,xordernum):
        return cls.query.filter_by(xordernum=xordernum).all()

    @classmethod
    def find_by_date(cls,fromDate, toDate):
        return cls.query.filter(and_(cls.xdate >= fromDate,cls.xdate <= toDate)).all()

    @classmethod
    def find_confirmed(cls,xterminal_list,ztime):
        return cls.query.filter(cls.xdate>=ztime).filter(cls.xordernum != '').filter(cls.xterminal.in_(xterminal_list)).all()

    @classmethod
    def find_not_confirmed(cls,xterminal_list,ztime):
        return cls.query.filter(cls.xdate>=ztime).filter(cls.xordernum == '').filter(cls.xterminal.in_(xterminal_list)).all()

    @classmethod
    def find_by_ztime(cls,ztime):
        return cls.query.filter(cls.ztime>ztime).all()

    @classmethod
    def find_count(cls):
        return cls.query.count()

    @classmethod
    def find_last_xsl(cls):
        return cls.query.order_by(cls.xsl.desc()).first()

    @classmethod
    def find_last_invoicesl(cls):
        return cls.query.order_by(cls.invoicesl.desc()).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

