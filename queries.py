from datetime import timedelta
from pymysql import MySQLError
from helpers import *
from flask import session

def get_latest_entries(user_id, limit):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """SELECT pieces.id, title, composers.name
        FROM pieces
        JOIN composers
            ON composers.id = pieces.composer_id
        WHERE pieces.user_id = %s
        ORDER BY created_at DESC
        LIMIT %s;"""
    values = (user_id, limit,)

    db.execute(sql, values)
    rows = db.fetchall()

    if db_connection:
        db_connection.close()

    return rows


def get_all_entries(user_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """SELECT pieces.id, title, composers.name
        FROM pieces
        JOIN composers
            ON composers.id = pieces.composer_id
        WHERE pieces.user_id = %s
        ORDER BY created_at DESC"""    

    db.execute(sql, (user_id,))
    rows = db.fetchall()

    if db_connection:
        db_connection.close()

    return rows

def get_piece_details(user_id, piece_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """
        SELECT 
            title,
            opus,
            number_in_opus,
            movement,
            composers.name AS composer,
            periods.name AS period,
            start_date,
            finish_date,
            instruments.name AS instrument,
            difficulty_level,
            is_in_repertoire
        FROM pieces
        JOIN users
            ON users.id = pieces.user_id
        JOIN composers
            ON composers.id = pieces.composer_id
        JOIN periods
            ON periods.id = composers.period_id
        JOIN instruments
            ON instruments.id = pieces.instrument_id
        WHERE user_id = %s AND pieces.id = %s;"""
    values = (user_id, piece_id,)

    db.execute(sql, values)
    details = db.fetchall()

    if db_connection:
        db_connection.close()

    if not details:
        return
    
    for detail in details[0]:
        if isinstance(details[0][detail], str):
            details[0][detail] = details[0][detail].title()

    return details[0]


def get_piece_schedule(piece_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """SELECT * FROM calendar
        WHERE piece_id = %s;"""
    values = (piece_id,)

    db.execute(sql, values)
    schedule = db.fetchall()

    if db_connection:
        db_connection.close()

    return schedule


def remove_piece(piece_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """DELETE FROM pieces
        WHERE id =  %s;"""
    values = (piece_id,)

    try:
        db.execute(sql, values)
        db_connection.commit()
    except:
        db_connection.rollback()
    finally:
        if db_connection:
            db_connection.close()


def update_piece(piece_id, title, opus,
                number_in_opus, movement,
                composer, instrument,
                difficulty_level,
                add_to_repertoire,
                start_date, finish_date):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """UPDATE pieces
        SET
            title = %s,
            opus = %s,
            number_in_opus = %s,
            movement = %s,
            composer_id = %s,
            instrument_id = %s,
            difficulty_level = %s,
            is_in_repertoire = %s,
            start_date = %s,
            finish_date = %s,
            updated_at = CURRENT_TIMESTAMP()
        WHERE id = %s;
            """
    values = (title, opus, number_in_opus,
              movement, composer, instrument,
              difficulty_level, add_to_repertoire,
              start_date, finish_date, piece_id)    

    try:
        db.execute(sql, values)
        db_connection.commit()
    except MySQLError as ex:
        db_connection.rollback()
        print("ex")
    finally:
        if db_connection:
            db_connection.close()


def get_finished_date(piece_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """SELECT finish_date
        FROM pieces
        WHERE id = %s;"""
    
    db.execute(sql, (piece_id,))
    finish_date = db.fetchall()[0]['finish_date']

    return finish_date


def remove_from_calendar(piece_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """DELETE FROM calendar
        WHERE piece_id = %s;"""
    
    try:
        db.execute(sql, (piece_id,))
        db_connection.commit()
    except:
        db_connection.rollback()
    finally:
        if db_connection:
            db_connection.close()


def is_in_calendar(piece_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """SELECT * FROM calendar
        WHERE piece_id = %s;"""
    
    db.execute(sql, (piece_id,))

    if db.fetchall():
        return True
    
    return False

def get_repertoire(user_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """
        SELECT 
            pieces.id AS piece_id,
            pieces.title AS title,
            MAX(composers.name) AS composer,
            MIN(calendar.date_to_play) AS date_to_play
        FROM pieces
        JOIN users
            ON users.id = pieces.user_id
        JOIN composers
            ON composers.id = pieces.composer_id
        JOIN calendar
            ON calendar.piece_id = pieces.id
        WHERE users.id = %s
        GROUP BY pieces.id
        ORDER BY date_to_play;"""
    
    db.execute(sql, (user_id,))
    repertoire = db.fetchall()

    return repertoire


def reset_roteation(start_date, piece_id):
    remove_from_calendar(piece_id)

    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    INTERVALS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 18, 22, 30, 38, 54, 70]
    sql = """INSERT INTO calendar
        (date_to_play, piece_id)
        VALUES (
            %s,
            %s);"""
    
    for interval in INTERVALS:
        tdelta = timedelta(days=interval)
        values = (start_date + tdelta, piece_id)
        try:
            db.execute(sql, values)
            db_connection.commit()
        except MySQLError as ex:
            db_connection.rollback()
            print("ex")

    if db_connection:
        db_connection.close()

# returns a a list of dictionaries with dates as keys and pieces as values
def search_calendar(start, end, user_id):
    db_connection = db_connect()
    db = db_connection.cursor(dictionary=True, buffered=True)
    sql = """
        SELECT
            date_to_play,
            pieces.title AS title,
            composers.name AS composer,
            calendar.piece_id AS piece_id
        FROM calendar
        JOIN pieces
            ON pieces.id = calendar.piece_id
        JOIN composers
            ON composers.id = pieces.composer_id
        WHERE
            (date_to_play BETWEEN %s AND %s)
            AND pieces.user_id = %s
        ORDER BY date_to_play;"""
    values = (start, end, user_id,)

    db.execute(sql, values)
    search_results = db.fetchall()
    search_results = format_calendar(search_results)

    return search_results
