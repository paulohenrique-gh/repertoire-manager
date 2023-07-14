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

    # {'date_to_play': datetime.date(2023, 7, 27), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 7, 28), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 7, 29), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 7, 30), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 7, 31), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 1), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 2), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 4), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 6), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 8), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 10), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 14), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 18), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 8, 26), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 9, 3), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 9, 19), 'piece_id': 5}
    # {'date_to_play': datetime.date(2023, 10, 5), 'piece_id': 5}

    db.execute(sql, values)
    schedule = db.fetchall()

    if db_connection:
        db_connection.close()

    return schedule


