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
            is_in_repertoire
        FROM pieces
        JOIN users
            ON users.id = pieces.user_id
        JOIN composers
            ON composers.id = pieces.composer_id
        JOIN periods
            ON periods.id = composers.period_id
        WHERE user_id = %s AND pieces.id = %s;"""
    values = (user_id, piece_id,)

    db.execute(sql, values)
    details = db.fetchall()

    if db_connection:
        db_connection.close()

    return details