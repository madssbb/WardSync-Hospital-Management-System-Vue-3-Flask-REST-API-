from flask import Blueprint, request, jsonify
from models import db, User, Role, PatientInfo
import bcrypt
from flask_jwt_extended import create_access_token
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'Username already exists'}), 400

    role_name = 'patient'
    patient_role = Role.query.filter_by(name=role_name).first()
    if not patient_role:
        # Fallback in case seeding was skipped
        patient_role = Role(name=role_name)
        db.session.add(patient_role)
        db.session.commit()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role_id=patient_role.id
    )
    db.session.add(new_user)
    db.session.flush()

    patient_info = PatientInfo(
        user_id=new_user.id,
        name=data.get('name', username),
        contact=data.get('contact'),
        dob=data.get('dob')
    )
    db.session.add(patient_info)
    db.session.commit()

    return jsonify({'msg': 'User registered'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not user.is_active or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'msg': 'Invalid credentials or account suspended'}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=datetime.timedelta(hours=1))

    return jsonify({
        'access_token': access_token,
        'user': {
            'username': user.username,
            'role': user.role.name
        }
    }), 200
