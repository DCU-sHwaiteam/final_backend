# app/models/club.py
from app import db

class Club(db.Model):
    __tablename__ = 'clubs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    leader_name = db.Column(db.String(100)) 
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "leader_name": self.leader_name   
       }
