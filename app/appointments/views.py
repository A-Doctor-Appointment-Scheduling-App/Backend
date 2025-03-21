from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import AppointmentSerializer
from .models import Appointment

@api_view(['POST'])
def create_appointment(request):
    serializer = AppointmentSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        appointment = serializer.save()
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
