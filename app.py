import re

import mysql.connector
from flask import Flask, flash, render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash

from error_messages import *
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


@app.route("/add_piece")
def add_piece():
    return render_template("add_piece.html")
