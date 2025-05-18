from django.db import models
from users.models import Doctor,Patient
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

class Appointment(models.Model):
    doctor = models.ForeignKey("users.Doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey("users.Patient", on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    def generate_qr_code(self):
        """Generate and save a QR code with appointment details."""
        qr_data = (
            f"Appointment ID: {self.id}\n"
            f"Doctor: {self.doctor.first_name} {self.doctor.last_name}\n"
            f"Patient: {self.patient.first_name} {self.patient.last_name}\n"
            f"Date: {self.date}\n"
            f"Time: {self.time}"
        )
        qr = qrcode.make(qr_data)

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"appointment_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Override save method to handle QR code generation only on confirmation."""
        if self.pk:  # Only for existing instances
            old_status = Appointment.objects.get(pk=self.pk).status
            if old_status != 'Confirmed' and self.status == 'Confirmed' and not self.qr_code:
                self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.time} | {self.doctor} with {self.patient}"
    
class Reminder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    scheduled_time = models.DateTimeField()
    message = models.TextField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.appointment} at {self.scheduled_time}"
