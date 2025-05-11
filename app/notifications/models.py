from django.db import models
from users.models import Patient,Doctor

# Create your models here.
class Notification(models.Model):
    recipient_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    recipient_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, default="Notification")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.message
    


class FCMDevice(models.Model):
    USER_TYPES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    
    user_id = models.IntegerField()
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    registration_id = models.TextField()  # Le token FCM
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user_id', 'user_type', 'registration_id')
    
    def __str__(self):
        return f"{self.user_type} {self.user_id}: {self.registration_id[:10]}..."