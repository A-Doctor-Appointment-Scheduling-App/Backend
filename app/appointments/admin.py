from django.contrib import admin
from users.models import Doctor, Patient,Clinic, TimeSlot
from appointments.models import Appointment,Reminder
from prescriptions.models import Prescription
from notifications.models import Notification


# Register your models here.

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Clinic)
admin.site.register(TimeSlot)
admin.site.register(Appointment)
admin.site.register(Reminder)
admin.site.register(Prescription)
admin.site.register(Notification)
