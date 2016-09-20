import json
import requests
import numpy as np

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
from app import app
from app.weather_terms import generate_weather_terms, SUMMER_MUST_HAVE, MOVIE_TIME
from geopy.geocoders import Nominatim

FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat={}&lon={}&start=now&end=+10%20hours&format=jsonarray'
ELASTIC_BASE = 'http://www-explorer.pthor.ch/elastic/all_products_spryker_read/_search?q={}&size=25'


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='Weather search')


@app.route('/geoLoca/<lat>/<lon>/', methods=['GET', 'POST'])
def html_position(lat, lon):
    lat_s = str(lat)
    lon_s = str(lon)

    locator = Nominatim()
    position = locator.reverse('%s, %s' % (lat_s, lon_s))
    location = position.address
    location = location.split(',')
    address = [location[0], location[1], location[4], location[5], location[6]]
    address_table = {'lat': lat_s, 'lon': lon_s, 'location': address}
    response = jsonify(address_table)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route('/weatherReport/<lat>/<lon>/', methods=['GET', 'POST'])
def weather_table(lat, lon):
    weather_items = get_weather_table(lat, lon)

    weather_json = jsonify(weather_items)
    weather_json.headers.add('Access-Control-Allow-Origin', '*')
    return weather_json


@app.route('/weatherPrediction/<lat>/<lon>/', methods=['GET', 'POST'])
def weather_prediction(lat, lon):
    w = get_weather_table(lat, lon)

    variables_result = [get_weather_item_list(item) for item in w]

    temperature = [i[0] for i in variables_result]
    rain = [i[1] for i in variables_result]
    sun = [i[2] for i in variables_result]
    wind = [i[3] for i in variables_result]
    humidity = [i[4] for i in variables_result]
    pressure = [i[5] for i in variables_result]
    #datetime = [i[6] for i in variables_result]

    # day = []
    # time = []
    #
    # for i in range(len(temperature)):
    #     day[i] = datetime[i].split('-')
    #     time[i] = datetime[i].split(' ')
    #
    # print time

    temp_n = temperature_normalization(temperature)
    rain_n = rain_normalization(rain)
    sun_n = sun_normalization(sun)
    wind_n = wind_normalization(wind)
    humidity_n = humidity_normalization(humidity)
    pressure_n = pressure_normalization(pressure)

    a = np.matrix([[0.6, 0.1, 0.3, 0.1, 0.2, 0.4], [0.3, 0.6, 0.1, 0.1, 0.4, 0.1]])
    theme_world_list = []

    for i in range(len(temperature)):
        weather_array = np.array((temp_n[i], rain_n[i], sun_n[i], wind_n[i], humidity_n[i], pressure_n[i]))
        theme_world = np.dot(a, weather_array)
        theme_world_list.insert(i, theme_world)

    weather = get_prediction(theme_world_list)

    products_info = products_generation(weather)
    print products_info
    # prediction = {'daytheme': day_theme, 'daylink': day_link, 'daypic': day_pic, 'weather': weatherPredict}
    # sum = products_info.insert
    # sum.update(products_info)

    products_table = jsonify(products_info)
    products_table.headers.add('Access-Control-Allow-Origin', '*')
    return products_table


def get_weather_table(lat, lon):
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

    return items


def get_weather_item_list(x):
    t = x['temperature']
    p = x['rrp']
    s = x['sun']
    u = x['wind']
    h = x['humidity']
    ap = x['pressure']
    d = x['datetime']

    return t, p, s, u, h, ap, d


def temperature_normalization(temperature):
    temp_n = []
    for i in range(len(temperature)):
        t_norm = ((temperature[i] + 40.0) / 80.0)  # highest measured temperature in switzerland goes from -40 to +40
        temp_n.insert(i, t_norm)

    return temp_n


def rain_normalization(rain):
    rain_n = []
    for i in range(len(rain)):
        r_norm = ((rain[i]) / 100.0)  # rain probability goes from 0 to 100%
        rain_n.insert(i, r_norm)

    return rain_n


def sun_normalization(sun):
    sun_n = []
    for i in range(len(sun)):
        s_norm = (sun[i] / 60.0)  # sun duration goes from 0 min to 60 min per hour
        sun_n.insert(i, s_norm)

    return sun_n


def wind_normalization(wind):
    wind_n = []
    for i in range(len(wind)):
        w_norm = (wind[i] / 118.0)  # velocity goes from 0 - 118 km/h, at 118 km/h it is classified as an "Orkan"
        wind_n.insert(i, w_norm)

    return wind_n


def humidity_normalization(humidity):
    humidity_n = []
    for i in range(len(humidity)):
        h_norm = (humidity[i] / 100.0)
        humidity_n.insert(i, h_norm)

    return humidity_n


def pressure_normalization(pressure):
    pressure_n = []
    for i in range(len(pressure)):
        ap_norm = ((pressure[i] - 970) / 70)
        pressure_n.insert(i, ap_norm)

    return pressure_n


def get_prediction(x):
    mean = np.mean(x, axis=0)

    if mean.item(0) < mean.item(1):
        #day_theme = 'MOVIE_TIME'
        #day_link = 'https://siroop.ch/inspiration/movie-time'
        #day_pic = '/static/rain.jpg'
        weatherPredict = MOVIE_TIME
    else:
        #day_theme = 'SUMMER_MUST_HAVES'
        #day_link = 'https://siroop.ch/inspiration/sommer-must-haves'
        #day_pic = '/static/summer.jpg'
        weatherPredict = SUMMER_MUST_HAVE

    return weatherPredict


def products_generation(x):
    def extract_product_info(hit):
        try:
            image = hit['_source']['images']['lowres'][0]
        except:
            image = ''

        return {'name': hit['_source']['de_CH']['name'],
                'image': image,
                'url': hit['_source']['de_CH']['url']}

    weather_terms = generate_weather_terms(x)

    products_table = search_products(weather_terms)
    products_info = map(extract_product_info, products_table)

    return products_info


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
