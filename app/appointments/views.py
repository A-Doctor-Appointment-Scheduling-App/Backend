# appointments/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentCreateSerializer  # Updated import
from users.models import Patient


class PatientAppointmentsView(APIView):
    def get(self, request, patient_id):
        try:
            # Fetch the patient object
            patient = Patient.objects.get(id=patient_id)
            # Fetch all appointments for the patient
            appointments = Appointment.objects.filter(patient=patient)
            # Serialize the appointments
            serializer = AppointmentCreateSerializer(appointments, many=True)  # Updated serializer
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
class BookAppointmentView(APIView):
    def post(self, request):
        # Deserialize and validate the input data
        serializer = AppointmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save the appointment
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



