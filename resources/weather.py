from flask import request
from flask_restful import Resource
from flask_jwt_extended import (jwt_required, fresh_jwt_required,jwt_refresh_token_required,
                                get_jwt_claims,get_jwt_identity)
from models.weather import WeatherModel



class WeatherCity(Resource):
    @jwt_required
    def get(self,city):
        claims = get_jwt_claims()
        if not claims['active']:
            return {'message': 'Error # 25 in Location Resource, You have not been activated by the admin'}

        weathercity = WeatherModel.find_by_country_city(city,'BD')

        return weathercity.json()

