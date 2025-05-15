from django.urls import path
from .views import *

urlpatterns = [
    path('doctor/register/', doctor_register_view, name='doctor-register'),
    path('patient/register/', patient_register_view, name='patient-register'),
    path('login/', login_view, name='login'),
    path('clinics/create/', create_clinic, name='create-clinic'),
    path('dashboard/', dashboard, name='dashboard'),
    path('doctors/', doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', doctor_details, name='doctor_details'),
]