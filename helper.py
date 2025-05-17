from flask import jsonify
import psycopg2
import logging
from psycopg2.extras import RealDictCursor

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",  # für Docker auf localhost
            port=5400,
            database="lib_mgmt",
            user="admin",
            password="1234"
        )
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def query(query):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'DB connection failed'}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            books = cur.fetchall()
            return jsonify(books)
    except Exception as e:
        #logging.error(f"Error fetching books: {e}")
        return jsonify({'error': 'Failed to fetch books'}), 500
    finally:
        conn.close()


if "__main__" == __name__:
    print("TEST")
    print(get_db_connection())