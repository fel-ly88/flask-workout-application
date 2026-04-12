from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from models import Exercise, Workout, WorkoutExercise

#exercise schemas


VALID_CATEGORIES = {"strength", "cardio", "flexibility", "balance", "other"}
 
 
class ExerciseSchema(Schema):
    """Schema for serializing/deserializing Exercise objects."""
 
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, error="Name must be at least 2 characters."),
    )
    category = fields.Str(
        required=True,
        validate=validate.OneOf(
            sorted(VALID_CATEGORIES),
            error="Category must be one of: balance, cardio, flexibility, other, strength.",
        ),
    )
    equipment_needed = fields.Bool(required=True)
 
    # Schema-level validation: name must not be blank/whitespace only
    @validates("name")
    def validate_name_not_blank(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Name cannot be blank or whitespace.")
 
    # Schema-level validation: category must be lowercase
    @validates("category")
    def validate_category_lowercase(self, value, **kwargs):
        if value != value.lower():
            raise ValidationError("Category must be lowercase.")
 
 
class ExerciseWithWorkoutsSchema(ExerciseSchema):
    """Exercise schema that nests associated workouts (for GET /exercises/<id>)."""
 
    workouts = fields.List(fields.Nested(lambda: WorkoutSchema(exclude=("exercises",))))
 
 
 #workout schemas
 
 

class WorkoutSchema(Schema):
    """Schema for serializing/deserializing Workout objects."""
 
    id = fields.Int(dump_only=True)
    date = fields.Date(
        required=True,
        error_messages={"required": "date is required.", "invalid": "Invalid date format. Use YYYY-MM-DD."},
    )
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="duration_minutes must be at least 1."),
    )
    notes = fields.Str(allow_none=True, load_default=None)

    @validates("duration_minutes")
    def validate_duration_max(self, value, **kwargs):
        if value > 600:
            raise ValidationError("duration_minutes cannot exceed 600 (10 hours).")
 
 
class WorkoutWithExercisesSchema(WorkoutSchema):
    """Workout schema that nests associated exercises with their join-table data."""
 
    workout_exercises = fields.List(
        fields.Nested(lambda: WorkoutExerciseDetailSchema())
    )
 
 
 #workoutexercise schemas
 

 
class WorkoutExerciseSchema(Schema):
    """Schema for creating a WorkoutExercise (POST body)."""
 
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, error="reps must be at least 1."),
    )
    sets = fields.Int(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, error="sets must be at least 1."),
    )
    duration_seconds = fields.Int(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, error="duration_seconds must be at least 1."),
    )
    
    @validates("reps")
    def validate_reps_type(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError("reps must be positive.")
 
    def validate_reps_or_duration(self, data):
        """Called manually in the route — ensures reps or duration_seconds is present."""
        if data.get("reps") is None and data.get("duration_seconds") is None:
            raise ValidationError(
                "At least one of 'reps' or 'duration_seconds' must be provided."
            )
 
 
class WorkoutExerciseDetailSchema(WorkoutExerciseSchema):
    """WorkoutExercise schema that also embeds exercise details."""
 
    exercise = fields.Nested(ExerciseSchema)
 
#shared schema instances


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_with_workouts_schema = ExerciseWithWorkoutsSchema()
 
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_with_exercises_schema = WorkoutWithExercisesSchema()
 
workout_exercise_schema = WorkoutExerciseSchema()
workout_exercise_detail_schema = WorkoutExerciseDetailSchema()
 