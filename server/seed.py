"""
seed.py — Populates the database with example data for all models.
Run from the server/ directory:  python seed.py
"""

from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise


def clear_data():
    """Remove all existing rows to avoid duplicate seeding."""
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()
    print("Cleared existing data.")


def seed_exercises():
    exercises = [
        Exercise(name="Barbell Squat",category="strength",equipment_needed=True),
        Exercise(name="Push-Up",category="strength",equipment_needed=False),
        Exercise(name="Pull-Up",category="strength",equipment_needed=True),
        Exercise(name="Deadlift",category="strength",equipment_needed=True),
        Exercise(name="Running",category="cardio",equipment_needed=False),
        Exercise(name="Cycling",category="cardio",equipment_needed=True),
        Exercise(name="Jump Rope",category="cardio",equipment_needed=True),
        Exercise(name="Downward Dog",category="flexibility",equipment_needed=False),
        Exercise(name="Single-Leg Stand",category="balance",equipment_needed=False),
        Exercise(name="Plank",category="other",equipment_needed=False),
    ]
    db.session.add_all(exercises)
    db.session.commit()
    print(f" Seeded {len(exercises)} exercises.")
    return exercises


def seed_workouts():
    workouts = [
        Workout(date=date(2025, 1, 6),  duration_minutes=45, notes="Morning strength session"),
        Workout(date=date(2025, 1, 8),  duration_minutes=30, notes="Quick cardio"),
        Workout(date=date(2025, 1, 10), duration_minutes=60, notes="Full-body day"),
        Workout(date=date(2025, 1, 13), duration_minutes=20, notes=None),
        Workout(date=date(2025, 1, 15), duration_minutes=50, notes="Leg day"),
    ]
    db.session.add_all(workouts)
    db.session.commit()
    print(f" Seeded {len(workouts)} workouts.")
    return workouts


def seed_workout_exercises(exercises, workouts):
    squat, pushup, pullup, deadlift, running, cycling, jumprope, dog, stand, plank = exercises
    w1, w2, w3, w4, w5 = workouts

    entries = [
        # Workout 1 — strength
        WorkoutExercise(workout=w1, exercise=squat, sets=4, reps=8,   duration_seconds=None),
        WorkoutExercise(workout=w1, exercise=deadlift,sets=3, reps=5,   duration_seconds=None),
        WorkoutExercise(workout=w1, exercise=plank, sets=3, reps=None, duration_seconds=60),

        # Workout 2 — cardio
        WorkoutExercise(workout=w2, exercise=running,sets=1, reps=None, duration_seconds=1200),
        WorkoutExercise(workout=w2, exercise=jumprope,sets=3, reps=None, duration_seconds=120),

        # Workout 3 — full body
        WorkoutExercise(workout=w3, exercise=pushup,sets=4, reps=12,  duration_seconds=None),
        WorkoutExercise(workout=w3, exercise=pullup, sets=3, reps=8,   duration_seconds=None),
        WorkoutExercise(workout=w3, exercise=cycling,sets=1, reps=None, duration_seconds=900),
        WorkoutExercise(workout=w3, exercise=dog,  sets=1, reps=None, duration_seconds=300),

        # Workout 4 — balance & flexibility
        WorkoutExercise(workout=w4, exercise=stand,sets=2, reps=None, duration_seconds=60),
        WorkoutExercise(workout=w4, exercise=dog, sets=2, reps=None, duration_seconds=120),

        # Workout 5 — leg day
        WorkoutExercise(workout=w5, exercise=squat,sets=5, reps=5,   duration_seconds=None),
        WorkoutExercise(workout=w5, exercise=deadlift, sets=4, reps=6,   duration_seconds=None),
    ]
    db.session.add_all(entries)
    db.session.commit()
    print(f"Seeded {len(entries)} workout_exercises.")


if __name__ == "__main__":
    with app.app_context():
        clear_data()
        exercises = seed_exercises()
        workouts = seed_workouts()
        seed_workout_exercises(exercises, workouts)
        print("\n Database seeded successfully!")