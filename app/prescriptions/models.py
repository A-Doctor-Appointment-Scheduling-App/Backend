from django.db import models
from appointments.models import Appointment

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment.patient} - {self.issued_date}"

class Medication(models.Model):
    prescription = models.ForeignKey(Prescription, related_name='medications', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} for {self.prescription.appointment.patient}"
