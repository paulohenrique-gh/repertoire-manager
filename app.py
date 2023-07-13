from datetime import datetime, timedelta, date
import re

import mysql.connector
from flask import Flask, flash, render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *
from queries import *
from flask_session import Session

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if not is_logged_in():
        return redirect("/login")
    
    latest = get_latest_entries(session["user_id"], 5)
    
    return render_template("index.html", latest=latest)

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
            return render_template("login.html")

        password = request.form.get("password")
        # Check if password is empty
        if not password:
            flash("Password field cannot be empty")
            return render_template("login.html")

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
            return render_template("login.html")

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

    if not is_logged_in():
        return redirect("/login")

    if request.method == "POST":

        user_id = session["user_id"]

        # Title validation
        title = request.form.get("title").lower()
        if not title:
            flash("A required field was left empty.")
            return redirect("/add_piece")

        # Opus validation
        opus = request.form.get("opus")
        if opus.isdigit():
            opus = int(opus)
        else: 
            opus = None

        # Number in opus validation
        number_in_opus = request.form.get("number_in_opus")
        if number_in_opus.isdigit():
            number_in_opus = int(number_in_opus)
        else:
            number_in_opus = None

        # Movement validation
        movement = request.form.get("movement")
        if movement.isdigit():
            movement = int(movement)
        else:
            movement = None

        # Period validation
        period = request.form.get("period").lower()
        if not period:
            flash("A required field was left empty.")
            return redirect("/add_piece")
        else:
            period = get_period_id(period)

        # Composer validation
        composer = request.form.get("composer").lower()
        if not composer:
            flash("A required field was left empty.")
            return redirect("/add_piece")
        else:
            composer = get_composer_id(composer, period)

        # Instrument validation
        instrument = request.form.get("instrument").lower()
        if not instrument:
            instrument = None
        else: 
            instrument = get_instrument_id(instrument)        

        # Difficulty level validation
        difficulty_level = request.form.get("difficulty_level")
        if difficulty_level.isdigit():
            difficulty_level = int(difficulty_level)
        else:
            difficulty_level = None

        # IsInRepertoire validation
        add_to_repertoire = request.form.get("add_to_repertoire")
        if add_to_repertoire:
            add_to_repertoire = True
        else:
            add_to_repertoire = False

        # Start date validation
        start_date = request.form.get("start_date")
        date_pattern = re.compile("^(\d{4})-(\d{2})-(\d{2})$")
        if start_date and date_pattern.match(start_date):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            # days_to_add = timedelta(days=7) # testing timedelta
            # print(f"Added 7 days: {start_date + days_to_add}", type(start_date + days_to_add))
        else:
            start_date = None
            print("Start date: ", start_date, ", type: ", type(start_date))        

        # Finish date validation
        finish_date = request.form.get("finish_date")
        date_pattern = re.compile("^(\d{4})-(\d{2})-(\d{2})$")
        if finish_date and date_pattern.match(finish_date):
            finish_date = datetime.strptime(finish_date, "%Y-%m-%d").date()
            if finish_date < start_date:
                flash("Start date cannot be greater than finish date")
                return redirect("/add_piece")
        else:
            finish_date = None


        # Debugging
        print(f"User ID: {user_id}, type: {type(user_id)}")
        print(f"Title: {title}, type: {type(title)}")
        print(f"Opus: {opus}, type: {type(opus)}")
        print(f"Number: {number_in_opus}, type: {type(number_in_opus)}")
        print(f"Movement: {movement}, type: {type(movement)}")
        print(f"Period ID: {period}, type: {type(period)}")
        print(f"Composer ID: {composer}, type: {type(composer)}")
        print(f"Instrument ID: {instrument}, type: {type(instrument)}")
        print(f"Difficulty level: {difficulty_level}, type: {type(difficulty_level)}")
        print(f"Is in repertoire: {add_to_repertoire}, type: {type(add_to_repertoire)}")
        print(f"Start date: {start_date}, type: {type(start_date)}")
        print(f"Finish date: {finish_date}, type: {type(finish_date)}")


        db_connection = db_connect()
        db = db_connection.cursor()

        sql = """INSERT INTO PIECES (
            user_id,
            title,
            opus,
            number_in_opus,
            movement,
            composer_id,
            instrument_id,
            difficulty_level,
            is_in_repertoire,
            start_date,
            finish_date,
            created_at,
            updated_at) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, now(), now())"""
        
        values = (user_id, title, opus,
                  number_in_opus, movement,
                  composer, instrument,
                  difficulty_level,
                  add_to_repertoire,
                  start_date, finish_date,)
        
        try:
            db.execute(sql, values)
            db_connection.commit()
        except:
            db_connection.rollback()
            flash("An error has ocurred")
            return redirect("/add_piece")
        finally:
            if db_connection:
                db_connection.close()

        if add_to_repertoire:
            create_rep_rotation(start_date, title, user_id)

        flash("Piece saved successfully")
        return render_template("add_piece.html")

    return render_template("add_piece.html")


@app.route("/details/<id>", methods=["GET", "POST"])
def details(id):

    if not is_logged_in():
        return redirect("/login")
    
    if request.method == "GET":
        details = get_piece_details(session["user_id"], id)

        # title <class 'str'>
        # opus <class 'int'>
        # number_in_opus <class 'int'>
        # movement <class 'int'>
        # composer <class 'str'>
        # period <class 'str'>
        # start_date <class 'datetime.date'>
        # finish_date <class 'datetime.date'>
        # is_in_repertoire <class 'int'>
        return render_template("details.html", details=details)

    
    return render_template("details.html", id=id)

