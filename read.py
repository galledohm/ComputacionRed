#!/usr/bin/python3
# -*- coding: utf-8 -*-
from pymongo import MongoClient
import json
client_mdb = MongoClient('localhost', 27017)
mongodb = client_mdb['p1-database']
counter = 0
items = []
for item in mongodb.mytable.find({"clics": {"$gt": 100}}):
    if counter < 10:
        aux = dict(titulo = item['titulo'], clics = item['clics'] , votos = item['votos'], date = item['date'])
        items.append(aux)
        counter = counter + 1

for item in items:
#return (aux)  
    print ('Clics: ',item['clics'])
    print ('Votos: ',item['votos'])
    print ('Titulo: ',item['titulo'])
    print ('Fecha: ',item['date'])
