from rest_framework import serializers
from .models import Course, Timetable, CourseDifficultyPrediction


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "code", "title", "weekly_hours", "difficulty_score")


class TimetableSerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = Timetable
        fields = ("id", "course", "day", "start_time", "end_time", "room")


class DifficultySerializer(serializers.ModelSerializer):
    course = CourseSerializer()

    class Meta:
        model = CourseDifficultyPrediction
        fields = ("course", "predicted_level", "confidence_score", "difficulty_score")
from rest_framework import serializers

from .models import Program, Course, Lecturer, Room, TimeSlot, Semester, Timetable, CourseDifficultyPrediction


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ["id", "code", "name", "level", "department"]


class CourseDifficultyPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDifficultyPrediction
        fields = ["course", "predicted_level", "difficulty_score", "confidence_score", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    difficulty = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "code", "title", "program", "lecturer", "weekly_hours", "student_count", "difficulty_score", "is_lab", "is_mathematical", "is_technical", "difficulty"]

    def get_difficulty(self, obj):
        return CourseDifficultyPredictionSerializer(getattr(obj, "coursedifficultyprediction", None)).data if hasattr(obj, "coursedifficultyprediction") else None


class TimetableSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    lecturer = serializers.StringRelatedField()
    room = serializers.StringRelatedField()
    semester = serializers.StringRelatedField()

    class Meta:
        model = Timetable
        fields = ["id", "program", "course", "lecturer", "room", "semester", "day", "start_time", "end_time"]
