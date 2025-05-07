from rest_framework import serializers
from .models import Prescription, Medication

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'frequency', 'instructions']

class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'medications', 'issued_date']

    def create(self, validated_data):
        medications_data = validated_data.pop('medications')
        prescription = Prescription.objects.create(**validated_data)
        for medication_data in medications_data:
            Medication.objects.create(prescription=prescription, **medication_data)
        return prescription
