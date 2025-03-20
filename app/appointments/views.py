# appointments/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer
from users.models import Patient

class PatientAppointmentsView(APIView):
    def get(self, request, patient_id):
        try:
            # Fetch the patient object
            patient = Patient.objects.get(id=patient_id)
            # Fetch all appointments for the patient
            appointments = Appointment.objects.filter(patient=patient)
            # Serialize the appointments
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)