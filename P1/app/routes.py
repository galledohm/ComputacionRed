#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request
#import urllib.request as urlreq
import re
import datetime
from pymongo import MongoClient
from beebotte import *
import requests
import numpy

global database  #Variable global para indicar la BBDD a usar

app = Flask(__name__)      

def proc_data():
    #Obtencion de la pagina web
    #req = urlreq.Request('https://meneame.net')
    #html = urlreq.urlopen(req, verify=False).read()
    #html_text = html.decode(encoding='UTF-8')   #byte-type a texto
    html = requests.get('https://meneame.net', verify=False) #Con este método no se verifica el certificado SSL
    html_text = html.text#decode(encoding='UTF-8')   #byte-type a texto

    #El contenido del título es el único ubicado en el header tipo 2, por tanto, se extraen todas las cadenas entre dichos tags
    titulo_h2 = re.findall('<h2>(.*?)</h2>',html_text)  #Ahorra usar reg.exp de urls
    titulo = re.findall('>(.*?)</a>',titulo_h2[0])  #Tratamos la cadena obtenida para obtener solo el título
    print ('Titulo:', titulo)

    n_clics = re.findall('<div class="clics">  (\d+) clics  </div>',html_text)
    n_clics_first = n_clics[0]
    print ('N_Clics:', n_clics_first)

    n_votos = re.findall('<a id="a-votes-\d{7}" href="/story/([a-z0-9]+-?)+\d?">(\d+)</a>',html_text)
    n_votos_first = n_votos[0][1]
    print ('NVotos:', n_votos_first)

    #Obtencion de la fecha y hora del sistema
    fecha = datetime.datetime.now()
    return titulo,n_clics_first,n_votos_first,fecha

def proc_umbral(umbral):
    client_mdb = MongoClient('localhost', 27017)
    mongodb = client_mdb['p1-database']
    counter = 0
    items = []
    for item in mongodb.mytable.find({"clics": {"$gt": int(umbral)}}):
        if counter < 10:
            aux = dict(titulo = item['titulo'], clics = item['clics'] , votos = item['votos'], date = item['date'])
            items.append(aux)
            counter = counter + 1
    return items

def mean_mdb():
    global database
    client_mdb = MongoClient('localhost', 27017)
    mongodb = client_mdb['p1-database']
    items = []
    for item in mongodb.mytable.find({}):
        items.append(item['clics'])

    media = numpy.mean(items)
    print ('Media MongoDB: ',media)
    database = 'Beebotte'
    return media

def mean_beebotte():
    global database
    database = 'MongoDB'
    bclient = BBT("tSMIxiJhc2vrUZV04YLPJHBP", "B8dx4NVHCoQW3n6ngsD8WOHUcQ4JDujy")
    records = bclient.read('P1', 'clics', limit = 10000 , source = 'raw')
    items = []
    for item in records:
        items.append(int(item['data']))
    media = numpy.mean(items)
    print ('Media Beebotte',media)
    return media

@app.route('/')
@app.route('/index')
def home():
    global database
    titulo,clics,votos,fecha = proc_data()
    database = 'MongoDB'
    return render_template('home.html', titulo=titulo, clics=clics,votos=votos, fecha=fecha.strftime('%Y-%d%m %H:%M:%S'))

@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
      umbral = request.form['umbral']
      print ('Umbral POST: ',umbral)
      items = proc_umbral(umbral)
      print ('\nPOST DATA:\n',items,'\n')
      return render_template('dashboard.html', items=items)
    return render_template('dashboard.html')
    
@app.route('/mean')
def media():
    global database
    print(database)
    local_db = database
    if database == 'MongoDB':
        media = mean_mdb()
    else:
        media = mean_beebotte()
    return render_template('dashboard.html', media=media, database=local_db)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
  app.run(debug=True)
