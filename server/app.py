import os
from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from server.config import Config

# Naming convention for foreign keys and indices
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy with naming convention
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Import models *after* db is initialized to avoid circular imports
from server.models import Camper, Activity, Signup 

# --- Routes will go here (Controller) ---

# Global error handler for 404 (Not Found)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

# Global error handler for 405 (Method Not Allowed)
@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method Not Allowed'}), 405)

if __name__ == '__main__':
    # Add context for flask commands
    with app.app_context():
        print(f"Running on http://localhost:5555")
        app.run(port=5555, debug=True)
