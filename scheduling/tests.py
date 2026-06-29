from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .admin import CourseDifficultyPredictionAdmin
from .models import Course, Department, Program, Room, Semester, Timetable, CourseDifficultyPrediction, Lecturer
from .services.scheduler import generate_timetable
from .views import get_export_group_rows


class SchedulerTests(TestCase):
    def test_lecturer_can_be_created_without_email_or_id(self):
        lecturer = Lecturer.objects.create(name="Dr. Ada")

        self.assertEqual(lecturer.name, "Dr. Ada")
        self.assertIsNone(lecturer.email)
        self.assertIsNone(lecturer.employee_id)

    def test_course_can_store_student_count(self):
        course = Course.objects.create(
            title="Data Structures",
            code="CS201",
            lecturer=None,
            weekly_hours=3,
            difficulty_score=0.4,
            student_count=120,
        )

        self.assertEqual(course.student_count, 120)

    def test_scheduler_uses_room_capacity_for_student_count(self):
        department = Department.objects.create(name="Computer Science")
        program = Program.objects.create(code="CS101", name="Computer Science", department=department)
        semester = Semester.objects.create(name="Semester 1", academic_year="2024/2025")

        small_room = Room.objects.create(name="R301", capacity=40)
        large_room = Room.objects.create(name="R302", capacity=80)
        program.rooms.add(small_room, large_room)

        course = Course.objects.create(
            title="Database Systems",
            code="CS301",
            lecturer=None,
            weekly_hours=2,
            student_count=70,
            difficulty_score=0.4,
        )
        course.programs.add(program)
        CourseDifficultyPrediction.objects.create(
            course=course,
            predicted_level="Medium",
            confidence_score=0.9,
            difficulty_score=0.4,
        )

        generate_timetable(program, semester)

        timetable_entry = Timetable.objects.get(course=course, program=program, semester=semester)
        self.assertEqual(timetable_entry.room, large_room)

    def test_course_difficulty_prediction_admin_allows_delete(self):
        request_factory = RequestFactory()
        request = request_factory.get("/")
        request.user = get_user_model().objects.create_superuser("admin", "admin@example.com", "password123")

        admin = CourseDifficultyPredictionAdmin(CourseDifficultyPrediction, AdminSite())

        self.assertTrue(admin.has_delete_permission(request))

    def test_generate_timetable_allows_courses_without_lecturer(self):
        department = Department.objects.create(name="Computer Science")
        program = Program.objects.create(code="BCS", name="Computer Science", department=department)
        semester = Semester.objects.create(name="Semester 1", academic_year="2024/2025")
        room = Room.objects.create(name="R101", capacity=60)

        course = Course.objects.create(
            title="Introduction to Programming",
            code="CS101",
            lecturer=None,
            weekly_hours=2,
            difficulty_score=0.3,
        )
        course.programs.add(program)
        CourseDifficultyPrediction.objects.create(
            course=course,
            predicted_level="Easy",
            confidence_score=0.95,
            difficulty_score=0.3,
        )

        generate_timetable(program, semester)

        self.assertTrue(Timetable.objects.filter(course=course, program=program, semester=semester).exists())
        self.assertIsNone(Timetable.objects.get(course=course, program=program, semester=semester).lecturer)

    def test_scheduler_ignores_rooms_restricted_to_other_programs(self):
        department = Department.objects.create(name="Mathematics")
        program_a = Program.objects.create(code="MTH", name="Mathematics", department=department)
        program_b = Program.objects.create(code="PHY", name="Physics", department=department)
        semester = Semester.objects.create(name="Semester 1", academic_year="2024/2025")

        restricted_room = Room.objects.create(name="R201", capacity=40)
        program_b.rooms.add(restricted_room)

        general_room = Room.objects.create(name="R202", capacity=40)
        program_a.rooms.add(general_room)

        course = Course.objects.create(
            title="Calculus",
            code="MTH101",
            lecturer=None,
            weekly_hours=2,
            difficulty_score=0.2,
        )
        course.programs.add(program_a)
        CourseDifficultyPrediction.objects.create(
            course=course,
            predicted_level="Easy",
            confidence_score=0.9,
            difficulty_score=0.2,
        )

        generate_timetable(program_a, semester)

        timetable_entry = Timetable.objects.get(course=course, program=program_a, semester=semester)
        self.assertEqual(timetable_entry.room, general_room)

    def test_export_group_rows_use_program_level_and_semester(self):
        department = Department.objects.create(name="Computer Science")
        first_program = Program.objects.create(code="BSDS", name="Business and Data Science", department=department, level=2)
        second_program = Program.objects.create(code="BSC", name="Computer Science", department=department, level=1)

        rows = get_export_group_rows([first_program, second_program], academic_semester=1)

        self.assertEqual(rows[0][1], "BSC 11")
        self.assertEqual(rows[1][1], "BSDS 21")
