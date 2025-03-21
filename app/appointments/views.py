from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Appointment

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

