from app import db
from datetime import datetime


class Mission(db.Model):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reward_points = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), default='general')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    completions = db.relationship('MissionCompletion', backref='mission', lazy=True)

    def __repr__(self):
        return f'<Mission {self.title}>'


class MissionCompletion(db.Model):
    __tablename__ = 'mission_completions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=False)
    proof_text = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Completion user={self.user_id} mission={self.mission_id}>'
