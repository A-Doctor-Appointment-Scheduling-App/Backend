from django.urls import path
from .views import doctor_list, doctor_details

urlpatterns = [
    path('doctors/', doctor_list, name='doctor_list'),
    path('doctors/<int:doctor_id>/', doctor_details, name='doctor_details'),
]
