from django.db import models



class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Program(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    level = models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    rooms = models.ManyToManyField("Room", blank=True, related_name="assigned_programs")

    def assigned_rooms(self):
        return ", ".join(room.name for room in self.rooms.all())

    def __str__(self):
        return self.code or self.name


class Lecturer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    employee_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)
    max_hours_per_day = models.IntegerField(default=6)
    max_hours_per_week = models.IntegerField(default=30)
    availability_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


ROOM_TYPES = [
    ("Lecture Hall", "Lecture Hall"),
    ("Laboratory", "Laboratory"),
    ("ODL Room", "ODL Room"),
    ("Computer Lab", "Computer Lab"),
]


class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()
    room_type = models.CharField(max_length=30, choices=ROOM_TYPES, default="Lecture Hall")

    def assigned_program_names(self):
        return ", ".join(program.name for program in self.assigned_programs.all())

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
    ]

    day = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Semester(models.Model):
    name = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"


# =========================
# COURSE (NO ML DATA INSIDE)
# =========================

class Course(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    programs = models.ManyToManyField(Program, blank=True, related_name="courses")
    lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)

    weekly_hours = models.IntegerField()
    student_count = models.PositiveIntegerField(default=0)
    difficulty_score = models.FloatField(default=0.0)

    is_lab = models.BooleanField(default=False)
    is_mathematical = models.BooleanField(default=False)
    is_technical = models.BooleanField(default=False)

    @property
    def program(self):
        return self.programs.first()

    def program_names(self):
        return ", ".join(program.name for program in self.programs.all())

    def __str__(self):
        return f"{self.code} - {self.title}"


# =========================
# ML OUTPUT TABLE (ONLY SOURCE OF DIFFICULTY)
# =========================

class CourseDifficultyPrediction(models.Model):
    DIFFICULTY_LEVELS = [
        ("Easy", "Easy"),
        ("Medium", "Medium"),
        ("Hard", "Hard"),
    ]

    course = models.OneToOneField(Course, on_delete=models.CASCADE)

    predicted_level = models.CharField(
        max_length=10,
        choices=DIFFICULTY_LEVELS
    )

    confidence_score = models.FloatField()
    difficulty_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} → {self.predicted_level}"


# =========================
# TIMETABLE (FINAL OUTPUT)
# =========================

class Timetable(models.Model):
    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
    ]
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT
    )
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.PROTECT, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT)

    day = models.CharField(max_length=10, choices=DAYS)

    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.course} ({self.day})"
class SystemControl(models.Model):
    class Meta:
        verbose_name = "System Control"
        verbose_name_plural = "System Control"

    def __str__(self):
        return "System Control"


class PasswordResetCode(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['code']), models.Index(fields=['created_at'])]

    def __str__(self):
        return f"PasswordResetCode({self.user.email} - {self.code})"