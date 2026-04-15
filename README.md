# Workout API

A RESTful Flask API for tracking workout sessions and exercises, built with Flask, SQLAlchemy, Flask-Migrate, and Marshmallow.

## Project Description

The Workout API allows you to:
- Create and manage workout sessions
- Create and manage exercises
- Link exercises to workouts with performance data (sets, reps, duration)
- Enforce validation at schema, model, and database levels
- Perform full CRUD operations on all core resources

## Tech Stack

- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Marshmallow
- SQLite

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/fel-ly88/flask-workout-application
cd flask-workout-application
```

### 2. Install dependencies and activate the virtual environment

```bash
pipenv install
pipenv shell
```

### 3. Move into the server directory

```bash
cd server
```

### 4. Initialize and run database migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Seed the database

```bash
python seed.py
```

### 6. Run the development server

```bash
python app.py
```

The API will be running at `http://127.0.0.1:5555`.

---

## Running Tests

```bash
pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Get one exercise with its workouts |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise |
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Get one workout with its exercises |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout |
| POST | `/workouts/<id>/exercises/<id>/workout_exercises` | Add an exercise to a workout |