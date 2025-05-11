# notification/views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

@csrf_exempt
def send_notification_to_patient(patient, message, title):
    # Créer la notification dans la base de données comme avant
    notification = Notification.objects.create(
        recipient_patient=patient,
        message=message,
        title=title
    )
    notification.save()
    
    # Envoyer la notification via WebSocket
    channel_layer = get_channel_layer()
    notification_data = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "created_at": notification.created_at.isoformat(),
    }
    
    async_to_sync(channel_layer.group_send)(
        f"notifications_{patient.id}_patient",
        {
            "type": "send_notification",
            "notification": notification_data 
        }
    )

@csrf_exempt
def send_notification_to_doctor(doctor, message, title):
    # Créer la notification dans la base de données comme avant
    notification = Notification.objects.create(
        recipient_doctor=doctor,
        message=message,
        title=title
    )
    notification.save()
    
    # Envoyer la notification via WebSocket
    channel_layer = get_channel_layer()
    notification_data = {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "created_at": notification.created_at.isoformat(),
    }
    
    # Modifier l'ordre pour correspondre au nouveau pattern
    async_to_sync(channel_layer.group_send)(
        f"notifications_{doctor.id}_doctor",
        {
            "type": "send_notification",
            "notification": notification_data
        }
    )

'''get notifications that are not read'''
@csrf_exempt
def get_notifications(request, user_id, user_type):
    if user_type == "patient":
        notifications = Notification.objects.filter(recipient_patient_id=user_id)
    elif user_type == "doctor":
        notifications = Notification.objects.filter(recipient_doctor_id=user_id)
    else:
        return JsonResponse({"error": "Invalid user type."}, status=400)

    data = [
        {
            "id": notif.id,
            "title": notif.title,
            "message": notif.message,
            "created_at": notif.created_at.isoformat()
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


# from django.shortcuts import render,get_object_or_404
# from django.http import JsonResponse
# from .models import Notification, FCMDevice
# from django.views.decorators.csrf import csrf_exempt
# from datetime import datetime, timedelta
# from appointments.models import Appointment
# from notifications.models import Notification
# from .fcm_service import send_push_notification
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# import json
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# # Create your views here.

# '''A function to create a notification'''
# @csrf_exempt
# def send_notification_to_patient(patient, message, title="Notification"):
#     # Créer la notification dans la base de données comme avant
#     notification = Notification.objects.create(
#         recipient_patient=patient,
#         message=message,
#         title=title
#     )
#     notification.save()

#     channel_layer = get_channel_layer()
#     notification_data = {
#         "id": notification.id,
#         "title": notification.title,
#         "message": notification.message,
#         "created_at": notification.created_at.isoformat(),
#     }
    
#     async_to_sync(channel_layer.group_send)(
#         f"notifications_patient_{patient.id}",
#         {
#             "type": "send_notification",
#             "notification": notification_data
#         }
#     )
    

# @csrf_exempt
# def send_notification_to_doctor(doctor, message, title="Notification"):
#     # Créer la notification dans la base de données comme avant
#     notification = Notification.objects.create(
#         recipient_doctor=doctor,
#         message=message,
#         title=title
#     )
#     notification.save()

#     channel_layer = get_channel_layer()
#     notification_data = {
#         "id": notification.id,
#         "title": notification.title,
#         "message": notification.message,
#         "created_at": notification.created_at.isoformat(),
#     }
    
#     async_to_sync(channel_layer.group_send)(
#         f"notifications_doctor_{doctor.id}",
#         {
#             "type": "send_notification",
#             "notification": notification_data
#         }
#     )
    
    
# '''get notifications that are not read'''
# @csrf_exempt
# def get_notifications(request, user_id, user_type):
#     if user_type == "patient":
#         notifications = Notification.objects.filter(recipient_patient_id=user_id, is_read=False)
#     elif user_type == "doctor":
#         notifications = Notification.objects.filter(recipient_doctor_id=user_id, is_read=False)
#     else:
#         return JsonResponse({"error": "Invalid user type."}, status=400)

#     data = [
#         {
#             "id": notif.id,
#             "message": notif.message,
#             "created_at": notif.created_at
#         }
#         for notif in notifications
#     ]

#     return JsonResponse({"notifications": data})

# # @csrf_exempt
# # def register_fcm_token(request):
# #     if request.method != 'POST':
# #         return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
# #     try:
# #         data = json.loads(request.body)
# #         user_id = data.get('user_id')
# #         user_type = data.get('user_type')
# #         token = data.get('token')
        
# #         if not all([user_id, user_type, token]):
# #             return JsonResponse({'error': 'Missing required fields'}, status=400)
        
# #         if user_type not in ['patient', 'doctor']:
# #             return JsonResponse({'error': 'Invalid user type'}, status=400)
        
# #         # Enregistrer ou mettre à jour le token
# #         device, created = FCMDevice.objects.update_or_create(
# #             user_id=user_id,
# #             user_type=user_type,
# #             registration_id=token,
# #             defaults={'active': True}
# #         )
        
# #         return JsonResponse({
# #             'success': True,
# #             'message': 'Device registered successfully'
# #         })
    
# #     except Exception as e:
# #         return JsonResponse({'error': str(e)}, status=500)

# # # 8. API pour marquer une notification comme lue (mise à jour de votre fonction existante)
# # @csrf_exempt
# # def mark_notification_as_read(request, notification_id):
# #     if request.method != 'POST':
# #         return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
# #     try:
# #         notification = Notification.objects.get(id=notification_id)
# #         notification.is_read = True
# #         notification.save()
# #         return JsonResponse({'message': 'Notification marked as read'})
# #     except Notification.DoesNotExist:
# #         return JsonResponse({'error': 'Notification not found'}, status=404)
# #     except Exception as e:
# #         return JsonResponse({'error': str(e)}, status=500)


# @csrf_exempt
# def mark_notification_as_read(request, notification_id):
#     notification = get_object_or_404(Notification, id=notification_id)
#     notification.is_read = True
#     notification.save()
#     return JsonResponse({"message": "Notification marked as read."})


# def send_appointment_reminders():
#     now = datetime.now()
#     reminder_time = now + timedelta(hours=24)  # 24 hours before the appointment

#     # Fetch appointments that are 24 hours away and are confirmed
#     appointments = Appointment.objects.filter(
#         date=reminder_time.date(),
#         time__lte=reminder_time.time(),
#         status="Confirmed"  # Only send reminders for confirmed appointments
#     )

#     for appointment in appointments:
#         # Check if a notification for this appointment already exists
#         existing_notification = Notification.objects.filter(
#             recipient_patient=appointment.patient,
#             message__contains=f"Reminder: You have an appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} on {appointment.date} at {appointment.time}."
#         ).exists()

#         # If no notification exists, create a new one
#         if not existing_notification:
#             message = f"Reminder: You have an appointment with Dr. {appointment.doctor.first_name} {appointment.doctor.last_name} on {appointment.date} at {appointment.time}."
#             Notification.objects.create(
#                 recipient_patient=appointment.patient,
#                 message=message
#             )