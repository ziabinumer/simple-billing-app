from asyncore import read
import os

import csv

from flask import Flask, session, request, redirect, render_template, flash, send_file
from flask_session import Session
from werkzeug.utils import secure_filename

from helpers import login_required

import random
import datetime
#import pdfkit


# configure app
app = Flask(__name__)

# templates auto reload
app.config["TEMPLATES_AUTO_RELOADED"] = True

# configure session
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'ghghdshjfhdsksukoqfFjsiRsJFJGZKAOF'

Session(app)


UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# functions
def filec(s):
    if not os.path.exists(s):
            return False
    return True

def fetchdata():
    if not filec("data.csv"):
        open("data.csv", 'a+').close()
    data = dict()
    data['customer'], data['product'], data['price'] = list(), list(), list()
    with open("data.csv") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data['customer'].append(row['Customer'].strip())
            data['product'].append(row['Product'].strip())
            data['price'].append(row['Price'].strip())
    return data

# routes
# home
@app.route("/")
@login_required
def index():
    session.permanent = False
    data = fetchdata()
    return render_template("index.html", data=data, len=len(data['customer']))

# login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Missing username or password")
            return redirect(request.url)
        if username != 'admin@123' or password != 'welcome123':
            flash("Incorrect username or password")
            return redirect(request.url)
        session["user"] = True
        return redirect("/")
    return render_template("login.html")

# logout
@app.route("/logout")
@login_required
def logout():
        session["user"] = False
        return redirect("/login")

# update
@app.route("/update", methods=["POST", "GET"])
@login_required
def update():
    if request.method == "POST":
        customer = request.form.get("customer")
        product = request.form.get("product")
        price = request.form.get("price")
        if not price:
            price = 0
        if not customer or not product:
            flash("missing customer name or product name")
            return redirect(request.url)
        with open("data.csv") as file:
            data = dict()
            data['customer'], data['product'], data['price'] = list(), list(), list()
            reader = csv.DictReader(file)
            for row in reader:
                if row['Customer'] == customer and row['Product'] == product:
                    data['customer'].append(customer)
                    data['product'].append(product)
                    data['price'].append(price)
                    continue
                data['customer'].append(row['Customer'])
                data['product'].append(row['Product'])
                data['price'].append(row['Price'])
        with open("data.csv", 'w') as file:
            file.write("Customer,Product,Price" + '\n')
            for i in range(len(data['customer'])):
                row = list()
                row.append(data['customer'][i]+',')
                row.append(data['product'][i]+',')
                row.append(data['price'][i])
                for i in range(len(row)):
                    file.write(row[i])
                file.write("\n")
        flash("Updated successfully")
        return redirect("/update")
        
    data = fetchdata()
    
    return render_template("update.html", data=data, len=len(data['customer']))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    if request.method == "POST":
        if not filec("reports.csv"):
            with open("reports.csv", 'a+') as file:
                file.write("Date,Customer Name,Phone No,Bill No,Product 1,Qty,Price,Product 2,Qty2,Price2,Total\n")
        file = open("reports.csv", "a+")
        file.write(date + request.form.get("towrite") + '\n')
        return redirect(request.url)
    data = fetchdata()
    price = list()
    for i in range(len(data['customer'])):
        price.append(data['price'][i])
    return render_template("checkout.html", price=price, date=date)



if __name__ == "__main__":
    app.run(debug=True)