# CAPACITY CONNECT

CAPACITY CONNECT is a Flask-based digital capacity-building and learning management portal designed for the Smart India Hackathon 2026 problem statement from the Ministry of Earth Sciences and India Meteorological Department.

## Overview

The platform is designed around the central value proposition of competency mapping:

- trainee skills and gaps
- trainer expertise and subjects
- relevant training paths
- assessment and credentialing
- learning progress monitoring

It is intentionally not a generic LMS. It focuses on a government-ready competency ecosystem for professional and technical training.

## Prerequisites

- Python 3.11+
- A Supabase project
- Virtual environment support
- Git

## Create a virtual environment

```bash
cd capacity-connect
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment variables

Copy the sample file and populate the values:

```bash
cp .env.example .env
```

Required settings:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY` (preferred) or `SUPABASE_ANON_KEY`
- `SUPABASE_SECRET_KEY` (preferred) or `SUPABASE_SERVICE_ROLE_KEY`
- `SECRET_KEY`

Never store secret/service-role values in frontend code or in version control.

## Supabase setup

1. Create a Supabase project.
2. Open SQL Editor in Supabase.
3. Run the contents of `supabase_schema.sql`.
4. Configure authentication for the app as needed.
5. Set up storage buckets if you intend to upload certificates, lectures, and course resources.

## Execute schema

```sql
-- Run in Supabase SQL Editor
-- contents of supabase_schema.sql
```

## Create the first admin

Create the first admin user through Supabase Auth, then assign the correct role in the `profiles` table or through a secure admin workflow.

Suggested rule:

- Use Supabase Auth to create the user.
- Insert a row into `profiles` with `role = 'admin'`.
- Ensure an `admin_profiles` row is created as required.

Do not allow arbitrary self-registration to become an admin.

## Run the Flask app

```bash
export FLASK_APP=app.py
flask run --debug
```

Or use:

```bash
python app.py
```

## Test the application

Use the demo interface to validate:

1. Home page
2. Public course listing
3. Login and registration flows
4. Trainee dashboard
5. Trainer dashboard
6. Admin dashboard
7. Competency mapping display
8. Assessment and feedback pages

## Project structure

```text
capacity-connect/
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── supabase_schema.sql
├── app/
│   ├── __init__.py
│   ├── auth/
│   ├── trainee/
│   ├── trainer/
│   ├── admin/
│   ├── courses/
│   ├── assessments/
│   ├── competency/
│   ├── feedback/
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
└── tests/
```

## Notes

This prototype is intentionally built to be demonstrable in a Hackathon setting while remaining aligned with the requested production-oriented architecture and Supabase-ready database design.
