from app import db

class ClubMembership(db.Model):
    __tablename__ = 'club_memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 승인 상태 추가
    joined_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 관계 정의
    user = db.relationship('User', backref='memberships', lazy=True)
    club = db.relationship('Club', backref='memberships', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "club_id": self.club_id,
            "status": self.status,  # 승인 상태 포함
            "joined_at": self.joined_at,
        }
