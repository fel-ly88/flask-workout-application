# flask-workout-application
#  Workout API

A RESTful Flask API for tracking workout sessions and exercises, built with Flask, SQLAlchemy, Flask-Migrate, and Marshmallow.



##  Project Description

The Workout API allows you to:

- Create and manage workout sessions
- Create and manage exercises
- Link exercises to workouts with performance data (sets, reps, duration)
- Enforce validation at schema, model, and database levels
- Perform full CRUD operations on all core resources



##  Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Marshmallow
- SQLite


### 1. Clone the repository
git clone <https://github.com/fel-ly88/flask-workout-application>
cd workout-api



##  Install dependencies
- pipenv install
- pipenv shell
- cd server
- export FLASK_APP=app.py
- flask db init
flask db migrate -m "Initial migration"
flask db upgrade
- python seed.py

