from flask import Blueprint, request, jsonify
from models import db, User, Role, DoctorInfo, Specialization, PatientInfo, Appointment
from utils.auth import role_required
import bcrypt

admin_bp = Blueprint('admin', __name__)
# We will use Flask-Caching imported from app
# But to avoid circular import, we can do from app import cache

@admin_bp.route('/stats', methods=['GET'])
@role_required(['admin'])
def get_stats():
    from app import cache
    # Implementation of caching within the route handler to avoid circular imports dynamically
    @cache.cached(timeout=60, key_prefix='admin_stats')
    def compute_stats():
        doctor_count = DoctorInfo.query.count()
        patient_count = PatientInfo.query.count()
        appointment_count = Appointment.query.count()
        return {'doctors': doctor_count, 'patients': patient_count, 'appointments': appointment_count}
    
    return jsonify(compute_stats())

@admin_bp.route('/specializations', methods=['GET'])
@role_required(['admin'])
def get_specializations():
    specs = Specialization.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'description': s.description} for s in specs])

@admin_bp.route('/specializations', methods=['POST'])
@role_required(['admin'])
def create_specialization():
    data = request.json
    spec = Specialization(name=data.get('name'), description=data.get('description'))
    db.session.add(spec)
    db.session.commit()
    return jsonify({'msg': 'Specialization added'}), 201

@admin_bp.route('/doctors', methods=['GET'])
@role_required(['admin'])
def get_doctors():
    query = request.args.get('q', '')
    spec_id = request.args.get('specialization_id')
    
    doctors_query = DoctorInfo.query.join(User)
    if query:
        doctors_query = doctors_query.filter(DoctorInfo.name.ilike(f'%{query}%'))
    if spec_id:
        doctors_query = doctors_query.filter(DoctorInfo.specialization_id == spec_id)
        
    doctors = doctors_query.all()
    
    result = []
    for d in doctors:
        result.append({
            'id': d.id,
            'name': d.name,
            'username': d.user.username,
            'specialization': d.specialization.name if d.specialization else None,
            'specialization_id': d.specialization_id,
            'experience': d.experience,
            'is_active': d.user.is_active
        })
    return jsonify(result)

@admin_bp.route('/doctors', methods=['POST'])
@role_required(['admin'])
def create_doctor():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    specialization_id = data.get('specialization_id')
    experience = data.get('experience', 0)

    if not username or not email or not password or not name:
        return jsonify({'msg': 'Missing required fields'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'msg': 'Username or Email already in use'}), 400

    doc_role = Role.query.filter_by(name='doctor').first()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    new_user = User(username=username, email=email, password_hash=hashed_password, role_id=doc_role.id)
    db.session.add(new_user)
    db.session.flush()

    doc_info = DoctorInfo(user_id=new_user.id, name=name, specialization_id=specialization_id, experience=experience)
    db.session.add(doc_info)
    db.session.commit()

    return jsonify({'msg': 'Doctor created successfully'}), 201

@admin_bp.route('/doctors/<int:id>', methods=['PUT'])
@role_required(['admin'])
def update_doctor(id):
    data = request.json
    doctor = DoctorInfo.query.get(id)
    if not doctor:
        return jsonify({'msg': 'Doctor not found'}), 404

    doctor.name = data.get('name', doctor.name)
    doctor.specialization_id = data.get('specialization_id', doctor.specialization_id)
    doctor.experience = data.get('experience', doctor.experience)
    db.session.commit()
    return jsonify({'msg': 'Doctor updated successfully'})

@admin_bp.route('/doctors/<int:id>', methods=['DELETE'])
@role_required(['admin'])
def delete_doctor(id):
    doctor = DoctorInfo.query.get(id)
    if not doctor:
        return jsonify({'msg': 'Doctor not found'}), 404
    doctor.user.is_active = False
    db.session.commit()
    return jsonify({'msg': 'Doctor removed'})

@admin_bp.route('/doctors/<int:id>/restore', methods=['POST'])
@role_required(['admin'])
def restore_doctor(id):
    doctor = DoctorInfo.query.get(id)
    if not doctor:
        return jsonify({'msg': 'Doctor not found'}), 404
    doctor.user.is_active = True
    db.session.commit()
    return jsonify({'msg': 'Doctor restored'})

@admin_bp.route('/patients', methods=['GET'])
@role_required(['admin'])
def get_patients():
    query = request.args.get('q', '')
    patients = PatientInfo.query.filter(PatientInfo.name.ilike(f'%{query}%')).all()
    result = []
    for p in patients:
        result.append({
            'id': p.id,
            'name': p.name,
            'username': p.user.username,
            'email': p.user.email,
            'is_active': p.user.is_active
        })
    return jsonify(result)

@admin_bp.route('/patients/<int:id>/toggle-active', methods=['POST'])
@role_required(['admin'])
def toggle_patient(id):
    patient = PatientInfo.query.get(id)
    if not patient:
        return jsonify({'msg': 'Patient not found'}), 404
    patient.user.is_active = not patient.user.is_active
    db.session.commit()
    return jsonify({'msg': 'Status updated', 'is_active': patient.user.is_active})

@admin_bp.route('/patients/<int:id>', methods=['PUT'])
@role_required(['admin'])
def update_patient(id):
    data = request.json
    patient = PatientInfo.query.get(id)
    if not patient:
        return jsonify({'msg': 'Patient not found'}), 404
        
    patient.name = data.get('name', patient.name)
    patient.contact = data.get('contact', patient.contact)
    patient.dob = data.get('dob', patient.dob)
    
    if 'email' in data:
        patient.user.email = data.get('email')
        
    db.session.commit()
    return jsonify({'msg': 'Patient updated successfully'})

@admin_bp.route('/patients/<int:id>/history', methods=['GET'])
@role_required(['admin'])
def get_patient_history(id):
    patient = PatientInfo.query.get(id)
    if not patient:
        return jsonify({'msg': 'Patient not found'}), 404
        
    apps = Appointment.query.filter_by(patient_id=id).order_by(Appointment.date.desc()).all()
    
    history = []
    for a in apps:
        history.append({
            'date': a.date,
            'time': a.time,
            'doctor': a.doctor.name,
            'status': a.status,
            'treatment': {
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes
            } if a.treatment else None
        })
        
    return jsonify({
        'patient': {
            'name': patient.name,
            'contact': patient.contact,
            'email': patient.user.email,
            'file': patient.past_treatment_file
        },
        'history': history
    })

@admin_bp.route('/appointments', methods=['GET'])
@role_required(['admin'])
def get_appointments():
    status = request.args.get('status')
    q = request.args.get('q')

    apps_query = Appointment.query.join(PatientInfo).join(DoctorInfo)
    if status and status != 'All':
        apps_query = apps_query.filter(Appointment.status == status)
    if q:
        apps_query = apps_query.filter(PatientInfo.name.ilike(f'%{q}%'))
        
    apps = apps_query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    result = []
    for a in apps:
        result.append({
            'id': a.id,
            'patient': a.patient.name,
            'doctor': a.doctor.name,
            'specialization': a.doctor.specialization.name if a.doctor.specialization else None,
            'date': a.date,
            'time': a.time,
            'status': a.status
        })
    return jsonify(result)
