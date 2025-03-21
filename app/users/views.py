from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import DoctorRegistrationSerializer, PatientRegistrationSerializer, UserLoginSerializer
from .serializers import ClinicSerializer
from .models import Clinic
@api_view(['POST'])
def doctor_register_view(request):
    serializer = DoctorRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        doctor = serializer.save()
        return Response(DoctorRegistrationSerializer(doctor).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def patient_register_view(request):
    serializer = PatientRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        patient = serializer.save()
        return Response(PatientRegistrationSerializer(patient).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            role = 'doctor' if hasattr(user, 'doctor') else 'patient'
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_clinic(request):
    serializer = ClinicSerializer(data=request.data)
    if serializer.is_valid():
        clinic = serializer.save()
        return Response(ClinicSerializer(clinic).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)