from os import environ
from flask import Flask, render_template, request, send_from_directory, jsonify, json, redirect, url_for, flash
from sqlalchemy import create_engine, distinct, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from calendar import calendar
from werkzeug.utils import secure_filename
from functools import reduce
import pandas as pd
import csv
import os

# Import modules to declare columns and column data types
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import Session
from collections import Counter

# Initializing Application
Base = declarative_base()
app = Flask(__name__)

# Set Database connection values
if (environ.get("DATABASE_URL")):
    connection_string = environ.get("DATABASE_URL")
else:
    HOSTNAME = environ.get("DB_HOSTNAME")
    PORT = environ.get("DB_PORT")
    USERNAME = environ.get("DB_USERNAME")
    PASSWORD = environ.get("DB_PASSWORD")
    DIALECT = environ.get("DB_DIALECT")
    DRIVER = environ.get("DB_DRIVER")
    DATABASE = environ.get("DB_DATABASE")
    connection_string = (f"{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}")

engine = create_engine(connection_string, pool_size=10, max_overflow=0)
engine.connect()
Base.metadata.create_all(engine)
session = Session(bind=engine)

class MixIn():
    def __repr__(self):
        return f"{self.__tablename__}(transaction_date: {self.transaction_date}, expense_amt: {self.expense_amt}, category: {self.category}, sub_category: {self.sub_category}, payment_method: {self.payment_method}, description: {self.description})"
    def to_dict(self):
        return {"expense_id": self.expense_id, "transaction_date": {self.transaction_date}, "expense_amt": self.expense_amt, "category": self.category, "sub_category": self.sub_category, "payment_method": self.payment_method, "description": self.description}

class MixIn2():
    def __repr__(self):
        return f"{self.__tablename__}(new_category: {self.new_category}, subcategory: {self.subcategory})"
    def to_dict(self):
        return {"new_category": {self.new_category}, "subcategory": {self.subcategory}}

class ExpenseInfo(Base, MixIn):
    __tablename__ = "expenses"
    expense_id = Column(Integer, primary_key=True)
    transaction_date = Column(Date)
    expense_amt = Column(Integer)
    category = Column(String(40))
    sub_category = Column(String(40))
    payment_method = Column(String(40))
    description = Column(String(500))

class IncomeInfo(Base):
    __tablename__ = "income"
    income_id = Column(Integer, primary_key=True)
    income_date = Column(Date, server_default=func.now())
    income_amt = Column(Integer)

class CategoryInfo(Base, MixIn2):
    __tablename__ = "categories"
    new_category = Column(String(25), primary_key=True)
    subcategory = Column(String(25))


def initQueryObjects():
    # session = Session(bind=engine)
    # Get Expenses
    expensesQuery = session.query(ExpenseInfo)

    # Get income
    income = round(session.query(func.avg(IncomeInfo.income_amt)).scalar(), 0)

    # Get distinct years from the database
    dates_query = expensesQuery.filter(ExpenseInfo.transaction_date > "1900-01-01")
    dates_list = [row.transaction_date.year for row in dates_query.all()]

    # Get categories from the database
    categories_list = sorted(Counter([row.category for row in expensesQuery.all()]).keys())

    # Sum of credits
    credit_amt_query = expensesQuery.filter(ExpenseInfo.payment_method == "Credit Card")
    
    # Sum of cash
    cash_amt_query = expensesQuery.filter(ExpenseInfo.payment_method == "Cash")

    session.close()

    return expensesQuery, income, dates_list, categories_list, credit_amt_query, cash_amt_query


@app.route('/')
def index():
    return send_from_directory("", "index.html")

    
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():

    expensesQuery, income, dates_list, categories_list, credit_amt_query, cash_amt_query = initQueryObjects()

    credit_amt_list = [row.expense_amt for row in credit_amt_query.all()]
    if (len(credit_amt_list) > 0):
        credit_amt = reduce(lambda x, y: x+y, credit_amt_list)

    cash_amt_list = [row.expense_amt for row in cash_amt_query.all()]
    if (len(cash_amt_list) > 0):
        cash_amt = reduce(lambda x, y: x+y, cash_amt_list)

    expenses_list = [row.expense_amt for row in expensesQuery.all()]
    if (len(cash_amt_list) > 0):
        expenses = reduce(lambda x, y: x+y, expenses_list)
    
    if income == 0:
        savings_rate = 0
    else:
        savings_rate = round((income - expenses) / income * 100, 2)

    return render_template("dashboard.html", 
                            years = Counter(dates_list).keys(), 
                            categories = categories_list,
                            transactions = expensesQuery.count(),
                            credit_amt = credit_amt,
                            cash_amt = cash_amt,
                            expenses = expenses,
                            income = income,
                            savings_rate = savings_rate)


@app.route("/filters", methods=['GET', 'POST'])
def filters():
    exp_key = []
    exp_val = []
    subcat_key = []
    subcat_val = []
    credit_amt = 0
    cash_amt = 0
    expenses = 0


    filters = request.json["filters"]

    expensesQuery, income, dates_list, categories_list, credit_amt_query, cash_amt_query = initQueryObjects()

    subcategories = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                        ExpenseInfo.sub_category).\
                        group_by(ExpenseInfo.sub_category).\
                        order_by(func.round(func.sum(ExpenseInfo.expense_amt)).desc())

    transactions_query = expensesQuery
   
    # Validate if the plot should be filtered
    def filtered():
        if (len(filters) == 0 or 
            (
            ("years" in filters and len(filters["years"]) == 0) and
            ("months" in filters and len(filters["months"]) == 0) and
            ("categories" in filters and len(filters["categories"]) == 0)
            )
            ):
            return False
        elif(
            ("years" in filters and len(filters["years"]) > 0) or 
            ("months" in filters and len(filters["months"]) > 0) or 
            ("categories" in filters and len(filters["categories"]) > 0)
            ):
            return True

    if not filtered(): 
        expenses_main = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                        ExpenseInfo.category).\
                        group_by(ExpenseInfo.category).\
                        order_by(func.round(func.sum(ExpenseInfo.expense_amt)).desc()) 
    else:    
        expenses_main = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                            func.year(ExpenseInfo.transaction_date),
                            func.month(ExpenseInfo.transaction_date),
                            func.max(ExpenseInfo.transaction_date.cast(Date))).\
                            group_by(func.year(ExpenseInfo.transaction_date),
                                    func.month(ExpenseInfo.transaction_date)).\
                            order_by(func.max(ExpenseInfo.transaction_date.cast(Date)))


    if ("years" in filters and len(filters["years"]) > 0):
        years = filters["years"]
        transactions_query = expensesQuery.filter(func.year(ExpenseInfo.transaction_date).in_(years))
        credit_amt_query = credit_amt_query.filter(func.year(ExpenseInfo.transaction_date).in_(years))
        cash_amt_query = cash_amt_query.filter(func.year(ExpenseInfo.transaction_date).in_(years))
        expensesQuery = expensesQuery.filter(func.year(ExpenseInfo.transaction_date).in_(years))
        income = session.query(func.avg(IncomeInfo.income_amt)).filter(func.year(IncomeInfo.income_date).in_(years)).order_by(IncomeInfo.income_date.desc()).first()[0]
        expenses_main = expenses_main.filter(func.year(ExpenseInfo.transaction_date).in_(years))

    
    if ("months" in filters and len(filters["months"]) > 0):
        months = filters["months"]
        transactions_query = expensesQuery.filter(func.month(ExpenseInfo.transaction_date).in_(months))
        credit_amt_query = credit_amt_query.filter(func.month(ExpenseInfo.transaction_date).in_(months))
        cash_amt_query = cash_amt_query.filter(func.month(ExpenseInfo.transaction_date).in_(months))
        expensesQuery = expensesQuery.filter(func.month(ExpenseInfo.transaction_date).in_(months))
        income = income/12
        expenses_main = expenses_main.filter(func.month(ExpenseInfo.transaction_date).in_(months))

     
    if ("categories" in filters and len(filters["categories"]) > 0):
        categories = filters["categories"]
        transactions_query = expensesQuery.filter(ExpenseInfo.category.in_(categories))
        credit_amt_query = credit_amt_query.filter(ExpenseInfo.category.in_(categories))
        cash_amt_query = cash_amt_query.filter(ExpenseInfo.category.in_(categories))
        expensesQuery = expensesQuery.filter(ExpenseInfo.category.in_(categories))
        subcategories =  subcategories.filter(ExpenseInfo.category.in_(categories))
        expenses_main = expenses_main.filter(ExpenseInfo.category.in_(categories))

    session.close()

    if not filtered():
        for i in expenses_main.all():
            exp_key.append(str(i[1]))
            exp_val.append(str(i[0]))
    else:
        for i in expenses_main.all():
            exp_key.append(str(i[3].strftime('%b-%Y')))
            exp_val.append(str(i[0]))


    for i in subcategories.limit(10).all():
        subcat_key.append(str(i[1]))
        subcat_val.append(str(i[0]))

    credit_amt_list = [row.expense_amt for row in credit_amt_query.all()]
    if (len(credit_amt_list) > 0):
        credit_amt = reduce(lambda x, y: x+y, credit_amt_list)

    cash_amt_list = [row.expense_amt for row in cash_amt_query.all()]
    if (len(cash_amt_list) > 0):
        cash_amt = reduce(lambda x, y: x+y, cash_amt_list)

    expenses_list = [row.expense_amt for row in expensesQuery.all()]
    if (len(expenses_list) > 0):
        expenses = reduce(lambda x, y: x+y, expenses_list)

    transactions = transactions_query.count()

    if not credit_amt:
        credit_amt = 0
    else:
        credit_amt = credit_amt

    if not cash_amt:
        cash_amt = 0
    else:
        cash_amt = cash_amt

    if not expenses:
        expenses = 0
    else:
        expenses = expenses

    if income == 0:
        savings_rate = 0
    else:
        savings_rate = round((income - expenses) / income * 100, 2)

    data = {
        "transactions": transactions,
        "credit_amt": str(credit_amt),
        "cash_amt": str(cash_amt),
        "expenses": str(expenses),
        "income": str(round(income, 0)),
        "savings_rate": str(savings_rate),
        "exp_key": exp_key,
        "exp_val": exp_val,
        "subcat_key": subcat_key,
        "subcat_val": subcat_val
    }

    return jsonify(data)

@app.route("/toptensubcat", methods=['GET','POST'])
def toptensubcat():
    session = Session(bind=engine)
    subcat_key = []
    subcat_val = []

    toptensubcat = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                        ExpenseInfo.sub_category).\
                        group_by(ExpenseInfo.sub_category).\
                        order_by(func.round(func.sum(ExpenseInfo.expense_amt)).desc())

    for i in toptensubcat.limit(10).all():
            subcat_key.append(str(i[1]))
            subcat_val.append(str(i[0]))

    data = {
        "subcat_key": subcat_key,
        "subcat_val": subcat_val
    }

    session.close()

    return jsonify(data)


@app.route("/mainplot", methods=['GET','POST'])
def mainplot():
    session = Session(bind=engine)
    mainplot_key = []
    mainplot_val = []

    mainplot = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                        ExpenseInfo.category).\
                        group_by(ExpenseInfo.category).\
                        order_by(func.round(func.sum(ExpenseInfo.expense_amt)).desc())

    for i in mainplot.all():
        mainplot_key.append(str(i[1]))
        mainplot_val.append(str(i[0]))

    data = {
        "mainplot_key": mainplot_key,
        "mainplot_val": mainplot_val
    }

    session.close()

    return jsonify(data)


@app.route("/ieplot/<period>", methods=['GET','POST'])
def ieplot(period):
    session = Session(bind=engine)
    inc_key = []
    inc_val = []
    exp_key = []
    exp_val = []

    if period == "annual":
        income = session.query(func.round(func.avg(IncomeInfo.income_amt)), 
                        func.year(IncomeInfo.income_date),
                        func.max(IncomeInfo.income_date.cast(Date))).\
                        group_by(func.year(IncomeInfo.income_date))

        expenses = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                        func.year(ExpenseInfo.transaction_date),
                        func.max(ExpenseInfo.transaction_date.cast(Date))).\
                        filter(ExpenseInfo.transaction_date > "1900-01-01").\
                        group_by(func.year(ExpenseInfo.transaction_date))

        for i in income.all():
            inc_key.append(str(i[2].year))
            inc_val.append(str(i[0]))

        for e in expenses.all():
             exp_key.append(str(e[2].year))
             exp_val.append(str(e[0]))



    if period == "monthly":
        income = session.query(func.round(func.avg(IncomeInfo.income_amt)), 
                        func.year(IncomeInfo.income_date),
                        func.month(IncomeInfo.income_date),
                        func.max(IncomeInfo.income_date.cast(Date))).\
                        group_by(func.year(IncomeInfo.income_date),
                                func.month(IncomeInfo.income_date)).\
                        order_by(func.max(IncomeInfo.income_date.cast(Date)))

        expenses = session.query(func.round(func.sum(ExpenseInfo.expense_amt)), 
                        func.year(ExpenseInfo.transaction_date),
                        func.month(ExpenseInfo.transaction_date),
                        func.max(ExpenseInfo.transaction_date.cast(Date))).\
                        group_by(func.year(ExpenseInfo.transaction_date),
                                func.month(ExpenseInfo.transaction_date)).\
                        order_by(func.max(ExpenseInfo.transaction_date.cast(Date)))

        for i in income.all():
            inc_key.append(str(i[3]))
            inc_val.append(str(i[0]/12))

        for e in expenses.all():
             exp_key.append(str(e[3]))
             exp_val.append(str(e[0]))

    data = {
        "inc_key": inc_key,
        "inc_val": inc_val,
        "exp_key": exp_key,
        "exp_val": exp_val
    }

    session.close()

    return jsonify(data)


@app.route("/transactions", methods=['GET','POST'])
def transactions():
    session = Session(bind=engine)
    cur = session.execute("select DISTINCT new_category FROM categories ORDER BY new_category")
    data = cur.fetchall()
    session.close()
    return render_template("transactions.html", data=data)


@app.route("/filtersubcat", methods=['GET','POST'])
def filtersubcat():
    session = Session(bind=engine)
    chosen_category = request.json["category"]
    subcategory = session.query(CategoryInfo.subcategory).distinct().\
                    filter(CategoryInfo.new_category == chosen_category).\
                    order_by(CategoryInfo.subcategory).all()
    session.close()
    return jsonify(subcategory)


@app.route("/uploadcsv", methods=['GET','POST'])
def uploadcsv():
    if request.method == 'POST':
        
        csvfile = request.files['file']
        if csvfile.filename == '':
            return render_template("transactions.html", message3='No file selected')
        else:
            csvfile.save("myfile.csv")
        
            with open("myfile.csv", encoding = "ISO-8859-1") as f:
                # session = Session(bind=engine)
                reader = csv.reader(f) 
                next(reader)
                for row in reader: 
                    transaction_date = row[0]
                    expense_amt = row[1]
                    category = row[2]
                    sub_category = row[3]
                    payment_method = row[4]
                    description = row[5]

                    upload_input = ExpenseInfo(transaction_date = transaction_date, 
                    expense_amt = expense_amt, category = category, sub_category = sub_category, 
                    payment_method = payment_method, description = description)
                    session.add(upload_input)
                    session.commit()
                    session.close()

    return render_template("transactions.html", message3='File has been uploaded')

@app.route('/home', methods = ['POST'])
def home():
    if request.method == 'POST':
        return render_template('index.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        # session = Session(bind=engine)
        transaction_date = request.form['transaction_date']
        expense_amt = request.form['expense_amt']
        category = request.form['category']
        sub_category = request.form['sub_category']
        payment_method = request.form['payment_method']
        description = request.form['description']
        
        if (transaction_date != "" and expense_amt != "" and category != "" and sub_category != "" and payment_method != "" and description != ""):
            expense_input = ExpenseInfo(transaction_date = transaction_date, 
            expense_amt = expense_amt, category = category, sub_category = sub_category, 
            payment_method = payment_method, description = description)

            session.add(expense_input)
            session.commit()
            session.close()

            return render_template("transactions.html", message = 'Expense added')  
        else:
            return render_template("transactions.html", message = 'Please enter data on all fields')
        

@app.route('/submitincome', methods=['POST'])
def submitincome():
    if request.method == 'POST':
        # session = Session(bind=engine)
        incomeamt = request.json["incomeamt"]

        if incomeamt == "" :
            message = "A value is required"
        else:
            income_input = IncomeInfo(income_amt = incomeamt)
            session.add(income_input)
            session.commit()
            message = "Income added"
            
        data = {
             "message": message
        }
        session.close()
        return jsonify(data)

@app.route('/addcat', methods=['POST'])
def addcat():
    if request.method == 'POST':
        # session = Session(bind=engine)
        new_category = request.form['new_category']
        subcategory = request.form['subcategory']
        
        if new_category != "" and subcategory != "":
            cat_input = CategoryInfo(new_category = new_category, subcategory = subcategory)
            
            session.add(cat_input)
            session.commit()
            session.close()
           
            return render_template('transactions.html', message2 = 'New categories added')
        else:
            return render_template('transactions.html', message2 = 'Please enter data on both fields')

@app.route("/dash-summary")
def dash_summary():
    return render_template("dash-summary.html")

@app.route("/users-link")
def users_link():
    return render_template("users-link.html")

if __name__ == '__main__':
    app.debug = environ.get("DEBUG")
    app.run()

