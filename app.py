import pytz
from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
#----------------------------------------------------------------------------------------------------------------------#
from bs4 import BeautifulSoup
import requests
import re

def get_cheapest_prices(gpu_list):

    list_of_cheapest_prices = []

    for gpu in gpu_list:

        list_of_prices = []

        url = f"https://www.newegg.com/p/pl?d={gpu}&Order=1&N=4131%204814"

        results = requests.get(url).text
        my_doc = BeautifulSoup(results,'html.parser')

        my_pattern = re.compile(pattern="^.*"+f"{gpu}"+".*$")

        price_tags = my_doc.find_all('div',class_='item-container')

        for entry in price_tags:
            text_child = entry.find('div',class_='item-info')
            grandchild = text_child.find('a',class_='item-title')
            valid_grandchild = re.search(pattern=my_pattern,string=grandchild.string)
            if valid_grandchild:
                current_price = entry.find('li',class_='price-current')
                try:
                    refined = current_price.strong.text.replace(',','')
                except:
                    refined = '0'
                if 300<int(refined)<1500:
                      list_of_prices.append(int(refined))

        if list_of_prices != []:
            cheapest_price = min(list_of_prices)
        else:
            cheapest_price = 'NOT FOUND!'

        list_of_cheapest_prices.append([gpu,cheapest_price])

    return list_of_cheapest_prices
#----------------------------------------------------------------------------------------------------------------------#
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signers.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prices.db'
db = SQLAlchemy(app)

class Signers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50),nullable=False)

class Prices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.String,nullable=False)

@app.route('/')
def home():
    title = 'HOME'
    return render_template('home.html',title=title)

@app.route('/nvidea')
def nvidea():
    title = 'NVIDEA'
    current_time = datetime.now()
    current_time = current_time.replace(microsecond=0, second=0)
    russia_timezone = pytz.timezone('Europe/Moscow')
    current_time_2 = current_time.astimezone(russia_timezone)
    time_as_str = current_time_2.strftime("'%H:%M', %A %B %Y")
    Prices.query.delete()
    db.session.commit()
    for result in get_cheapest_prices(['RTX 3060 Ti','RTX 3070','RTX 3070 Ti','RTX 3080','RTX 3090']):
        gpu_and_price = Prices(name=result[0], price=result[1])
        db.session.add(gpu_and_price)
        db.session.commit()
    info_we_need = Prices.query.order_by(Prices.id)
    return render_template('nvidea.html',title=title,info_we_need=info_we_need,
                           current_time=time_as_str)

@app.route('/amd')
def amd():
    title = 'AMD'
    current_time = datetime.now()
    current_time = current_time.replace(microsecond=0, second=0)
    russia_timezone = pytz.timezone('Europe/Moscow')
    current_time_2 = current_time.astimezone(russia_timezone)
    time_as_str = current_time_2.strftime("'%H:%M', %A %B %Y")
    Prices.query.delete()
    db.session.commit()
    for result in get_cheapest_prices(['RX 6700 XT','RX 6800']):
        gpu_and_price = Prices(name=result[0], price=result[1])
        db.session.add(gpu_and_price)
        db.session.commit()
    info_we_need = Prices.query.order_by(Prices.id)
    return render_template('amd.html', title=title, info_we_need=info_we_need,
                           current_time=time_as_str)

@app.route('/intel')
def intel():
    title = 'INTEL'
    return render_template('intel.html',title=title)

@app.route('/bancrypto',methods=['GET','POST'])
def bancrypto():
    title = 'PETITION'
    if request.method == 'GET':
        signers = Signers.query.order_by(Signers.id)
        return render_template('bancrypto.html',title=title,signers=signers)
    else:
        person_to_add = request.form['petition_form']
        new_entry = Signers(name=person_to_add)
        try:
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/bancrypto')
        except:
            return 'ERROR adding name!!!'
