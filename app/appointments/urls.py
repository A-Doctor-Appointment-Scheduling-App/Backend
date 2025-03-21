from django.urls import path
from .views import confirm_appointment, scan_qr_code, appointment_details

urlpatterns = [
    path('<int:appointment_id>/', appointment_details, name='appointment_details'),
    path('confirm/<int:appointment_id>/', confirm_appointment, name='confirm_appointment'),
    path('scan/<int:appointment_id>/', scan_qr_code, name='scan_qr_code'),
]
