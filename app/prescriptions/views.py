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

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO
from .models import Prescription

def generate_prescription_pdf(prescription_id):
    """
    Generates a professionally styled PDF prescription document.
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from io import BytesIO
    from django.conf import settings
    import os
    from datetime import datetime, timedelta

    # Retrieve the prescription
    prescription = Prescription.objects.get(pk=prescription_id)
    patient = prescription.appointment.patient
    doctor = prescription.appointment.doctor

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Set up document with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Initialize story container for PDF elements
    story = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Modify existing Title style instead of adding a new one
    title_style = styles['Title']
    title_style.fontSize = 16
    title_style.leading = 20
    title_style.alignment = 1  # Center alignment
    title_style.spaceAfter = 12
    title_style.textColor = colors.HexColor('#2c3e50')
    
    # Add other custom styles
    styles.add(ParagraphStyle(
        name='PrescriptionHeading',
        fontSize=14,
        leading=16,
        spaceAfter=10,
        textColor=colors.HexColor('#2980b9')
    ))
    styles.add(ParagraphStyle(
        name='PrescriptionSubHeading',
        fontSize=12,
        leading=14,
        spaceAfter=8,
        textColor=colors.HexColor('#3498db')
    ))
    
    # Also modify Normal style for consistency
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 12
    normal_style.spaceAfter = 6
    
    # Try to add a logo if available
    try:
        logo_path = os.path.join(settings.STATIC_ROOT, 'images/hospital_logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=2*inch, height=1*inch)
            story.append(logo)
    except:
        # Continue without logo if there's an issue
        pass
    
    # Add clinic/hospital header
    clinic_name = getattr(settings, 'CLINIC_NAME', 'Medical Clinic')
    story.append(Paragraph(clinic_name, styles['Title']))
    
    clinic_address = getattr(settings, 'CLINIC_ADDRESS', '123 Healthcare Ave, Medical City')
    clinic_contact = getattr(settings, 'CLINIC_CONTACT', 'Phone: (555) 123-4567')
    
    story.append(Paragraph(clinic_address, styles['Normal']))
    story.append(Paragraph(clinic_contact, styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Add a horizontal line
    story.append(Paragraph("<hr width='100%'/>", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Prescription title and number
    story.append(Paragraph(f"PRESCRIPTION #{prescription.id}", styles['PrescriptionHeading']))
    story.append(Spacer(1, 0.5*cm))
    
    # Create a two-column table for patient and doctor info
    data = [
        ["PATIENT INFORMATION", "PRESCRIBING DOCTOR"],
        [f"Name: {patient.first_name} {patient.last_name}", f"Name: Dr. {doctor.first_name} {doctor.last_name}"],
        [f"ID: {patient.id}", f"License #: {getattr(doctor, 'license_number', 'N/A')}"],
        [f"DOB: {getattr(patient, 'date_of_birth', 'N/A')}", f"Specialty: {getattr(doctor, 'specialty', 'N/A')}"]
    ]
    
    info_table = Table(data, colWidths=[doc.width/2.0-12, doc.width/2.0-12])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#3498db')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Prescription date and other details
    issue_date = prescription.issued_date
    if isinstance(issue_date, datetime):
        issue_date_str = issue_date.strftime("%B %d, %Y")
        valid_until = getattr(prescription, 'valid_until', 
                          (issue_date + timedelta(days=30)).strftime("%B %d, %Y"))
    else:
        # Handle case where issue_date might be a string
        issue_date_str = str(issue_date)
        valid_until = getattr(prescription, 'valid_until', 'N/A')
        
    prescription_data = [
        ["Date Issued:", issue_date_str],
        ["Valid Until:", valid_until],
        ["Prescription ID:", prescription.id]
    ]
    
    prescription_table = Table(prescription_data, colWidths=[doc.width/4.0, doc.width*3/4.0-24])
    prescription_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f2f2f2')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(prescription_table)
    story.append(Spacer(1, 1*cm))
    
    # Medications section
    story.append(Paragraph("PRESCRIBED MEDICATIONS", styles['PrescriptionHeading']))
    story.append(Spacer(1, 0.3*cm))
    
    # Create medication table headers
    medication_data = [["Medication", "Dosage", "Frequency", "Duration", "Instructions"]]
    
    # Add medication rows
    for medication in prescription.medications.all():
        medication_data.append([
            medication.name,
            medication.dosage,
            medication.frequency,
            getattr(medication, 'duration', 'As needed'),
            medication.instructions
        ])
    
    # If no medications exist, add a placeholder row
    if len(medication_data) == 1:
        medication_data.append(["No medications prescribed", "", "", "", ""])
    
    # Create the medication table
    col_widths = [doc.width*0.20, doc.width*0.15, doc.width*0.15, doc.width*0.15, doc.width*0.35-24]
    medication_table = Table(medication_data, colWidths=col_widths)
    
    # Style the medication table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (4, 1), (4, -1), True),
    ])
    
    # Add zebra striping for better readability
    for i in range(1, len(medication_data)):
        if i % 2 == 1:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f2f2f2'))
    
    medication_table.setStyle(table_style)
    story.append(medication_table)
    
    # Add notes section
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("NOTES AND SPECIAL INSTRUCTIONS:", styles['PrescriptionSubHeading']))
    
    notes = getattr(prescription, 'notes', '')
    if not notes:
        notes = "No special instructions."
    
    story.append(Paragraph(notes, styles['Normal']))
    
    # Add signature section
    story.append(Spacer(1, 2*cm))
    
    signature_data = [
        ["", ""],
        ["______________________________", "______________________________"],
        ["Doctor's Signature", "Date"]
    ]
    
    signature_table = Table(signature_data, colWidths=[doc.width/2.0-12, doc.width/2.0-12])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 1), (0, 1), 'CENTER'),
        ('ALIGN', (1, 1), (1, 1), 'CENTER'),
        ('ALIGN', (0, 2), (0, 2), 'CENTER'),
        ('ALIGN', (1, 2), (1, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Oblique'),
        ('TEXTCOLOR', (0, 2), (1, 2), colors.grey),
    ]))
    
    story.append(signature_table)
    
    # Add footer with disclaimer
    story.append(Spacer(1, 2*cm))
    footer_text = "This prescription is only valid if signed by the prescribing doctor. " \
                 "Please consult your pharmacist or doctor if you have any questions regarding this prescription."
    
    story.append(Paragraph(footer_text, ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1  # Center alignment
    )))
    
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
def get_prescriptions_by_doctor_and_patient(request, doctor_id, patient_id):
    prescriptions = Prescription.objects.filter(appointment__doctor_id=doctor_id, appointment__patient_id=patient_id)
    if not prescriptions.exists():
        return Response({'error': 'No prescriptions found for the given doctor and patient'}, status=status.HTTP_404_NOT_FOUND)
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)