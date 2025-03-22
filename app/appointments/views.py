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
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Appointment

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
from notifications.views import send_notification_to_patient

class BookAppointmentView(APIView):
    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save the appointment
            appointment = serializer.save()

            # Send a reminder notification to the patient
            message = f"Reminder: You have an appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} on {appointment.date} at {appointment.time}."
            send_notification_to_patient(appointment.patient, message)

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
# appointments/views.py
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

        appointment.status = "Pending"  # Needs to be reconfirmed by the doctor
        appointment.save()

        # Send a reminder notification to the patient
        message = f"Reminder: Your appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} has been rescheduled to {appointment.date} at {appointment.time}."
        send_notification_to_patient(appointment.patient, message)

        return JsonResponse({"message": "Appointment rescheduled successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=405)

def confirm_appointment(request, appointment_id):
    """Doctor confirms the appointment and generates a QR code."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "Scheduled":
        return JsonResponse({"error": "Appointment is already confirmed or cancelled"}, status=400)

    appointment.status = "Scheduled"
    appointment.save()

    return JsonResponse({
        "message": "Appointment confirmed",
        "qr_code": appointment.qr_code.url if appointment.qr_code else None
    })

def scan_qr_code(request, appointment_id):
    """Doctor scans the QR code, updating the appointment status."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "Scheduled":
        return JsonResponse({"error": "Invalid QR code or appointment status"}, status=400)

    appointment.status = "Completed"
    appointment.save()

    return JsonResponse({"message": "Appointment completed successfully"})


def appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    data = {
        "id": appointment.id,
        "doctor": f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
        "date": appointment.date,
        "status": appointment.status,
        "qr_code": appointment.qr_code.url if appointment.qr_code else None,
    }
    return JsonResponse(data)

