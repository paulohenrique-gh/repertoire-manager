import re
from datetime import date, datetime, timedelta

import mysql.connector
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from flask_session import Session
from helpers import *
from queries import *

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    if not is_logged_in():
        return redirect("/login")
    
    latest = get_latest_entries(session["user_id"], 5)
    play_today = search_calendar(datetime.now().date(),
                                 datetime.now().date(),
                                 session["user_id"])
    
    print(play_today)
    currently_learning = get_pieces_learning(session["user_id"])
    total_in_collection = get_total_in_collection(session["user_id"])
    total_in_repertoire = get_total_in_repertoire(session["user_id"])
    highest_level = get_highest_level(session["user_id"])
    longest_to_learn = get_longest_to_learn(session["user_id"])
    top_composer = get_top_composer(session["user_id"])

    return render_template("index.html",
                            latest=latest,
                            play_today=play_today[0]['pieces'],
                            currently_learning=currently_learning,
                            total_in_collection=total_in_collection,
                            total_in_repertoire=total_in_repertoire,
                            highest_level=highest_level,
                            longest_to_learn=longest_to_learn,
                            top_composer=top_composer)


@app.route("/view_all")
def view_all():
    if not is_logged_in():
        return redirect("/login")
    
    all_entries = get_all_entries(session["user_id"])

    return render_template("index_all.html", entries=all_entries)


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
        
        # Check existence of email in DB    
        sql = """SELECT * FROM users
            WHERE email = %s"""
        db.execute(sql, (email,))
        rows = db.fetchall()
        if len(rows) >= 1:
            flash("Email already registered")
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
            flash("A required field was left empty.")
            return redirect("/add_piece")
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
            return render_template("add_piece.html")
        finally:
            if db_connection:
                db_connection.close()

        if add_to_repertoire and finish_date:
            create_rep_rotation(finish_date, title, user_id)

        flash("Piece saved successfully")
        return render_template("add_piece.html")

    return render_template("add_piece.html")


@app.route("/details/<id>")
def details(id):

    if not is_logged_in():
        return redirect("/login")
    
    if not get_piece_details(session["user_id"], id):
        return redirect("/")
    
    details = get_piece_details(session["user_id"], id)
    schedule = get_piece_schedule(id)

    opus = f"op+{details['opus']}" if details['opus'] else ""
    number = f"number+{details['number_in_opus']}" if details['number_in_opus'] else ""
    movement =f"movement+{details['movement']}" if details['movement'] else ""

    details['google_string'] = f"""
        https://www.google.com/search?q={details['composer']}
        +{details['title']}
        +{opus}
        +{number}
        +{movement}
        +filetype:pdf"""
    
    details['youtube_string'] = f"""
        https://www.youtube.com/results?search_query={details['composer']}
        +{details['title']}
        +{opus}
        +{number}
        +{movement}"""


    return render_template("details.html", 
                            details=details,
                            schedule=schedule,
                            piece_id=id,
                            today=datetime.now().date())


@app.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):

    if not is_logged_in():
        return redirect("/login")
    
    if not get_piece_details(session["user_id"], id):
        return redirect("/")
    
    details = get_piece_details(session["user_id"], id) 

    if request.method == "POST":

        details = get_piece_details(session["user_id"], id) 

        title = request.form.get("title").lower()

        opus = request.form.get("opus")
        if opus.isdigit():
            opus = int(opus)
        else: 
            opus = None

        number_in_opus = request.form.get("number_in_opus")
        if number_in_opus.isdigit():
            number_in_opus = int(number_in_opus)
        else:
            number_in_opus = None

        movement = request.form.get("movement")
        if movement.isdigit():
            movement = int(movement)
        else:
            movement = None

        period = request.form.get("period").lower()
        if not period:
            flash("A required field was left empty.")
            return render_template("edit.html", details=details, piece_id=id)
        else:
            period = get_period_id(period)

        composer = request.form.get("composer").lower()
        if not composer:
            flash("A required field was left empty.")
            return render_template("edit.html", details=details, piece_id=id)
        else:
            composer = get_composer_id(composer, period)

        instrument = request.form.get("instrument").lower()
        if not instrument:
            instrument = None
        else: 
            instrument = get_instrument_id(instrument)

        difficulty_level = request.form.get("difficulty_level")
        if difficulty_level.isdigit():
            difficulty_level = int(difficulty_level)
        else:
            difficulty_level = None                 

        start_date = request.form.get("start_date")
        date_pattern = re.compile("^(\d{4})-(\d{2})-(\d{2})$")
        if start_date and date_pattern.match(start_date):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date = None
            print("Start date: ", start_date, ", type: ", type(start_date))        

        finish_date = request.form.get("finish_date")
        date_pattern = re.compile("^(\d{4})-(\d{2})-(\d{2})$")
        if finish_date and date_pattern.match(finish_date):
            finish_date = datetime.strptime(finish_date, "%Y-%m-%d").date()
            if finish_date < start_date:
                flash("Start date cannot be greater than finish date")
                return render_template("edit.html", details=details, piece_id=id)
        else:
            finish_date = None

        add_to_repertoire = request.form.get("add_to_repertoire")
        if add_to_repertoire:
            add_to_repertoire = True
            if not is_in_calendar(id) and finish_date:
                create_rep_rotation(finish_date, title, session["user_id"])
            
            if not finish_date:
                remove_from_calendar(id)

            if is_in_calendar(id) and not finish_date == get_finished_date(id):
                reset_roteation(finish_date, id)
        else:
            add_to_repertoire = False
            remove_from_calendar(id)

        update_piece(id, title, opus, number_in_opus,
                     movement, composer, instrument,
                     difficulty_level, add_to_repertoire,
                     start_date, finish_date)      
        
        flash("Piece details were updated")
        return redirect("/")

    return render_template("edit.html", details=details, piece_id=id)


@app.route("/remove/<id>")
def remove(id):

    if not is_logged_in():
        return redirect("/login")

    if not get_piece_details(session["user_id"], id):
        return redirect("/")

    remove_piece(id)
    flash("Piece removed from collection successfully")
    return redirect("/")


@app.route("/repertoire")
def repertoire():

    if not is_logged_in():
        return redirect("/login")

    # CURRENTLY IN ROTATION
    repertoire_in_rotation = get_pieces_in_rotation(session["user_id"])
    print("IN ROTATION")
    for piece in repertoire_in_rotation:
        print(piece)

    # IN REPERTOIRE BUT NOT IN ROTATION
    repertoire_not_rotation = get_pieces_not_rotation(session["user_id"])
    print("NOT IN ROTATION")
    for piece in repertoire_not_rotation:
        print(piece)
    
    return render_template("repertoire.html",
                           repertoire_in_rotation=repertoire_in_rotation,
                           repertoire_not_rotation=repertoire_not_rotation,
                           today=datetime.now().date())
    

@app.route("/reset", methods=["POST"])
def reset():

    if not is_logged_in():
        return redirect("/login")
    
    id = request.form.get("id")
        
    remove_from_calendar(id)
    reset_roteation(datetime.now().date(), id)

    flash("Rotation reset")
    return redirect("/repertoire")


@app.route("/calendar", methods=["GET", "POST"])
def calendar():

    if not is_logged_in():
        return redirect("/login")

    search_results = []

    if request.method == "POST":

        start = request.form.get("start")
        date_pattern = re.compile("^(\d{4})-(\d{2})-(\d{2})$")
        if start and date_pattern.match(start):
            start = datetime.strptime(start, "%Y-%m-%d").date()
        else:
            flash("Invalid date format")
            return redirect("/calendar")
        
        end = request.form.get("end")   
        date_pattern = re.compile("^(\d{4})-(\d{2})-(\d{2})$")
        if end and date_pattern.match(end):
            end = datetime.strptime(end, "%Y-%m-%d").date()
            if end < start:
                flash("Start date cannot be greater than end date")
                return redirect("/calendar")
        else:
            flash("Invalid date format")
            return redirect("/calendar")
        
        search_results = search_calendar(start, end, session["user_id"])

        for date in search_results:
            print(date)

        return render_template("calendar_search.html", results=search_results)

        
    return render_template("calendar.html")

@app.route("/search")
def search():
    
    if not is_logged_in():
        return redirect("/login")
    
    search = request.args.get("search").lower()
    search_results = None
    if search: 
        search_results = get_search_results(session["user_id"], search)

    print(search)
    print(search_results)
    
    return render_template("search_results.html",
                           search=string.capwords(search),
                           results=search_results)