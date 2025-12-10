"""Database manager for SQLite operations."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import config
from database.schema import Base, Patient, Visit, Medication, TestResult, PatternAnalysis


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(config.DATABASE_PATH)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._initialize_db()
    
    def _initialize_db(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_patient(self, patient_data: dict) -> Patient:
        """Create a new patient record."""
        session = self.SessionLocal()
        try:
            patient = Patient(**patient_data)
            session.add(patient)
            session.commit()
            session.refresh(patient)
            # Access all attributes while session is open
            _ = patient.id, patient.patient_id, patient.first_name, patient.last_name
            session.expunge(patient)
            return patient
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_patient(self, patient_id: int = None, patient_code: str = None) -> Patient:
        """Retrieve a patient by ID or patient code."""
        session = self.SessionLocal()
        try:
            if patient_id:
                patient = session.query(Patient).filter(Patient.id == patient_id).first()
            elif patient_code:
                patient = session.query(Patient).filter(Patient.patient_id == patient_code).first()
            else:
                return None
            
            if patient:
                # Access all attributes while session is open
                _ = patient.id, patient.patient_id, patient.first_name, patient.last_name
                session.expunge(patient)
            
            return patient
        finally:
            session.close()
    
    def get_patient_visits(self, patient_id: int, limit: int = None) -> list:
        """Get all visits for a patient, ordered by date."""
        session = self.SessionLocal()
        try:
            query = session.query(Visit).filter(Visit.patient_id == patient_id).order_by(Visit.visit_date.desc())
            if limit:
                query = query.limit(limit)
            visits = query.all()
            # Expunge all visits
            for visit in visits:
                _ = visit.id, visit.patient_id, visit.visit_date
                session.expunge(visit)
            return visits
        finally:
            session.close()
    
    def get_patient_medications(self, patient_id: int, active_only: bool = True) -> list:
        """Get medications for a patient."""
        session = self.SessionLocal()
        try:
            query = session.query(Medication).filter(Medication.patient_id == patient_id)
            if active_only:
                query = query.filter(Medication.is_active == True)
            medications = query.order_by(Medication.start_date.desc()).all()
            # Expunge all medications
            for med in medications:
                _ = med.id, med.medication_name, med.dosage
                session.expunge(med)
            return medications
        finally:
            session.close()
    
    def get_patient_test_results(self, patient_id: int, test_type: str = None) -> list:
        """Get test results for a patient."""
        session = self.SessionLocal()
        try:
            query = session.query(TestResult).filter(TestResult.patient_id == patient_id)
            if test_type:
                query = query.filter(TestResult.test_type == test_type)
            test_results = query.order_by(TestResult.test_date.desc()).all()
            # Expunge all test results
            for test in test_results:
                _ = test.id, test.test_name, test.test_type
                session.expunge(test)
            return test_results
        finally:
            session.close()
    
    def create_visit(self, visit_data: dict) -> Visit:
        """Create a new visit record."""
        session = self.SessionLocal()
        try:
            visit = Visit(**visit_data)
            session.add(visit)
            session.commit()
            session.refresh(visit)
            # Access key attributes while session is open
            _ = visit.id, visit.patient_id, visit.visit_date
            session.expunge(visit)
            return visit
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def update_visit(self, visit_id: int, update_data: dict):
        """Update a visit record."""
        with self.get_session() as session:
            visit = session.query(Visit).filter(Visit.id == visit_id).first()
            if visit:
                for key, value in update_data.items():
                    setattr(visit, key, value)
                session.flush()
    
    def get_visit(self, visit_id: int) -> Visit:
        """Get a visit by ID."""
        session = self.SessionLocal()
        try:
            visit = session.query(Visit).filter(Visit.id == visit_id).first()
            if visit:
                # Access key attributes while session is open
                _ = visit.id, visit.patient_id, visit.visit_date
                session.expunge(visit)
            return visit
        finally:
            session.close()
    
    def add_medication(self, medication_data: dict) -> Medication:
        """Add a medication record."""
        session = self.SessionLocal()
        try:
            medication = Medication(**medication_data)
            session.add(medication)
            session.commit()
            session.refresh(medication)
            # Access key attributes while session is open
            _ = medication.id, medication.medication_name, medication.dosage
            session.expunge(medication)
            return medication
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_all_patients(self) -> list:
        """Get all patients."""
        session = self.SessionLocal()
        try:
            patients = session.query(Patient).all()
            # Expunge all patients and access their attributes
            for patient in patients:
                _ = patient.id, patient.patient_id, patient.first_name, patient.last_name, patient.date_of_birth, patient.phone
                session.expunge(patient)
            return patients
        finally:
            session.close()
    
    def add_test_result(self, test_data: dict) -> TestResult:
        """Add a test result."""
        session = self.SessionLocal()
        try:
            test_result = TestResult(**test_data)
            session.add(test_result)
            session.commit()
            session.refresh(test_result)
            # Access key attributes while session is open
            _ = test_result.id, test_result.test_name, test_result.test_type
            session.expunge(test_result)
            return test_result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global instance
db_manager = DatabaseManager()

