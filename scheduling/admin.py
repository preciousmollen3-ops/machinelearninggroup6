from django.contrib import admin
from django.http import HttpResponse

from .models import (
    Department,
    Program,
    Lecturer,
    Room,
    TimeSlot,
    Semester,
    Course,
    Timetable,
    CourseDifficultyPrediction,
    SystemControl
)

from .services.scheduler import generate_timetable


# =========================
# CORE ADMIN CLASSES
# =========================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "is_active", "assigned_rooms")
    list_filter = ("department", "is_active")
    search_fields = ("name", "code")
    filter_horizontal = ("rooms",)


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ("name", "employee_id", "email", "department", "availability_status")
    search_fields = ("name", "email", "employee_id")
    list_filter = ("department", "availability_status")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "room_type", "assigned_program_names")
    search_fields = ("name",)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("day", "start_time", "end_time", "active")
    list_filter = ("day", "active")
    ordering = ("day", "start_time")


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "program_names", "department", "weekly_hours", "student_count", "difficulty_score", "is_lab")
    list_filter = ("department", "is_lab", "is_mathematical", "is_technical")
    search_fields = ("title", "code")
    filter_horizontal = ("programs",)
    readonly_fields = ("difficulty_score",)



@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("course", "lecturer", "room", "day", "start_time", "end_time", "semester")
    list_filter = ("day", "semester", "room")

    actions = ["generate_timetable_action"]

    def generate_timetable_action(self, request, queryset):
        program = Program.objects.first()
        semester = Semester.objects.first()

        if not program or not semester:
            self.message_user(request, "Create Program and Semester first!")
            return

        generate_timetable(program, semester)
        self.message_user(request, "Timetable generated successfully!")

    generate_timetable_action.short_description = "Generate Full Timetable (ML + Scheduler)"


@admin.register(CourseDifficultyPrediction)
class CourseDifficultyPredictionAdmin(admin.ModelAdmin):
    list_display = ("course", "predicted_level", "confidence_score", "created_at")
    readonly_fields = ("course", "predicted_level", "confidence_score", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff


# =========================
# SYSTEM CONTROL PANEL
# =========================

@admin.register(SystemControl)
class SystemControlAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):

        if "generate" in request.GET:
            program = Program.objects.first()
            semester = Semester.objects.first()

            if program and semester:
                generate_timetable(program, semester)
                self.message_user(request, "Timetable generated successfully!")

        return HttpResponse("""
            <h2>System Control Panel</h2>
            <a href="?generate=1">Generate Timetable</a>
        """)