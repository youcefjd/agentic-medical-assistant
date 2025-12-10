"""PDF generation for patient visit summaries."""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
import config
from database import Visit, Patient


class PDFGenerator:
    """Generates PDF documents for patient visits."""
    
    def __init__(self):
        self.output_dir = config.PDF_OUTPUT_DIR
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='MedicalTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='MedicalHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c5f8d'),
            spaceAfter=8,
            spaceBefore=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='MedicalBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY
        ))
    
    def generate_visit_summary(self, visit: Visit, patient: Patient) -> str:
        """
        Generate a PDF summary for a patient visit.
        
        Returns:
            Path to generated PDF file
        """
        # Create filename
        timestamp = visit.visit_date.strftime("%Y%m%d_%H%M%S")
        filename = f"{patient.patient_id}_visit_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Header
        story.append(Paragraph("RÉSUMÉ DE CONSULTATION MÉDICALE", self.styles['MedicalTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Patient Information
        patient_info = [
            ["ID Patient:", patient.patient_id],
            ["Nom:", f"{patient.first_name} {patient.last_name}"],
            ["Date de Naissance:", patient.date_of_birth.strftime("%Y-%m-%d") if patient.date_of_birth else "N/A"],
            ["Date de Consultation:", visit.visit_date.strftime("%Y-%m-%d %H:%M")],
            ["Type de Consultation:", visit.visit_type or "Consultation"],
        ]
        
        patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Chief Complaint
        if visit.chief_complaint:
            story.append(Paragraph("<b>Motif de Consultation:</b>", self.styles['MedicalHeading']))
            story.append(Paragraph(visit.chief_complaint, self.styles['MedicalBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Topics Discussed
        if visit.topics_discussed:
            story.append(Paragraph("<b>Sujets Discutés:</b>", self.styles['MedicalHeading']))
            topics_text = " • ".join(visit.topics_discussed)
            story.append(Paragraph(topics_text, self.styles['MedicalBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Summary
        if visit.cleaned_summary or visit.summary:
            story.append(Paragraph("<b>Résumé de la Consultation:</b>", self.styles['MedicalHeading']))
            summary_text = visit.cleaned_summary or visit.summary
            story.append(Paragraph(summary_text, self.styles['MedicalBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Diagnosis
        if visit.diagnosis:
            story.append(Paragraph("<b>Diagnostic:</b>", self.styles['MedicalHeading']))
            story.append(Paragraph(visit.diagnosis, self.styles['MedicalBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Recommendations
        if visit.recommendations:
            story.append(Paragraph("<b>Recommandations:</b>", self.styles['MedicalHeading']))
            story.append(Paragraph(visit.recommendations, self.styles['MedicalBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # Additional Notes
        if visit.notes:
            story.append(Paragraph("<b>Notes Supplémentaires:</b>", self.styles['MedicalHeading']))
            story.append(Paragraph(visit.notes, self.styles['MedicalBody']))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = f"Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )))
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_patient_history(self, patient: Patient, visits: list, medications: list = None, test_results: list = None) -> str:
        """Generate a comprehensive patient history PDF with all medical records."""
        from database import db_manager
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{patient.patient_id}_complete_history_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph("HISTORIQUE MÉDICAL COMPLET DU PATIENT", self.styles['MedicalTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Patient Info
        patient_info = [
            ["Nom du Patient:", f"{patient.first_name} {patient.last_name}"],
            ["ID Patient:", patient.patient_id],
            ["Date de Naissance:", patient.date_of_birth.strftime("%Y-%m-%d") if patient.date_of_birth else "N/A"],
            ["Sexe:", patient.gender or "N/A"],
            ["Téléphone:", patient.phone or "N/A"],
            ["Email:", patient.email or "N/A"],
        ]
        
        patient_table = Table(patient_info, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Medications
        if medications:
            story.append(Paragraph("MÉDICAMENTS ACTUELS", self.styles['MedicalHeading']))
            for med in medications:
                med_text = f"<b>{med.medication_name}</b> - {med.dosage} - {med.frequency}"
                if med.start_date:
                    med_text += f" (Started: {med.start_date.strftime('%Y-%m-%d')})"
                story.append(Paragraph(med_text, self.styles['MedicalBody']))
            story.append(Spacer(1, 0.2*inch))
            story.append(PageBreak())
        
        # Test Results
        if test_results:
            story.append(Paragraph("RÉSULTATS DE TESTS & IMAGERIE MÉDICALE", self.styles['MedicalHeading']))
            
            # Group by type
            by_type = {}
            for test in test_results:
                test_type = test.test_type or "other"
                if test_type not in by_type:
                    by_type[test_type] = []
                by_type[test_type].append(test)
            
            for test_type, tests in by_type.items():
                type_label = test_type.replace("_", " ").title()
                story.append(Paragraph(f"<b>{type_label}</b>", self.styles['MedicalHeading']))
                
                for test in sorted(tests, key=lambda x: x.test_date, reverse=True):
                    story.append(Paragraph(f"{test.test_name} - {test.test_date.strftime('%Y-%m-%d')}", 
                                         ParagraphStyle(name='TestName', parent=self.styles['Normal'], fontSize=12, textColor=colors.HexColor('#2c5f8d'))))
                    
                    if test.results_data and isinstance(test.results_data, dict):
                        if "values" in test.results_data or "results" in test.results_data:
                            values = test.results_data.get("values") or test.results_data.get("results", {})
                            for param, value in list(values.items())[:15]:
                                story.append(Paragraph(f"  • {param}: {value}", self.styles['MedicalBody']))
                        elif "modality" in test.results_data:
                            story.append(Paragraph(f"  Modality: {test.results_data.get('modality', 'N/A')}", self.styles['MedicalBody']))
                            story.append(Paragraph(f"  Study: {test.results_data.get('study_description', 'N/A')}", self.styles['MedicalBody']))
                    
                    if test.interpretation:
                        story.append(Paragraph(f"<b>Interpretation:</b> {test.interpretation}", self.styles['MedicalBody']))
                    
                    story.append(Spacer(1, 0.1*inch))
                
                story.append(Spacer(1, 0.2*inch))
            
            story.append(PageBreak())
        
        # Visit History
        story.append(Paragraph("HISTORIQUE DES CONSULTATIONS", self.styles['MedicalHeading']))
        for visit in sorted(visits, key=lambda v: v.visit_date, reverse=True):
            story.append(Paragraph(f"Consultation: {visit.visit_date.strftime('%Y-%m-%d %H:%M')} - {visit.visit_type}", 
                                 self.styles['MedicalHeading']))
            
            if visit.chief_complaint:
                story.append(Paragraph(f"<b>Motif de Consultation:</b> {visit.chief_complaint}", self.styles['MedicalBody']))
            
            if visit.cleaned_summary or visit.summary:
                story.append(Paragraph(f"<b>Résumé:</b>", self.styles['MedicalBody']))
                story.append(Paragraph(visit.cleaned_summary or visit.summary, self.styles['MedicalBody']))
            
            if visit.diagnosis:
                story.append(Paragraph(f"<b>Diagnostic:</b> {visit.diagnosis}", self.styles['MedicalBody']))
            
            if visit.recommendations:
                story.append(Paragraph(f"<b>Recommandations:</b> {visit.recommendations}", self.styles['MedicalBody']))
            
            story.append(Spacer(1, 0.2*inch))
            story.append(PageBreak())
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = f"Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )))
        
        doc.build(story)
        return str(filepath)

