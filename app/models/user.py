from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)
    total_earned = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    discord_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    missions_completed = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<User {self.username}>'
