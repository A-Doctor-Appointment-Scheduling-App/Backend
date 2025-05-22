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
from .models import Doctor, TimeSlot
from time import time
from datetime import date
GOOGLE_TOKEN_INFO_URL = 'https://oauth2.googleapis.com/tokeninfo'
import requests
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
            "clinic": {
                "name": doctor.clinic.name,
                "address": doctor.clinic.address,
                "location": doctor.clinic.location,
            } if doctor.clinic else None
        }
        for doctor in doctors
    ]
    return JsonResponse(data, safe=False)


def doctor_details(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    timeslots = []
    for slot in doctor.availability.all():
        timeslots.append({
            "id": slot.id,
            "start_time": slot.start_time.strftime("%H:%M:%S"),
            "end_time": slot.end_time.strftime("%H:%M:%S"),
            "date": slot.date.strftime("%Y-%m-%d") if slot.date else None,
            "is_booked": slot.is_booked
        })


    data = {
        "id": doctor.id,
        "first_name": doctor.first_name,
        "last_name": doctor.last_name,
        "email": doctor.email,
        "phone_number": doctor.phone_number,
        "specialty": doctor.specialty,
        "photo_url": doctor.photo_url,
        "clinic": {
            "name": doctor.clinic.name,
            "address": doctor.clinic.address,
            "location": doctor.clinic.location,
        } if doctor.clinic else None,
        "facebook_link": doctor.facebook_link,
        "instagram_link": doctor.instagram_link,
        "twitter_link": doctor.twitter_link,
        "linkedin_link": doctor.linkedin_link,
        "timeslots": timeslots
    }
    return JsonResponse(data)


from .serializers import PatientSerializer
from .models import Patient

@api_view(['GET'])
def get_patient_details(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def google_login(request):
    token = request.data.get('id_token')
    if not token:
        return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Verify the token with Google
    resp = requests.get(GOOGLE_TOKEN_INFO_URL, params={'id_token': token})
    if resp.status_code != 200:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    data = resp.json()

    email = data.get('email')
    if not email:
        return Response({'error': 'Email not provided by Google'}, status=status.HTTP_400_BAD_REQUEST)

    first_name = data.get('given_name', '')
    last_name = data.get('family_name', '')

    try:
        user = Patient.objects.get(email=email)
    except Patient.DoesNotExist:
        # Création utilisateur (signup) en tant que Patient
        user = Patient.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=f"google_{email}",  # Dummy unique phone
            address="",  # Default empty address (you can prompt user to fill later)
            date_of_birth="2000-01-01",  # Default date, change as needed
            password=Patient.objects.make_random_password()
        )

    refresh = RefreshToken.for_user(user)
    role = 'patient'
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'role': role
    })
