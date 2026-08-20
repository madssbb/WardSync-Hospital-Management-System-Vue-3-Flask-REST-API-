from flask import Blueprint, request, jsonify, send_from_directory
from models import db, PatientInfo, DoctorInfo, Specialization, Availability, Appointment, Treatment, User
from utils.auth import role_required, get_current_user
from datetime import datetime
import bcrypt
import os
from werkzeug.utils import secure_filename
from tasks import export_patient_history

patient_bp = Blueprint('patient', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@patient_bp.route('/doctors', methods=['GET'])
@role_required(['patient'])
def get_doctors():
    spec_id = request.args.get('specialization_id')
    q = request.args.get('q', '')
    
    query = DoctorInfo.query
    if q:
        query = query.filter(DoctorInfo.name.ilike(f'%{q}%'))
    if spec_id:
        query = query.filter(DoctorInfo.specialization_id == spec_id)
        
    doctors = query.all()
    
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M')
    
    result = []
    for d in doctors:
        availabilities = []
        for s in d.availabilities:
            if not s.is_booked:
                if s.date > today_str or (s.date == today_str and s.start_time[:5] > current_time):
                    availabilities.append({'id': s.id, 'date': s.date, 'time': s.start_time})
        
        result.append({
            'id': d.id,
            'name': d.name,
            'specialization': d.specialization.name if d.specialization else None,
            'experience': d.experience,
            'availability': availabilities
        })
    return jsonify(result)

@patient_bp.route('/specializations', methods=['GET'])
@role_required(['patient'])
def get_specializations():
    specs = Specialization.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'description': s.description} for s in specs])

@patient_bp.route('/book', methods=['POST'])
@role_required(['patient'])
def book_appointment():
    user = get_current_user()
    patient = PatientInfo.query.filter_by(user_id=user.id).first()
    data = request.json
    slot_id = data.get('slot_id')
    
    slot = Availability.query.get(slot_id)
    if not slot or slot.is_booked:
        return jsonify({'msg': 'Slot unavailable'}), 400
        
    now = datetime.now()
    slot_datetime_str = f"{slot.date} {slot.start_time}"
    # Python datetime.strptime isn't strictly necessary for direct comparison if format is exactly %Y-%m-%d %H:%M:%S
    # We will do a generic check
    if slot.date < now.strftime('%Y-%m-%d') or (slot.date == now.strftime('%Y-%m-%d') and slot.start_time[:5] <= now.strftime('%H:%M')):
        return jsonify({'msg': 'Cannot book a slot that has already passed'}), 400
        
    app = Appointment(
        patient_id=patient.id,
        doctor_id=slot.doctor_id,
        date=slot.date,
        time=slot.start_time,
        status='Booked'
    )
    db.session.add(app)
    
    slot.is_booked = True
    db.session.commit()
    
    return jsonify({'msg': 'Appointment booked'}), 201

@patient_bp.route('/appointments', methods=['GET'])
@role_required(['patient'])
def get_appointments():
    user = get_current_user()
    patient = PatientInfo.query.filter_by(user_id=user.id).first()
    apps = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.date.desc()).all()
    
    result = []
    for a in apps:
        result.append({
            'id': a.id,
            'doctor': a.doctor.name,
            'specialization': a.doctor.specialization.name if a.doctor.specialization else None,
            'date': a.date,
            'time': a.time,
            'status': a.status,
            'treatment': {
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes
            } if a.treatment else None
        })
    return jsonify(result)

@patient_bp.route('/appointments/<int:id>/cancel', methods=['POST'])
@role_required(['patient'])
def cancel_appointment(id):
    user = get_current_user()
    patient = PatientInfo.query.filter_by(user_id=user.id).first()
    app = Appointment.query.get(id)
    
    if not app or app.patient_id != patient.id:
        return jsonify({'msg': 'Unauthorized'}), 403
    if app.status != 'Booked':
        return jsonify({'msg': 'Cannot cancel'}), 400
        
    app.status = 'Cancelled'
    
    slot = Availability.query.filter_by(doctor_id=app.doctor_id, date=app.date, start_time=app.time).first()
    if slot:
        slot.is_booked = False
        
    db.session.commit()
    return jsonify({'msg': 'Cancelled'})

@patient_bp.route('/appointments/<int:id>/reschedule', methods=['POST'])
@role_required(['patient'])
def reschedule_appointment(id):
    user = get_current_user()
    patient = PatientInfo.query.filter_by(user_id=user.id).first()
    app = Appointment.query.get(id)
    
    if not app or app.patient_id != patient.id:
        return jsonify({'msg': 'Unauthorized'}), 403
    if app.status != 'Booked':
        return jsonify({'msg': 'Only booked appointments can be rescheduled'}), 400
        
    data = request.json
    new_slot = Availability.query.get(data.get('slot_id'))
    if not new_slot or new_slot.is_booked:
        return jsonify({'msg': 'New slot unavailable'}), 400
        
    old_slot = Availability.query.filter_by(doctor_id=app.doctor_id, date=app.date, start_time=app.time).first()
    if old_slot:
        old_slot.is_booked = False
        
    app.doctor_id = new_slot.doctor_id
    app.date = new_slot.date
    app.time = new_slot.start_time
    # Status remains booked
    
    new_slot.is_booked = True
    db.session.commit()
    
    return jsonify({'msg': 'Appointment rescheduled successfully'})

@patient_bp.route('/profile', methods=['GET'])
@role_required(['patient'])
def get_profile():
    user = get_current_user()
    patient = PatientInfo.query.filter_by(user_id=user.id).first()
    return jsonify({
        'name': patient.name,
        'contact': patient.contact,
        'dob': patient.dob,
        'username': user.username,
        'email': user.email
    })

@patient_bp.route('/profile', methods=['PUT'])
@role_required(['patient'])
def update_profile():
    user = get_current_user()
    patient = PatientInfo.query.filter_by(user_id=user.id).first()
    data = request.json
    
    patient.name = data.get('name', patient.name)
    patient.contact = data.get('contact', patient.contact)
    patient.dob = data.get('dob', patient.dob)
    
    if 'email' in data:
        user.email = data.get('email')
    if 'password' in data and data.get('password'):
        user.password_hash = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    db.session.commit()
    return jsonify({'msg': 'Profile updated successfully'})

@patient_bp.route('/upload-document', methods=['POST'])
@role_required(['patient'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'msg': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        user = get_current_user()
        patient = PatientInfo.query.filter_by(user_id=user.id).first()
        
        filename = secure_filename(f"patient_{patient.id}_{file.filename}")
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        patient.past_treatment_file = filename
        db.session.commit()
        
        return jsonify({'msg': 'File uploaded successfully', 'filename': filename})
    return jsonify({'msg': 'File type not allowed'}), 400

@patient_bp.route('/view-document/<filename>', methods=['GET'])
@role_required(['patient', 'doctor', 'admin'])
def view_document(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
