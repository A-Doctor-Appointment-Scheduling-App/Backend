# appointments/urls.py
from django.urls import path
from .views import PatientAppointmentsView, BookAppointmentView
from .views import BookAppointmentView  # Import the view

urlpatterns = [
    path('patient/<int:patient_id>/appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('appointments/book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),

]