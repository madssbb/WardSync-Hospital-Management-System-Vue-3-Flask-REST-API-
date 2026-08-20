# 🏥 WardSync — Hospital Management System

A full-stack hospital management system built with **Vue 3** and **Flask REST API**, designed to streamline hospital workflows for administrators, doctors, and patients.

## ✨ Features

### 👨‍💼 Admin
- Admin authentication and role-based access
- Manage patients and doctors
- View and update patient information
- Monitor hospital users and activities
- Manage patient status

### 👨‍⚕️ Doctor
- Doctor authentication
- View assigned patients
- Access patient information
- Manage patient-related records
- Handle medical reports and treatment information

### 🧑‍🦽 Patient
- Patient registration and login
- View personal information
- Access medical information
- Upload previous treatment documents
- View treatment-related records

## 🛠️ Tech Stack

### Frontend
- Vue 3
- Vite
- JavaScript
- CSS
- Vue Router
- Pinia

### Backend
- Python
- Flask
- Flask REST API
- SQLAlchemy
- Flask-JWT-Extended
- Celery

### Database
- SQLite

## 📁 Project Structure

```text
WardSync/
│
├── backend/
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── doctor.py
│   │   └── patient.py
│   │
│   ├── utils/
│   ├── reports/
│   ├── uploads/
│   ├── app.py
│   ├── models.py
│   ├── tasks.py
│   ├── celery_worker.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   ├── router/
│   │   ├── store/
│   │   └── assets/
│   │
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── api.yaml
├── package.json
└── package-lock.json
