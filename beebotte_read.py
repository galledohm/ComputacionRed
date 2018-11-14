#!/usr/bin/python3
# -*- coding: utf-8 -*-

from beebotte import *
import numpy

bclient = BBT("tSMIxiJhc2vrUZV04YLPJHBP", "B8dx4NVHCoQW3n6ngsD8WOHUcQ4JDujy")

records = bclient.read('P1', 'clics', limit = 10000 , source = 'raw')
items = []
for item in records:
    items.append(int(item['data']))
print (len(records))
print (items)
media = numpy.mean(items)
print (media)
