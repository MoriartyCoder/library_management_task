from flask import jsonify
import logging
import pymongo

def get_db_connection(db_name="lib_mgmt"):
    try:
        myclient = pymongo.MongoClient(
            "mongodb://admin:1234@127.0.0.1:27017/lib_mgmt?" \
            "directConnection=true&" \
            "serverSelectionTimeoutMS=2000&" \
            "authSource=admin&" \
            "appName=mongosh+2.5.0")
        return myclient, myclient[db_name]
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

