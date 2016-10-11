import json
import requests
import numpy as np
import datetime
from datetime import timedelta

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
from app import app
from app.weather_terms import generate_weather_terms, SUMMER_MUST_HAVE, MOVIE_TIME
from geopy.geocoders import Nominatim

# FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat={}&lon={}&start=now&end=+10%20hours&format=jsonarray'
ELASTIC_BASE = 'http://www-explorer.pthor.ch/elastic/all_products_spryker_read/_search?q={}&size=19'
FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts_termin&lat={}&lon={}&format=json'


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

    tomorrow = datetime.datetime.now() + timedelta(days=1)
    month = tomorrow.month

    temp_max_n = temperature_normalization(w['temp_max'])
    temp_min_n = temperature_normalization(w['temp_min'])
    wind_n = wind_normalization(w['wind'])
    rain_rate_n = rain_rate_normalization(w['rain_rate'])
    humidity_n = humidity_normalization(w['humidity'])
    thunder_prob_n = thunder_prob_normalization(w['thunder_prob'])
    clouds_n = clouds_normalization(w['clouds'])

    weighting_vector, cut = get_weighting(month)

    a = np.array(weighting_vector)

    weather_array = np.array((temp_max_n, temp_min_n, wind_n, rain_rate_n, humidity_n,
                              thunder_prob_n, clouds_n))
    # weather_array = np.array((temp_n[i], rain_n[i], sun_n[i], wind_n[i], humidity_n[i], pressure_n[i]))
    theme_world = np.dot(a, weather_array)

    weather = get_prediction(theme_world, cut)

    products_info = products_generation(weather)

    products_table = jsonify(products_info)
    products_table.headers.add('Access-Control-Allow-Origin', '*')
    return products_table


def get_weather_table(lat, lon):
    lat_s = str(lat)
    lon_s = str(lon)

    forecast_url = generate_forecast_url(lat_s, lon_s)
    w = requests.get(forecast_url)

    forecast_message = json.loads(w.content)
    # rrp_table = forecast_message['payload']['mos']['location']
    rrp_table = forecast_message['payload']['prognose']['location']

    items_am = {}
    items_pm = {}
    items_ppm = {}
    for key, val in rrp_table[1].iteritems():
        if key == 'V':
            items_am.update({'temp_max': val['TX'],
                             'temp_min': val['TN'],
                             'wind': val['FF'],
                             'rain_rate': val['RR'],
                             'symbol': val['SY'],
                             'humidity': val['RH'],
                             'thunder_prob': val['TH'],
                             'clouds': val['N']})
        if key == 'N':
            items_pm.update({'temp_max': val['TX'],
                             'temp_min': val['TN'],
                             'wind': val['FF'],
                             'rain_rate': val['RR'],
                             'symbol': val['SY'],
                             'humidity': val['RH'],
                             'thunder_prob': val['TH'],
                             'clouds': val['N']})
        if key == 'A':
            items_ppm.update({'temp_max': val['TX'],
                              'temp_min': val['TN'],
                              'wind': val['FF'],
                              'rain_rate': val['RR'],
                              'symbol': val['SY'],
                              'humidity': val['RH'],
                              'thunder_prob': val['TH'],
                              'clouds': val['N']})

    main_items = get_main_items(items_am, items_pm, items_ppm)
    return main_items


def get_main_items(x, y, v):
    z = {}

    temp_max = maximum(x['temp_max'], y['temp_max'], v['temp_max'])
    z.update({'temp_max': temp_max})

    temp_min = minimum(x['temp_min'], y['temp_min'], v['temp_min'])
    z.update({'temp_min': temp_min})

    wind = maximum(x['wind'], y['wind'], v['wind'])
    z.update({'wind': wind})

    rain_rate = x['rain_rate'] + y['rain_rate'] + v['rain_rate']
    z.update({'rain_rate': rain_rate})

    symbol = maximum(x['symbol'], y['symbol'], v['symbol'])
    z.update({'symbol': symbol})

    humidity = maximum(x['humidity'], y['humidity'], v['humidity'])
    z.update({'humidity': humidity})

    thunder_prob = maximum(x['thunder_prob'], y['thunder_prob'], v['thunder_prob'])
    z.update({'thunder_prob': thunder_prob})

    clouds = maximum(x['clouds'], y['clouds'], v['clouds'])
    z.update({'clouds': clouds})
    return z


def maximum(a, b, c):
    max_val = a
    if b > max_val:
        max_val = b
    if c > max_val:
        max_val = c
        if b > c:
            max_val = b
    return max_val


def minimum(a, b, c):
    min_val = a
    if b < min_val:
        min_val = b
    if c < min_val:
        min_val = c
        if b < c:
            min_val = b
    return min_val


def temperature_normalization(temperature):
    t_norm = ((temperature + 40.0) / 80.0)  # highest measured temperature in switzerland goes from -40 to +40
    return t_norm


def wind_normalization(x):
    w_norm = (x / 118.0)  # velocity goes from 0 - 118 km/h, at 118 km/h it is classified as an "Orkan"
    return w_norm


def humidity_normalization(x):
    h_norm = (x / 100.0)
    return h_norm


def clouds_normalization(x):
    n_norm = (x / 8)
    return n_norm


def thunder_prob_normalization(thunder_prob):
    th_norm = (thunder_prob / 100.0)
    return th_norm


def rain_rate_normalization(rain_rate):
    rr_norm = (rain_rate / 1.4)
    return rr_norm


def get_prediction(x, y):
    if x > y:
        weatherPredict = MOVIE_TIME
    else:
        weatherPredict = SUMMER_MUST_HAVE
    return weatherPredict


def get_weighting(x):
    weight = []
    cut = 0

    if x == 1:
        weight = [-0.00382586, -0.00393746, 0.01642025, 0.01486812, 0.00067475, 0.00816414, 0.02697238]
        cut = 0.0180544
    if x == 2:
        weight = [-0.00670504, -0.00607809, 0.01811662, 0.01676428, 0.00068154, 0.00797337, 0.02836731]
        cut = 0.0140927
    if x == 3:
        weight = [-0.01540678, -0.00560556, 0.01492506, 0.00911104, 0.0006391, 0.00486679, 0.02658187]
        cut = 0.00495968
    if x == 4:
        weight = [-0.00912813, -0.00685701, 0.01483072, 0.01232059, 0.00062824, 0.00816203, 0.02681441]
        cut = 0.0107762
    if x == 5:
        weight = [-0.01107693, -0.00930273, 0.00781883, 0.01228519, 0.00064858, 0.00565221, 0.02554234]
        cut = 0.00523185
    if x == 6:
        weight = [-0.01209097, -0.01066439, 0.01337936, 0.01159317, 0.00074469, 0.00629606, 0.02954978]
        cut = 0.00504032
    if x == 7:
        weight = [-0.01077415, -0.00736007, 0.01555851, 0.01222838, 0.00071556, 0.00577852, 0.02675358]
        cut = 0.00697581
    if x == 8:
        weight = [-0.00960805, -0.00957767, 0.01580726, 0.01168713, 0.00068414, 0.00605758, 0.02491569]
        cut = 0.00622984
    if x == 9:
        weight = [-0.01081972, -0.00625248, 0.01550218, 0.00951834, 0.00073142, 0.0065168, 0.02742618]
        cut = 0.00859879
    if x == 10:
        weight = [-0.01046757, -0.0081211, 0.01410185, 0.01148382, 0.0006921, 0.00669379, 0.02556196]
        cut = 0.00905242
    if x == 11:
        weight = [-0.01264252, -0.00652497, 0.01316371, 0.01072454, 0.00064546, 0.00708285, 0.02793529]
        cut = 0.00796371
    if x == 12:
        weight = [-0.00762027, -0.00306047, 0.01080757, 0.01092766, 0.0006615, 0.00605315, 0.02827403]
        cut = 0.0140726
    return weight, cut

    #if x == 1:
    #     weight = [-0.00909824, 0.00943982, -0.00684809, 0.00660464, 0.01447286, -0.01459643]
    #     cut = 0.00298387
    # if x == 2:
    #     weight = [-0.01282424, 0.00894633, -0.00570136, -0.00373348, 0.01624247, -0.01323499]
    #     cut = 0.00258065
    # if x == 3:
    #     weight = [-0.00803732, 0.00893287, -0.0066863, -0.00242146, 0.0140223, -0.01454846]
    #     cut = -0.000241935
    # if x == 4:
    #     weight = [-0.00898446, 0.00829643, -0.0066594, 0.00530684, 0.01627399, -0.01421073]
    #     cut = 0.00104839
    # if x == 5:
    #     weight = [-0.00995442, 0.00882052, -0.00599414, 0.00488401, 0.0164064, -0.01297599]
    #     cut = 0.00104839
    # if x == 6:
    #     weight = [-0.00967134, 0.00813585, -0.00546412, -0.00564167, 0.0153748, -0.01391193]
    #     cut = -0.00122984
    # if x == 7:
    #     weight = [-0.00988417, 0.00858781, -0.00583501, -0.00745723, 0.0165972, -0.01388873]
    #     cut = -0.00077621
    # if x == 8:
    #     weight = [-0.00942567, 0.00923738, -0.00645289, 0.00360788, 0.01589958, -0.01411208]
    #     cut = 0.000403226
    # if x == 9:
    #     weight = [-0.00912792, 0.00831796, -0.00602797, -0.00635364, 0.01566218, -0.01444709]
    #     cut = 0.00016129
    # if x == 10:
    #     weight = [-0.00781921, 0.00851862, -0.00575595, 0.00289248, 0.01664236, -0.01430174]
    #     cut = 0.00372379
    # if x == 11:
    #     weight = [-0.01152125, 0.00911835, -0.00631822, 0.00247476, 0.01666723, -0.01424621]
    #     cut = 0.00240927
    # if x == 12:
    #     weight = [-0.00726646, 0.00869168, -0.00713663, -0.0075033, 0.01841887, -0.01386321]
    #     cut = 0.00560484
    #
    # return weight, cut


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
