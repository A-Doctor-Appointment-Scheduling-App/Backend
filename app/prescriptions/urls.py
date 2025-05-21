from django.urls import path
from .views import *

urlpatterns = [
path('create/', create_prescription, name='create-prescription'),
path('<int:pk>/', get_prescription_by_id, name='get-prescription-by-id'),
path('<int:pk>/download/', download_prescription_pdf, name='download-prescription-pdf'),
path('doctor/<int:doctor_id>/patient/<int:patient_id>/', get_prescriptions_by_doctor_and_patient, name='get-prescriptions-by-doctor-and-patient'),
path('doctor/<int:doctor_id>/prescriptions/', DoctorPrescriptionsView.as_view(), name='doctor_prescriptions'),
path('patient/<int:patient_id>/prescriptions/', PatientPrescriptionsView.as_view(), name='patient_prescriptions'),
path('appointment/<int:appointment_id>/', get_prescription_by_appointment_id, name='get_prescription_by_appointment_id'),
]
