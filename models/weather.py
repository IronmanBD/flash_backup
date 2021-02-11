from db import db
import datetime
from flask import current_app as app


class WeatherModel(db.Model):

    __tablename__ = 'weather'

    id = db.Column(db.Integer, primary_key=True)
    ztime = db.Column(db.DateTime)
    short_desc = db.Column(db.String(50))
    full_desc = db.Column(db.String(50))
    temp = db.Column(db.Float)
    feels_like = db.Column(db.Float)
    pressure = db.Column(db.Float)
    humidity = db.Column(db.Float)
    country = db.Column(db.String(50))
    name = db.Column(db.String(50))

    def myConverter(self,o):
        if isinstance(o, datetime.datetime):
            return o.__str__()


    def __init__(self, ztime, short_desc, full_desc, temp, feels_like, pressure, humidity, country, name):
        self.ztime  = ztime
        self.short_desc  = short_desc
        self.full_desc = full_desc
        self.temp = temp
        self.feels_like = feels_like
        self.pressure = pressure
        self.humidity = humidity
        self.country = country
        self.name = name

    def json(self):
        return {
            'entry_time': self.myConverter(self.ztime),
            'short_desc': self.short_desc,
            'full_desc' : self.full_desc,
            'temp' : self.temp,
            'feels_like' : self.feels_like,
            'pressure' : self.pressure,
            'humidity' : self.humidity,
            'country' : self.country,
            'name' : self.name
        }

    @classmethod
    def find_by_country_city(cls, name, country):
        return cls.query.filter_by(name=name).filter_by(country=country).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
