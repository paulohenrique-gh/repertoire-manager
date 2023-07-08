from flask import Flask, render_template, request, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from error_messages import *
import mysql.connector
import re

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

db_connection = db_connect()

db = db_connection.cursor(dictionary=True, buffered=True)

@app.route("/")
def index():

    db.execute("SELECT name FROM instruments WHERE id=%s", (1,))
    rows = db.fetchall()
    for row in rows:
        print(row)
   
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
            return render_template("error.html", error_message=get_registration_error())
        
        # Validate password
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not confirmation == password:
            return render_template("error.html", error_message=get_registration_error())

        hash = generate_password_hash(password)

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
    return render_template("login.html")
