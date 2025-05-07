from django.core.management.base import BaseCommand
from users.models import Clinic, Doctor, Patient

class Command(BaseCommand):
    help = 'Populate the database with initial data'

    def handle(self, *args, **kwargs):
        # Create Clinic instance
        clinic_data = {
            "name": "City Hospital",
            "address": "123 Hospital St, City",
            "location": "City Center"
        }
        clinic = Clinic.objects.create(**clinic_data)

        # Create Doctor instance
        doctor_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "doctor@example.com",
            "phone_number": "1234567890",
            "specialty": "Cardiologist",
            "photo_url": "http://example.com/photo.jpg",
            "clinic": clinic,
            "password": "securepassword"
        }
        doctor = Doctor.objects.create_user(**doctor_data)

        # Create Patient instance
        patient_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "patient@example.com",
            "phone_number": "0987654321",
            "address": "123 Main St",
            "date_of_birth": "1990-01-01",
            "password": "securepassword"
        }
        patient = Patient.objects.create_user(**patient_data)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database'))
