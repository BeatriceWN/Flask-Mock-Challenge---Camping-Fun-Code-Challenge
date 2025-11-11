from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from .db_config import db


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    signups = db.relationship(
        'Signup',
        backref='camper',
        cascade='all, delete-orphan',
        overlaps='activities,camper'
    )
    activities = db.relationship(
        'Activity',
        secondary='signups',
        back_populates='campers',
        overlaps='signups,camper'
    )

    # Prevent circular nesting
    serialize_rules = (
        '-signups.camper',
        '-signups.activity.campers',
        '-activities.signups',
        '-activities.campers'
    )

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Name is required.")
        return name

    @validates('age')
    def validate_age(self, key, age):
        if not isinstance(age, int) or not (8 <= age <= 18):
            raise ValueError("Age must be an integer between 8 and 18 (inclusive).")
        return age

    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship(
        'Signup',
        backref='activity',
        cascade='all, delete-orphan',
        overlaps='campers,activity'
    )
    campers = db.relationship(
        'Camper',
        secondary='signups',
        back_populates='activities',
        overlaps='signups,activity,camper'
    )

    serialize_rules = (
        '-signups.activity',
        '-signups.camper',
        '-campers.activities',
        '-campers.signups'
    )

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, nullable=False)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)

    # Keep relationships flat for most serializations
    serialize_rules = (
        '-camper.signups',
        '-camper.activities',
        '-activity.signups',
        '-activity.campers'
    )

    def to_dict(self, rules=None):
        """Include nested activity inside signup for GET camper routes."""
        base = super().to_dict(rules=rules)
        if self.activity:
            base['activity'] = {
                'id': self.activity.id,
                'name': self.activity.name,
                'difficulty': self.activity.difficulty
            }
        return base

    @validates('time')
    def validate_time(self, key, time):
        if not isinstance(time, int) or not (0 <= time <= 23):
            raise ValueError("Time must be an integer between 0 and 23 (inclusive).")
        return time

    @validates('camper_id')
    def validate_camper_id(self, key, camper_id):
        if db.session.get(Camper, camper_id) is None:
            raise ValueError("Camper ID must exist.")
        return camper_id

    @validates('activity_id')
    def validate_activity_id(self, key, activity_id):
        if db.session.get(Activity, activity_id) is None:
            raise ValueError("Activity ID must exist.")
        return activity_id

    def __repr__(self):
        return f'<Signup {self.id}: Camper {self.camper_id} for Activity {self.activity_id} at {self.time}:00>'