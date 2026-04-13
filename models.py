from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm  import validates
from datetime import date

db = SQLAlchemy()
 
class Exercise(db.Model):
    """Represents a single exercise (e.g. Push-Up, Squat)."""
 
    __tablename__ = "exercises"
 
    #  Table Constraints 
    __table_args__ = (
        db.CheckConstraint("length(name) >= 2", name="exercise_name_min_length"),
        db.CheckConstraint(
            "category IN ('strength', 'cardio', 'flexibility', 'balance', 'other')",
            name="exercise_category_valid",
        ),
    )
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)
 
    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
        overlaps="workouts",
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        overlaps="workout_exercises",
    )
 
    #  Model Validations 
    @validates("name")
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters.")
        return value.strip()
 
    @validates("category")
    def validate_category(self, key, value):
        allowed = {"strength", "cardio", "flexibility", "balance", "other"}
        if value not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(sorted(allowed))}.")
        return value
 
    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name!r} category={self.category!r}>"
 
 
class Workout(db.Model):
    """Represents a single workout session."""
 
    __tablename__ = "workouts"
 
    #  Table Constraints 
    __table_args__ = (
        db.CheckConstraint("duration_minutes > 0", name="workout_positive_duration"),
        db.CheckConstraint("date IS NOT NULL", name="workout_date_required"),
    )
 
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
 
    # Relationships
    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        overlaps="exercises",
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        overlaps="workout_exercises",
    )
 
    # Model Validations 
    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if value is None or int(value) <= 0:
            raise ValueError("Duration must be a positive integer (minutes).")
        return int(value)
 
    @validates("date")
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Workout date is required.")
        # Accept both date objects and ISO strings
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError("Date must be a valid ISO format string (YYYY-MM-DD).")
        return value
 
    def __repr__(self):
        return f"<Workout id={self.id} date={self.date} duration={self.duration_minutes}min>"
 
 
class WorkoutExercise(db.Model):
    """Join table linking a Workout to an Exercise, with performance data."""
 
    __tablename__ = "workout_exercises"
 
    #  Table Constraints 
    __table_args__ = (
        db.CheckConstraint("reps IS NULL OR reps > 0", name="we_positive_reps"),
        db.CheckConstraint("sets IS NULL OR sets > 0", name="we_positive_sets"),
        db.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="we_positive_duration_seconds",
        ),
        # At least one of reps or duration_seconds must be provided
        db.CheckConstraint(
            "reps IS NOT NULL OR duration_seconds IS NOT NULL",
            name="we_reps_or_duration_required",
        ),
    )
 
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer, db.ForeignKey("workouts.id"), nullable=False
    )
    exercise_id = db.Column(
        db.Integer, db.ForeignKey("exercises.id"), nullable=False
    )
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
 
    # Relationships
    workout = db.relationship(
        "Workout",
        back_populates="workout_exercises",
        overlaps="exercises,workouts",
    )
    exercise = db.relationship(
        "Exercise",
        back_populates="workout_exercises",
        overlaps="exercises,workouts",
    )
 
    #  Model Validations 
    @validates("reps", "sets", "duration_seconds")
    def validate_positive_int(self, key, value):
        if value is not None and int(value) <= 0:
            raise ValueError(f"{key} must be a positive integer.")
        return value
 
    def __repr__(self):
        return (
            f"<WorkoutExercise workout={self.workout_id} "
            f"exercise={self.exercise_id} reps={self.reps} sets={self.sets}>"
        )