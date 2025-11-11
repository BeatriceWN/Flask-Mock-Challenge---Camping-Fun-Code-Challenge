import os
from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from .config import Config 
from .db_config import db, metadata 

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy with the Flask App 
db.init_app(app) 

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# --- Error Handlers & Helper Functions ---

# Global error handler for validation failure (Part 2)
def validation_error(e):
    # This will catch exceptions raised by @validates (ValueError)
    return make_response(jsonify({"errors": ["validation errors"]}), 400)

# Global error handler for 404 (Not Found)
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

# Global error handler for 405 (Method Not Allowed)
@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method Not Allowed'}), 405)


# Import models *after* db and migrate are initialized to avoid circular imports
from .models import Camper, Activity, Signup 

# --- API Routes (Part 3) ---

# GET /campers - FIX: Exclude all relationships for clean list view
@app.route('/campers', methods=['GET'])
def list_campers():
    campers = Camper.query.all()
    # Exclude signups AND the complex activities list to prevent swapped data in the list view
    campers_data = [camper.to_dict(rules=('-signups', '-activities')) for camper in campers]
    return jsonify(campers_data), 200

# GET /campers/<int:id> - Now fixed by models.py serialization rules
@app.route('/campers/<int:id>')
def get_camper(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return jsonify({'error': 'Camper not found'}), 404

    camper_data = {
        "id": camper.id,
        "name": camper.name,
        "age": camper.age,
        "activities": [
            {
                "id": a.id,
                "name": a.name,
                "difficulty": a.difficulty
            } for a in camper.activities
        ],
        "signups": [s.to_dict() for s in camper.signups]  # <- nested activity included
    }

    return jsonify(camper_data), 200

# POST /campers
@app.route('/campers', methods=['POST'])
def create_camper():
    data = request.get_json()
    try:
        new_camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
        db.session.add(new_camper)
        db.session.commit()
        return jsonify(new_camper.to_dict(rules=('-signups',))), 201
    except (ValueError, KeyError, IntegrityError) as e:
        db.session.rollback()
        return validation_error(e)

# PATCH /campers/<int:id>
@app.route('/campers/<int:id>', methods=['PATCH'])
def update_camper(id):
    camper = db.session.get(Camper, id)
    if not camper:
        return make_response(jsonify({"error": "Camper not found"}), 404)

    data = request.get_json()
    try:
        if 'name' in data:
            camper.name = data['name']
        if 'age' in data:
            camper.age = data['age']

        db.session.commit()
        return jsonify(camper.to_dict(rules=('-signups',))), 202
    except (ValueError, KeyError, IntegrityError) as e:
        db.session.rollback()
        return validation_error(e)

# GET /activities - FIX: Exclude all relationships for clean list view
@app.route('/activities', methods=['GET'])
def list_activities():
    activities = Activity.query.all()
    # Exclude signups AND the complex campers list to prevent swapped data in the list view
    activities_data = [activity.to_dict(rules=('-signups', '-campers')) for activity in activities]
    return jsonify(activities_data), 200

# DELETE /activities/<int:id>
@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = db.session.get(Activity, id)
    if not activity:
        return make_response(jsonify({"error": "Activity not found"}), 404)

    # Cascade delete handles associated signups
    db.session.delete(activity)
    db.session.commit()
    
    return '', 204

# POST /signups
@app.route('/signups', methods=['POST'])
def create_signup():
    data = request.get_json()
    try:
        # Camper ID, Activity ID, and time validation happen in models.py
        new_signup = Signup(
            camper_id=data.get('camper_id'),
            activity_id=data.get('activity_id'),
            time=data.get('time')
        )
        db.session.add(new_signup)
        db.session.commit()

        return jsonify(new_signup.to_dict()), 201

    except (ValueError, KeyError, IntegrityError) as e:
        db.session.rollback()
        return validation_error(e)

if __name__ == '__main__':
    # Add context for flask commands
    with app.app_context():
        print(f"Running on http://localhost:5555")
        app.run(port=5555, debug=True)