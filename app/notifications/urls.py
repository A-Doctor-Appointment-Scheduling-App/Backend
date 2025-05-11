from django.urls import path
from .views import get_notifications, mark_notification_as_read

urlpatterns = [
      # URL to fetch notifications for a user (patient or doctor)
    path("<int:user_id>/<str:user_type>/", get_notifications, name="get_notifications"),

    # # URL to mark a notification as read
    path("read/<int:notification_id>/", mark_notification_as_read, name="mark_notification_as_read"),
  ]