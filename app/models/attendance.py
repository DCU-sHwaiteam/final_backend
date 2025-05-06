from app import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendances'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # PIN/QR/와이파이
    pin = db.Column(db.String(4), nullable=True)
    time = db.Column(db.String(5), nullable=True)  # HH:MM

    def to_dict(self):
        return {
            "id": self.id,
            "club_id": self.club_id,
            "week": self.week,
            "type": self.type,
            "pin": self.pin,
            "time": self.time,
            "status": "출석"
        }

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    attendance_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), default='미정')  # 출석/결석/미정
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "attendance_id": self.attendance_id,
            "status": self.status,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

