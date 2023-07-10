from datetime import datetime
import re

import mysql.connector
from flask import Flask, flash, render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from error_messages import *
from helpers import *
from flask_session import Session

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Configure MySQL connection
def db_connect():
    db_connection = mysql.connector.connect(
        host="localhost",
        username="root",
        password="db@2023",
        database="music_pieces"
    )
    return db_connection



@app.route("/")
def index():

    """ db.execute("SELECT name FROM instruments WHERE id=%s", (1,))
    rows = db.fetchall()
    for row in rows:
        print(row) """
   
    return render_template("index.html")

# Registration route
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        name = request.form.get("name")

        # Validate email
        email = request.form.get("email")
        email_pattern = re.compile("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$")
        if not email_pattern.match(email):
            flash("Invalid email")
            return render_template("signup.html")
        
        # Validate password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not confirmation == password:
            flash("Passwords don't match")
            return render_template("signup.html")

        hash = generate_password_hash(password)

        # Open DB connection        
        db_connection = db_connect()
        db = db_connection.cursor(dictionary=True, buffered=True)

        # Check existence of username in DB
        sql = """SELECT * FROM users
            WHERE name = %s"""
        db.execute(sql, (name,))
        rows = db.fetchall()
        if len(rows) >= 1:
            flash("Username already exists")
            return render_template("signup.html")
        

        
        # Insert into database if everything is valid
        sql = """INSERT INTO users
           (name, email, hash)
           VALUES(%s, %s, %s)"""
        
        try: 
            db.execute(sql, (name, email, hash,))
            db_connection.commit()
        except:
            db_connection.rollback()
        finally:
            if db_connection:
                db_connection.close()

        flash("Registration successful! Please login")
        return render_template("login.html")
        

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    
    if request.method == "POST":
         
        email = request.form.get("email")
        # Check for empty email
        if not email:
            flash("Email field cannot be empty")

        password = request.form.get("password")
        # Check if password is empty
        if not password:
            flash("Password field cannot be empty")

        # Open DB connection        
        db_connection = db_connect()
        db = db_connection.cursor(dictionary=True, buffered=True)

        sql = """SELECT * FROM users
            WHERE email = %s"""

        # Check that user is registered and password is correct        
        db.execute(sql, (email,))        
        rows = db.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password")      

        # Save user id in session
        session["user_id"] = rows[0]["id"]
        

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")


@app.route("/add_piece", methods=["GET", "POST"])
def add_piece():

    if request.method == "POST":

        # Title validation and debugging
        title = request.form.get("title")
        if not title:
            flash("Make sure the required fields are not left empty.")
            return redirect("/add_piece")
        print("Title: ", title, ", type: ", type(title))

        # Opus validation and debugging
        opus = request.form.get("opus")
        if opus.isdigit():
            opus = int(opus)
        else: 
            opus = 0
        print("Opus: ", opus, ", type: ", type(opus))

        # Number in opus validation and debugging
        number_in_opus = request.form.get("number_in_opus")
        if number_in_opus.isdigit():
            number_in_opus = int(number_in_opus)
        else:
            number_in_opus = 0
        print("Number: ", number_in_opus, ", type: ", type(number_in_opus))

        # Movement validation and debugging
        movement = request.form.get("movement")
        if movement.isdigit():
            movement = int(movement)
        else:
            movement = 0
        print("Movement: ", movement, ", type: ", type(movement))

        # Composer validation
        composer = request.form.get("composer")
        if not composer:
            flash("Make sure the required fields are not left empty.")
        print("Composer: ", composer, ", type: ", type(composer))

        # Start date parsing and debugging
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        print("Start date: ", start_date, ", type: ", type(start_date))

        # TODO Finish date parsing and debugging
        finish_date = request.form.get("finish_date")
        print("Finish date: ", finish_date, ", type: ", type(finish_date))

        instrument = request.form.get("instrument")
        print("Instrument: ", instrument, ", type: ", type(instrument))

        difficulty_level = request.form.get("difficulty_level")
        print("Difficulty level: ", difficulty_level, ", type: ", type(difficulty_level))

        add_to_repertoire = request.form.get("add_to_repertoire")
        if add_to_repertoire:
            add_to_repertoire = True
        else:
            add_to_repertoire = False
        print("Add to repertoire: ", add_to_repertoire, ", type: ", type(add_to_repertoire))

        
        return render_template("add_piece.html")

    return render_template("add_piece.html")
