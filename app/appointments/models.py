# appointments/models.py
from django.db import models
<<<<<<< HEAD
from users.models import Doctor, Patient, User
=======
from users.models import Doctor,Patient
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
>>>>>>> djihene

class Appointment(models.Model):
    doctor = models.ForeignKey("users.Doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey("users.Patient", on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
<<<<<<< HEAD
        choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    qr_code_data = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} - {self.time} | {self.doctor} with {self.patient}"
=======
        choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default="Scheduled"
    )
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)  # Store QR Code Image

    def generate_qr_code(self):
        """Generate and save a QR code when an appointment is confirmed."""
        qr_data = f"Doctor: {self.doctor.first_name} {self.doctor.last_name}, Patient: {self.patient.first_name} {self.patient.last_name}, Appointment Time: {self.date} {self.time}"
        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"appointment_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Automatically generate QR code when the appointment is confirmed."""
        if self.status == "Scheduled" and not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.time} | {self.doctor} with {self.patient}"

>>>>>>> djihene

class Reminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    message = models.TextField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.appointment} at {self.scheduled_time}"