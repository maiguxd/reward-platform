from app import create_app, db
from app.models.user import User
from app.models.mission import Mission
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_admin=True,
            points=9999
        )
        db.session.add(admin)

    missions = [
        Mission(title='Regístrate en RewardPlay', description='Crea una cuenta en RewardPlay y gana puntos.', reward_points=50, link='https://example.com/register', category='registro'),
        Mission(title='Descarga App X', description='Descarga y llega al nivel 5.', reward_points=100, link='https://example.com/app', category='descarga'),
        Mission(title='Completa una encuesta', description='Responde una encuesta de 5 minutos.', reward_points=30, link='https://example.com/survey', category='encuesta'),
    ]

    for m in missions:
        if not Mission.query.filter_by(title=m.title).first():
            db.session.add(m)

    db.session.commit()
    print('Base de datos poblada!')
    print('Admin: admin / admin123')
