from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Appointment


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentCreateSerializer  # Updated import
from .serializers import AppointmentFullSerializer
from users.models import Patient,Doctor
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notifications.views import send_notification_to_doctor,send_notification_to_patient




def confirm_appointment(request, appointment_id):
    """Doctor confirms the appointment and generates a QR code."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "Pending":
        return JsonResponse({"error": "Appointment is already confirmed or cancelled"}, status=400)

    appointment.status = "Pending"
    appointment.save()

    return JsonResponse({
        "message": "Appointment confirmed",
        "qr_code": appointment.qr_code.url if appointment.qr_code else None
    })

def scan_qr_code(request, appointment_id):
    """Doctor scans the QR code, updating the appointment status."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "Pending":
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




class PatientAppointmentsView(APIView):
    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
            appointments = Appointment.objects.filter(patient=patient)
            serializer = AppointmentCreateSerializer(appointments, many=True)  # Updated serializer
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)


class DoctorAppointmentsView(APIView):
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            appointments = Appointment.objects.filter(doctor=doctor)
            serializer = AppointmentCreateSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

class PatientAppointmentsFullView(APIView):
    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
            appointments = Appointment.objects.filter(patient=patient)
            serializer = AppointmentFullSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

class DoctorAppointmentsFullView(APIView):
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            appointments = Appointment.objects.filter(doctor=doctor)
            serializer = AppointmentFullSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
def book_appointment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            patient_id = data.get("patient_id")
            doctor_id = data.get("doctor_id")
            date = data.get("date")
            time = data.get("time")

            if not all([patient_id, doctor_id, date, time]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            patient = Patient.objects.get(id=patient_id)
            doctor = Doctor.objects.get(id=doctor_id)

            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                date=date,
                time=time,
                status="Pending"
            )

            message = f"Reminder: You have an appointment with Dr. {doctor.first_name} {doctor.last_name} on {date} at {time}."
            title = "Appointment Reminder"

            send_notification_to_patient(patient, message, title=title)

            return JsonResponse({
                "message": "Appointment booked successfully.",
                "appointment_id": appointment.id,
                "status": appointment.status
            })

        except Patient.DoesNotExist:
            return JsonResponse({"error": "Invalid patient ID"}, status=404)
        except Doctor.DoesNotExist:
            return JsonResponse({"error": "Invalid doctor ID"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method. Use POST."}, status=405)

'''The doctor confirms an appointement with the call to this function'''
@csrf_exempt
def confirm_appointment_(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.status = "Confirmed"
        appointment.save()

        notification_title = "Appointment Confirmed"
        notification_message = f"Your appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} has been confirmed."
        
        # Envoyer la notification avec titre
        send_notification_to_patient(
            appointment.patient, 
            notification_message,
            title=notification_title
        )


        return JsonResponse({"message": "Appointment Confirmed successfully."})
    return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)
    

'''The doctor rejects an appointement with the call to this function'''
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

@csrf_exempt
def reject_appointment(request, appointment_id):
    if request.method == "POST":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        try:
            data = json.loads(request.body)
            reason = data.get("reason", "").strip()
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON or missing 'reason' field"}, status=400)

        if not reason:
            return JsonResponse({"error": "A rejection reason is required."}, status=400)

        appointment.status = "Rejected"
        appointment.save()

        notification_title = "Appointment rejected"
        message = (
            f"Your appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} "
            f"has been rejected. Reason: {reason}"
        )
        send_notification_to_patient(
            appointment.patient, 
            message,
            title=notification_title
        )

        return JsonResponse({"message": "Appointment rejected successfully."})



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
       
        notification_title = "Appointment cancelled"

        send_notification_to_doctor(appointment.doctor, f"Mr. {appointment.patient.first_name} {appointment.patient.last_name} cancelled his appointement.",notification_title)
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


        notification_title = "Appointment rescheduling demand"
        message = f"The appointment with {appointment.patient.first_name} {appointment.patient.last_name} has been rescheduled to {appointment.date} at {appointment.time}. Please review and confirm the new schedule."

        send_notification_to_doctor(appointment.doctor,message,notification_title)
        
        return JsonResponse({"message": "Appointment rescheduled successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=405)
