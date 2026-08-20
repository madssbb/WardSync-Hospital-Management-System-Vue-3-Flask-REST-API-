from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from models import db
from celery import Celery
import os
import sqlite3

def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        backend='redis://localhost:6379/0',
        broker='redis://localhost:6379/0'
    )
    # We will configure it fully in the create_app to bind it to the app context
    return celery

celery_app = make_celery()
cache = Cache()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'hosp.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'dev_secret'  # Change this in production
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    db.init_app(app)
    JWTManager(app)
    cache.init_app(app)
    
    celery_app.conf.update(app.config)
    
    # We need a context wrapper for celery tasks
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask

    # Import routes
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'healthy'})

    with app.app_context():
        db.create_all() # Ensure schema is created
        
        # Seed default roles and admin
        from models import Role, User
        import bcrypt
        
        roles = ['admin', 'doctor', 'patient']
        for r in roles:
            if not Role.query.filter_by(name=r).first():
                db.session.add(Role(name=r))
        db.session.commit()
        
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            hashed = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')
            db.session.add(User(username='admin', email='admin@hms.com', password_hash=hashed, role_id=admin_role.id))
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
