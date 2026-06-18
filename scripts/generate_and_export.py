import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "timetable_system.settings")

import django
django.setup()

from scheduling.models import Department, Program, Semester, Lecturer, Room, Course
from scheduling.services.scheduler import generate_timetable
from scheduling.views import api_export_timetable_xlsx
from django.test import RequestFactory

# Create minimal data
dept, _ = Department.objects.get_or_create(name='Education')
program, _ = Program.objects.get_or_create(code='BEDA11', defaults={'name':'Bachelor Education Arts','level':1,'department':dept})
semester, _ = Semester.objects.get_or_create(name='Semester1', defaults={'academic_year':'2024/2025'})
lecturer, _ = Lecturer.objects.get_or_create(email='lect1@example.com', defaults={'name':'Lecturer One','employee_id':'E001','department':dept})
room, _ = Room.objects.get_or_create(name='ODL-A', defaults={'capacity':50,'room_type':'ODL Room'})

# Create sample courses
c1, _ = Course.objects.get_or_create(code='FREN1102', defaults={'title':'FREN 1102 - French Language II','program':program,'lecturer':lecturer,'weekly_hours':4,'is_lab':True})
c2, _ = Course.objects.get_or_create(code='ENGL1101', defaults={'title':'ENGL 1101 - English','program':program,'lecturer':lecturer,'weekly_hours':2,'is_lab':False})

# Generate timetable
generate_timetable(program, semester)

# Export XLSX via view
rf = RequestFactory()
request = rf.get('/api/timetable/export/', {'program_code': program.code})
response = api_export_timetable_xlsx(request)

outfile = f'timetable_{program.code}.xlsx'
with open(outfile, 'wb') as f:
    f.write(response.content)

print('Saved', outfile)
