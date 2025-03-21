from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Doctor

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

