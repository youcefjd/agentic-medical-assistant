"""Database schema definitions."""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Patient(Base):
    """Patient master record."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    test_results = relationship("TestResult", back_populates="patient", cascade="all, delete-orphan")


class Visit(Base):
    """Patient visit record."""
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    visit_type = Column(String(50))  # consultation, follow-up, emergency, etc.
    
    # Conversation data
    audio_file_path = Column(String(500))
    transcription = Column(Text)
    summary = Column(Text)
    cleaned_summary = Column(Text)
    
    # Structured data
    topics_discussed = Column(JSON)  # List of topics
    chief_complaint = Column(Text)
    diagnosis = Column(Text)
    recommendations = Column(Text)
    notes = Column(Text)
    
    # Metadata
    duration_minutes = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="visits")
    medications_prescribed = relationship("Medication", back_populates="visit")


class Medication(Base):
    """Medication records."""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    
    medication_name = Column(String(200), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="medications")
    visit = relationship("Visit", back_populates="medications_prescribed")


class TestResult(Base):
    """Medical test results (blood tests, MRIs, scans, etc.)."""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=True)
    
    test_type = Column(String(100), nullable=False)  # blood_test, mri, ct_scan, xray, etc.
    test_name = Column(String(200), nullable=False)
    test_date = Column(DateTime, nullable=False)
    
    # Results storage
    results_data = Column(JSON)  # Structured results
    results_file_path = Column(String(500))  # Path to DICOM or PDF file
    interpretation = Column(Text)
    notes = Column(Text)
    
    # Source
    source = Column(String(50))  # api, local_upload
    source_reference = Column(String(200))  # API ID or local file name
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="test_results")


class PatternAnalysis(Base):
    """Stored pattern analyses for patients."""
    __tablename__ = "pattern_analyses"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    analysis_type = Column(String(50))  # pathology_evolution, medication_changes, etc.
    analysis_data = Column(JSON)
    insights = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient")

