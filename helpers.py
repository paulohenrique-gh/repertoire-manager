from flask import session, redirect
import mysql.connector


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