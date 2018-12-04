#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
import bcrypt
#import urllib.request as urlreq
import re
import datetime
from pymongo import MongoClient
from beebotte import *
import requests
import numpy

global database  #Variable global para indicar la BBDD a usar

"""Inicio de aplicación y caracterización para acceso de usuarios"""
app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'

app.config['MONGO_dbname'] = 'users'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(app)

"""Definición de funciones"""

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

"""Acciones"""
#Página de inicio con opción de login
@app.route('/')
@app.route('/home')
def home():
    global database
    titulo,clics,votos,fecha = proc_data()
    database = 'MongoDB'
    if 'username' in session:
        return render_template('home.html', username=session['username'], titulo=titulo, clics=clics,votos=votos, fecha=fecha.strftime('%Y-%d-%m %H:%M:%S'))
    return render_template('home.html', titulo=titulo, clics=clics,votos=votos, fecha=fecha.strftime('%Y-%d%m %H:%M:%S'))

#Página de inicio con loggin de un usuario
#@app.route('/index')
#def index():
#    if 'username' in session:
#        return render_template('home.html', username=session['username'])
#    return render_template('home.html')

#Página de datos
@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():    
    if request.method == 'POST':
        umbral = request.form['umbral']
        print ('Umbral POST: ',umbral)
        items = proc_umbral(umbral)
        print ('\nPOST DATA:\n',items,'\n')
        if 'username' in session:            
            return render_template('dashboard.html', items=items, username=session['username'])
        return render_template('dashboard.html', items=items)
    return render_template('dashboard.html')

#Acción para obtener las medias
@app.route('/mean')
def media():
    global database
    print(database)
    local_db = database
    if database == 'MongoDB':
        media = mean_mdb()
    else:
        media = mean_beebotte()
    if 'username' in session:
        return render_template('dashboard.html', media=media, database=local_db, username=session['username'])
    return render_template('dashboard.html', media=media, database=local_db)

#Página para darse de alta y acciones
@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        users = mongo.db.users
        signup_user = users.find_one({'username': request.form['username']})

        if signup_user:
            flash(request.form['username'] + ' username already exist')
            return redirect(url_for('signup'))

        hashed = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt(14))
        users.insert({'username': request.form['username'], 'password': hashed, 'email': request.form['email']})
        return redirect(url_for('signin'))
    return render_template('signup.html')

#Página para logearse y acciones
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        signin_user = users.find_one({'username': request.form['username']})

        if signin_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), signin_user['password']) == \
                    signin_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('home'))
        flash('Username and password combination is wrong')
        return render_template('signin.html')
    return render_template('signin.html')

#Acción de logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

#Página de about
@app.route('/about')
def about():
    if 'username' in session:
        return render_template('about.html', username=session['username'])
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
