from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import DoctorRegistrationSerializer, PatientRegistrationSerializer, UserLoginSerializer
from .serializers import ClinicSerializer
from .models import Clinic
from django.shortcuts import render
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Doctor

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


def dashboard(request):
    # Fetch user-specific data here
    user = request.user
    context = {
        'user': user,
        # Add more context data as needed
    }
    return render(request, 'users/dashboard.html', context)

def doctor_list(request):
    doctors = Doctor.objects.all()
    data = [
        {
            "id": doctor.id,
            "first_name": doctor.first_name,
            "last_name": doctor.last_name,
            "specialty": doctor.specialty,
            "photo_url": doctor.photo_url,
            "clinic": doctor.clinic.name,  # Assuming Clinic model has a name field
        }
        for doctor in doctors
    ]
    return JsonResponse(data, safe=False)


def doctor_details(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    data = {
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "specialty": doctor.specialty,
        "photo_url": doctor.photo_url,
        "clinic": doctor.clinic.name,
        "availability": [str(slot) for slot in doctor.availability.all()],  # Assuming TimeSlot has a string representation
        "facebook_link": doctor.facebook_link,
        "instagram_link": doctor.instagram_link,
        "twitter_link": doctor.twitter_link,
        "linkedin_link": doctor.linkedin_link,
    }
    return JsonResponse(data)

def patient_list(request):
    patients = Patient.objects.all()
    data = [
        {
            "id": patient.id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "email": patient.email,
            "phone_number": patient.phone_number,
            "address": patient.address,
            "date_of_birth": patient.date_of_birth
        }
        for patient in patients
    ]
    return JsonResponse(data, safe=False)

def patient_details(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    data = {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "email": patient.email,
        "phone_number": patient.phone_number,
        "address": patient.address,
        "date_of_birth": patient.date_of_birth
    }
    return JsonResponse(data)

