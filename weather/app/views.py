# coding=utf8
import json
import requests
import numpy as np
import datetime
from datetime import timedelta

from flask import jsonify, render_template
from app import app
from app.weather_terms import generate_weather_terms, SUMMER_MUST_HAVE, MOVIE_TIME
from geopy.geocoders import Nominatim

# FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts&lat={}&lon={}&start=now&end=+10%20hours&format=jsonarray'
ELASTIC_BASE = 'http://www-explorer.pthor.ch/elastic/all_products_spryker_read/_search?q={}&size=19'
FORECAST_BASE = 'https://mdx.meteotest.ch/api_v1?key=0F9D9B3DBE6716943C6D9A4776940F94&service=prod2data&action=iterativ_forecasts_termin&lat={}&lon={}&format=json'


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index_landing.html', title='Weather search')


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
    for key, val in rrp_table[0].iteritems():
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
    w = get_symbol_description(main_items['symbol'])
    main_items.update({'description': w['description']})
    return main_items


def get_main_items(x, y, v):
    z = {}

    temp_max = maximum(x['temp_max'], y['temp_max'], v['temp_max'])
    z.update({'temp_max': temp_max})

    temp_min = minimum(x['temp_min'], y['temp_min'], v['temp_min'])
    z.update({'temp_min': temp_min})

    wind_list = np.array([x['wind'], y['wind'], v['wind']])
    wind = int(wind_list.mean() + 0.5)
    z.update({'wind': wind})

    rain_rate = x['rain_rate'] + y['rain_rate'] + v['rain_rate']
    z.update({'rain_rate': rain_rate})

    symbol_list = np.array([x['symbol'], y['symbol'], v['symbol']])
    symbol = int(symbol_list.mean() + 0.5)
    z.update({'symbol': symbol})

    humidity_list = np.array([x['humidity'], y['humidity'], v['humidity']])
    humidity = int(humidity_list.mean() + 0.5)
    z.update({'humidity': humidity})

    thunder_prob = maximum(x['thunder_prob'], y['thunder_prob'], v['thunder_prob'])
    z.update({'thunder_prob': thunder_prob})

    clouds_list = np.array([x['clouds'], y['clouds'], v['clouds']])
    clouds = int(clouds_list.mean() + 0.5)
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
        weight = [-0.00335513, -0.00359237, 0.01732439, 0.01079877, 0.00059825, 0.00711425, 0.01937825]
        cut = 0.0116935
    if x == 2:
        weight = [-0.00530129, -0.0026943, 0.01525563, 0.00970345, 0.00059218, 0.00655433, 0.02047455]
        cut = 0.00967742
    if x == 3:
        weight = [-0.01590454, -0.00534317, 0.01659892, 0.00880971, 0.00058768, 0.00581285, 0.01955624]
        cut = 0.00016129
    if x == 4:
        weight = [-0.00942814, -0.00478461, 0.01845482, 0.01110916, 0.00064272, 0.00703559, 0.01944698]
        cut = 0.0058871
    if x == 5:
        weight = [-0.01165691, -0.00955254, 0.01597078, 0.01190846, 0.00061923, 0.00552247, 0.02154132]
        cut = 0.00185484
    if x == 6:
        weight = [-0.0134208, -0.01214072, 0.01703924, 0.01386619, 0.00061871, 0.00660583, 0.02127785]
        cut = 0.00137097
    if x == 7:
        weight = [-0.00975982, -0.01123043, 0.01413246, 0.01315478, 0.00061742, 0.00641805, 0.02138029]
        cut = 0.00185484
    if x == 8:
        weight = [-0.0115865, -0.00925401, 0.013127, 0.01252089, 0.00059309, 0.00533109, 0.02085148]
        cut = 0.000887097
    if x == 9:
        weight = [-0.01041435, -0.00758956, 0.01237047, 0.00833742, 0.00054605, 0.0062977, 0.01953063]
        cut = 0.000967742
    if x == 10:
        weight = [-0.01033804, -0.00841469, 0.01507056, 0.0114441, 0.0006528, 0.00755849, 0.02146566]
        cut = 0.00459677
    if x == 11:
        weight = [-0.01141499 -0.00611244, 0.01409918, 0.01213419, 0.00065773, 0.00737693, 0.02384542]
        cut = 0.00678427
    if x == 12:
        weight = [-0.00705209, -0.0054105, 0.0117761, 0.01033537, 0.00060414, 0.00748263, 0.0212954]
        cut = 0.00904234
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


def get_symbol_description(x):
    symbol = {}
    if x == 1:
        symbol.update({'description': 'sonnig sein'})
    if x == 2:
        symbol.update({'description': 'meist sonnig sein'})
    if x == 3:
        symbol.update({'description': 'bewölkt sein'})
    if x == 4:
        symbol.update({'description': 'stark bewölkt sein'})
    if x == 5:
        symbol.update({'description': 'Wärmegewitter geben'})
    if x == 6:
        symbol.update({'description': 'starken Regen geben'})
    if x == 7:
        symbol.update({'description': 'Schneefall geben'})
    if x == 8:
        symbol.update({'description': 'nebelig sein'})
    if x == 9:
        symbol.update({'description': 'Schneeregen geben'})
    if x == 10:
        symbol.update({'description': 'Regenschauer geben'})
    if x == 11:
        symbol.update({'description': 'leichten Regen geben'})
    if x == 12:
        symbol.update({'description': 'Schneeschauer geben'})
    if x == 13:
        symbol.update({'description': 'Frontgewitter geben'})
    if x == 14:
        symbol.update({'description': 'Hochnebel geben'})
    if x == 15:
        symbol.update({'description': 'Schneeregenschauer geben'})
    return symbol


def products_generation(x):
    def extract_product_info(hit):
        try:
            image = hit['_source']['images']['lowres'][0]
        except:
            image = ''

        return {'name': hit['_source']['de_CH']['name'],
                'image': image,
                'url': hit['_source']['de_CH']['url'],
                'price': ((hit['_source']['min_price'])),
                'merchant': hit['_source']['merchants']}

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
