from django.urls import path
from .views import dashboard, landing, timetable_view, lecturer_timetable, export_timetable_pdf
from .views import api_generate_timetable, api_preview_difficulties, api_export_timetable_xlsx
from .views import password_reset_request, password_reset_verify, open_admin

urlpatterns = [
    path("", landing, name="landing"),
    path("dashboard/", dashboard, name="dashboard"),
    path("admin/open/", open_admin, name="open_admin"),
    path("timetable/", timetable_view, name="timetable"),
    path("timetable/pdf/", export_timetable_pdf, name="timetable_pdf"),
    # Password reset by code
    path("accounts/password-reset/", password_reset_request, name="password_reset_request"),
    path("accounts/password-reset/verify/", password_reset_verify, name="password_reset_verify"),
    path("accounts/password-reset/sent/", lambda r: render(r, 'registration/password_reset_sent.html'), name='password_reset_sent'),
    # API
    path("api/timetable/generate/", api_generate_timetable, name="api_generate_timetable"),
    path("api/timetable/preview_difficulties/", api_preview_difficulties, name="api_preview_difficulties"),
    path("api/timetable/export/", api_export_timetable_xlsx, name="api_export_timetable_export"),
    path("lecturer/<int:lecturer_id>/", lecturer_timetable, name="lecturer_timetable"),
]