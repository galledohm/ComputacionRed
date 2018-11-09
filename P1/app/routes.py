#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import Flask, render_template
import urllib.request as urlreq
import re
import datetime

app = Flask(__name__)      

def proc_data():
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

    n_votos = re.findall('<a id="a-votes-\d{7}" href="/story/([a-z0-9]+-?)+\d?">(\d+)</a>',html_text)
    n_votos_first = n_votos[0][1]
    print ('NVotos:', n_votos_first)

    #Obtencion de la fecha y hora del sistema
    fecha = datetime.datetime.now()
    return titulo,n_clics_first,n_votos_first,fecha

@app.route('/')
@app.route('/index')
def home():
    titulo,clics,votos,fecha = proc_data()
    return render_template('home.html', titulo=titulo, clics=clics,votos=votos, fecha=fecha.strftime('%Y-%d%m %H:%M:%S'))
 
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
  app.run(debug=True)
