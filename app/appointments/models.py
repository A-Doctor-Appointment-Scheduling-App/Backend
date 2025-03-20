from django.db import models
from users.models import Doctor,Patient, User


# Create your models here.
class Appointment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'),('Confirmed', 'Confirmed'),('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    qr_code_data = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.date} - {self.time} | {self.doctor} with {self.patient}"
    

class Reminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    message = models.TextField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.appointment} at {self.scheduled_time}"
