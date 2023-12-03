import sqlite3


def get_db_connection_users():
    conn = sqlite3.connect('databases/users.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db_connection_books():
    conn = sqlite3.connect('databases/books_database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_db_connection_reviews():
    conn = sqlite3.connect('databases/reviews_database.db')
    conn.row_factory = sqlite3.Row
    # fake line
    return conn