#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib.request as urlreq
import re
import datetime
from pymongo import MongoClient
from beebotte import *

#Obtencion de la pagina web
req = urlreq.Request('https://meneame.net')
html = urlreq.urlopen(req).read()
html_text = html.decode(encoding='UTF-8')   #byte-type a texto

#El contenido del título es el único ubicado en el header tipo 2, por tanto, se extraen todas las cadenas entre dichos tags
titulo_h2 = re.findall('<h2>(.*?)</h2>',html_text)  #Ahorra usar reg.exp de urls
titulo = re.findall('>(.*?)</a>',titulo_h2[0])  #Tratamos la cadena obtenida para obtener solo el título
print ('Titulo:', titulo)

n_clics = re.findall('<div class="clics">  (\d+) clics  </div>',html_text)
n_clics_first = n_clics[0]
print ('N_Clics:', n_clics_first)

# Hay que sacar los meneos no los VOTOS!!!
n_votos = re.findall('<a id="a-votes-\d{7}" href="/story/([a-z0-9]+-?)+\d?">(\d+)</a>',html_text)
n_votos_first = n_votos[0][1]
print ('NVotos:', n_votos_first)

"""Generación del cliente de MongoDB y conexion con la BBDD
Nombre BBDD: 'p1-database'"""
client_mdb = MongoClient('localhost', 27017)
mongodb = client_mdb['p1-database']

#Obtencion de la fecha y hora del sistema
fecha = datetime.datetime.now()

myrecord = {
        "titulo": titulo,
        "clics" : n_clics_first,
        "votos" : n_votos_first,
        "date" : fecha
        }

record_id = mongodb.mytable.insert(myrecord)

print ('MongoDB: ',record_id)
print (mongodb.collection_names())

"""Generación cliente Beebotte y conexion"""

bclient = BBT("tSMIxiJhc2vrUZV04YLPJHBP", "B8dx4NVHCoQW3n6ngsD8WOHUcQ4JDujy")

record_id = bclient.writeBulk('P1', [
  {'resource': 'titulo', 'data': ''.join(titulo)},
  {'resource': 'votos', 'data': int(n_votos_first)},
  {'resource': 'clics', 'data': int(n_clics_first)},
  {'resource': 'fecha', 'data': fecha.strftime('%Y-%d-%m %H:%M:%S')}
])

print ('Beebotte: ', record_id, '\n\n')

#"""Prueba escritura datos en fichero"""
#with open('data_file.txt','a') as f:
#    f.write(' '.join(titulo))
#    f.write(n_clics_first)
#    f.write(n_votos_first)
#    f.write(fecha.strftime('  %m%d%Y %H:%M:%S'))
#print (html_text)      #Para Testeo
