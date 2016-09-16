# -*- coding: utf-8 -*-
#
# Iterativ GmbH
# http://www.iterativ.ch/
#
# Copyright (c) 2016 Iterativ GmbH. All rights reserved.
#
# Created on 05/08/16
# @author: pawel
import pydash
from pydash import foldl



def main():
    aas = [1, 2, 3, 4, 5, 5, 10]
    ascs = foldl(aas, lambda x, val: x + [{'val': val, 'asc': val - x[0]['val']}], [{'val': 1, 'asc': 0}])
    max_(ascs, 'asc')
    

main()