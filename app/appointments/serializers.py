# appointments/serializers.py
from rest_framework import serializers
from .models import Appointment
from users.models import Doctor, Patient  # Import the Doctor and Patient models

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'date', 'time', 'status', 'qr_code']

class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), source='doctor')
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), source='patient')

    class Meta:
        model = Appointment
        fields = ['doctor_id', 'patient_id', 'date', 'time', 'status', 'qr_code']