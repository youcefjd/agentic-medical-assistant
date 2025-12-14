#!/usr/bin/env python3
"""Comprehensive test suite for the Agentic Medical Assistant application."""

import sys
from pathlib import Path
import traceback
from datetime import datetime, timedelta
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import db_manager, Patient, Visit, Medication, TestResult
from services import Transcriber, MedicalSummarizer, PatternAnalyzer, PDFGenerator, VectorStore, MedicalChat
from integrations import DICOMParser, LabResultsParser
import config

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log_test(name, status, message=""):
    """Log test result."""
    result = {"name": name, "status": status, "message": message}
    if status == "PASS":
        test_results["passed"].append(result)
        print(f"✅ {name}")
    elif status == "FAIL":
        test_results["failed"].append(result)
        print(f"❌ {name}: {message}")
    elif status == "WARN":
        test_results["warnings"].append(result)
        print(f"⚠️  {name}: {message}")
    else:
        print(f"ℹ️  {name}: {message}")

def test_database_connection():
    """Test database connection and basic operations."""
    try:
        # Test connection
        patient = db_manager.get_patient(patient_id="TEST_999")
        log_test("Database Connection", "PASS")
        return True
    except Exception as e:
        log_test("Database Connection", "FAIL", str(e))
        return False

def test_patient_creation():
    """Test patient creation."""
    try:
        patient_data = {
            "patient_id": f"TEST_{int(datetime.now().timestamp())}",
            "first_name": "Test",
            "last_name": "Patient",
            "date_of_birth": datetime(1980, 1, 1),
            "gender": "M",
            "phone": "1234567890",
            "email": "test@example.com"
        }
        patient = db_manager.create_patient(patient_data)
        
        if patient and patient.patient_id == patient_data["patient_id"]:
            log_test("Patient Creation", "PASS", f"Created patient {patient.patient_id}")
            return patient
        else:
            log_test("Patient Creation", "FAIL", "Patient not created correctly")
            return None
    except Exception as e:
        log_test("Patient Creation", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_services_initialization():
    """Test that all services can be initialized."""
    try:
        vector_store = VectorStore()
        transcriber = Transcriber()
        summarizer = MedicalSummarizer(vector_store=vector_store)
        pattern_analyzer = PatternAnalyzer(vector_store=vector_store)
        pdf_generator = PDFGenerator()
        medical_chat = MedicalChat(vector_store=vector_store)
        
        services = {
            "vector_store": vector_store,
            "transcriber": transcriber,
            "summarizer": summarizer,
            "pattern_analyzer": pattern_analyzer,
            "pdf_generator": pdf_generator,
            "medical_chat": medical_chat
        }
        
        log_test("Services Initialization", "PASS")
        return services
    except Exception as e:
        log_test("Services Initialization", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_transcription(services, audio_file_path=None):
    """Test audio transcription."""
    try:
        if not audio_file_path:
            # Create a simple test audio file path (would need actual file for real test)
            log_test("Transcription", "WARN", "No audio file provided for testing")
            return None
        
        transcriber = services["transcriber"]
        result = transcriber.transcribe(audio_file_path)
        
        if result and "text" in result:
            log_test("Transcription", "PASS", f"Transcribed {len(result['text'])} characters")
            return result
        else:
            log_test("Transcription", "FAIL", "Transcription failed")
            return None
    except Exception as e:
        log_test("Transcription", "FAIL", str(e))
        return None

def test_visit_creation(services, patient):
    """Test visit creation with summary."""
    try:
        # Create a test visit with mock transcription
        visit_data = {
            "patient_id": patient.id,
            "visit_date": datetime.now(),
            "visit_type": "Consultation",
            "transcription": "Patient présente des maux de tête depuis une semaine. Diagnostic: migraines. Recommandations: prendre de l'ibuprofène.",
            "summary": "Patient avec maux de tête, diagnostic de migraines",
            "cleaned_summary": "**Résumé Médical**\n\nLe patient présente des maux de tête depuis une semaine. Diagnostic: migraines. Recommandations: prendre de l'ibuprofène.",
            "topics_discussed": ["symptoms", "diagnosis", "medication"],
            "chief_complaint": "Maux de tête",
            "diagnosis": "Migraines",
            "recommendations": "Prendre de l'ibuprofène (400mg, 3 fois par jour) pendant une semaine",
            "duration_minutes": 15.0
        }
        
        visit = db_manager.create_visit(visit_data)
        
        if visit and visit.id:
            # Add to vector store
            vector_store = services["vector_store"]
            vector_store.add_conversation(
                visit_id=visit.id,
                patient_id=patient.id,
                transcription=visit_data["transcription"],
                summary=visit_data.get("summary", visit_data.get("cleaned_summary", ""))
            )
            vector_store.add_medical_note(
                note_id=f"visit_{visit.id}_note",
                patient_id=patient.id,
                note_text=f"Diagnostic: {visit_data['diagnosis']}. Recommandations: {visit_data['recommendations']}",
                note_type="diagnosis_recommendation"
            )
            
            log_test("Visit Creation", "PASS", f"Created visit {visit.id}")
            return visit
        else:
            log_test("Visit Creation", "FAIL", "Visit not created")
            return None
    except Exception as e:
        log_test("Visit Creation", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_medication_creation(patient):
    """Test medication creation."""
    try:
        med_data = {
            "patient_id": patient.id,
            "medication_name": "Ibuprofène",
            "dosage": "400mg",
            "frequency": "3 fois par jour",
            "start_date": datetime.now(),
            "is_active": True
        }
        
        medication = db_manager.add_medication(med_data)
        
        if medication and medication.id:
            log_test("Medication Creation", "PASS", f"Created medication {medication.medication_name}")
            return medication
        else:
            log_test("Medication Creation", "FAIL", "Medication not created")
            return None
    except Exception as e:
        log_test("Medication Creation", "FAIL", str(e))
        return None

def test_test_results_upload(services, patient):
    """Test test results upload (lab and imaging)."""
    try:
        # Test lab results
        lab_data = {
            "patient_id": patient.id,
            "test_type": "blood_test",
            "test_name": "Hémogramme complet",
            "test_date": datetime.now(),
            "results_data": {
                "values": {
                    "Hémoglobine": "14.5",
                    "Hématocrite": "42.3",
                    "Leucocytes": "7.2"
                },
                "reference_ranges": {
                    "Hémoglobine": {"unit": "g/dL", "min": 12.0, "max": 16.0},
                    "Hématocrite": {"unit": "%", "min": 36.0, "max": 48.0}
                }
            },
            "interpretation": "Résultats normaux",
            "notes": "Test de routine"
        }
        
        lab_test = db_manager.add_test_result(lab_data)
        
        if not lab_test or not lab_test.id:
            log_test("Test Results Upload (Lab)", "FAIL", "Lab test not created")
            return None
        
        # Test imaging (mock DICOM data)
        imaging_data = {
            "patient_id": patient.id,
            "test_type": "mri",
            "test_name": "IRM Cérébrale",
            "test_date": datetime.now(),
            "results_data": {
                "modality": "MR",
                "study_description": "IRM du cerveau",
                "manufacturer": "Siemens",
                "image_dimensions": {"rows": 512, "columns": 512}
            },
            "interpretation": "Pas d'anomalie détectée",
            "notes": "IRM de routine"
        }
        
        imaging_test = db_manager.add_test_result(imaging_data)
        
        if imaging_test and imaging_test.id:
            log_test("Test Results Upload", "PASS", "Lab and imaging tests created")
            return [lab_test, imaging_test]
        else:
            log_test("Test Results Upload", "FAIL", "Imaging test not created")
            return None
    except Exception as e:
        log_test("Test Results Upload", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_medical_chat(services, patient):
    """Test medical chat functionality."""
    try:
        medical_chat = services["medical_chat"]
        
        # Test questions
        test_questions = [
            "Quels sont les médicaments actifs?",
            "Résumez l'évolution de la pathologie",
            "Quels sont les tests récents?",
            "Y a-t-il eu des changements de médicaments?",
            "Quel était le dernier diagnostic?"
        ]
        
        results = []
        for question in test_questions:
            try:
                response = medical_chat.chat(
                    patient_id=patient.id,
                    user_message=question,
                    use_vector_search=True
                )
                
                if response.get("error"):
                    log_test(f"Medical Chat: '{question[:30]}...'", "FAIL", response.get("response", "Unknown error"))
                    results.append(False)
                elif not response.get("response") or len(response.get("response", "")) < 10:
                    log_test(f"Medical Chat: '{question[:30]}...'", "WARN", "Response too short or empty")
                    results.append(False)
                else:
                    log_test(f"Medical Chat: '{question[:30]}...'", "PASS", f"Got response ({len(response.get('response', ''))} chars)")
                    results.append(True)
            except Exception as e:
                log_test(f"Medical Chat: '{question[:30]}...'", "FAIL", str(e))
                results.append(False)
        
        if all(results):
            log_test("Medical Chat (All Questions)", "PASS", f"{sum(results)}/{len(results)} questions answered")
        elif any(results):
            log_test("Medical Chat (All Questions)", "WARN", f"Only {sum(results)}/{len(results)} questions answered")
        else:
            log_test("Medical Chat (All Questions)", "FAIL", "No questions answered")
        
        return results
    except Exception as e:
        log_test("Medical Chat", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_semantic_search(services, patient):
    """Test semantic search functionality."""
    try:
        vector_store = services["vector_store"]
        
        # Test searches
        search_queries = [
            "maux de tête",
            "migraines",
            "médicaments",
            "diagnostic"
        ]
        
        results = []
        for query in search_queries:
            try:
                search_results = vector_store.search_all(
                    query=query,
                    patient_id=patient.id,
                    n_results=3
                )
                
                if search_results and (search_results.get("conversations") or search_results.get("medical_notes")):
                    log_test(f"Semantic Search: '{query}'", "PASS", "Found results")
                    results.append(True)
                else:
                    log_test(f"Semantic Search: '{query}'", "WARN", "No results found")
                    results.append(False)
            except Exception as e:
                log_test(f"Semantic Search: '{query}'", "FAIL", str(e))
                results.append(False)
        
        if all(results):
            log_test("Semantic Search (All Queries)", "PASS", f"{sum(results)}/{len(results)} queries successful")
        elif any(results):
            log_test("Semantic Search (All Queries)", "WARN", f"Only {sum(results)}/{len(results)} queries successful")
        else:
            log_test("Semantic Search (All Queries)", "FAIL", "No queries successful")
        
        return results
    except Exception as e:
        log_test("Semantic Search", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_patient_overview(services, patient):
    """Test patient overview generation."""
    try:
        summarizer = services["summarizer"]
        
        # Get patient data
        visits = db_manager.get_patient_visits(patient.id)
        medications = db_manager.get_patient_medications(patient.id)
        test_results = db_manager.get_patient_test_results(patient.id)
        
        # Format test results
        test_results_data = []
        for test in test_results:
            test_info = {
                "type": test.test_type,
                "name": test.test_name,
                "date": test.test_date.strftime("%Y-%m-%d"),
                "interpretation": test.interpretation
            }
            test_results_data.append(test_info)
        
        overview = summarizer.generate_patient_overview(
            patient_name=f"{patient.first_name} {patient.last_name}",
            visits=visits,
            medications=medications,
            test_results=test_results_data
        )
        
        # Check for refusal messages
        refusal_phrases = [
            "je suis désolé",
            "je ne peux pas",
            "je ne peux pas répondre",
            "i'm sorry",
            "i cannot",
            "i cannot respond"
        ]
        
        overview_lower = overview.lower()
        has_refusal = any(phrase in overview_lower for phrase in refusal_phrases)
        
        if has_refusal:
            log_test("Patient Overview", "WARN", "LLM refused or apologized (may need prompt adjustment)")
        elif not overview or len(overview) < 50:
            log_test("Patient Overview", "FAIL", "Overview too short or empty")
        else:
            log_test("Patient Overview", "PASS", f"Generated overview ({len(overview)} chars)")
        
        return overview
    except Exception as e:
        log_test("Patient Overview", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_pdf_generation(services, patient):
    """Test PDF generation."""
    try:
        pdf_generator = services["pdf_generator"]
        
        # Get patient data
        visits = db_manager.get_patient_visits(patient.id)
        medications = db_manager.get_patient_medications(patient.id)
        test_results = db_manager.get_patient_test_results(patient.id)
        
        if not visits:
            log_test("PDF Generation", "WARN", "No visits to generate PDF for")
            return None
        
        # Test visit summary PDF
        visit = visits[0]
        pdf_path = pdf_generator.generate_visit_summary(visit, patient)
        
        if pdf_path and Path(pdf_path).exists():
            log_test("PDF Generation (Visit)", "PASS", f"Generated {Path(pdf_path).name}")
        else:
            log_test("PDF Generation (Visit)", "FAIL", "PDF not generated")
            return None
        
        # Test patient history PDF
        history_pdf_path = pdf_generator.generate_patient_history(
            patient=patient,
            visits=visits,
            medications=medications,
            test_results=test_results
        )
        
        if history_pdf_path and Path(history_pdf_path).exists():
            log_test("PDF Generation (History)", "PASS", f"Generated {Path(history_pdf_path).name}")
            return [pdf_path, history_pdf_path]
        else:
            log_test("PDF Generation (History)", "FAIL", "History PDF not generated")
            return None
    except Exception as e:
        log_test("PDF Generation", "FAIL", str(e))
        traceback.print_exc()
        return None

def test_pattern_analysis(services, patient):
    """Test pattern analysis."""
    try:
        pattern_analyzer = services["pattern_analyzer"]
        
        # Get patient data
        visits = db_manager.get_patient_visits(patient.id)
        medications = db_manager.get_patient_medications(patient.id)
        
        if len(visits) < 2:
            log_test("Pattern Analysis", "WARN", "Need at least 2 visits for pattern analysis")
            return None
        
        analysis = pattern_analyzer.analyze_patient_evolution(
            patient_id=patient.id,
            visits=visits,
            medications=medications
        )
        
        if analysis and len(analysis) > 50:
            log_test("Pattern Analysis", "PASS", f"Generated analysis ({len(analysis)} chars)")
            return analysis
        else:
            log_test("Pattern Analysis", "WARN", "Analysis too short or empty")
            return None
    except Exception as e:
        log_test("Pattern Analysis", "FAIL", str(e))
        traceback.print_exc()
        return None

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 COMPREHENSIVE TEST SUITE - Agentic Medical Assistant")
    print("=" * 60)
    print()
    
    # Initialize
    if not test_database_connection():
        print("\n❌ Database connection failed. Cannot continue tests.")
        return
    
    # Initialize services
    services = test_services_initialization()
    if not services:
        print("\n❌ Services initialization failed. Cannot continue tests.")
        return
    
    # Create test patient
    patient = test_patient_creation()
    if not patient:
        print("\n❌ Patient creation failed. Cannot continue tests.")
        return
    
    print("\n" + "=" * 60)
    print("📋 Testing Core Functionality")
    print("=" * 60)
    
    # Test visit creation
    visit = test_visit_creation(services, patient)
    
    # Test medication
    medication = test_medication_creation(patient)
    
    # Test test results
    test_results_list = test_test_results_upload(services, patient)
    
    print("\n" + "=" * 60)
    print("🤖 Testing AI Features")
    print("=" * 60)
    
    # Test medical chat
    chat_results = test_medical_chat(services, patient)
    
    # Test semantic search
    search_results = test_semantic_search(services, patient)
    
    # Test patient overview
    overview = test_patient_overview(services, patient)
    
    # Test pattern analysis
    pattern_analysis = test_pattern_analysis(services, patient)
    
    print("\n" + "=" * 60)
    print("📄 Testing PDF Generation")
    print("=" * 60)
    
    # Test PDF generation
    pdf_files = test_pdf_generation(services, patient)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    print()
    
    if test_results['failed']:
        print("Failed Tests:")
        for result in test_results['failed']:
            print(f"  ❌ {result['name']}: {result['message']}")
        print()
    
    if test_results['warnings']:
        print("Warnings:")
        for result in test_results['warnings']:
            print(f"  ⚠️  {result['name']}: {result['message']}")
        print()
    
    # Cleanup test patient (optional)
    # db_manager.delete_patient(patient.id)  # Uncomment if you want to clean up
    
    print("=" * 60)
    if len(test_results['failed']) == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Please review above")
    print("=" * 60)

if __name__ == "__main__":
    main()
