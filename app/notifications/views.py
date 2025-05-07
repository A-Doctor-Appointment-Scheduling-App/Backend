from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from .models import Notification
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from appointments.models import Appointment
from notifications.models import Notification
# Create your views here.

'''A function to create a notification'''
@csrf_exempt
def send_notification_to_patient(patient, message):
    notification = Notification.objects.create(
        recipient_patient=patient,
        message=message
    )
    notification.save()

@csrf_exempt
def send_notification_to_doctor(doctor, message):
    notification = Notification.objects.create(
        recipient_doctor=doctor,
        message=message
    )
    notification.save()

'''get notifications that are not read'''
@csrf_exempt
def get_notifications(request, user_id, user_type):
    if user_type == "patient":
        notifications = Notification.objects.filter(recipient_patient_id=user_id, is_read=False)
    elif user_type == "doctor":
        notifications = Notification.objects.filter(recipient_doctor_id=user_id, is_read=False)
    else:
        return JsonResponse({"error": "Invalid user type."}, status=400)

    data = [
        {
            "id": notif.id,
            "message": notif.message,
            "created_at": notif.created_at
        }
        for notif in notifications
    ]

    return JsonResponse({"notifications": data})


@csrf_exempt
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return JsonResponse({"message": "Notification marked as read."})


def send_appointment_reminders():
    now = datetime.now()
    reminder_time = now + timedelta(hours=24)  # 24 hours before the appointment

    # Fetch appointments that are 24 hours away and are confirmed
    appointments = Appointment.objects.filter(
        date=reminder_time.date(),
        time__lte=reminder_time.time(),
        status="Confirmed"  # Only send reminders for confirmed appointments
    )

    for appointment in appointments:
        # Check if a notification for this appointment already exists
        existing_notification = Notification.objects.filter(
            recipient_patient=appointment.patient,
            message__contains=f"Reminder: You have an appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} on {appointment.date} at {appointment.time}."
        ).exists()

        # If no notification exists, create a new one
        if not existing_notification:
            message = f"Reminder: You have an appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} on {appointment.date} at {appointment.time}."
            Notification.objects.create(
                recipient_patient=appointment.patient,
                message=message
            )