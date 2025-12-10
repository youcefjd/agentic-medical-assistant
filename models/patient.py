"""Patient data models."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PatientCreate(BaseModel):
    """Schema for creating a patient."""
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class VisitCreate(BaseModel):
    """Schema for creating a visit."""
    patient_id: int
    visit_type: str
    audio_file_path: Optional[str] = None
    transcription: Optional[str] = None
    summary: Optional[str] = None

