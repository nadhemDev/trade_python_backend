import math
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv

import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()



def add_capital(current_capital, amount, user_id, mysql, currency_type='USD'):
    # Placeholder implementation - Add the amount to the current capital
    new_capital = current_capital + amount

    try:
        with mysql.connection.cursor() as cursor:
            # Update the capital in the database for the given user_id
            cursor.execute("UPDATE users SET capital = %s WHERE id = %s", (new_capital, user_id))
            mysql.connection.commit()
            
            # Insert the transaction details into the capital table with the currency type
            cursor.execute("INSERT INTO capital (user_id, amount, currency_type) VALUES (%s, %s, %s)", (user_id, amount, currency_type))
            mysql.connection.commit()
            
            # Fetch the currency type from the database for the user
            cursor.execute("SELECT currency_type FROM capital WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
            row = cursor.fetchone()
            if row:
                currency_type = row[0]
    except Exception as e:
        # Handle the exception if the database operation fails
        print(f"Error updating capital in the database: {e}")
        # You may choose to raise the exception or handle it differently based on your requirements

    return {'new_capital': new_capital, 'currency_type': currency_type}




    # Placeholder implementation - Add the amount to the current capital
    new_capital = current_capital + amount

    try:
        with mysql.connection.cursor() as cursor:
            # Update the capital in the database for the given user_id
            cursor.execute("UPDATE users SET capital = %s WHERE id = %s", (new_capital, user_id))
            mysql.connection.commit()
    except Exception as e:
        # Handle the exception if the database operation fails
        print(f"Error updating capital in the database: {e}")
        # You may choose to raise the exception or handle it differently based on your requirements

    return new_capital
    # Placeholder implementation - Add the amount to the current capital
    new_capital = current_capital + amount
    
    try:
        with mysql.connection.cursor() as cursor:
            # Update the user's capital in the database
            cursor.execute("UPDATE users SET capital = %s WHERE id = %s", (new_capital, user_id))
            mysql.connection.commit()
    except Exception as e:
        # Handle any database errors
        print(f"Error updating capital in the database: {e}")
    
    return new_capital


def withdraw_capital(current_capital, amount, user_id):
    # Placeholder implementation - Subtract the amount from the current capital
    new_capital = current_capital - amount
    return new_capital

def update_capital_after_trade(current_capital, trade_percentage, is_successful, user_id):

    # Placeholder implementation - Update the capital based on the outcome of a trade
    if is_successful:
        new_capital = current_capital * (1 + trade_percentage / 100)
    else:
        new_capital = current_capital * (1 - trade_percentage / 100)
    return new_capital

# Define other functions related to capital management...
def percentage_to_value(currency_price, percentage, user_id):
  
    value = currency_price * (percentage / 100)
    return value

def calculate_required_trades(initial_capital, target_capital, profit_percentage):
    return math.ceil(math.log(target_capital / initial_capital) / math.log(1 + profit_percentage))

if __name__ == '__main__':
    app.run(debug=True)