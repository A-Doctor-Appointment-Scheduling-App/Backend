from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import PrescriptionSerializer
from .models import Prescription
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from .models import Prescription
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from io import BytesIO
from django.conf import settings
import os


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Appointment
from users.models import Patient,Doctor


@api_view(['POST'])
def create_prescription(request):
    serializer = PrescriptionSerializer(data=request.data)
    if serializer.is_valid():
        prescription = serializer.save()
        return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_prescription_by_id(request, pk):
    try:
        prescription = Prescription.objects.get(pk=pk)
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)
    except Prescription.DoesNotExist:
        return Response({'error': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)


class DoctorPrescriptionsView(APIView):
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            prescriptions = Prescription.objects.filter(appointment__doctor=doctor)
            serializer = PrescriptionSerializer(prescriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        

class PatientPrescriptionsView(APIView):
    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
            prescriptions = Prescription.objects.filter(appointment__patient=patient)
            serializer = PrescriptionSerializer(prescriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)


def generate_prescription_pdf(prescription_id):
    """
    Generates an elegant and beautifully styled PDF prescription document following Algerian standards.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO
    from django.conf import settings
    import os
    from datetime import datetime, timedelta

    # Retrieve the prescription
    prescription = Prescription.objects.get(pk=prescription_id)
    patient = prescription.appointment.patient
    doctor = prescription.appointment.doctor
    clinic = doctor.clinic

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Set up document with margins (A4 is more common in Algeria than US letter)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Try to register custom fonts if available
    try:
        # Elegant fonts - adjust paths to your actual font locations
        font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
        pdfmetrics.registerFont(TTFont('Montserrat', os.path.join(font_dir, 'Montserrat-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat-Bold', os.path.join(font_dir, 'Montserrat-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('Montserrat-Italic', os.path.join(font_dir, 'Montserrat-Italic.ttf')))
        main_font = 'Montserrat'
    except:
        # Fallback to standard fonts if custom fonts not available
        main_font = 'Helvetica'
    
    # Initialize story container for PDF elements
    story = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Define color scheme for elegant design - using standard reportlab colors to avoid issues
    primary_color = colors.navy
    secondary_color = colors.dodgerblue
    accent_color = colors.goldenrod
    
    # Header style
    title_style = ParagraphStyle(
        name='Title',
        fontName=f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,  # Center alignment
        spaceAfter=6,
        textColor=primary_color
    )
    
    # Doctor info style
    doctor_style = ParagraphStyle(
        name='DoctorInfo',
        fontName=main_font,
        fontSize=11,
        leading=14,
        alignment=0,  # Left alignment
        textColor=primary_color
    )
    
    # Prescription heading style
    prescription_heading_style = ParagraphStyle(
        name='PrescriptionHeading',
        fontName=f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold',
        fontSize=16,
        leading=18,
        alignment=1,  # Center alignment
        spaceAfter=8,
        textColor=primary_color
    )
    
    # Normal text style
    normal_style = ParagraphStyle(
        name='Normal',
        fontName=main_font,
        fontSize=10,
        leading=13,
        spaceAfter=4
    )
    
    # Medication name style
    medication_name_style = ParagraphStyle(
        name='MedicationName',
        fontName=f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=secondary_color
    )
    
    # Medication instructions style
    medication_instructions_style = ParagraphStyle(
        name='MedicationInstructions',
        fontName=main_font,
        fontSize=10,
        leading=13,
        leftIndent=0.6*cm
    )
    
    # Header section with clinic logo if available
    try:
        logo_path = os.path.join(settings.MEDIA_ROOT, 'clinic_logos', f'{clinic.id}_logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*cm, height=2*cm)
            logo.hAlign = 'LEFT'
            story.append(logo)
            story.append(Spacer(1, 0.5*cm))
    except:
        pass  # Skip logo if not available
    
    # Doctor and clinic information at the top with elegant styling
    # FIXED: Using standard color names instead of hexadecimal values
    doctor_info = [
        f"<b>Dr. {doctor.first_name} {doctor.last_name}</b>",
        f"<i>{doctor.specialty}</i>",
        f"<b>{clinic.name}</b>",
        f"{clinic.location}",
        f"Tél: {clinic.address}"  # Using address field for phone number
    ]
    
    for line in doctor_info:
        story.append(Paragraph(line, doctor_style))
    
    # Add elegant separator
    story.append(Spacer(1, 1*cm))
    
    # Create an elegant separator line
    separator = Table([['']], colWidths=[doc.width], rowHeights=[1])
    separator.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, 0), 1, secondary_color),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, accent_color),
    ]))
    story.append(separator)
    
    # "ORDONNANCE" heading (French is common in Algeria for medical terms)
    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("ORDONNANCE", prescription_heading_style))
    story.append(Spacer(1, 0.6*cm))
    
    # Create a table for patient information with elegant styling
    issue_date = prescription.issued_date
    if isinstance(issue_date, datetime):
        issue_date_str = issue_date.strftime("%d/%m/%Y")  # DD/MM/YYYY format common in Algeria
    else:
        issue_date_str = str(issue_date)
    
    # Get patient date of birth with fallback
    patient_dob = getattr(patient, 'date_of_birth', 'Non précisée')
    if isinstance(patient_dob, datetime):
        patient_dob_str = patient_dob.strftime("%d/%m/%Y")
    else:
        patient_dob_str = str(patient_dob)
    
    # Patient age calculation
    patient_age = "N/A"
    if isinstance(patient_dob, datetime):
        today = datetime.now()
        patient_age = today.year - patient_dob.year - ((today.month, today.day) < (patient_dob.month, patient_dob.day))
    
    # Patient information block with elegant styling
    patient_data = [
        ["Patient:", f"{patient.first_name} {patient.last_name}", "Date:", issue_date_str],
        ["Né(e) le:", patient_dob_str, "Age:", f"{patient_age} ans"],
        ["N° dossier:", str(patient.id), "", ""]
    ]
    
    patient_table = Table(patient_data, colWidths=[doc.width*0.15, doc.width*0.35, doc.width*0.15, doc.width*0.35])
    patient_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), primary_color),
        ('TEXTCOLOR', (2, 0), (2, -1), primary_color),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),  # Light blue background
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 1*cm))
    
    # Prescription symbol with elegant styling
    # FIXED: Using style-based coloring instead of inline HTML
    rx_symbol_style = ParagraphStyle(
        name='RxSymbol',
        fontName=f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=accent_color
    )
    story.append(Paragraph("℞", rx_symbol_style))
    story.append(Spacer(1, 0.3*cm))
    
    # Medications with elegant styling
    for i, medication in enumerate(prescription.medications.all(), 1):
        # Create a KeepTogether group for each medication to prevent splitting across pages
        medication_group = []
        
        # Medication name and dosage
        medication_group.append(Paragraph(
            f"{i}. <b>{medication.name}</b> - {medication.dosage}", 
            medication_name_style
        ))
        
        # Dosage instructions with indent
        medication_group.append(Paragraph(
            f"{medication.frequency} - {medication.instructions}", 
            medication_instructions_style
        ))
        
        medication_group.append(Spacer(1, 0.5*cm))
        story.append(KeepTogether(medication_group))
    
    # If no medications exist
    if not prescription.medications.exists():
        story.append(Paragraph("Aucun médicament prescrit", normal_style))
        story.append(Spacer(1, 0.5*cm))
    
    # Add an elegant separator before signature
    story.append(Spacer(1, 0.5*cm))
    story.append(separator)
    story.append(Spacer(1, 0.8*cm))
    
    # Date and doctor signature with elegant styling
    city = getattr(clinic, 'city', 'Alger')
    
    signature_data = [
        [f"Fait à {city}, le {issue_date_str}", ""],
        ["", "Signature et cachet du médecin"],
        ["", ""],
        ["", ""],
        ["", ""],
        ["", f"Dr. {doctor.first_name} {doctor.last_name}"]
    ]
    
    # Try to add doctor signature image if available
    try:
        signature_path = os.path.join(settings.MEDIA_ROOT, 'signatures', f'{doctor.id}_signature.png')
        if os.path.exists(signature_path):
            signature = Image(signature_path, width=3*cm, height=1.5*cm)
            signature.hAlign = 'CENTER'
            signature_data[3][1] = signature
    except:
        pass  # Skip signature image if not available
    
    signature_table = Table(signature_data, colWidths=[doc.width/2.0, doc.width/2.0])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('VALIGN', (1, 2), (1, 4), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (0, 0), primary_color),
        ('TEXTCOLOR', (1, 1), (1, 1), primary_color),
        ('FONTNAME', (1, 1), (1, 1), f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold'),
        ('FONTNAME', (1, -1), (1, -1), f'{main_font}-Bold' if main_font == 'Montserrat' else 'Helvetica-Bold'),
    ]))
    
    story.append(signature_table)
    
    # Add footer with prescription validity in an elegant box
    story.append(Spacer(1, 1.5*cm))
    
    footer_text = "Cette ordonnance est valable pour une durée d'un mois à compter de sa date d'émission."
    
    footer_style = ParagraphStyle(
        name='Footer',
        fontName=main_font,
        fontSize=8,
        leading=10,
        alignment=1,  # Center alignment
        textColor=primary_color
    )
    
    footer_table = Table([[Paragraph(footer_text, footer_style)]], colWidths=[doc.width])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightcyan),  # Very light background
        ('BOX', (0, 0), (-1, -1), 0.5, secondary_color),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(footer_table)
    
    # Build the PDF
    doc.build(story)
    
    # File position to the beginning of the buffer
    buffer.seek(0)
    return buffer

@api_view(['GET'])
def download_prescription_pdf(request, pk):
    try:
        # Generate the PDF
        buffer = generate_prescription_pdf(pk)

        # Return the PDF as a file response
        return FileResponse(buffer, as_attachment=True, filename=f'prescription_{pk}.pdf')
    except Prescription.DoesNotExist:
        return Response({'error': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def get_prescription_by_appointment_id(request, appointment_id):
    try:
        prescription = Prescription.objects.get(appointment_id=appointment_id)
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)
    except Prescription.DoesNotExist:
        return Response({'error': 'Prescription not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_prescriptions_by_doctor_and_patient(request, doctor_id, patient_id):
    prescriptions = Prescription.objects.filter(appointment__doctor_id=doctor_id, appointment__patient_id=patient_id)
    if not prescriptions.exists():
        return Response({'error': 'No prescriptions found for the given doctor and patient'}, status=status.HTTP_404_NOT_FOUND)
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)