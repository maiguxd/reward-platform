from app import db
from datetime import datetime


class RedeemRequest(db.Model):
    __tablename__ = 'redeem_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # robux, giftcard, etc
    amount = db.Column(db.Integer, nullable=False)
    points_cost = db.Column(db.Integer, nullable=False)
    discord_contact = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='redeem_requests')

    def __repr__(self):
        return f'<Redeem {self.reward_type} x{self.amount}>'
