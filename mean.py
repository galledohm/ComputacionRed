#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import numpy
client_mdb = MongoClient('localhost', 27017)
mongodb = client_mdb['p1-database']
items = []
for item in mongodb.mytable.find({}):
    items.append(item['clics'])

media = numpy.mean(items)
print (media)
