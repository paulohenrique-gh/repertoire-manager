from pymysql import MySQLError
from helpers import db_connect
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





