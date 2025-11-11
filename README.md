# Access Camp: Backend Service API

This project implements a RESTful API for managing campers, activities, and signups for Access Camp, built using Flask, Flask-SQLAlchemy, and Flask-Migrate.

### Author & Repository

| Detail | Value |
| :--- | :--- |
| **Author** | Beatrice Wambui Ndungu |
| **GitHub Repository** | [BeatriceWN/Flask-Mock-Challenge---Camping-Fun-Code-Challenge](https://github.com/BeatriceWN/Flask-Mock-Challenge---Camping-Fun-Code-Challenge) |

### Project Status

All **Part 1 (Models/Migrations)**, **Part 2 (Validations)**, and **Part 3 (API Routes)** requirements have been successfully implemented as an API-only service.

---

### Setup Instructions

Follow these steps to set up and run the project locally.

#### Prerequisites

* Python 3.8+
* `pip`

#### 1. Clone and Navigate

```bash
git clone [repository-link]
cd [repository-name]
```

#### 2. Environment Setup
Create and activate the virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run Migrations
The database schema must be initialized and upgraded before running the server.

```bash
# 1. Export the Flask application path
export FLASK_APP=server/app.py

# 2. Run initial migrations
python -m flask db init
python -m flask db migrate -m 'initial model'
python -m flask db upgrade head

# 3. Run relationships migration
python -m flask db migrate -m 'implement relationships'
python -m flask db upgrade head
```

#### 5. Run the Server
Run the application as a Python module from the project root to correctly resolve package imports:

```bash
python -m server.app
# Server will run on: [http://127.0.0.1:5555](http://127.0.0.1:5555)
```

#### 6. Running Tests
To verify the API functionality against the provided tests:

```bash
pytest -x
```

### Validation Rules

* Camper

    - name is required

    - age must be an integer between 8 and 18 inclusive

* Signup

    - time must be an integer between 0 and 23

    - camper_id and activity_id must refer to existing records


### API Endpoints (Controller)

| Method | Route | Description | Success Status |
| :--- | :--- | :--- | :--- |
| **GET** | `/campers` | List all campers (excluding signups). | 200 |
| **GET** | `/campers/<id>` | Retrieve camper details, including nested signups and activities. | 200 |
| **POST** | `/campers` | Create a new camper (validated: name, age 8-18). | 201 |
| **PATCH** | `/campers/<id>` | Update camper name and/or age (validated). | 202 |
| **GET** | `/activities` | List all activities (excluding signups). | 200 |
| **DELETE** | `/activities/<id>` | Delete activity and associated signups (cascades). | 204 |
| **POST** | `/signups` | Create a new signup (validated: time 0-23, valid FKs). | 201 |


### Example Responses
GET /campers

```bash
[
  {"id": 1, "name": "Caitlin", "age": 8},
  {"id": 2, "name": "Lizzie", "age": 9}
]
```

GET /campers/1 (exists)

```bash
{
  "id": 1,
  "name": "Nicholas Martinez",
  "age": 12,
  "activities": [
    {"id": 5, "name": "Hiking by the stream.", "difficulty": 2}
  ],
  "signups": [
    {
      "id": 39,
      "camper_id": 1,
      "activity_id": 5,
      "time": 8,
      "activity": {"id": 5, "name": "Hiking by the stream.", "difficulty": 2}
    }
  ]
}
```

GET /campers/999 (missing)

```bash
{"error": "Camper not found"}
```

POST /campers (validation failure)

```bash
{"errors": ["validation errors"]}
```

POST /signups (success)

```bash
{
  "id": 100,
  "camper_id": 1,
  "activity_id": 3,
  "time": 9,
  "activity": {"id": 3, "name": "Swim in the lake.", "difficulty": 3},
  "camper": {"id": 1, "name": "Ashley Delgado", "age": 11}
}
```

### Error Handling
* Validation Errors (400): Handled by a global error handler that returns a consistent JSON object: {"errors": ["validation errors"]}.
* Not Found (404): Returns a descriptive error, such as {"error": "Camper not found"}.

### License
This project is licensed under the MIT License.