# Import necessary libraries
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import os
import re  # Import re for regular expressions
import capital  # Import the capital module

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Get MySQL connection details from environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')

# Initialize MySQL connection
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
mysql = MySQL(app)

# Initialize Bcrypt and get JWT_SECRET_KEY from environment variables
bcrypt = Bcrypt(app)
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

# Function to validate email format using regex
def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
  
    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            mysql.connection.commit()

            # Fetch the newly registered user's information
            cursor.execute("SELECT id, name, email, role FROM users WHERE email = %s", (email,))
            user_info = cursor.fetchone()

            if user_info:
                return jsonify({'message': 'User registered successfully', 'user_info': user_info}), 201
            else:
                return jsonify({'message': 'User registration successful but failed to fetch user information'}), 201
    except Exception as e:
        return jsonify({'message': 'User registration failed', 'error': str(e)}), 500

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

    if user and bcrypt.check_password_hash(user[1], password):
        token_payload = {'user_id': user[0], 'exp': datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')

        return jsonify({'message': 'Login successful', 'token': token}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


    


# Route for retrieving user information including capital
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        with mysql.connection.cursor() as cursor:
            # Fetch user information including capital from the database
            cursor.execute("SELECT id, name, email, capital FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                user_info = {
                    'id': user_data[0],
                    'name': user_data[1],
                    'email': user_data[2],
                    'capital': user_data[3]
                }
                return jsonify(user_info), 200
            else:
                return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Failed to retrieve user information', 'error': str(e)}), 500



# Route for adding capital
@app.route('/add-capital', methods=['POST'])
def add_capital_api():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400

    current_capital = data.get('current_capital')
    amount = data.get('amount')
    user_id = data.get('user_id')

    if current_capital is None or amount is None or user_id is None:
        return jsonify({'error': 'Missing required data in JSON'}), 400

    # Call the add_capital function to update capital and store the value in the database
    new_capital = capital.add_capital(current_capital, amount, user_id, mysql)

    # Return a success message along with the new capital value
    return jsonify({'message': 'Capital added successfully', 'new_capital': new_capital}), 201
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'No JSON data provided'}), 400

    current_capital = data.get('current_capital')
    amount = data.get('amount')
    user_id = data.get('user_id')

    if current_capital is None or amount is None or user_id is None:
        return jsonify({'error': 'Missing required data in JSON'}), 400

    new_capital = capital.add_capital(current_capital, amount, user_id, mysql)  # Pass mysql object

    return jsonify({'new_capital': new_capital}), 200

# Route for withdrawing capital
@app.route('/withdraw-capital', methods=['POST'])
def withdraw_capital_api():
    data = request.get_json()
    current_capital = data.get('current_capital')
    amount = data.get('amount')
    user_id = data.get('user_id')  # Assuming user_id is provided in the request JSON
    new_capital = capital.withdraw_capital(current_capital, amount, user_id)
    return jsonify({'new_capital': new_capital})

# Route for updating capital after trade
@app.route('/update-capital-after-trade', methods=['POST'])
def update_capital_after_trade_api():
    data = request.get_json()
    current_capital = data.get('current_capital')
    trade_percentage = data.get('trade_percentage')
    is_successful = data.get('is_successful')
    user_id = data.get('user_id')  # Add user_id parameter
    new_capital = capital.update_capital_after_trade(current_capital, trade_percentage, is_successful, user_id)  # Pass user_id
    return jsonify({'new_capital': new_capital})

# Route for converting percentage to value
@app.route('/percentage-to-value', methods=['POST'])
def percentage_to_value_api():
    data = request.get_json()
    currency_price = data.get('currency_price')
    percentage = data.get('percentage')
    user_id = data.get('user_id')  # Assuming user_id is provided in the request JSON
    value = capital.percentage_to_value(currency_price, percentage, user_id)
    return jsonify({'value': value})

# Function to convert value to percentage
def value_to_percentage(currency_price, value):
    return ((value / currency_price) - 1) * 100

# Route for converting value to percentage
@app.route('/value-to-percentage', methods=['POST'])
def value_to_percentage_api():
    data = request.get_json()
    currency_price = data.get('currency_price')
    value = data.get('value')
    user_id = data.get('user_id')  # Extracting user_id from the request data

    # Check if currency_price or value is missing or None
    if currency_price is None or value is None:
        return jsonify({'error': 'currency_price or value is missing or invalid'}), 400

    # Perform the calculation
    percentage = value_to_percentage(currency_price, value)
    return jsonify({'percentage': percentage})

# Route for calculating required trades
@app.route('/calculate-required-trades', methods=['POST'])
def calculate_required_trades_api():
    data = request.get_json()
    initial_capital = data.get('initial_capital')
    target_capital = data.get('target_capital')
    profit_percentage = data.get('profit_percentage')
    required_trades = capital.calculate_required_trades(initial_capital, target_capital, profit_percentage)
    return jsonify({'required_trades': required_trades})

# Default route
@app.route('/')
def index():
    return 'Welcome to the trading system API!'

# Route for adding trade
@app.route('/add-trade', methods=['POST'])
def add_trade_api():
    data = request.get_json()
    trade_percentage = data.get('trade_percentage')
    is_successful = data.get('is_successful')
    user_id = data.get('user_id')  # Assuming user_id is provided in the request JSON
    add_trade_to_database(trade_percentage, is_successful, user_id)
    return jsonify({'message': 'Trade added successfully'}), 201

# Function to add trade to the database
def add_trade_to_database(trade_percentage, is_successful, user_id):
    try:
        with mysql.connection.cursor() as cursor:
            cursor.execute("INSERT INTO trades (trade_percentage, is_successful, user_id) VALUES (%s, %s, %s)",
                           (trade_percentage, is_successful, user_id))
            mysql.connection.commit()
    except Exception as e:
        return jsonify({'message': 'Failed to add trade', 'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
