"""Pattern analysis for patient history."""
from typing import Dict, List, Optional
from datetime import datetime
from database import db_manager, Patient, Visit, Medication
import ollama
import config
import json


class PatternAnalyzer:
    """Analyzes patient history for patterns and evolution."""
    
    def __init__(self, vector_store=None):
        self.model = config.OLLAMA_MODEL
        self.vector_store = vector_store
    
    def analyze_patient_evolution(self, patient_id: int) -> Dict:
        """
        Analyze patient's medical evolution across visits.
        Identifies pathology evolution, medication changes, etc.
        """
        patient = db_manager.get_patient(patient_id=patient_id)
        if not patient:
            return {}
        
        visits = db_manager.get_patient_visits(patient_id)
        medications = db_manager.get_patient_medications(patient_id, active_only=False)
        
        if len(visits) < 2:
            return {"message": "Insufficient visit history for pattern analysis"}
        
        # Use vector search to find similar cases if available
        similar_context = ""
        if self.vector_store:
            try:
                # Search for similar patterns in patient's history
                search_results = self.vector_store.search_conversations(
                    query="symptom progression medication changes pathology evolution",
                    patient_id=patient_id,
                    n_results=3
                )
                if search_results:
                    similar_context = "\n\nSimilar historical patterns:\n"
                    for result in search_results:
                        similar_context += f"- {result['document'][:200]}\n"
            except Exception as e:
                print(f"Vector search error: {e}")
        
        # Prepare context for LLM analysis
        visit_summaries = []
        for visit in sorted(visits, key=lambda v: v.visit_date):
            visit_summaries.append({
                "date": visit.visit_date.isoformat(),
                "summary": visit.summary or visit.transcription[:500] if visit.transcription else "",
                "diagnosis": visit.diagnosis,
                "topics": visit.topics_discussed or []
            })
        
        medication_history = []
        for med in sorted(medications, key=lambda m: m.start_date if m.start_date else datetime.min):
            medication_history.append({
                "name": med.medication_name,
                "dosage": med.dosage,
                "start_date": med.start_date.isoformat() if med.start_date else None,
                "end_date": med.end_date.isoformat() if med.end_date else None,
                "is_active": med.is_active
            })
        
        prompt = f"""Vous êtes un assistant médical professionnel dans un système de gestion de dossiers médicaux pour une clinique. Votre rôle est d'analyser l'historique médical RÉEL d'un patient et d'identifier les modèles pour aider le médecin.

CONTEXTE:
- Vous travaillez dans un environnement médical contrôlé pour des professionnels de santé
- Toutes les informations fournies sont des données RÉELLES déjà enregistrées dans le système
- Votre tâche est d'analyser les données existantes pour identifier des tendances et des modèles
- Cette analyse est destinée à un médecin professionnel dans un environnement médical contrôlé

INFORMATIONS DU PATIENT (données réelles du système):
Patient: {patient.first_name} {patient.last_name}
Date de Naissance: {patient.date_of_birth}

Historique des Consultations (données réelles):
{json.dumps(visit_summaries, indent=2)}

Historique des Médicaments (données réelles):
{json.dumps(medication_history, indent=2)}
{similar_context}

TÂCHE:
Analysez l'historique médical RÉEL de ce patient et identifiez les modèles basés sur les données fournies. Fournissez l'analyse en format JSON. TOUS LES TEXTES DOIVENT ÊTRE EN FRANÇAIS:
{{
    "pathology_evolution": {{
        "summary": "Comment la condition a évolué dans le temps",
        "key_changes": ["changement1", "changement2"],
        "trend": "amélioration/stable/aggravation"
    }},
    "medication_changes": {{
        "new_medications": ["med1", "med2"],
        "discontinued_medications": ["med3"],
        "dosage_changes": [{{"medication": "...", "old_dosage": "...", "new_dosage": "...", "date": "..."}}],
        "summary": "Évolution globale des médicaments"
    }},
    "key_insights": ["insight1", "insight2"],
    "recommendations": "Suggestions basées sur les modèles"
}}"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}
            )
            
            content = response["message"]["content"]
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(content[json_start:json_end])
        except Exception as e:
            print(f"Error in pattern analysis: {e}")
        
        return {}
    
    def compare_visits(self, visit1_id: int, visit2_id: int) -> Dict:
        """Compare two visits to identify changes."""
        with db_manager.get_session() as session:
            visit1 = session.query(Visit).filter(Visit.id == visit1_id).first()
            visit2 = session.query(Visit).filter(Visit.id == visit2_id).first()
            
            if not visit1 or not visit2:
                return {}
            
            prompt = f"""Compare these two medical visits and identify key differences:

Visit 1 ({visit1.visit_date}):
Summary: {visit1.summary or (visit1.transcription[:500] if visit1.transcription else "")}
Diagnosis: {visit1.diagnosis}

Visit 2 ({visit2.visit_date}):
Summary: {visit2.summary or (visit2.transcription[:500] if visit2.transcription else "")}
Diagnosis: {visit2.diagnosis}

Provide comparison in JSON:
{{
    "time_gap_days": ...,
    "condition_changes": ["change1", "change2"],
    "symptom_changes": ["change1", "change2"],
    "medication_changes": ["change1", "change2"],
    "overall_assessment": "..."
}}"""

            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.3}
                )
                
                content = response["message"]["content"]
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    return json.loads(content[json_start:json_end])
            except Exception as e:
                print(f"Error comparing visits: {e}")
            
            return {}

