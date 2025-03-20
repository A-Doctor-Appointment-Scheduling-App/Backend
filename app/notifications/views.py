from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from .models import Notification
from django.views.decorators.csrf import csrf_exempt

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