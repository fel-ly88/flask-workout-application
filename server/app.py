from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema,
    exercises_schema,
    exercise_with_workouts_schema,
    workout_schema,
    workouts_schema,
    workout_with_exercises_schema,
    workout_exercise_schema,
    workout_exercise_detail_schema,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
db.init_app(app)


# helper
def error_response(message, status=400):
    return make_response(jsonify({"error": message}), status)


# exercise routes
@app.get("/exercises")
def get_exercises():
    """Return a list of all exercises."""
    exercises = Exercise.query.all()
    return make_response(jsonify(exercises_schema.dump(exercises)), 200)


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    """Return a single exercise with its associated workouts."""
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response("Exercise not found.", 404)
    return make_response(jsonify(exercise_with_workouts_schema.dump(exercise)), 200)


@app.post("/exercises")
def create_exercise():
    """Create a new exercise."""
    data = request.get_json()
    if not data:
        return error_response("Request body must be JSON.")

    try:
        validated = exercise_schema.load(data)
    except ValidationError as e:
        return error_response(e.messages)

    try:
        exercise = Exercise(**validated)
        db.session.add(exercise)
        db.session.commit()
    except (ValueError, IntegrityError) as e:
        db.session.rollback()
        return error_response(str(e))

    return make_response(jsonify(exercise_schema.dump(exercise)), 201)


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    """Delete an exercise and its associated WorkoutExercises (cascade)."""
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response("Exercise not found.", 404)

    db.session.delete(exercise)
    db.session.commit()
    return make_response(jsonify({"message": f"Exercise {exercise_id} deleted."}), 200)


# workout routes
@app.get("/workouts")
def get_workouts():
    """Return a list of all workouts."""
    workouts = Workout.query.all()
    return make_response(jsonify(workouts_schema.dump(workouts)), 200)


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    """Return a single workout with its exercises and per-exercise performance data."""
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response("Workout not found.", 404)
    return make_response(jsonify(workout_with_exercises_schema.dump(workout)), 200)


@app.post("/workouts")
def create_workout():
    """Create a new workout session."""
    data = request.get_json()
    if not data:
        return error_response("Request body must be JSON.")

    try:
        validated = workout_schema.load(data)
    except ValidationError as e:
        return error_response(e.messages)

    try:
        workout = Workout(**validated)
        db.session.add(workout)
        db.session.commit()
    except (ValueError, IntegrityError) as e:
        db.session.rollback()
        return error_response(str(e))

    return make_response(jsonify(workout_schema.dump(workout)), 201)


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    """Delete a workout and its associated WorkoutExercises (cascade)."""
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response("Workout not found.", 404)

    db.session.delete(workout)
    db.session.commit()
    return make_response(jsonify({"message": f"Workout {workout_id} deleted."}), 200)


# workout_exercise routes
@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    """
    Add an exercise to a workout, recording reps, sets, and/or duration_seconds.
    At least one of 'reps' or 'duration_seconds' is required.
    """
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response("Workout not found.", 404)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response("Exercise not found.", 404)

    data = request.get_json() or {}

    try:
        validated = workout_exercise_schema.load(data)
    except ValidationError as e:
        return error_response(e.messages)

    if validated.get("reps") is None and validated.get("duration_seconds") is None:
        return error_response(
            "At least one of 'reps' or 'duration_seconds' must be provided."
        )

    try:
        we = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            **validated,
        )
        db.session.add(we)
        db.session.commit()
    except (ValueError, IntegrityError) as e:
        db.session.rollback()
        return error_response(str(e))

    return make_response(jsonify(workout_exercise_detail_schema.dump(we)), 201)


# entry point
if __name__ == "__main__":
    app.run(port=5555, debug=True)