from django.urls import path
from .views import doctor_register_view, patient_register_view, login_view,create_clinic

urlpatterns = [
    path('doctor/register/', doctor_register_view, name='doctor-register'),
    path('patient/register/', patient_register_view, name='patient-register'),
    path('login/', login_view, name='login'),
    path('clinics/create/', create_clinic, name='create-clinic'),
]