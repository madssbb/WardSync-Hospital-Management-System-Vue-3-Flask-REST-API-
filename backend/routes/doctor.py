from flask import Blueprint, request, jsonify
from models import db, DoctorInfo, Appointment, PatientInfo, Treatment, Availability
from utils.auth import role_required, get_current_user
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/appointments', methods=['GET'])
@role_required(['doctor'])
def get_appointments():
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    apps = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    
    result = []
    for a in apps:
        result.append({
            'id': a.id,
            'patient': a.patient.name,
            'patient_id': a.patient.id,
            'date': a.date,
            'time': a.time,
            'status': a.status,
            'diagnosis': a.treatment.diagnosis if a.treatment else None,
            'prescription': a.treatment.prescription if a.treatment else None,
            'notes': a.treatment.notes if a.treatment else None
        })
    return jsonify(result)

@doctor_bp.route('/appointments/<int:id>/complete', methods=['POST'])
@role_required(['doctor'])
def complete_appointment(id):
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    app = Appointment.query.get(id)
    
    if not app or app.doctor_id != doctor.id:
        return jsonify({'msg': 'Unauthorized'}), 403
        
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M')
    
    if app.date > today_str:
        return jsonify({'msg': 'Cannot complete an appointment scheduled for a future date'}), 400
        
    data = request.json
    app.status = 'Completed'
    
    if app.treatment:
        app.treatment.diagnosis = data.get('diagnosis')
        app.treatment.prescription = data.get('prescription')
        app.treatment.notes = data.get('notes')
    else:
        new_treatment = Treatment(
            appointment_id=app.id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            notes=data.get('notes')
        )
        db.session.add(new_treatment)
        
    db.session.commit()
    return jsonify({'msg': 'Appointment updated'})

@doctor_bp.route('/appointments/<int:id>/cancel', methods=['POST'])
@role_required(['doctor'])
def cancel_appointment(id):
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    app = Appointment.query.get(id)
    
    if not app or app.doctor_id != doctor.id:
        return jsonify({'msg': 'Unauthorized'}), 403
    if app.status != 'Booked':
        return jsonify({'msg': 'Can only cancel booked appointments'}), 400
        
    app.status = 'Cancelled'
    
    # Release the slot
    slot = Availability.query.filter_by(doctor_id=doctor.id, date=app.date, start_time=app.time).first()
    if slot:
        slot.is_booked = False
        
    db.session.commit()
    return jsonify({'msg': 'Appointment cancelled by doctor'})

@doctor_bp.route('/availability', methods=['GET'])
@role_required(['doctor'])
def get_availability():
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    slots = Availability.query.filter_by(doctor_id=doctor.id).all()
    
    return jsonify([{
        'id': s.id,
        'date': s.date,
        'start_time': s.start_time,
        'end_time': s.end_time,
        'is_booked': s.is_booked
    } for s in slots])

@doctor_bp.route('/availability', methods=['POST'])
@role_required(['doctor'])
def post_availability():
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    data = request.json
    
    date = data.get('date')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    if not date or not start_time or not end_time:
        return jsonify({'msg': 'Missing timing details'}), 400
        
    if end_time <= start_time:
        return jsonify({'msg': 'End time must be after start time'}), 400
        
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    if date < today_str:
        return jsonify({'msg': 'Cannot add availability for a past date'}), 400
        
    if date == today_str:
        current_time = now.strftime('%H:%M')
        if start_time[:5] <= current_time:
            return jsonify({'msg': 'Start time must be in the future for today\'s date'}), 400
            
    existing = Availability.query.filter_by(doctor_id=doctor.id, date=date, start_time=start_time).first()
    if existing:
        return jsonify({'msg': 'Slot already exists for this time'}), 400
        
    slot = Availability(date=date, start_time=start_time, end_time=end_time, doctor_id=doctor.id)
    db.session.add(slot)
    db.session.commit()
    return jsonify({'msg': 'Slot added successfully'}), 201

@doctor_bp.route('/availability/<int:id>', methods=['DELETE'])
@role_required(['doctor'])
def delete_availability(id):
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    slot = Availability.query.get(id)
    
    if not slot or slot.doctor_id != doctor.id:
        return jsonify({'msg': 'Unauthorized or slot not found'}), 403
    if slot.is_booked:
        return jsonify({'msg': 'Cannot delete a booked slot'}), 400
        
    db.session.delete(slot)
    db.session.commit()
    return jsonify({'msg': 'Slot deleted successfully'})

@doctor_bp.route('/patient-history/<int:id>', methods=['GET'])
@role_required(['doctor'])
def patient_history(id):
    apps = Appointment.query.filter_by(patient_id=id, status='Completed').all()
    patient = PatientInfo.query.get(id)
    
    history = []
    for a in apps:
        if a.treatment:
            history.append({
                'date': a.date,
                'doctor': a.doctor.name,
                'diagnosis': a.treatment.diagnosis,
                'prescription': a.treatment.prescription,
                'notes': a.treatment.notes
            })
            
    return jsonify({
        'patient': patient.name if patient else 'Unknown',
        'history': history
    })

@doctor_bp.route('/appointments/<int:id>/treatment', methods=['PUT'])
@role_required(['doctor'])
def edit_treatment(id):
    user = get_current_user()
    doctor = DoctorInfo.query.filter_by(user_id=user.id).first()
    app = Appointment.query.get(id)
    
    if not app or app.doctor_id != doctor.id:
        return jsonify({'msg': 'Unauthorized'}), 403
    if app.status != 'Completed':
        return jsonify({'msg': 'Can only edit completed appointments'}), 400
        
    data = request.json
    if app.treatment:
        app.treatment.diagnosis = data.get('diagnosis')
        app.treatment.prescription = data.get('prescription')
        app.treatment.notes = data.get('notes')
        db.session.commit()
        
    return jsonify({'msg': 'Treatment updated successfully'})
