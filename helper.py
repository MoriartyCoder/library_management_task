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

def query(sql):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        conn.commit()

        if cursor.description:
            result = cursor.fetchall()
        else:
            result = []

        cursor.close()
        conn.close()
        return result

    except Exception as e:
        print("DB-Fehler:", e)
        # Wirf den Fehler hoch, damit die Flask-Route sauber catchen kann
        raise

def update_query(sql, success_msg="Success", fail_msg="Fail"):
    try:
        query(sql)
        return jsonify({'message': success_msg}), 200
    except Exception as e:
        return jsonify({'error': fail_msg}), 500


if "__main__" == __name__:
    print("TEST")
    print(get_db_connection())