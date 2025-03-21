from django.test import TestCase

import requests

# API endpoint URL
url = "http://localhost:8000/api/appointments/book/"

# JSON payload
payload = {
    "doctor_id": 1,
    "patient_id": 1,
    "date": "2023-10-20",
    "time": "14:00:00",
    "status": "Scheduled",
    "qr_code_data": "some_qr_code_data"
}

# Send the POST request
response = requests.post(url, json=payload)

# Print the response
print("Status Code:", response.status_code)
print("Response Body:", response.json())