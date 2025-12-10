#!/usr/bin/env python3
"""Test uploading and processing French audio conversation."""
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import db_manager
from services import Transcriber, MedicalSummarizer, VectorStore

def process_audio_for_patient(patient_code: str, audio_path: str):
    """Process audio file and create visit record."""
    print(f"🔍 Looking for patient: {patient_code}")
    
    # Get patient
    patient = db_manager.get_patient(patient_code=patient_code)
    if not patient:
        print(f"❌ Patient {patient_code} not found!")
        return
    
    print(f"✅ Found patient: {patient.first_name} {patient.last_name} (ID: {patient.id})")
    print(f"\n📝 Processing audio file: {audio_path}")
    
    # Initialize services
    print("\n1️⃣ Initializing services...")
    transcriber = Transcriber()
    vector_store = VectorStore()
    summarizer = MedicalSummarizer(vector_store=vector_store)
    
    # Transcribe
    print("\n2️⃣ Transcribing audio (this may take a moment)...")
    try:
        transcription_result = transcriber.transcribe(audio_path)
        transcription = transcription_result["text"]
        print(f"✅ Transcription complete!")
        print(f"   Duration: {transcription_result.get('duration', 0):.2f} seconds")
        print(f"   Language detected: {transcription_result.get('language', 'unknown')}")
        print(f"\n📄 Transcription preview (first 200 chars):")
        print(f"   {transcription[:200]}...")
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return
    
    # Summarize
    print("\n3️⃣ Summarizing conversation with AI...")
    try:
        summary_data = summarizer.summarize_conversation(transcription)
        print(f"✅ Summary complete!")
        print(f"\n📋 Summary:")
        print(f"   Topics: {summary_data.get('topics_discussed', [])}")
        print(f"   Chief Complaint: {summary_data.get('chief_complaint', 'N/A')}")
        print(f"   Diagnosis: {summary_data.get('diagnosis', 'N/A')}")
    except Exception as e:
        print(f"❌ Summarization error: {e}")
        return
    
    # Clean summary
    print("\n4️⃣ Cleaning summary...")
    try:
        cleaned_summary = summarizer.clean_summary(summary_data.get("summary", ""))
        print(f"✅ Summary cleaned!")
    except Exception as e:
        print(f"⚠️  Cleaning error: {e}")
        cleaned_summary = summary_data.get("summary", "")
    
    # Create visit record
    print("\n5️⃣ Creating visit record...")
    try:
        # Convert recommendations list to string if it's a list
        recommendations = summary_data.get("recommendations", "")
        if isinstance(recommendations, list):
            recommendations = "\n".join(recommendations) if recommendations else ""
        
        visit = db_manager.create_visit({
            "patient_id": patient.id,
            "visit_type": "Consultation",
            "audio_file_path": str(audio_path),
            "transcription": transcription,
            "summary": summary_data.get("summary", ""),
            "cleaned_summary": cleaned_summary,
            "topics_discussed": summary_data.get("topics_discussed", []),
            "chief_complaint": summary_data.get("chief_complaint", ""),
            "diagnosis": summary_data.get("diagnosis", ""),
            "recommendations": recommendations,
            "duration_minutes": transcription_result.get("duration", 0) / 60,
        })
        print(f"✅ Visit created! (Visit ID: {visit.id})")
    except Exception as e:
        print(f"❌ Error creating visit: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Add medications
    print("\n6️⃣ Adding medications...")
    medications = summary_data.get("medications_mentioned", [])
    for med in medications:
        try:
            db_manager.add_medication({
                "patient_id": patient.id,
                "visit_id": visit.id,
                "medication_name": med.get("name", ""),
                "dosage": med.get("dosage", ""),
                "frequency": med.get("frequency", ""),
            })
            print(f"   ✅ Added: {med.get('name', 'Unknown')} - {med.get('dosage', 'N/A')}")
        except Exception as e:
            print(f"   ⚠️  Error adding medication: {e}")
    
    # Add to vector store
    print("\n7️⃣ Adding to vector store for semantic search...")
    try:
        vector_store.add_conversation(
            visit_id=visit.id,
            patient_id=patient.id,
            transcription=transcription,
            summary=summary_data.get("summary", ""),
            metadata={
                "visit_date": visit.visit_date.isoformat(),
                "visit_type": "Consultation",
                "topics": str(summary_data.get("topics_discussed", []))
            }
        )
        
        if summary_data.get("diagnosis"):
            vector_store.add_medical_note(
                note_id=f"diagnosis_{visit.id}",
                patient_id=patient.id,
                note_text=summary_data.get("diagnosis", ""),
                note_type="diagnosis",
                metadata={"visit_id": visit.id}
            )
        
        if summary_data.get("recommendations"):
            rec_text = summary_data.get("recommendations", "")
            # Convert list to string if needed
            if isinstance(rec_text, list):
                rec_text = "\n".join(rec_text) if rec_text else ""
            if rec_text:
                vector_store.add_medical_note(
                    note_id=f"recommendations_{visit.id}",
                    patient_id=patient.id,
                    note_text=rec_text,
                    note_type="recommendations",
                    metadata={"visit_id": visit.id}
                )
        
        print(f"✅ Added to vector store!")
    except Exception as e:
        print(f"⚠️  Vector store error: {e}")
    
    print("\n" + "="*60)
    print("✅ PROCESSING COMPLETE!")
    print("="*60)
    print(f"\nVisit Summary:")
    print(f"  Patient: {patient.first_name} {patient.last_name}")
    print(f"  Visit ID: {visit.id}")
    print(f"  Date: {visit.visit_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Type: {visit.visit_type}")
    print(f"  Duration: {visit.duration_minutes:.2f} minutes")
    print(f"\nYou can now view this visit in the Streamlit app!")

if __name__ == "__main__":
    audio_file = Path("data/conversations/test_conversation_fr.mp3")
    
    if not audio_file.exists():
        print(f"❌ Audio file not found: {audio_file}")
        print("Please run create_test_audio.py first")
        sys.exit(1)
    
    process_audio_for_patient("001", str(audio_file))

