from flask import Flask, request, jsonify
from flask import render_template, url_for, redirect, flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, desc, func
from flask_marshmallow import Marshmallow

from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

import datetime as dt
import os
import simplejson

## ===================================================================================================================
## INIT - CONFIG 
## ===================================================================================================================

# INIT APP
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# CONFIG SECRET
app.secret_key = "mysecretkey"

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = "<db_credentials>"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INIT DB
db = SQLAlchemy(app)

# INIT MA
ma = Marshmallow(app)

## ===================================================================================================================
## CONTACTS 
## ===================================================================================================================

# CONTACT CLASS/MODEL
class Contact(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fullname = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def __init__(self,fullname,phone,email):
        self.fullname = fullname
        self.phone = phone
        self.email = email

# CONTACT SCHEMA
class ContactSchema(ma.Schema):
    class Meta:
        fields = ('id','fullname','phone','email')

contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

## CONTACT - CRUD =============================

# INSERT
@app.route('/contact/add_contact/',methods=["POST"])
def add_contact():
    if request.method == "POST": 
        fullname = request.form["fullname"]
        phone = request.form["phone"]
        email = request.form["email"]

        new_contact = Contact(fullname,phone,email)

        db.session.add(new_contact)
        db.session.commit()

        flash('Contact Added sucessfully')
        return redirect(url_for('mainPage'))

# EDIT-FORM
@app.route('/contact/edit/<id>')
def edit_contact(id):
    contact = Contact.query.get(id)
    return render_template('edit_contact.html', contact = contact)
# UPDATE
@app.route('/contact/update/<id>',methods=['POST'])
def update_contact(id):
    if request.method == "POST": 
        contact = Contact.query.get(id)
        fullname = request.form["fullname"]
        phone = request.form['phone']
        email = request.form['email']

        contact.fullname = fullname
        contact.phone = phone
        contact.email = email
        db.session.commit()
        flash("Contact UPDATED successfully")

    return redirect(url_for("mainPage"))


# DELETE
@app.route('/contact/delete/<id>')
def delete_contact(id):
    contact = Contact.query.get(id)
    db.session.delete(contact)
    db.session.commit()

    flash('Contact Deleted sucessfully')
    return redirect(url_for('mainPage'))

## ===================================================================================================================
## PRODUCTS 
## ===================================================================================================================

# PRODUCT CLASS/MODEL
class Product(db.Model):
    product_id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255),unique = True)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)

    def __init__(self,name,description,price,quantity):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

# PRODUCT SCHEMA
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('product_id','name','description','price','quantity')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

## PRODUCT -CRUD =============================

# INSERT
@app.route('/product/add_product/',methods=["POST"])
def add_product():
    if request.method == "POST": 
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']

        new_product = Product(name,description,price,quantity)

        db.session.add(new_product)
        db.session.commit()

        flash('Product Added sucessfully')
        return redirect(url_for('productsPage'))

# EDIT-FORM
@app.route('/product/edit/<product_id>')
def edit_product(product_id):
    product = Product.query.get(product_id)
    return render_template('edit_product.html', product = product)
# UPDATE
@app.route('/product/update/<product_id>',methods=['POST'])
def update_product(product_id):
    if request.method == "POST": 
        product = Product.query.get(product_id)
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']

        product.name = name
        product.description = description
        product.price = price
        product.quantity = quantity
        db.session.commit()
        flash("Product UPDATED successfully")

    return redirect(url_for("productsPage"))


# DELETE
@app.route('/product/delete/<product_id>')
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()

    flash('Product Deleted sucessfully')
    return redirect(url_for('productsPage'))

## ===================================================================================================================
## PURCHASES 
## ===================================================================================================================

# PURCHASE CLASS/MODEL
class Purchase(db.Model):
    purchase_id = db.Column(db.Integer,primary_key=True)
    contact_id = db.Column(db.Integer,ForeignKey("contact.id"))
    product_id = db.Column(db.Integer,ForeignKey("product.product_id"))
    purchase_datetime = db.Column(db.DateTime)
    purchase_quantity = db.Column(db.Integer)

    def __init__(self,contact_id,product_id,purchase_datetime,purchase_quantity):
        self.contact_id = contact_id
        self.product_id = product_id
        self.purchase_datetime = purchase_datetime
        self.purchase_quantity = purchase_quantity

# PURCHASE SCHEMA
class PurchaseSchema(ma.Schema):
    class Meta:
        fields = ('purchase_id','contact_id','product_id','purchase_datetime','purchase_quantity')

purchase_schema = PurchaseSchema()
purchases_schema = PurchaseSchema(many=True)

# PURCHASE-REPORT SCHEMA
class PurchaseReportSchema(ma.Schema):
    total_spend = fields.Float()
    avg_spend = fields.Float()
    class Meta:
        fields = ('fullname','purchase_count','total_spend','avg_spend')
        json_module = simplejson

purchaseReport_schema = PurchaseReportSchema()
purchasesReport_schema = PurchaseReportSchema(many=True)

# From <Purchase,Contact,Product> To-List-of-Dicts function
# Funcion auxiliar para pasar de un 'join' a List-of-dicts
def purchase_join_to_dict(dict_purchases):
    result = {}
    for key,content in dict_purchases.items():
        if key == "Purchase":
            res = {"Purchase":purchase_schema.dump(content)}
        elif key == "Contact":
            res = {"Contact":contact_schema.dump(content)}
        elif key == "Product":
            res = {"Product":product_schema.dump(content)}
        result.update(res)
    return result

## PURCHASE - CRUD =============================

# INSERT
@app.route('/purchase/add_purchase/',methods=["POST"])
def add_purchase():
    if request.method == "POST": 
        contact_id = request.form['contacts']
        product_id = request.form['products']
        purchase_quantity = request.form['purchase_quantity']

        new_purchase = Purchase(contact_id,product_id,dt.datetime.now(),purchase_quantity)
        db.session.add(new_purchase)
        db.session.commit()

        flash('Purchase Added sucessfully')
        return redirect(url_for('purchasesPage'))

# EDIT-FORM
@app.route('/purchase/edit/<purchase_id>')
def edit_purchase(purchase_id):
    purchase = db.session.query(Purchase,Contact,Product
                    ).filter(Purchase.contact_id == Contact.id
                    ).filter(Purchase.product_id == Product.product_id
                    ).filter(Purchase.purchase_id== purchase_id
                    ).first()
    
    res_purchase = purchase_join_to_dict(purchase._asdict())

    all_contacts = Contact.query.all()
    res_contacts = contacts_schema.dump(all_contacts)

    all_products = Product.query.all()
    res_products = products_schema.dump(all_products)

    return render_template('edit_purchase.html', 
                            purchase = res_purchase,
                            contacts = res_contacts,
                            products = res_products)
# UPDATE
@app.route('/purchase/update/<purchase_id>',methods=['POST'])
def update_purchase(purchase_id):
    if request.method == "POST": 
        purchase = Purchase.query.get(purchase_id)
        contact_id = request.form['contacts']
        product_id = request.form['products']
        purchase_quantity = request.form['purchase_quantity']

        purchase.contact_id = contact_id
        purchase.product_id = product_id
        purchase.purchase_quantity = purchase_quantity
        db.session.commit()
        flash("Purchase UPDATED successfully")

    return redirect(url_for("purchasesPage"))

# DELETE
@app.route('/purchase/delete/<purchase_id>')
def delete_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    db.session.delete(purchase)
    db.session.commit()

    flash('Purchase Deleted sucessfully')
    return redirect(url_for('purchasesPage'))

## ===================================================================================================================
## MAIN APP MODULES 
## ===================================================================================================================

@app.route('/')
def mainPage():
    all_contacts = Contact.query.all()
    result = contacts_schema.dump(all_contacts)

    return render_template('index.html',contacts = result)

@app.route('/product/')
def productsPage():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)

    return render_template('products.html',products = result)

@app.route('/purchase/')
def purchasesPage():
    all_purchases = db.session.query(Purchase,Contact,Product
                    ).filter(Purchase.contact_id == Contact.id
                    ).filter(Purchase.product_id == Product.product_id
                    ).order_by(desc(Purchase.purchase_id)
                    ).all()

    dict_purchases =  [r._asdict() for r in all_purchases]
    res_purchases = [purchase_join_to_dict(x) for x in dict_purchases]
    
    all_contacts = Contact.query.all()
    res_contacts = contacts_schema.dump(all_contacts)

    all_products = Product.query.all()
    res_products = products_schema.dump(all_products)

    all_report = db.engine.execute(
        """
        SELECT Contact.fullname AS fullname, 
            COUNT(Contact.id) AS purchase_count, 
            SUM(Product.price * Purchase.purchase_quantity) AS total_spend,
            AVG(Product.price * Purchase.purchase_quantity) AS avg_spend
        FROM purchase AS Purchase
        LEFT JOIN contact AS Contact 
        ON Contact.id = Purchase.contact_id
        LEFT JOIN product AS Product 
        ON Product.product_id = Purchase.product_id
        GROUP BY Contact.fullname 

        """)
    res_report = purchasesReport_schema.dump(all_report)

    return render_template('purchases.html',
                            purchases = res_purchases,
                            contacts = res_contacts,
                            products = res_products,
                            report = res_report)

if __name__ == "__main__":
    app.run(port=3000,debug=True)
