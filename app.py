from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

db_connection = mysql.connector.connect(
    host="localhost",
    username="root",
    password="db@2023",
    database="music_pieces"
)

db = db_connection.cursor(dictionary=True, buffered=True)

@app.route("/")
def index():

    db.execute("SELECT name FROM instruments WHERE id=%s", (1,))
   
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=False)



