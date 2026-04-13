"""
tests/test_app.py — Test suite for the Workout API.
Run with: pytest tests/ -v
"""

import pytest
from datetime import date
from app import app
from models import db, Exercise, Workout, WorkoutExercise




@pytest.fixture
def client():
    """Configure app for testing with an in-memory SQLite database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_exercise(client):
    with app.app_context():
        ex = Exercise(name="Push-Up", category="strength", equipment_needed=False)
        db.session.add(ex)
        db.session.commit()
        return ex.id


@pytest.fixture
def sample_workout(client):
    with app.app_context():
        wo = Workout(date=date(2025, 1, 1), duration_minutes=30)
        db.session.add(wo)
        db.session.commit()
        return wo.id


class TestExerciseModelValidations:
    def test_name_too_short_raises(self, client):
        with app.app_context():
            with pytest.raises(ValueError, match="at least 2 characters"):
                ex = Exercise(name="A", category="strength", equipment_needed=False)
                db.session.add(ex)
                db.session.flush()

    def test_invalid_category_raises(self, client):
        with app.app_context():
            with pytest.raises(ValueError, match="Category must be one of"):
                ex = Exercise(name="Squat", category="yoga", equipment_needed=False)
                db.session.add(ex)
                db.session.flush()

    def test_valid_exercise_saves(self, client):
        with app.app_context():
            ex = Exercise(name="Squat", category="strength", equipment_needed=True)
            db.session.add(ex)
            db.session.commit()
            assert ex.id is not None




class TestWorkoutModelValidations:
    def test_zero_duration_raises(self, client):
        with app.app_context():
            with pytest.raises(ValueError, match="positive integer"):
                wo = Workout(date=date(2025, 1, 1), duration_minutes=0)
                db.session.add(wo)
                db.session.flush()

    def test_negative_duration_raises(self, client):
        with app.app_context():
            with pytest.raises(ValueError, match="positive integer"):
                wo = Workout(date=date(2025, 1, 1), duration_minutes=-10)
                db.session.add(wo)
                db.session.flush()

    def test_valid_workout_saves(self, client):
        with app.app_context():
            wo = Workout(date=date(2025, 6, 1), duration_minutes=45, notes="Test")
            db.session.add(wo)
            db.session.commit()
            assert wo.id is not None



class TestExerciseEndpoints:
    def test_get_exercises_empty(self, client):
        resp = client.get("/exercises")
        assert resp.status_code == 200
        assert resp.json == []

    def test_post_exercise_success(self, client):
        resp = client.post(
            "/exercises",
            json={"name": "Deadlift", "category": "strength", "equipment_needed": True},
        )
        assert resp.status_code == 201
        assert resp.json["name"] == "Deadlift"

    def test_post_exercise_invalid_category(self, client):
        resp = client.post(
            "/exercises",
            json={"name": "Deadlift", "category": "yoga", "equipment_needed": True},
        )
        assert resp.status_code == 400

    def test_post_exercise_short_name(self, client):
        resp = client.post(
            "/exercises",
            json={"name": "A", "category": "cardio", "equipment_needed": False},
        )
        assert resp.status_code == 400

    def test_get_exercise_by_id(self, client, sample_exercise):
        resp = client.get(f"/exercises/{sample_exercise}")
        assert resp.status_code == 200
        assert resp.json["name"] == "Push-Up"

    def test_get_exercise_not_found(self, client):
        resp = client.get("/exercises/9999")
        assert resp.status_code == 404

    def test_delete_exercise(self, client, sample_exercise):
        resp = client.delete(f"/exercises/{sample_exercise}")
        assert resp.status_code == 200
        # Confirm it's gone
        assert client.get(f"/exercises/{sample_exercise}").status_code == 404



class TestWorkoutEndpoints:
    def test_get_workouts_empty(self, client):
        resp = client.get("/workouts")
        assert resp.status_code == 200
        assert resp.json == []

    def test_post_workout_success(self, client):
        resp = client.post(
            "/workouts",
            json={"date": "2025-03-01", "duration_minutes": 45, "notes": "Morning"},
        )
        assert resp.status_code == 201
        assert resp.json["duration_minutes"] == 45

    def test_post_workout_zero_duration(self, client):
        resp = client.post(
            "/workouts", json={"date": "2025-03-01", "duration_minutes": 0}
        )
        assert resp.status_code == 400

    def test_post_workout_missing_date(self, client):
        resp = client.post("/workouts", json={"duration_minutes": 30})
        assert resp.status_code == 400

    def test_get_workout_by_id(self, client, sample_workout):
        resp = client.get(f"/workouts/{sample_workout}")
        assert resp.status_code == 200

    def test_delete_workout(self, client, sample_workout):
        resp = client.delete(f"/workouts/{sample_workout}")
        assert resp.status_code == 200
        assert client.get(f"/workouts/{sample_workout}").status_code == 404


class TestWorkoutExerciseEndpoints:
    def test_add_exercise_to_workout_with_reps(self, client, sample_workout, sample_exercise):
        resp = client.post(
            f"/workouts/{sample_workout}/exercises/{sample_exercise}/workout_exercises",
            json={"sets": 3, "reps": 10},
        )
        assert resp.status_code == 201
        assert resp.json["reps"] == 10

    def test_add_exercise_to_workout_with_duration(self, client, sample_workout, sample_exercise):
        resp = client.post(
            f"/workouts/{sample_workout}/exercises/{sample_exercise}/workout_exercises",
            json={"duration_seconds": 60},
        )
        assert resp.status_code == 201

    def test_add_exercise_missing_reps_and_duration(self, client, sample_workout, sample_exercise):
        resp = client.post(
            f"/workouts/{sample_workout}/exercises/{sample_exercise}/workout_exercises",
            json={"sets": 3},
        )
        assert resp.status_code == 400

    def test_add_exercise_workout_not_found(self, client, sample_exercise):
        resp = client.post(
            f"/workouts/9999/exercises/{sample_exercise}/workout_exercises",
            json={"reps": 5},
        )
        assert resp.status_code == 404

    def test_add_exercise_exercise_not_found(self, client, sample_workout):
        resp = client.post(
            f"/workouts/{sample_workout}/exercises/9999/workout_exercises",
            json={"reps": 5},
        )
        assert resp.status_code == 404