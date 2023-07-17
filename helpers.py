from flask import session, redirect
import mysql.connector
from pymysql import MySQLError
from datetime import timedelta


def is_logged_in():
    if session.get("user_id") is None:
        return False
    else:
        return True
    
# Configure MySQL connection
def db_connect():
    db_connection = mysql.connector.connect(
        host="localhost",
        username="root",
        password="db@2023",
        database="music_pieces"
    )
    return db_connection


def get_instrument_id(instrument):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """INSERT INTO instruments
            (name) VALUES (%s)"""
    values = (instrument,)
    try:
        db.execute(sql, values)
        db_connection.commit()
    except:
        db_connection.rollback()
    finally:
        sql = """SELECT id FROM instruments
            WHERE name = %s"""
        values = (instrument,)

        db.execute(sql, values)
        rows = db.fetchall()
        instrument_id = rows[0]["id"]
        if db_connection:
            db_connection.close()
        
        return instrument_id

def get_period_id(period):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """INSERT INTO periods
            (name) VALUES (%s)"""
    values = (period,)
    try:
        db.execute(sql, values)
        db_connection.commit()
    except:
        db_connection.rollback()
    finally:
        sql = """SELECT id FROM periods
            WHERE name = %s"""
        values = (period,)

        db.execute(sql, values)
        rows = db.fetchall()
        period_id = rows[0]["id"]
        if db_connection:
            db_connection.close()
        
        return period_id
    

def get_composer_id(composer, period_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """INSERT INTO composers
            (name, period_id) VALUES (%s, %s)"""
    values = (composer, period_id,)
    try:
        db.execute(sql, values)
        db_connection.commit()
    except:
        db_connection.rollback()
    finally:
        sql = """SELECT id FROM composers
            WHERE name = %s"""
        values = (composer,)

        db.execute(sql, values)
        rows = db.fetchall()
        composer_id = rows[0]["id"]
        if db_connection:
            db_connection.close()
        
        return composer_id
    

def create_rep_rotation(start_date, title, user_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    INTERVALS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 18, 22, 30, 38, 54, 70]
    sql = """INSERT INTO calendar
        (date_to_play, piece_id)
        VALUES (
            %s,
            (SELECT id FROM pieces
            WHERE title = %s AND user_id = %s)
        );"""
    
    for interval in INTERVALS:
        tdelta = timedelta(days=interval)
        values = (start_date + tdelta, title, user_id)
        try:
            db.execute(sql, values)
            db_connection.commit()
        except MySQLError as ex:
            db_connection.rollback()
            print("ex")

    if db_connection:
        db_connection.close()

# Receives the raw result of the calendar query which contains a row for each piece
# and returns it formatted as dictionary with unique dates as keys
# and the values are the pieces to play that day
def format_calendar(calendar):
    unique_dates = []
    formatted_list = []
    for result in calendar:
        if result['date_to_play'] not in unique_dates:
            unique_dates.append(result['date_to_play'])            

    for date in unique_dates:
        pieces = []
        for result in calendar:
            if result['date_to_play'] == date:
                pieces.append({
                    'title': result['title'],
                    'composer': result['composer'],
                    'piece_id': result['piece_id']
                })    
        formatted_list.append({'date_to_play': date, 'pieces': pieces})

    return formatted_list