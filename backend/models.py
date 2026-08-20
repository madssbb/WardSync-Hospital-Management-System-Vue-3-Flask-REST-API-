from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')

class Specialization(db.Model):
    __tablename__ = 'specialization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text)

class DoctorInfo(db.Model):
    __tablename__ = 'doctor_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    experience = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    specialization_id = db.Column(db.Integer, db.ForeignKey('specialization.id'))
    
    user = db.relationship('User', backref=db.backref('doctor_info', uselist=False))
    specialization = db.relationship('Specialization', backref='doctors')

class PatientInfo(db.Model):
    __tablename__ = 'patient_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contact = db.Column(db.String)
    dob = db.Column(db.String) # SQLite DATE is stored as string 'YYYY-MM-DD' natively. Using String or Date works. Let's use db.String for easy JSON serialization.
    past_treatment_file = db.Column(db.String) # Stores filename of uploaded document
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', backref=db.backref('patient_info', uselist=False))

class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False) # 'YYYY-MM-DD'
    start_time = db.Column(db.String, nullable=False) # 'HH:MM:SS'
    end_time = db.Column(db.String, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_info.id'))
    
    doctor = db.relationship('DoctorInfo', backref='availabilities')

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='Booked')
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_info.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_info.id'))
    
    patient = db.relationship('PatientInfo', backref='appointments')
    doctor = db.relationship('DoctorInfo', backref='appointments')

class Treatment(db.Model):
    __tablename__ = 'treatment'
    id = db.Column(db.Integer, primary_key=True)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    next_visit_date = db.Column(db.String)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    
    appointment = db.relationship('Appointment', backref=db.backref('treatment', uselist=False))
