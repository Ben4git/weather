# -*- coding: utf-8 -*-
#
# Iterativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2016 Iterativ GmbH. All rights reserved.
#
# Created on 29/07/16
# @author: pawel
from app.weather_terms import SONNE, generate_weather_terms


def test():
    terms = generate_weather_terms(SONNE)
    print terms

test()
