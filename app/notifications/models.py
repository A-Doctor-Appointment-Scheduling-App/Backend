from django.db import models
from users.models import Patient,Doctor

# Create your models here.
class Notification(models.Model):
    recipient_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    recipient_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message