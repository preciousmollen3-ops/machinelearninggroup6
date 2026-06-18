from django.urls import path
from .views import dashboard, timetable_view, lecturer_timetable, export_timetable_pdf
from .views import api_generate_timetable, api_preview_difficulties, api_export_timetable_xlsx

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("timetable/", timetable_view, name="timetable"),
    path("timetable/pdf/", export_timetable_pdf, name="timetable_pdf"),
    # API
    path("api/timetable/generate/", api_generate_timetable, name="api_generate_timetable"),
    path("api/timetable/preview_difficulties/", api_preview_difficulties, name="api_preview_difficulties"),
    path("api/timetable/export/", api_export_timetable_xlsx, name="api_export_timetable_export"),
    path("lecturer/<int:lecturer_id>/", lecturer_timetable, name="lecturer_timetable"),
]