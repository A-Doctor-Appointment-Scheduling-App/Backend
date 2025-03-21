from rest_framework import serializers
from .models import Appointment, Doctor, Patient

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date', 'time', 'status', 'qr_code_data']

    def validate(self, data):
        return data
