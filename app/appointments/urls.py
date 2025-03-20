# appointments/urls.py
from django.urls import path
from .views import PatientAppointmentsView

urlpatterns = [
    path('patient/<int:patient_id>/appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
]