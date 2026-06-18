import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "timetable_system.settings")

import django
django.setup()

from django.test import RequestFactory
from scheduling.views import api_export_timetable_xlsx

rf = RequestFactory()
request = rf.get('/api/timetable/export/', {'all_programs': '1'})
response = api_export_timetable_xlsx(request)

outfile = 'timetable_all_programs.xlsx'
with open(outfile, 'wb') as f:
    f.write(response.content)

print('Saved', outfile)
