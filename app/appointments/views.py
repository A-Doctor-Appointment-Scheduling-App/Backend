from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentCreateSerializer  # Updated import
from users.models import Patient
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notifications.views import send_notification_to_doctor,send_notification_to_patient


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

'''The doctor confirms an appointement with the call to this function'''
@csrf_exempt
def confirm_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = "Confirmed"
        appointment.save()

        send_notification_to_patient(appointment.patient, f"Your appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} has been confirmed.")

        return JsonResponse({"message": "Appointment Confirmed successfully."})
    return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)
    

'''The doctor rejects an appointement with the call to this function'''
@csrf_exempt
def reject_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = "Rejected"
        appointment.save()
        send_notification_to_patient(appointment.patient, f"Your appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} has been rejected.")
        return JsonResponse({"message": "Appointment Rejected successfully."})


'''The doctor completes an appointement with the call to this function'''
@csrf_exempt
def complete_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = "Completed"
        appointment.save()
        return JsonResponse({"message": "Appointment Completed successfully."})


'''The patient cancels an appointement with the call to this function'''
@csrf_exempt
def cancel_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = "Cancelled"
        appointment.save()
        send_notification_to_doctor(appointment.doctor, f"Mr. {appointment.patient.first_name} {appointment.patient.last_name} cancelled his appointement.")
        return JsonResponse({"message": "Appointment cancelled successfully."})


'''The patient reschedules an appointement with the call to this function'''
@csrf_exempt
def reschedule_appointment(request, appointment_id, new_date, new_time):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if not new_date and not new_time:
            return JsonResponse({"error": "Provide at least a new date or time."}, status=400)

        if new_date:
            appointment.date = new_date
        if new_time:
            appointment.time = new_time

        appointment.status = "Pending" '''needs to be reconfirmed from the doctor'''
        appointment.save()
        send_notification_to_patient(appointment.doctor, f"Mr. {appointment.patient.first_name} {appointment.patient.last_name} rescheduled the appointement to {appointment.date} {appointment.time}.")

        return JsonResponse({"message": "Appointment rescheduled successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=405)


