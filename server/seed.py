from .models import Camper, Activity, Signup
from .app import app
from .db_config import db
from sqlalchemy.exc import IntegrityError
import random

with app.app_context():
    # 1. CREATE TABLES (In case migrations haven't run or tables are missing)
    # This ensures all defined models in models.py exist in the DB.
    db.create_all() 

    print("Clearing database...")
    # 2. DELETE DATA (Order matters for foreign keys: Signups -> Campers/Activities)
    Signup.query.delete()
    Camper.query.delete()
    Activity.query.delete()
    db.session.commit()

    print("Creating Activities...")
    activities = [
        Activity(name="Hiking", difficulty=3),
        Activity(name="Archery", difficulty=2),
        Activity(name="Canoeing", difficulty=4),
        Activity(name="Campfire Stories", difficulty=1),
        Activity(name="Wildlife Watching", difficulty=2),
    ]
    db.session.add_all(activities)
    db.session.commit()

    print("Creating Campers...")
    campers = [
        Camper(name="Alice Kui", age=10),
        Camper(name="Bobo Wambo", age=15),
        Camper(name="Jackie Chan", age=8),
        Camper(name="Manny Montana", age=18),
        Camper(name="Elizabeth Car", age=12),
    ]
    db.session.add_all(campers)
    db.session.commit()

    # --- server/seed.py (Snippet) ---

    # --- server/seed.py (Snippet) ---

    print("Creating Signups...")
    signups_data = [
        Signup(camper_id=campers[0].id, activity_id=activities[0].id, time=9),
        Signup(camper_id=campers[0].id, activity_id=activities[3].id, time=16), 
        Signup(camper_id=campers[1].id, activity_id=activities[2].id, time=14),
        Signup(camper_id=campers[2].id, activity_id=activities[1].id, time=11),
        Signup(camper_id=campers[3].id, activity_id=activities[4].id, time=8), 
]
    
    # Randomly add more signups
    for camper in campers:
        activity = random.choice(activities)
        time = random.randint(8, 16) 
        try:
            signups_data.append(
                Signup(camper_id=camper.id, activity_id=activity.id, time=time)
            )
        except IntegrityError:
            db.session.rollback()
            continue

    db.session.add_all(signups_data)
    db.session.commit()

    print("Seeding complete!")