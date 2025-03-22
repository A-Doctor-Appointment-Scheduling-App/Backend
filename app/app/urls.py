
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('prescriptions/', include('prescriptions.urls')),
    path('appointments/', include('appointments.urls')),

    path('accounts/', include('allauth.urls')),
     path('api/appointments/', include('appointments.urls')),
    path('api/notifications/', include('notifications.urls')),  


]

