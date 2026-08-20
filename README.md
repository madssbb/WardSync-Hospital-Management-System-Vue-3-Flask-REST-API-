# WardSync — Hospital Management System (Vue 3 + Flask REST API)

A role-based Hospital Management System (HMS) rebuilt as a decoupled Single Page Application — a Vue 3 frontend backed by a JWT-secured Flask REST API, with Celery/Redis handling asynchronous reminders and reporting. Built as a second pass at the same problem as [WardSync (Flask, server-rendered)](#), on purpose, to compare monolithic vs. decoupled architectures.

Admins get a single place to manage staff, Doctors track their availability and log treatments, and Patients book appointments and view their medical history.

## Features

- JWT-based stateless authentication (Flask-JWT-Extended + bcrypt password hashing)
- Role-Based Access Control across Admin / Doctor / Patient views
- Interactive dashboards with live statistics and graphs for all three roles
- Live scheduling grid — booked slots clear automatically
- Doctor availability management
- Treatment logging and patient medical history
- CSV export of patient history, run as an async background job
- Email notifications for appointment reminders and reports
- Redis-backed API response caching to reduce database load

## Tech Stack

**Frontend:** Vue.js 3 (Composition API) · Vue Router · Pinia · Axios · Vite · Bootstrap 5
**Backend:** Flask · Flask-SQLAlchemy (ORM) · Flask-JWT-Extended · Flask-CORS · Flask-Caching
**Async / Jobs:** Celery + Celery Beat, Redis (broker, cache, and result backend)
**Database:** SQLite

## Architecture

A decoupled client-server setup:

- **`backend/`** — Flask REST API, organized into role-based Blueprints (`auth.py`, `admin.py`, `doctor.py`, `patient.py`), each mounted under `/api/<role>`. SQLAlchemy models live in `models.py`; Celery tasks live in `tasks.py`, wired up in `celery_worker.py`.
- **`frontend/`** — Vue 3 SPA (`hms-v2-frontend`) under `frontend/src`, routed with Vue Router and using Axios (with interceptors for bearer JWTs and global error handling) to talk to the API.

### API Overview

| Area | Prefix | Examples |
|---|---|---|
| Auth | `/api/auth` | `/login`, `/register` |
| Admin | `/api/admin` | user management, specialties, hospital stats |
| Doctor | `/api/doctor` | `/availability`, `/appointments`, treatment reporting |
| Patient | `/api/patient` | doctor search, `/book`, `/appointments`, `/export` |

A full API spec is documented separately (`api.yaml` / Swagger).

### Scheduled & Background Jobs (Celery + Redis)

- **Daily reminders** — Celery Beat runs every day, checks same-day appointments, and emails/notifies patients.
- **Monthly activity report** — runs on the 1st of each month, summarizing completed appointments, diagnoses, and treatments, emailed to doctors and patients.
- **15-minute pre-appointment alert** — a one-off task scheduled dynamically at booking time, firing 15 minutes before the appointment.

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis server running locally (`redis-server`)

### Setup

```bash
# clone the repo
git clone <this-repo-url>
cd hms-v2

# install everything (backend venv + deps, frontend deps)
npm run install:all
```

### Running locally

This project needs four processes running together — a Flask API server, a Celery worker, Celery Beat (for scheduled jobs), and the Vite dev server:

```bash
npm run dev
```

This runs all four concurrently. To run them individually instead:

```bash
npm run dev:backend         # Flask API on :5000
npm run dev:celery:worker   # Celery worker
npm run dev:celery:beat     # Celery Beat scheduler
npm run dev:frontend        # Vite dev server (Vue frontend)
```

On first run, the backend seeds the database (`backend/instance/hosp.db`) with default roles and an admin account:

| Role  | Username | Password  |
|-------|----------|-----------|
| Admin | `admin`  | `admin123`|

> `JWT_SECRET_KEY` and the admin credentials are hardcoded for local dev — replace both before any real deployment.

## Project Status

Complete — meets all functional requirements while adding real-world touches (async reminders, monthly reporting, response caching) on top of the core appointment/treatment workflow.
