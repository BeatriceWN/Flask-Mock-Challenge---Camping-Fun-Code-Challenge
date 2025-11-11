import pytest
import json
from server.app import app
from server.db_config import db
from server.models import Camper, Activity, Signup

# Use a test client for all requests
@pytest.fixture
def client():
    # Configure app for testing
    app.config['TESTING'] = True
    # Use an in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            # Create all tables for the test database
            db.create_all()
            
            # Seed minimal, necessary data for testing relationships and lookups
            activity1 = Activity(name='Swimming', difficulty=3)
            activity2 = Activity(name='Climbing', difficulty=5)
            camper1 = Camper(name='Test Camper A', age=10)
            camper2 = Camper(name='Test Camper B', age=18)
            
            db.session.add_all([activity1, activity2, camper1, camper2])
            db.session.commit()
            
            # Set IDs for easy reference in tests
            pytest.activity_id = activity1.id
            pytest.camper_id = camper1.id
            
            # Create a signup
            signup1 = Signup(
                camper_id=camper1.id, 
                activity_id=activity1.id, 
                time=10
            )
            db.session.add(signup1)
            db.session.commit()
            pytest.signup_id = signup1.id
            
        yield client
        
        # Clean up the database after tests
        with app.app_context():
            db.drop_all()

# --- PART 3: API ROUTE TESTS ---

def test_get_campers(client):
    response = client.get('/campers')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data) == 2
    # Check exclusion rule: signups must NOT be present
    assert 'signups' not in data[0]

def test_get_camper_by_id_success(client):
    response = client.get(f'/campers/{pytest.camper_id}')
    data = json.loads(response.data)
    assert response.status_code == 200
    # Check for nested signups and nested activity within signup
    assert 'signups' in data
    assert len(data['signups']) == 1
    assert 'activity' in data['signups'][0]

def test_get_camper_by_id_404(client):
    response = client.get('/campers/999')
    data = json.loads(response.data)
    assert response.status_code == 404
    assert data == {"error": "Camper not found"}

def test_post_camper_success(client):
    response = client.post('/campers', json={"name": "Zoe New", "age": 16})
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['name'] == 'Zoe New'

def test_post_camper_validation_400(client):
    # Test age validation (age < 8)
    response = client.post('/campers', json={"name": "Youngster", "age": 5})
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data == {"errors": ["validation errors"]}

def test_patch_camper_success(client):
    response = client.patch(f'/campers/{pytest.camper_id}', json={"age": 13})
    data = json.loads(response.data)
    assert response.status_code == 202
    assert data['age'] == 13

def test_patch_camper_404(client):
    response = client.patch('/campers/999', json={"age": 13})
    data = json.loads(response.data)
    assert response.status_code == 404
    assert data == {"error": "Camper not found"}

def test_delete_activity_and_cascade(client):
    # 1. Check signup exists
    with app.app_context():
        assert Signup.query.get(pytest.signup_id) is not None

    # 2. Delete the activity which should cascade-delete the signup
    response = client.delete(f'/activities/{pytest.activity_id}')
    assert response.status_code == 204
    
    # 3. Check activity is gone
    with app.app_context():
        assert Activity.query.get(pytest.activity_id) is None
        # 4. Check the signup was CASCADE DELETED
        assert Signup.query.get(pytest.signup_id) is None

def test_post_signup_success(client):
    response = client.post('/signups', json={
        "camper_id": pytest.camper_id, 
        "activity_id": pytest.activity_id,
        "time": 22 
    })
    data = json.loads(response.data)
    assert response.status_code == 201
    assert data['time'] == 22
    # Check for required nested data
    assert 'camper' in data
    assert 'activity' in data

def test_post_signup_validation_400(client):
    # Test time validation (time > 23)
    response = client.post('/signups', json={
        "camper_id": pytest.camper_id, 
        "activity_id": pytest.activity_id, 
        "time": 25
    })
    data = json.loads(response.data)
    assert response.status_code == 400
    assert data == {"errors": ["validation errors"]}