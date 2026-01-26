# Gym SaaS Application

## Overview
A gym management SaaS application built with Flask that allows gym owners to manage members, plans, memberships, and payments.

## Project Architecture
- **Framework**: Flask (Python 3.11)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based authentication with Flask-JWT-Extended
- **Password Hashing**: Flask-Bcrypt
- **Migrations**: Flask-Migrate (Alembic)

## Project Structure
```
gym-saas/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── extensions.py     # SQLAlchemy, JWT, Bcrypt extensions
│   ├── models/           # Database models
│   │   ├── gym.py        # Gym model
│   │   ├── user.py       # User model (staff/owner)
│   │   ├── members.py    # Member model
│   │   ├── plan.py       # Subscription plans
│   │   ├── membership.py # Member subscriptions
│   │   └── payment.py    # Payment records
│   ├── routes/           # API endpoints
│   │   ├── gym_auth.py   # Gym registration/login
│   │   ├── member.py     # Member CRUD
│   │   ├── plans.py      # Plan management
│   │   ├── membership.py # Membership management
│   │   └── payment.py    # Payment tracking
│   ├── services/         # Business logic
│   ├── templates/        # Jinja2 HTML templates
│   └── utils/            # Helper utilities
├── migrations/           # Database migrations
├── config.py             # Configuration settings
└── app.py                # Application entry point
```

## API Endpoints
- `/gym/register` - Gym owner registration
- `/gym/login` - Gym authentication
- `/member/*` - Member management
- `/plan/*` - Plan CRUD operations
- `/membership/*` - Membership management
- `/payment/*` - Payment tracking

## Running the Application
- Development: `python app.py` (runs on 0.0.0.0:5000)
- Production: `gunicorn --bind 0.0.0.0:5000 app:app`

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT authentication secret
