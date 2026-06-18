from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import openpyxl

from .models import Program, Course, Timetable, Semester
from .serializers import CourseSerializer, TimetableSerializer
from .services.scheduler import generate_timetable


@api_view(["GET"])
def preview_difficulties(request, program_code=None):
    program = get_object_or_404(Program, code=program_code)
    courses = Course.objects.filter(program=program)
    serializer = CourseSerializer(courses, many=True)
    return Response({"courses": serializer.data})


@api_view(["POST"])
def generate_timetable_api(request):
    program_code = request.data.get("program_code")
    semester_id = request.data.get("semester_id")

    if not program_code or not semester_id:
        return Response({"detail": "program_code and semester_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    program = get_object_or_404(Program, code=program_code)
    semester = get_object_or_404(Semester, id=semester_id)

    generate_timetable(program, semester)

    return Response({"success": True, "message": "Timetable generated."})


@api_view(["GET"])
def view_timetable(request):
    program_code = request.query_params.get("program_code")
    semester_id = request.query_params.get("semester_id")

    if not program_code or not semester_id:
        return Response({"detail": "program_code and semester_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    program = get_object_or_404(Program, code=program_code)
    semester = get_object_or_404(Semester, id=semester_id)

    timetable = Timetable.objects.filter(program=program, semester=semester)
    serializer = TimetableSerializer(timetable, many=True)
    return Response({"program": program.code, "semester": str(semester), "entries": serializer.data})


@api_view(["GET"])
def export_timetable(request):
    timetable_id = request.query_params.get("timetable_id")

    if not timetable_id:
        return Response({"detail": "timetable_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    timetable = Timetable.objects.filter(id=timetable_id).select_related("course", "room", "program", "semester")
    if not timetable.exists():
        return Response({"detail": "Timetable not found."}, status=status.HTTP_404_NOT_FOUND)

    workbook = openpyxl.Workbook()
    sheets = {day: workbook.create_sheet(day) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    workbook.remove(workbook["Sheet"])

    for day, sheet in sheets.items():
        sheet.append([day.upper()])
        header = ["", "07:45AM", "08:45AM", "09:45AM", "10:45AM", "11:45AM", "12:45PM", "01:45PM", "02:45PM", "03:45PM", "04:45PM", "05:45PM"]
        sheet.append(header)
        sheet.append(["", "08:45AM", "09:45AM", "10:45AM", "11:45AM", "12:45PM", "01:45PM", "02:45PM", "03:45PM", "04:45PM", "05:45PM", "06:45PM"])

        day_entries = timetable.filter(day=day)
        program_rows = {}

        for entry in day_entries:
            key = entry.program.code
            if key not in program_rows:
                program_rows[key] = [key] + [""] * 11

            try:
                slot_index = ["07:45AM", "08:45AM", "09:45AM", "10:45AM", "11:45AM", "12:45PM", "01:45PM", "02:45PM", "03:45PM", "04:45PM", "05:45PM"].index(entry.start_time.strftime("%I:%M%p"))
            except ValueError:
                continue

            program_rows[key][slot_index + 1] = f"{entry.course.code}\n{entry.room.name}"

        for row in program_rows.values():
            sheet.append(row)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=timetable.xlsx"
    workbook.save(response)
    return response
