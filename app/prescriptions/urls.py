from django.urls import path
from .views import *

urlpatterns = [
path('create/', create_prescription, name='create-prescription'),
    path('prescriptions/<int:pk>/', get_prescription_by_id, name='get-prescription-by-id'),
    path('prescriptions/<int:pk>/download/', download_prescription_pdf, name='download-prescription-pdf'),
        path('prescriptions/doctor/<int:doctor_id>/patient/<int:patient_id>/', get_prescriptions_by_doctor_and_patient, name='get-prescriptions-by-doctor-and-patient'),
    # other paths
]
