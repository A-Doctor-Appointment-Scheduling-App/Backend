# users/management/commands/populate_db.py
from django.core.management.base import BaseCommand
from users.models import Clinic, Doctor, Patient, TimeSlot
from appointments.models import Appointment

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **kwargs):
        # Delete all existing data (optional, to start fresh)
        Appointment.objects.all().delete()
        TimeSlot.objects.all().delete()
        Doctor.objects.all().delete()
        Patient.objects.all().delete()
        Clinic.objects.all().delete()

        # Create a clinic
        clinic = Clinic.objects.create(
            name="City Hospital",
            address="123 Main St",
            location="City Center"
        )
        self.stdout.write(self.style.SUCCESS('Clinic created.'))

        # Create a doctor
        doctor = Doctor.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="1234567890",
            password="password123",
            specialty="Cardiologist",
            photo_url="https://example.com/doctor.jpg",
            clinic=clinic
        )
        self.stdout.write(self.style.SUCCESS('Doctor created.'))

        # Create a time slot
        time_slot = TimeSlot.objects.create(
            start_time="09:00:00",
            end_time="10:00:00"
        )
        self.stdout.write(self.style.SUCCESS('Time slot created.'))

        # Add the time slot to the doctor's availability
        doctor.availability.add(time_slot)
        self.stdout.write(self.style.SUCCESS('Time slot added to doctor\'s availability.'))

        # Create a patient
        patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="0987654321",
            password="password123",
            address="456 Elm St",
            date_of_birth="1990-01-01"
        )
        self.stdout.write(self.style.SUCCESS('Patient created.'))

        # Create an appointment
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            date="2023-10-15",
            time="10:00:00",
            status="Scheduled",
            qr_code_data="some_qr_code_data"
        )
        self.stdout.write(self.style.SUCCESS('Appointment created.'))

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))