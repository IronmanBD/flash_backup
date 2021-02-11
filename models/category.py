from db import db
import datetime
from flask import current_app as app

class CategoryModel(db.Model):

    __tablename__ = 'approvedCategory'

    id = db.Column(db.Integer, primary_key=True)
    zid = db.Column(db.Integer, nullable = False)
    approvedCategory = db.Column(db.String, nullable=False)
    xtra1 = db.Column(db.Integer, nullable=True)
    xtra2 = db.Column(db.String, nullable=True)
    xtra3 = db.Column(db.String, nullable=True)
    xtra4 = db.Column(db.String, nullable=True)
    xtra5 = db.Column(db.String, nullable=True)

    def __init__(self,zid,approvedCategory,xtra1,xtra2,xtra3,xtra4,xtra5):
        self.zid = zid
        self.approvedCategory = approvedCategory
        self.xtra1 = xtra1
        self.xtra2 = xtra2
        self.xtra3 = xtra3
        self.xtra4 = xtra4
        self.xtra5 = xtra5

    def json(self):
        return {
            'businessId':self.zid,
            'product_Category': self.approvedCategory
        }

    @classmethod
    def find_by_zid_category(cls,zid,approvedCategory):
        return cls.query.filter_by(zid=zid).filter_by(approvedCategory=approvedCategory).first()

    @classmethod
    def find_all_category_list(cls):
        category_model = cls.query.all()
        category_list = []
        for category in category_model:
            category_list.append(category.approvedCategory)

        return category_list

    @classmethod
    def find_all_category(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
