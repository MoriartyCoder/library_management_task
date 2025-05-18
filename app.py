from datetime import date, timedelta
from flask import Flask, render_template, jsonify, request
import configparser
import requests
import logging
from flask_cors import CORS

from psycopg2.extras import RealDictCursor
from helper import query, update_query

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
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

TABLES = ("book", "genre", "author", "publisher", '"User"')
TABLES_WITH_DESCRIPTION = ("book", "author") 

@app.route('/api/users')
def get_users():
    return query('SELECT * FROM "User";')

@app.route('/api/get_entire_table', methods=['GET'])
def get_entire_table():
    table = request.args.get("table")
    return query(f"SELECT * FROM {table};")

@app.route('/api/get_from_table', methods=['GET'])
def get_from_table():
    table = request.args.get("table").lower()
    pk_name = request.args.get("pk_name").lower()
    pk_value = int(request.args.get("pk_value"))
    try:
        pk_value = int(request.args.get("pk_value"))
    except Exception as e:
        return jsonify({'error': "The primary key must be an int!"}), 500

    if table == "user":
        table = '"User"'

    if table not in TABLES:
        return jsonify({'error': "Table not found!"}), 500
    
    sql = f"SELECT * FROM {table} WHERE {pk_name} = {pk_value};"
    return query(sql)

@app.route('/api/get_detail_view', methods=['GET'])
def get_detail_view():
    table = request.args.get("table").lower()
    pk_name = request.args.get("pk_name").lower()
    pk_value = int(request.args.get("pk_value"))
    try:
        pk_value = int(request.args.get("pk_value"))
    except Exception as e:
        return jsonify({'error': "The primary key must be an int!"}), 500

    if table == "user":
        table = '"User"'

    if table not in TABLES:
        return jsonify({'error': "Table not found!"}), 500
    
    sql = f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'
            AND table_schema = 'public';
            """

    table_cols = query(sql)

    selections = []
    joins = []
    for col in table_cols:
        col_name = col["column_name"]
        col_name_shortend = col_name.replace("_id", "")
        _col_name_shortend = col_name_shortend if col_name_shortend != "user" else '"User"'
        
        if col_name_shortend in ("author", "user", "genre", "publisher") and not col_name == pk_name:
            _as = col_name_shortend.capitalize() if col_name_shortend != "user" else "Borrower"

            selections.append(f"{_col_name_shortend}.{col_name}")
            selections.append(f"{_col_name_shortend}.name AS \"{_as}\"")

            joins.append(f"LEFT JOIN {_col_name_shortend} ON {table}.{col_name} = {_col_name_shortend}.{col_name}")
        else:
            selections.append(f"{table}.{col_name}")

    selection = ", ".join(selections)
    join = " ".join(joins)

    sql = f"SELECT {selection} FROM {table} {join} WHERE {pk_name} = {pk_value};"
    print(sql)
    return query(sql)

@app.route('/api/update_description', methods=['POST'])
def update_description():
    table = request.args.get("table").lower()
    pk_name = request.args.get("pk_name").lower()
    pk_value = int(request.args.get("pk_value"))
    description = request.get_json()

    try:
        pk_value = int(request.args.get("pk_value"))
    except Exception as e:
        return jsonify({'error': "The primary key must be an int!"}), 500

    if table not in TABLES_WITH_DESCRIPTION:
        return jsonify({'error': "Table not found!"}), 500

    return update_query(f"""UPDATE {table} SET 
                        description = '{description}'
                        WHERE {pk_name} = {pk_value};
                        """)

@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    try:
        user_id = request.args.get("user_id")
        book_id = request.args.get("book_id")
        borrow_date = date.today()
        due_date = borrow_date + timedelta(days=14)
    except Exception as e:
        return jsonify({'error': "Failed to finish the peperations."}), 500
    
    return update_query(f"""UPDATE Book SET 
                        user_id = {user_id}, 
                        borrow_date = '{borrow_date}', 
                        due_date = '{due_date}' 
                        WHERE book_id = {book_id};
                        """)

@app.route('/api/return', methods=['POST'])
def return_book():
    try:
        book_id = request.args.get("book_id")
    except Exception as e:
        return jsonify({'error': "Failed to finish the peperations."}), 500
    
    return update_query(f"""UPDATE Book SET 
                        user_id = null, 
                        borrow_date = null, 
                        due_date = null 
                        WHERE book_id = {book_id};
                        """)

@app.route('/api/list')
def get_book_table_list():
    return query("""SELECT
                    b.book_id AS "Book ID",
                    b.book_id,
                    b.title AS "Title",
                    a.author_id,
                    a.name AS "Author",
                    p.publisher_id,
                    p.name AS "Publisher",
                    g.genre_id,
                    g.name AS "Genre",
                    u.user_id,
                    u.name AS "Borrower",
                    b.borrow_date AS "Borrow Date",
                    b.due_date AS "Return Date"
                    FROM Book b
                    JOIN Author a ON b.author_id = a.author_id
                    JOIN Publisher p ON b.publisher_id = p.publisher_id
                    JOIN Genre g ON b.genre_id = g.genre_id
                    LEFT JOIN "User" u ON b.user_id = u.user_id
                    ORDER BY b.book_id;
                    """)

@app.route('/api/totalreset', methods=['POST'])
def reset_all_borrowed_books():
    return update_query("""UPDATE Book SET user_id = null, borrow_date = null, due_date = null;""",
                        'All borrowed books reset.',
                        'Failed to reset borrowed books')


if __name__ == '__main__':
    app.run(debug=True)
