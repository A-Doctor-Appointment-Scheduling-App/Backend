from rest_framework import serializers
from .models import Doctor, Patient, Clinic

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Doctor
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'specialty', 'photo_url', 'clinic', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        doctor = Doctor.objects.create_user(password=password, **validated_data)
        return doctor

class PatientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        patient = Patient.objects.create_user(password=password, **validated_data)
        return patient

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['name', 'address', 'location']