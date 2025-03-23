from django.test import TestCase
from datetime import datetime, timedelta
from users.models import Doctor, Patient, Clinic  # Import the Clinic model
from appointments.models import Appointment
from notifications.models import Notification
from notifications.views import send_appointment_reminders

class SendReminderTests(TestCase):
    def setUp(self):
        # Create a clinic for testing
        self.clinic = Clinic.objects.create(
            name="Test Clinic",
            address="123 Test Street",
            location="Test Location"  # Add the required 'location' field
        )

        # Create a doctor and a patient for testing
        self.doctor = Doctor.objects.create(
            first_name="John4",
            last_name="Doe4",
            email="john8.doe@example.com",
            phone_number="12567890",
            specialty="Cardiologist",  # Required field for Doctor
            photo_url="http://example.com/photo.jpg",  # Required field for Doctor
            clinic=self.clinic,
            password= "securepassword",
            username="doctor_john_doe"  # Ensure this is unique  # Assign the clinic to the doctor

        )
        self.patient = Patient.objects.create(
            first_name="Jane44",
            last_name="Smith",
            email="jane.smi44th@example.com",
            phone_number="0654321",
            address="123 Patient Street",  # Required field for Patient
            date_of_birth="1990-01-01" ,
            password= "securepassword" ,# Required field for Patient
            username="patient_jane_smith"  # Ensure this is unique
        )

    def test_send_reminder_for_appointment_24_hours_away(self):
        # Create an appointment 24 hours from now
        appointment_time = datetime.now() + timedelta(hours=24)
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=appointment_time.date(),
            time=appointment_time.time(),
            status="Confirmed"
        )

        # Call the send_appointment_reminders function
        send_appointment_reminders()

        # Check if a notification was created
        notification = Notification.objects.filter(recipient_patient=self.patient).first()
        self.assertIsNotNone(notification, "Notification was not created for the appointment.")
        self.assertIn("Reminder: You have an appointment with Dr.", notification.message)

    def test_no_duplicate_notifications(self):
        # Create an appointment 24 hours from now
        appointment_time = datetime.now() + timedelta(hours=24)
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=appointment_time.date(),
            time=appointment_time.time(),
            status="Confirmed"
        )

        # Call the send_appointment_reminders function twice
        send_appointment_reminders()
        send_appointment_reminders()

        # Check that only one notification was created
        notifications = Notification.objects.filter(recipient_patient=self.patient)
        self.assertEqual(notifications.count(), 1, "Duplicate notifications were created.")

    def test_no_reminder_for_non_confirmed_appointments(self):
        # Create an appointment 24 hours from now with status "Pending"
        appointment_time = datetime.now() + timedelta(hours=24)
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=appointment_time.date(),
            time=appointment_time.time(),
            status="Pending"
        )

        # Call the send_appointment_reminders function
        send_appointment_reminders()

        # Check that no notification was created
        notification = Notification.objects.filter(recipient_patient=self.patient).first()
        self.assertIsNone(notification, "Notification was created for a non-confirmed appointment.")

    def test_no_reminder_for_appointments_not_24_hours_away(self):
        # Create an appointment 25 hours from now (not 24 hours)
        appointment_time = datetime.now() + timedelta(hours=25)
        appointment = Appointment.objects.create(
            doctor=self.doctor,
            patient=self.patient,
            date=appointment_time.date(),
            time=appointment_time.time(),
            status="Confirmed"
        )

        # Call the send_appointment_reminders function
        send_appointment_reminders()

        # Check that no notification was created
        notification = Notification.objects.filter(recipient_patient=self.patient).first()
        self.assertIsNone(notification, "Notification was created for an appointment not 24 hours away.")