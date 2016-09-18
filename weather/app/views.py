import json
import requests
import numpy as np

from flask import jsonify, Flask
from flask import render_template, request
from app import app
from app.weather_terms import generate_weather_terms, SUMMER_MUST_HAVE, MOVIE_TIME
from geopy.geocoders import Nominatim

FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat={}&lon={}&start=now&end=+10%20hours&format=jsonarray'
ELASTIC_BASE = 'http://www-explorer.pthor.ch/elastic/all_products_spryker_read/_search?q={}'


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
    location = geolocation.address
    location = location.split(',')
    address = [location[0], location[1], location[5], location[6]]
    loca = {'lat': lat_s, 'lon': lon_s, 'geolocation': address}
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


@app.route('/weatherPrediction/<weather_json>/', methods=['GET', 'POST'])
def Prediction(weather_json):

    print weather_json[object]

    for i in range(len(weather_json)):
        print weather_json[i]

    def variables(x):
        t = x['temperature']
        p = x['rrp']
        s = x['sun']
        u = x['wind']
        h = x['humidity']
        ap = x['pressure']
        d = x['datetime']
        return t, p, s, u, h, ap, d

    variables_result = [variables(item) for item in weather_json]

    temperature = [i[0] for i in variables_result]
    rain = [i[1] for i in variables_result]
    sun = [i[2] for i in variables_result]
    wind = [i[3] for i in variables_result]
    humidity = [i[4] for i in variables_result]
    pressure = [i[5] for i in variables_result]
    datetime = [i[6] for i in variables_result]

    print temperature

    #
    # for i in range(len(temperature)):
    #     print datetime[i]
    #
    # temp_n = []
    # rain_n = []
    # sun_n = []
    # wind_n = []
    # humidity_n = []
    # pressure_n = []
    #
    # for i in range(len(temperature)):
    #     t_norm = ((temperature[i] + 40.0) / 80.0)  # highest measured temperature in switzerland goes from -40 to +40
    #     r_norm = ((rain[i]) / 100.0)  # rain probability goes from 0 to 100%
    #     s_norm = (sun[i] / 60.0)  # sun duration goes from 0 min to 60 min per hour
    #     w_norm = (wind[i] / 118.0)  # velocity goes from 0 - 118 km/h, at 118 km/h it is classified as an "Orkan"
    #     h_norm = (humidity[i] / 100.0)
    #     ap_norm = ((pressure[i] - 970) / 70)
    #     temp_n.insert(i, t_norm)
    #     rain_n.insert(i, r_norm)
    #     sun_n.insert(i, s_norm)
    #     wind_n.insert(i, w_norm)
    #     humidity_n.insert(i, h_norm)
    #     pressure_n.insert(i, ap_norm)
    #
    # a = np.matrix([[0.6, 0.1, 0.3, 0.1, 0.2, 0.4], [0.3, 0.6, 0.1, 0.1, 0.4, 0.1]])
    # theme_world_list = []
    #
    # for i in range(len(temperature)):
    #     weather_array = np.array((temperature[i], rain[i], sun[i], wind[i], humidity[i], pressure[i]))
    #     theme_world = np.dot(a, weather_array)
    #     theme_world_list.insert(i, theme_world)
    #
    # mean = np.mean(theme_world_list, axis=0)
    #
    # if mean.item(0) < mean.item(1):
    #     day_theme = 'Movie Time'
    #     day_link = 'https://siroop.ch/inspiration/movie-time'
    #     day_pic = '/static/rain.jpg'
    #     weatherPredict = MOVIE_TIME
    # else:
    #     day_theme = 'Summer Must-Haves'
    #     day_link = 'https://siroop.ch/inspiration/sommer-must-haves'
    #     day_pic = '/static/summer.jpg'
    #     weatherPredict = SUMMER_MUST_HAVE
    #
    # def extract_product_info(hit):
    #     try:
    #         image = hit['_source']['images']['lowres'][0]
    #     except:
    #         image = ''
    #
    #     return {'name': hit['_source']['de_CH']['name'],
    #             'image': image,
    #             'url': hit['_source']['de_CH']['url']}
    #
    # weather_terms = generate_weather_terms(weatherPredict)
    #
    # products = search_products(weather_terms)
    # products_info = map(extract_product_info, products)
    #
    # prediction = {'daytheme': day_theme, 'daylink': day_link, 'daypic': day_pic, 'weather': weatherPredict}
    # sum = prediction.copy()
    # sum.update(products_info)
    #
    # sum = jsonify(sum)
    # sum.headers.add('Access-Control-Allow-Origin', '*')

    return temperature


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
