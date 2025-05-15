from django.urls import path,include

from .views import *
urlpatterns = [
    path('<int:appointment_id>/', appointment_details, name='appointment_details'),
    path('confirm/<int:appointment_id>/', confirm_appointment, name='confirm_appointment'),
    path('scan/<int:appointment_id>/', scan_qr_code, name='scan_qr_code'),

    path('patient/<int:patient_id>/appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('doctor/<int:doctor_id>/appointments/', DoctorAppointmentsView.as_view(), name='doctor-appointments'),
    path('book/', book_appointment, name='book_appointment'),
    path("<int:appointment_id>/confirm/", confirm_appointment_, name="confirm_appointment"),
    path("<int:appointment_id>/reject/", reject_appointment, name="reject_appointment"),
    path("<int:appointment_id>/complete/", complete_appointment, name="complete_appointment"),
    path("<int:appointment_id>/cancel/", cancel_appointment, name="cancel_appointment"),
    path("<int:appointment_id>/reschedule/<str:new_date>/<str:new_time>/", reschedule_appointment,name="reschedule_appointment"),
]
