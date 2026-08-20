from celery import shared_task
from models import db, Appointment, DoctorInfo, PatientInfo, Treatment
from datetime import datetime
import os
import csv
import time

@shared_task
def send_daily_reminders():
    # Simulate work
    time.sleep(1)
    today = datetime.utcnow().strftime('%Y-%m-%d')
    from app import app
    with app.app_context():
        apps = Appointment.query.filter_by(date=today, status='Booked').all()
        for app_obj in apps:
            email_content = f"""
            Subject: Appointment Reminder - {app_obj.date}
            Hi {app_obj.patient.name},
            
            This is a friendly reminder for your scheduled visit with Dr. {app_obj.doctor.name} today.
            Time: {app_obj.time}
            Location: City General Hospital - Main Wing
            
            Please arrive 15 minutes early. 
            If you need to reschedule, please use the portal.
            """
            print(f"[SIMULATED EMAIL SENT to {app_obj.patient.user.email}]:\n{email_content}")

@shared_task
def generate_monthly_reports():
    # Simulate heavier work
    time.sleep(3)
    from app import app
    with app.app_context():
        doctors = DoctorInfo.query.all()
        for doc in doctors:
            # Gather stats for the month (simplified logic)
            total_apps = Appointment.query.filter(Appointment.doctor_id == doc.id, Appointment.status == 'Completed').count()
            
            report_content = f"""
            <html>
            <body>
                <h1>Monthly Performance Report - Dr. {doc.name}</h1>
                <p>Month: {datetime.now().strftime('%B %Y')}</p>
                <hr>
                <h3>Stats Summary:</h3>
                <ul>
                    <li>Total Completed Appointments: {total_apps}</li>
                    <li>Patient Satisfaction Score: 4.8/5.0 (Simulated)</li>
                </ul>
                <h3>Treatment Overview:</h3>
                <p>Most common diagnosis this month: Viral Fever, Hypertension.</p>
                <p>Download detailed CSV from your dashboard.</p>
            </body>
            </html>
            """
            print(f"[SIMULATED HTML EMAIL SENT to {doc.user.email}]:\n{report_content}")

@shared_task
def export_patient_history(patient_id, patient_name):
    print(f"[BACKGROUND TASK] Starting export for {patient_name}...")
    
    # Simulate work
    time.sleep(2)
    
    try:
        from app import app
        with app.app_context():
            apps = Appointment.query.filter_by(patient_id=patient_id, status='Completed').all()
            treatments = []
            for a in apps:
                if a.treatment:
                    treatments.append({
                        'date': a.date,
                        'doctor': a.doctor.name,
                        'diagnosis': a.treatment.diagnosis,
                        'prescription': a.treatment.prescription,
                        'notes': a.treatment.notes
                    })

            reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            filename = f"history_{patient_id}_{int(time.time()*1000)}.csv"
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Doctor', 'Diagnosis', 'Prescription', 'Notes'])
                for t in treatments:
                    writer.writerow([t['date'], t['doctor'], t['diagnosis'], t['prescription'], t['notes']])
            
            print(f"[BACKGROUND TASK] Export completed for {patient_name}: {filename}")
    except Exception as e:
        print(f"[BACKGROUND TASK] Export failed for {patient_name}:", e)
