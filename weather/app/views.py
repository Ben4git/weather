import json
import requests
import numpy as np

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
from app import app
from app.weather_terms import generate_weather_terms, SUMMER_MUST_HAVE, MOVIE_TIME
from geopy.geocoders import Nominatim

FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat={}&lon={}&start=now&end=+10%20hours&format=jsonarray'
ELASTIC_BASE = 'http://www-explorer.pthor.ch/elastic/all_products_spryker_read/_search?q={}&size=20'


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
    address = [location[1] + " " + location[0], location[6]]
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
    print variables_result

    temperature = [i[0] for i in variables_result]
    rain = [i[1] for i in variables_result]
    sun = [i[2] for i in variables_result]
    wind = [i[3] for i in variables_result]
    humidity = [i[4] for i in variables_result]
    pressure = [i[5] for i in variables_result]
    clouds = [i[6] for i in variables_result]
    datetime = [i[7] for i in variables_result]

    date = [i.split(' ', 1)[0] for i in datetime]
    month = [i.split('-', 1)[1] for i in date]
    month = [i.split('-', 1)[0] for i in month]
    time = [i.split(' ', 1)[1] for i in datetime]

    print month, time

    temp_n = temperature_normalization(temperature)
    rain_n = rain_normalization(rain)
    sun_n = sun_normalization(sun)
    wind_n = wind_normalization(wind)
    humidity_n = humidity_normalization(humidity)
    pressure_n = pressure_normalization(pressure)
    clouds_n = clouds_normalization(clouds)

    weighting_vector, cut = get_weighting(month)

    a = np.array(weighting_vector)
    theme_world_list = []

    for i in range(len(temperature)):
        weather_array = np.array((temp_n[i], rain_n[i], sun_n[i], wind_n[i], humidity_n[i], pressure_n[i]))
        theme_world = np.dot(a, weather_array)
        theme_world_list.insert(i, theme_world)

    weather = get_prediction(theme_world_list, cut)

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
                'pressure': val['qff'],
                'clouds': val['n']}

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
    n = x['clouds']

    return t, p, s, u, h, ap, n, d


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

def clouds_normalization(clouds):
    clouds_n = []
    for i in range(len(clouds)):
        n_norm = ((clouds[i]) / 8)
        clouds_n.insert(i, n_norm)

    return clouds_n


def get_prediction(x, y):
    mean = np.mean(x, axis=0)
    print mean
    if mean.item(0) > y:
        weatherPredict = MOVIE_TIME
    else:
        weatherPredict = SUMMER_MUST_HAVE

    return weatherPredict


def get_weighting(x):

    weight = []
    cut = 0

    if x[0] == '01':
        weight = [-0.00909824, 0.00943982, -0.00684809, 0.00660464, 0.01447286, -0.01459643]
        cut = 0.00298387
    if x[0] == '02':
        weight = [-0.01282424, 0.00894633, -0.00570136, -0.00373348, 0.01624247, -0.01323499]
        cut = 0.00258065
    if x[0] == '03':
        weight = [-0.00803732, 0.00893287, -0.0066863, -0.00242146, 0.0140223, -0.01454846]
        cut = -0.000241935
    if x[0] == '04':
        weight = [-0.00898446, 0.00829643, -0.0066594, 0.00530684, 0.01627399, -0.01421073]
        cut = 0.00104839
    if x[0] == '05':
        weight = [-0.00995442, 0.00882052, -0.00599414, 0.00488401, 0.0164064, -0.01297599]
        cut = 0.00104839
    if x[0] == '06':
        weight = [-0.00967134, 0.00813585, -0.00546412, -0.00564167, 0.0153748, -0.01391193]
        cut = -0.00122984
    if x[0] == '07':
        weight = [-0.00988417, 0.00858781, -0.00583501, -0.00745723, 0.0165972, -0.01388873]
        cut = -0.00077621
    if x[0] == '08':
        weight = [-0.00942567, 0.00923738, -0.00645289, 0.00360788, 0.01589958, -0.01411208]
        cut = 0.000403226
    if x[0] == '09':
        weight = [-0.00912792, 0.00831796, -0.00602797, -0.00635364, 0.01566218, -0.01444709]
        cut = 0.00016129
    if x[0] == '10':
        weight = [-0.00781921, 0.00851862, -0.00575595, 0.00289248, 0.01664236, -0.01430174]
        cut = 0.00372379
    if x[0] == '11':
        weight = [-0.01152125, 0.00911835, -0.00631822, 0.00247476, 0.01666723, -0.01424621]
        cut = 0.00240927
    if x[0] == '12':
        weight = [-0.00726646, 0.00869168, -0.00713663, -0.0075033, 0.01841887, -0.01386321]
        cut = 0.00560484

    return weight, cut


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
