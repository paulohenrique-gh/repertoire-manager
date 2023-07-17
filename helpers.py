import os

import mysql.connector
from flask import session


def is_logged_in():
    if session.get("user_id") is None:
        return False
    else:
        return True
    
# Configure MySQL connection
def db_connect():
    db_username = os.environ.get('DB_USERNAME')
    db_password = os.environ.get('DB_PASSWORD')
    db_connection = mysql.connector.connect(
        host="localhost",
        username=db_username,
        password=db_password,
        database="music_pieces"
    )
    return db_connection


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