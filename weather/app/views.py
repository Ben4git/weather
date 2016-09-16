import json
import requests
import numpy as np

from flask import jsonify, Flask
from flask import render_template, request
from app import app
from app.weather_terms import generate_weather_terms, SUMMER_MUST_HAVE, MOVIE_TIME
from geopy.geocoders import Nominatim

FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat={}&lon={}&start=now&end=+10%20hours&format=jsonarray'
ELASTIC_BASE = 'http://www-explorer.pthor.ch/elastic/all_products_spryker_read/_search?q={}&size=5'

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Weather search')


@app.route('/geoLoca/<lat>/<lon>/', methods=['GET', 'POST'])
def test(lat, lon):

    lat_s = str(lat)
    lon_s = str(lon)

    geolocator = Nominatim()
    geolocation = geolocator.reverse('%s, %s' % (lat_s, lon_s))
    loca = {'lat': lat_s, 'lon': lon_s, 'geolocation': geolocation.address}
    response = jsonify(loca)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/weatherReport/<lat>/<lon>/', methods=['GET', 'POST'])
def weather(lat, lon):

    lat_s = str(lat)
    lon_s = str(lon)

    forecast_url = generate_forecast_url(lat_s, lon_s)
    w = requests.get(forecast_url)

    forecast_message = json.loads(w.content)
    rrp_table = forecast_message['payload']['mos']['location']

    def add_weather(val):
        return {'datetime': val['datetime'],
                'rrp': val['rrp'],
                'temperature': val['tt'],
                'sun': val.get('ss', 0),
                'wind': val['ff'],
                'humidity': val['rh'],
                'pressure': val['qff']}

    items = map(add_weather, rrp_table)

    weather_json = jsonify(items)
    weather_json.headers.add('Access-Control-Allow-Origin', '*')
    return weather_json

def search_products(search_terms):
    search_query = '+OR+'.join(search_terms)

    search_url = generate_elastic_url(search_query)
    search_result = requests.get(search_url)
    result_dict = json.loads(search_result.content)
    search_table = result_dict['hits']['hits']

    return search_table


def generate_forecast_url(lat, lon):
    return FORECAST_BASE.format(lat, lon)


def generate_elastic_url(weather):
    return ELASTIC_BASE.format(weather)