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
    patient_date_birth = serializers.CharField(source='patient.date_of_birth', read_only=True)


    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'patient_first_name', 'patient_last_name', 'patient_date_birth' ,'date', 'time', 'status', 'qr_code']



class PatientAppointmentStatsSerializer(serializers.ModelSerializer):
    doctor_first_name = serializers.CharField(source='doctor.first_name', read_only=True)
    doctor_last_name = serializers.CharField(source='doctor.last_name', read_only=True)
    doctor_specialty = serializers.CharField(source='doctor.specialty', read_only=True)
    clinic_name = serializers.CharField(source='doctor.clinic.name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'doctor',
            'doctor_first_name',
            'doctor_last_name',
            'doctor_specialty',
            'clinic_name',
            'date',
            'time',
            'status',
            'qr_code'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), source='doctor')
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), source='patient')

    class Meta:
        model = Appointment
        fields = ['doctor_id', 'patient_id', 'date', 'time', 'status', 'qr_code']

    

class ConsultedDoctorSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number' ,'specialty', 'clinic_name']
