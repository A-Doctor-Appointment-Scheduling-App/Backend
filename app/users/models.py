from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Abstract User Model
class User(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)  # Add this field
    phone_number = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    registration_date = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email



class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
    
class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Doctor(User):
    SPECIALTY_CHOICES = [
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('General', 'General Practitioner'),
        ('Neurologist', 'Neurologist'),
        ('Orthopedic', 'Orthopedic Surgeon'),
    ]
    
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES)
    photo_url = models.URLField()
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    availability = models.ManyToManyField(TimeSlot, blank=True)
    
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)


    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} - {self.specialty}"
    

class Patient(User):
    address = models.TextField()
    date_of_birth = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"   