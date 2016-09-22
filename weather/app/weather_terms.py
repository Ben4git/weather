# -*- coding: utf-8 -*-
#
# Siroop AG & Iterativ GmbH
# http ://www.siroop.ch/ & http://www.iterativ.ch/
#
# Copyright (c) 2016 Siroop AG & Iterativ GmbH. All rights reserved.
#
# Created on 29/07/16
# @author: benjamin & pawel
from random import sample

SAMPLE_SIZE = 20

SUMMER_MUST_HAVE = 'SUMMER_MUST_HAVE'
MOVIE_TIME = 'MOVIE_TIME'

WEATHER_TERMS = {
    'SUMMER_MUST_HAVE': ['296400', '332686', '61000', '70395', '498721', '57679', '328534', '339427', '338392', '283495', '231512', '375322', '471398', '271547', '310194', '484068', '176662', '324834', '536452', '254490', '62765', '293802', '297914', '301111', '221569', '294282', '296632', '195814'],
    'MOVIE_TIME': ['68004', '310575', '114301', '118575', '112086', '105671', '102159', '303754', '196254', '111734', '303727',  '65894', '116308', '283438', '288081', '191826', '82807', '116146', '112212']
}
def generate_weather_terms(weather):
    choice_basis = WEATHER_TERMS[weather]
    return sample(choice_basis, SAMPLE_SIZE)

