from datetime import datetime, timedelta, time
from typing import Optional

from scheduling.models import (
    Course,
    Timetable,
    Room,
    TimeSlot,
    CourseDifficultyPrediction,
)

# Configuration
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
DEFAULT_SLOTS = [
    ("07:45", "08:45"),
    ("08:45", "09:45"),
    ("09:45", "10:45"),
    ("10:45", "11:45"),
    ("11:45", "12:45"),
    ("12:45", "13:45"),
    ("13:45", "14:45"),
    ("14:45", "15:45"),
    ("15:45", "16:45"),
    ("16:45", "17:45"),
    ("17:45", "18:45"),
]


# Time helpers
def parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def add_minutes(time_obj, minutes):
    return (datetime.combine(datetime.today(), time_obj) + timedelta(minutes=minutes)).time()


def in_range(start, end, window_start, window_end):
    return start >= window_start and end <= window_end


def get_default_time_slots(day):
    return [
        (day, parse_time(start), parse_time(end))
        for start, end in DEFAULT_SLOTS
    ]


def get_time_slots(day):
    active_slots = TimeSlot.objects.filter(day=day, active=True).order_by("start_time")
    if not active_slots.exists():
        return get_default_time_slots(day)
    return [(slot.day, slot.start_time, slot.end_time) for slot in active_slots]


# ML difficulty functions
def get_difficulty_score(course) -> float:
    try:
        pred = CourseDifficultyPrediction.objects.get(course=course)
        return pred.difficulty_score
    except CourseDifficultyPrediction.DoesNotExist:
        return getattr(course, "difficulty_score", 0.5)
    except Exception:
        return getattr(course, "difficulty_score", 0.5)


def get_difficulty_tier(course) -> str:
    score = get_difficulty_score(course)
    if score >= 0.7:
        return "Hard"
    if score >= 0.4:
        return "Medium"
    return "Easy"


def difficulty_rank(course) -> float:
    return get_difficulty_score(course)


# Course duration
def get_duration(course) -> int:
    return 180 if getattr(course, "is_lab", False) else 120


# Conflict checking
def is_free(room, lecturer, day, start, end) -> bool:
    room_conflict = Timetable.objects.filter(
        room=room, day=day, start_time__lt=end, end_time__gt=start
    ).exists()

    lecturer_conflict = False
    if lecturer is not None:
        lecturer_conflict = Timetable.objects.filter(
            lecturer=lecturer, day=day, start_time__lt=end, end_time__gt=start
        ).exists()

    return not (room_conflict or lecturer_conflict)


def get_available_room(day, start, end) -> Optional[Room]:
    for room in Room.objects.all():
        occupied = Timetable.objects.filter(
            room=room, day=day, start_time__lt=end, end_time__gt=start
        ).exists()
        if not occupied:
            return room
    return None


def lecturer_daily_minutes(lecturer, day):
    if lecturer is None:
        return 0
    entries = Timetable.objects.filter(lecturer=lecturer, day=day)
    total = 0
    for entry in entries:
        duration = (datetime.combine(datetime.today(), entry.end_time) - datetime.combine(datetime.today(), entry.start_time)).seconds // 60
        total += duration
    return total


def can_assign_lecturer(lecturer, day, duration):
    if lecturer is None:
        return True
    current = lecturer_daily_minutes(lecturer, day)
    max_daily_minutes = getattr(lecturer, "max_hours_per_day", 6) * 60
    return current + duration <= max_daily_minutes


def get_slot_window(course):
    tier = get_difficulty_tier(course)
    if tier == "Hard":
        return parse_time("07:45"), parse_time("11:45")
    if tier == "Medium":
        return parse_time("11:45"), parse_time("15:45")
    return parse_time("15:45"), parse_time("18:45")


def generate_timetable(program, semester):
    Timetable.objects.filter(program=program, semester=semester).delete()

    courses = Course.objects.filter(program=program).order_by("code")
    courses = sorted(courses, key=difficulty_rank, reverse=True)

    for course in courses:
        sessions_left = max(1, round(course.weekly_hours / (get_duration(course) / 60)))
        duration = get_duration(course)
        window_start, window_end = get_slot_window(course)

        for day in DAYS:
            if sessions_left <= 0:
                break

            for _, start_time, _ in get_time_slots(day):
                if sessions_left <= 0:
                    break

                end_time = add_minutes(start_time, duration)

                if not in_range(start_time, end_time, window_start, window_end):
                    continue

                if not can_assign_lecturer(course.lecturer, day, duration):
                    continue

                room = get_available_room(day, start_time, end_time)
                if room is None:
                    continue

                if not is_free(room, course.lecturer, day, start_time, end_time):
                    continue

                Timetable.objects.create(
                    program=program,
                    course=course,
                    lecturer=course.lecturer if course.lecturer else None,
                    room=room,
                    semester=semester,
                    day=day,
                    start_time=start_time,
                    end_time=end_time,
                )

                sessions_left -= 1

        if sessions_left > 0:
            # Fall back to any remaining slot after window if there are unresolved sessions
            for day in DAYS:
                if sessions_left <= 0:
                    break

                for _, start_time, _ in get_time_slots(day):
                    end_time = add_minutes(start_time, duration)
                    if end_time > parse_time("18:45"):
                        continue

                    if not can_assign_lecturer(course.lecturer, day, duration):
                        continue

                    room = get_available_room(day, start_time, end_time)
                    if room is None:
                        continue

                    if not is_free(room, course.lecturer, day, start_time, end_time):
                        continue

                    Timetable.objects.create(
                        program=program,
                        course=course,
                        lecturer=course.lecturer if course.lecturer else None,
                        room=room,
                        semester=semester,
                        day=day,
                        start_time=start_time,
                        end_time=end_time,
                    )
                    sessions_left -= 1
                    if sessions_left <= 0:
                        break
