from django.db import models
from appointments.models import Appointment


# Create your models here.
class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    medication_names = models.TextField()
    dosage = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)  
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment.patient} - {self.issued_date}"