# appointments/serializers.py
from rest_framework import serializers
from .models import Appointment
from users.models import Doctor, Patient  # Import the Doctor and Patient models

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'date', 'time', 'status', 'qr_code']


class AppointmentStatsSerializer(serializers.ModelSerializer):
    patient_first_name = serializers.CharField(source='patient.first_name', read_only=True)
    patient_last_name = serializers.CharField(source='patient.last_name', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'patient_first_name', 'patient_last_name', 'date', 'time', 'status', 'qr_code']

class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), source='doctor')
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), source='patient')

    class Meta:
        model = Appointment
        fields = ['doctor_id', 'patient_id', 'date', 'time', 'status', 'qr_code']


class AppointmentFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'