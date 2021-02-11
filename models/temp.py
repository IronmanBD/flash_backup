from db import db
import datetime
from sqlalchemy import or_

from sqlalchemy.dialects.postgresql import UUID
import uuid

class TempModel(db.Model):

    __tablename__ = 'temp_celery'

    temp_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    temp_name = db.Column(db.String(100))


    def myconverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()



    def __init__(self,temp_id, temp_name):
        self.temp_id = temp_id
        self.temp_name = temp_name


    def json(self):
        return {
                'temp_id': self.temp_id,
                'temp_name': self.temp_name
                }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
