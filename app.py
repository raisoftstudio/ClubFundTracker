import os
import logging
import json
from flask import Flask
from werkzeug.security import generate_password_hash
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Create uploads directory if it doesn't exist
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create data files if they don't exist
def initialize_data_files():
    # Create users.json if it doesn't exist
    if not os.path.exists('users.json'):
        with open('users.json', 'w') as f:
            json.dump([], f)
    
    # Create funds.json if it doesn't exist
    if not os.path.exists('funds.json'):
        with open('funds.json', 'w') as f:
            json.dump([], f)
    
    # Create expenses.json if it doesn't exist
    if not os.path.exists('expenses.json'):
        with open('expenses.json', 'w') as f:
            json.dump([], f)
    
    # Create fund_submissions.json if it doesn't exist
    if not os.path.exists('fund_submissions.json'):
        with open('fund_submissions.json', 'w') as f:
            json.dump([], f)
    
    # Create a default admin user if no users exist
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    if not users:
        admin_user = {
            'id': 1,
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'is_admin': True
        }
        users.append(admin_user)
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)
        logging.info("Created default admin user: username='admin', password='admin123'")

# Call the initialization function
initialize_data_files()

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))