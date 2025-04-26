# app/models/club.py
from app import db

from app import db

class Club(db.Model):
    __tablename__ = 'clubs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    leader_email = db.Column(db.String(100), nullable=False)
    leader_name = db.Column(db.String(100), nullable=False)
    advisor = db.Column(db.String(100), nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    current_members = db.Column(db.Integer, default=0)
    activity_schedule = db.Column(db.String(100))
    tags = db.Column(db.String(255))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "leader_email": self.leader_email,
            "leader_name": self.leader_name,  
            "advisor": self.advisor,
            "max_members": self.max_members,
            "current_members": self.current_members,
            "activity_schedule": self.activity_schedule,
            "tags": self.tags,
            "description": self.description
        }

