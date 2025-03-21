# appointments/urls.py
from django.urls import path, include
from django.contrib import admin
from .views import PatientAppointmentsView, BookAppointmentView
from .views import BookAppointmentView
from .views import confirm_appointment, reject_appointment,complete_appointment,cancel_appointment,reschedule_appointment


urlpatterns = [
    path('patient/<int:patient_id>/appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('appointments/book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path("<int:appointment_id>/confirm/", confirm_appointment, name="confirm_appointment"),
    path("<int:appointment_id>/reject/", reject_appointment, name="reject_appointment"),
    path("<int:appointment_id>/complete/", complete_appointment, name="complete_appointment"),
    path("<int:appointment_id>/cancel/", cancel_appointment, name="cancel_appointment"),
    path("<int:appointment_id>/reschedule/<str:new_date>/<str:new_time>/", reschedule_appointment,name="reschedule_appointment"),
    path('admin/', admin.site.urls),
    path('api/notifications/', include('notifications.urls')), 
]