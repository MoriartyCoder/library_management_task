from datetime import date, datetime, timedelta
from flask import Flask, render_template, jsonify, request
import configparser
import requests
import logging
from flask_cors import CORS
from bson import json_util
from flask import Response
from helper import get_db_connection

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to DEBUG
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logging.log")
    ]
)

# Load the configuration from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API key and URL from the configuration
try:
    GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
    GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
    logging.info("Gemini API configuration loaded successfully.")
except Exception as e:
    logging.error("Error reading config.ini: %s", e)
    GEMINI_API_KEY = None
    GEMINI_API_URL = None

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

# API route to fetch description from Gemini API
@app.route('/api/description', methods=['GET'])
def get_description():
    entity_name = request.args.get('name')
    logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

    if not entity_name:
        logging.warning("Missing entity name in request.")
        return jsonify({'error': 'Missing entity name'}), 400

    if not GEMINI_API_URL or not GEMINI_API_KEY:
        logging.error("Gemini API configuration missing.")
        return jsonify({'error': 'Server configuration error'}), 500

    # Prepare the JSON payload with explicit instructions
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Provide a detailed description of '{entity_name}'"
                            "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
                            "Do not include any concluding remarks or questions."
                            "Do not mention any Note at the end about not including concluding remarks or questions."
                        )
                    }
                ]
            }
        ]
    }

    # Construct the API URL with the API key as a query parameter
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Log the API URL and payload for debugging
    logging.debug(f"API URL: {api_url_with_key}")
    logging.debug(f"Payload: {payload}")

    try:
        # Make the POST request to the Gemini API
        response = requests.post(
            api_url_with_key,  # Include the API key in the URL
            headers=headers,
            json=payload,
            timeout=10  # seconds
        )
        logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

        if response.status_code != 200:
            logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return jsonify({
                'error': 'Failed to fetch description from Gemini API',
                'status_code': response.status_code,
                'response': response.text
            }), 500

        response_data = response.json()
        # Extract the description from the response
        description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
        logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

        return jsonify({'description': description})

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception during Gemini API request: {e}")
        return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
    except ValueError as e:
        logging.error(f"JSON decoding failed: {e}")
        return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

COLLECTIONS = ("book", "genre", "author", "publisher", "user")
COLLECTIONS_WITH_DESCRIPTION = ("book", "genre", "author", "publisher") 

@app.route('/api/users')
def get_users():
    conn, db = get_db_connection()
    col = db["user"]
    users = list(col.find())
    conn.close()
    return Response(json_util.dumps(users), mimetype='application/json')

@app.route('/api/get_detail_view', methods=['GET'])
def get_detail_view():
    try:
        collection_name = request.args.get("collection").lower()
        id = int(request.args.get("id"))
    except Exception as e:
        return jsonify({'error': "The primary key must be an int!"}), 500

    if collection_name not in COLLECTIONS:
        return jsonify({'error': "Table not found!"}), 500
    
    conn, db = get_db_connection()
    collection = db[collection_name]
    attribute_names = [c for c in collection.find_one({"_id": id})]

    pipeline = []
    pipeline.append({
        "$match": {
            "_id": id
        }
    })

    projection = {"_id": 0}
    for attribute_name in attribute_names:
        if attribute_name == "_id":
            continue
        is_id = "_id" in attribute_name

        if is_id:
            other_collection_name = attribute_name.replace("_id", "")
            pipeline.append({
                "$lookup": {
                    "from": other_collection_name,
                    "localField": attribute_name,
                    "foreignField": "_id",
                    "as": other_collection_name
                }
            })
            pipeline.append({"$unwind": f"${other_collection_name}"})
        
            projection[attribute_name] = f"${other_collection_name}._id"
            projection[attribute_name.replace("_id", "").capitalize()] = f"${other_collection_name}.name"
        else:
            projection[attribute_name] = f"${attribute_name}"

    pipeline.append({
        "$project": projection
    })

    cursor = collection.aggregate(pipeline)
    data = list(cursor)
    conn.close()
    return Response(json_util.dumps(data), mimetype='application/json')

@app.route('/api/update_description', methods=['POST'])
def update_description():
    collection_name = request.args.get("collection").lower()
    description = request.get_json()
    try:
        id = int(request.args.get("id"))
    except Exception as e:
        return jsonify({'error': "The primary key must be an int!"}), 500

    if collection_name not in COLLECTIONS_WITH_DESCRIPTION:
        return jsonify({'error': "Table not found!"}), 500

    conn, db = get_db_connection()
    db[collection_name].update_one(
        {"_id": id},
        {
            "$set": {
                "description": description
        }
    })
    
    conn.close()
    return jsonify({'message': 'Success'}), 200

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    try:
        user_id = int(request.args.get("user_id"))
        book_id = int(request.args.get("book_id"))
        borrow_date = datetime.utcnow()
        due_date = borrow_date + timedelta(days=14)
    except Exception as e:
        return jsonify({'error': "Failed to finish the preparations."}), 500
    
    conn, db = get_db_connection()
    db.book.update_one(
        {"_id": book_id},
        {
            "$set": {
                "user_id": user_id,
                "borrow_date": borrow_date,
                "due_date": due_date
        }
    })
    conn.close()
    return jsonify({'message': 'Success'}), 200

@app.route('/api/return', methods=['POST'])
def return_book():
    try:
        book_id = int(request.args.get("book_id"))
    except Exception as e:
        return jsonify({'error': "Failed to finish the preparations."}), 500
    
    conn, db = get_db_connection()
    db.book.update_one(
        {"_id": book_id},
        {
            "$unset": {
                "user_id": "",
                "borrow_date": "",
                "due_date": ""
        }
    })
    conn.close()
    return jsonify({'message': 'Success'}), 200

@app.route('/api/list')
def get_book_table_list():
    conn, db = get_db_connection()
    cursor = db.book.aggregate([
    # Join Author
    {
        "$lookup": {
            "from": "author",
            "localField": "author_id",
            "foreignField": "_id",
            "as": "author"
        }
    },
    { "$unwind": "$author" },

    # Join Publisher
    {
        "$lookup": {
            "from": "publisher",
            "localField": "publisher_id",
            "foreignField": "_id",
            "as": "publisher"
        }
    },
    { "$unwind": "$publisher" },

    # Join Genre
    {
        "$lookup": {
            "from": "genre",
            "localField": "genre_id",
            "foreignField": "_id",
            "as": "genre"
        }
    },
    { "$unwind": "$genre" },

    # Optional User (LEFT JOIN)
    {
        "$lookup": {
            "from": "user",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    {
        "$unwind": {
            "path": "$user",
            "preserveNullAndEmptyArrays": True
        }
    },

    # Final projection
    {
        "$project": {
            "_id": 0,
            "Book ID": "$_id",
            "book_id": "$_id",
            "Title": "$title",
            "author_id": "$author._id",
            "Author": "$author.name",
            "publisher_id": "$publisher._id",
            "Publisher": "$publisher.name",
            "genre_id": "$genre._id",
            "Genre": "$genre.name",
            "user_id": "$user._id",
            "Borrower": "$user.name",
            "Borrow Date": "$borrow_date",
            "borrow_date": "$borrow_date",
            "Return Date": "$due_date",
            "due_date": "$due_date"
        }
    },

    # Order by book_id
    { "$sort": { "book_id": 1 } }
    ])

    data = list(cursor)
    conn.close()
    return Response(json_util.dumps(data), mimetype='application/json')

@app.route('/api/totalreset', methods=['POST'])
def reset_all_borrowed_books():
    conn, db = get_db_connection()
    db.book.update_many(
        {},
        {
            "$unset": {
                "user_id": "",
                "borrow_date": "",
                "due_date": ""
        }
    })
    conn.close()
    return jsonify({'message': 'Success'}), 200


if __name__ == '__main__':
    app.run(debug=True)
