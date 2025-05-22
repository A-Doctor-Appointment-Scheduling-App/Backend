from .serializers import AppointmentSerializer, AppointmentStatsSerializer,AppointmentFullSerializer,PatientAppointmentStatsSerializer,ConsultedDoctorSerializer,AppointmentFullSerializer
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from .models import Appointment
from django.db.models import Count
from datetime import date
from .serializers import AppointmentSerializer, AppointmentStatsSerializer, AppointmentFullSerializer 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentCreateSerializer  # Updated import
from users.models import Patient,Doctor
from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notifications.views import send_notification_to_doctor,send_notification_to_patient
from datetime import datetime


@csrf_exempt
def scan_qr_code(request, appointment_id):
    """Doctor scans the QR code, updating the appointment status."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != "Confirmed":
        return JsonResponse({"error": "Invalid QR code or appointment status"}, status=400)

    appointment.status = "Completed"
    appointment.save()

    return JsonResponse({"message": "Appointment completed successfully"})

def get_qr_code(request, appointment_id):
    """Retourne le QR code d'un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not appointment.qr_code:
        return JsonResponse({"error": "QR code not available"}, status=404)
    
    qr_code_path = appointment.qr_code.path
    if not default_storage.exists(qr_code_path):
        return JsonResponse({"error": "QR code file not found"}, status=404)
    
    with default_storage.open(qr_code_path, 'rb') as f:
        return HttpResponse(f.read(), content_type="image/png")
    
def appointment_qr_code(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if not appointment.qr_code and appointment.status == "Confirmed":
        appointment.generate_qr_code()
        appointment.save()

    if appointment.qr_code:
        with open(appointment.qr_code.path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/png")
    else:
        return HttpResponse("QR code not available for this appointment.", status=404)
    

def appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    patient = appointment.patient  
    doctor = appointment.doctor

    data = {
        "id": appointment.id,
        "doctor": f"{doctor.first_name} {doctor.last_name}",
        "patient": {
            "full_name": f"{patient.first_name} {patient.last_name}",
            "email": patient.email,
            "phone_number": patient.phone_number,
            "address": patient.address,
            "date_of_birth": patient.date_of_birth
        },
        "date": appointment.date,
        "time": appointment.time,
        "status": appointment.status,
        "qr_code": appointment.qr_code.url if appointment.qr_code else None,
    }
    return JsonResponse(data)


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
            # Verify patient exists
            patient = Patient.objects.get(id=patient_id)
            # Get all appointments for this patient
            appointments = Appointment.objects.filter(patient=patient)
            # Serialize with all fields
            serializer = AppointmentFullSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

class DoctorAppointmentsFullView(APIView):
    def get(self, request, doctor_id):
        try:
            # Verify doctor exists
            doctor = Doctor.objects.get(id=doctor_id)
            # Get all appointments for this doctor
            appointments = Appointment.objects.filter(doctor=doctor)
            # Serialize with all fields
            serializer = AppointmentFullSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        
'''The patient books an appointement with the call to this function'''
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

            # Send a reminder notification to the patient
            title = "Appointment reminder"
            message = f"Reminder: You have an appointment with Dr. {doctor.first_name} {doctor.last_name} on {date} at {time}."
            send_notification_to_patient(patient, message,title=title)

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
        appointment.save()  # This will trigger the QR code generation

        notification_title = "Appointment Confirmed"
        notification_message = f"Your appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} has been confirmed."
        
        send_notification_to_patient(
            appointment.patient, 
            notification_message,
            title=notification_title
        )

        return JsonResponse({
            "message": "Appointment Confirmed successfully.",
            "qr_code": appointment.qr_code.url if appointment.qr_code else None,
            "qr_data": {  # Optionnel: renvoyer aussi les données en JSON
                "appointment_id": appointment.id,
                "doctor": f"{appointment.doctor.first_name} {appointment.doctor.last_name}",
                "patient": f"{appointment.patient.first_name} {appointment.patient.last_name}",
                "date": str(appointment.date),
                "time": str(appointment.time)
            }
        })
    return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)

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
def reschedule_appointment(request, appointment_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_date = data.get("new_date")
            new_time = data.get("new_time")

            if not new_date and not new_time:
                return JsonResponse({"error": "Provide at least a new date or time."}, status=400)

            appointment = get_object_or_404(Appointment, id=appointment_id)

            if new_date:
                appointment.date = new_date
            if new_time:
                appointment.time = new_time

            appointment.status = "Pending"  # Needs to be reconfirmed by the doctor
            appointment.save()

            notification_title = "Appointment rescheduling demand"
            message = (
                f"The appointment with {appointment.patient.first_name} "
                f"{appointment.patient.last_name} has been rescheduled to "
                f"{appointment.date} at {appointment.time}. Please review and confirm."
            )
            send_notification_to_doctor(appointment.doctor, message, notification_title)

            return JsonResponse({"message": "Appointment rescheduled successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)



def get_doctor_statistics(doctor_id):
    try:
        # Get the doctor object
        doctor = Doctor.objects.get(id=doctor_id)
        
        # Total appointments today
        total_appointments_today = Appointment.objects.filter(
            doctor=doctor, 
            date=date.today()
        ).count()

        # Upcoming appointment (next one)
        upcoming_appointment = Appointment.objects.filter(
            doctor=doctor,
            date__gt=date.today(),  # Only appointments scheduled for after today
        ).order_by('date', 'time').first()

        # Completed appointments
        completed_appointments = Appointment.objects.filter(
            doctor=doctor,
            status="Completed"
        ).count()

        # Number of patients attended (distinct patients)
        patients_attended = Appointment.objects.filter(
            doctor=doctor,
            status="Completed"
        ).values('patient').distinct().count()

        # Pending appointment requests
        pending_appointments = Appointment.objects.filter(
            doctor=doctor,
            status="Pending"
        ).count()

        # Return the statistics
        statistics = {
            "total_appointments_today": total_appointments_today,
            "upcoming_appointment": upcoming_appointment,
            "completed_appointments": completed_appointments,
            "patients_attended": patients_attended,
            "pending_appointments": pending_appointments
        }

        return statistics

    except Doctor.DoesNotExist:
        return {"error": "Doctor not found"}
    


class DoctorStatisticsView(APIView):
    def get(self, request, doctor_id):
        statistics = get_doctor_statistics(doctor_id)

        if "error" in statistics:
            return Response(statistics, status=status.HTTP_404_NOT_FOUND)

        if statistics['upcoming_appointment']:
            upcoming_appointment_data = AppointmentStatsSerializer(statistics['upcoming_appointment']).data
            statistics['upcoming_appointment'] = upcoming_appointment_data


        return Response(statistics, status=status.HTTP_200_OK)
    

def get_patient_statistics(patient_id):
    try:
        # Get the patient object
        patient = Patient.objects.get(id=patient_id)

        # Total appointments today
        total_appointments_today = Appointment.objects.filter(
            patient=patient, 
            date=date.today()
        ).count()

        now = datetime.now().time()

        upcoming_appointment = Appointment.objects.filter(
            patient=patient,
            date=date.today(),
            time__gt=now,
            status="Confirmed"
        ).order_by('date', 'time').first()

        # If no appointment left today, check future days
        if not upcoming_appointment:
            upcoming_appointment = Appointment.objects.filter(
                patient=patient,
                date__gt=date.today(),
                status="Confirmed"
            ).order_by('date', 'time').first()

        # Completed appointments
        completed_appointments = Appointment.objects.filter(
            patient=patient,
            status="Completed"
        ).count()

        consulted_doctors = Doctor.objects.filter(
            appointment__patient=patient,
            appointment__status="Completed"
        ).distinct()

        # Pending appointment requests
        pending_appointments = Appointment.objects.filter(
            patient=patient,
            status="Pending"
        ).count()

        # Return statistics
        statistics = {
            "total_appointments_today": total_appointments_today,
            "upcoming_appointment": upcoming_appointment,
            "completed_appointments": completed_appointments,
            "doctors_consulted": consulted_doctors,
            "pending_appointments": pending_appointments
        }

        return statistics

    except Patient.DoesNotExist:
        return {"error": "Patient not found"}


class PatientStatisticsView(APIView):
    def get(self, request, patient_id):
        statistics = get_patient_statistics(patient_id)

        if "error" in statistics:
            return Response(statistics, status=status.HTTP_404_NOT_FOUND)

        if statistics['upcoming_appointment']:
            statistics['upcoming_appointment'] = PatientAppointmentStatsSerializer(
                statistics['upcoming_appointment']
            ).data

        statistics['doctors_consulted'] = ConsultedDoctorSerializer(
            statistics['doctors_consulted'], many=True
        ).data

        return Response(statistics, status=status.HTTP_200_OK)