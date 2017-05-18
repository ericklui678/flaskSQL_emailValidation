from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
import os, binascii
app = Flask(__name__)
mysql = MySQLConnector(app,'email') #database name
app.secret_key = 'ThisIsSecret'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    email_form = request.form['email']
    if len(email_form) < 1: # if empty
        flash('Email cannot be blank!')
        return redirect('/')
    elif not EMAIL_REGEX.match(email_form): # if invalid format
        flash('Invalid Email Address')
        return redirect('/')
    else: # if correct format
        # SELECT EXISTS returns boolean whether email exists in db
        query = "SELECT EXISTS (SELECT * FROM email WHERE email = '" + email_form + "')"
        show_query = mysql.query_db(query)
        for dict in show_query:
            for key in dict:
                if dict[key] == 1:   # if email exists in database
                    flash('Email already exists in database')
                    return redirect('/')
                else:
                    flash('Your email '+ email_form + ' has been added to the database')
                    query = "INSERT INTO email (email, created_at, updated_at) VALUES (:email, NOW(), NOW())"
                    query_data = {'email': email_form}
                    mysql.query_db(query, query_data)

    return redirect('/success')

@app.route('/success')
def success():
    query = "SELECT id, email, DATE_FORMAT(created_at, '%m/%d/%y %l:%i %p') as cDate FROM email"
    show_query = mysql.query_db(query)

    return render_template('success.html', show_query=show_query)

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    query = "DELETE FROM email WHERE id = :id"
    query_data = {'id': id}
    mysql.query_db(query, query_data)
    return redirect('/success')

app.run(debug = True)
