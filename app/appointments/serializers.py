# appointments/serializers.py
from rest_framework import serializers
from .models import Appointment
from users.models import Doctor, Patient
from prescriptions.models import Prescription  # Import the Doctor and Patient models

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
    patient = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    has_prescription = serializers.SerializerMethodField()


    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'patient', 'date', 'time', 'status', 'qr_code','has_prescription']

    def get_patient(self, obj):
        return {
            "id": obj.patient.id,
            "full_name": f"{obj.patient.first_name} {obj.patient.last_name}",
        }
    
    def get_doctor(self, obj):
        return {
            "id": obj.doctor.id,
            "full_name": f"{obj.doctor.first_name} {obj.doctor.last_name}",
            "speciality": f"{obj.doctor.specialty}",
            "profile_image": f"{obj.doctor.photo_url}",
        }
    
    def get_has_prescription(self, obj):
        return Prescription.objects.filter(appointment=obj).exists()

    

class ConsultedDoctorSerializer(serializers.ModelSerializer):
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number' ,'specialty', 'clinic_name']


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