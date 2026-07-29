from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SITE_NAME'] = os.getenv('SITE_NAME', 'RewardHub')
    app.config['DISCORD_LINK'] = os.getenv('DISCORD_LINK', '#')

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import auth, main, admin
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)

    with app.app_context():
        from app.models import user, mission, redeem
        db.create_all()

    return app
