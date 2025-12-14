"""Interactive chat service for querying patient medical records."""
import ollama
import config
import json
from typing import List, Dict, Optional
from datetime import datetime
from database import db_manager


class MedicalChat:
    """Interactive chat for querying patient medical records."""
    
    def __init__(self, vector_store=None):
        self.model = config.OLLAMA_MODEL
        self.base_url = config.OLLAMA_BASE_URL
        self.vector_store = vector_store
        self.conversation_history = {}  # patient_id -> list of messages
    
    def _load_patient_context(self, patient_id: int) -> Dict:
        """Load complete patient context for chat."""
        patient = db_manager.get_patient(patient_id=patient_id)
        if not patient:
            return {}
        
        # Get all patient data
        visits = db_manager.get_patient_visits(patient_id)
        medications = db_manager.get_patient_medications(patient_id)
        test_results = db_manager.get_patient_test_results(patient_id)
        
        # Format visits
        visits_data = []
        for visit in sorted(visits, key=lambda v: v.visit_date, reverse=True):
            visits_data.append({
                "date": visit.visit_date.strftime("%Y-%m-%d"),
                "type": visit.visit_type or "consultation",
                "summary": visit.cleaned_summary or visit.summary or "",
                "diagnosis": visit.diagnosis or "",
                "recommendations": visit.recommendations or "",
                "chief_complaint": visit.chief_complaint or ""
            })
        
        # Format medications
        meds_data = []
        for med in medications:
            med_info = {
                "name": med.medication_name,
                "dosage": med.dosage or "",
                "frequency": med.frequency or "",
                "is_active": med.is_active,
                "start_date": med.start_date.strftime("%Y-%m-%d") if med.start_date else None,
                "end_date": med.end_date.strftime("%Y-%m-%d") if med.end_date else None
            }
            meds_data.append(med_info)
        
        # Format test results
        tests_data = []
        for test in sorted(test_results, key=lambda t: t.test_date, reverse=True):
            test_info = {
                "type": test.test_type or "unknown",
                "name": test.test_name,
                "date": test.test_date.strftime("%Y-%m-%d"),
                "interpretation": test.interpretation or "",
                "notes": test.notes or ""
            }
            # Add key results if available
            if test.results_data and isinstance(test.results_data, dict):
                if "values" in test.results_data or "results" in test.results_data:
                    values = test.results_data.get("values") or test.results_data.get("results", {})
                    test_info["key_results"] = dict(list(values.items())[:10])  # First 10 values
                elif "modality" in test.results_data:
                    test_info["modality"] = test.results_data.get("modality")
                    test_info["study_description"] = test.results_data.get("study_description")
            tests_data.append(test_info)
        
        return {
            "patient": {
                "name": f"{patient.first_name} {patient.last_name}",
                "patient_id": patient.patient_id,
                "date_of_birth": patient.date_of_birth.strftime("%Y-%m-%d") if patient.date_of_birth else None,
                "gender": patient.gender or ""
            },
            "visits": visits_data,
            "medications": meds_data,
            "test_results": tests_data,
            "total_visits": len(visits),
            "active_medications": len([m for m in medications if m.is_active]),
            "total_tests": len(test_results)
        }
    
    def _search_relevant_context(self, query: str, patient_id: int, n_results: int = 3) -> str:
        """Search for relevant context using vector store."""
        if not self.vector_store:
            return ""
        
        try:
            # Search conversations and medical notes
            results = self.vector_store.search_all(
                query=query,
                patient_id=patient_id,
                n_results=n_results
            )
            
            relevant_context = ""
            if results.get("conversations"):
                relevant_context += "\n\nConversations pertinentes:\n"
                for i, conv in enumerate(results["conversations"][:2], 1):
                    relevant_context += f"{i}. {conv['document'][:300]}...\n"
            
            if results.get("medical_notes"):
                relevant_context += "\n\nNotes médicales pertinentes:\n"
                for i, note in enumerate(results["medical_notes"][:2], 1):
                    relevant_context += f"{i}. {note['document'][:300]}...\n"
            
            return relevant_context
        except Exception as e:
            print(f"Error in vector search: {e}")
            return ""
    
    def _build_system_prompt(self, patient_context: Dict) -> str:
        """Build system prompt with patient context."""
        patient = patient_context.get("patient", {})
        
        prompt = f"""Vous êtes un assistant médical professionnel aidant un médecin à interroger le dossier médical d'un patient.

CONTEXTE DU PATIENT:
Nom: {patient.get('name', 'N/A')}
ID Patient: {patient.get('patient_id', 'N/A')}
Date de Naissance: {patient.get('date_of_birth', 'N/A')}
Sexe: {patient.get('gender', 'N/A')}

RÉSUMÉ DU DOSSIER:
- Total consultations: {patient_context.get('total_visits', 0)}
- Médicaments actifs: {patient_context.get('active_medications', 0)}
- Résultats de tests: {patient_context.get('total_tests', 0)}

INSTRUCTIONS:
1. Répondez UNIQUEMENT basé sur les informations du dossier fourni
2. Si une information n'est pas disponible, dites-le clairement
3. Soyez concis mais complet
4. Utilisez un langage médical professionnel
5. Citez les dates et sources quand pertinent
6. Répondez en français

Vous avez accès à:
- Historique complet des consultations
- Médicaments (actifs et passés)
- Résultats de tests (analyses, IRM, scanners, etc.)

Répondez aux questions du médecin de manière précise et professionnelle."""
        
        return prompt
    
    def _format_patient_context_for_llm(self, patient_context: Dict, max_visits: int = 10) -> str:
        """Format patient context for LLM consumption."""
        context_text = f"\n=== DOSSIER MÉDICAL COMPLET ===\n\n"
        
        # Patient info
        patient = patient_context.get("patient", {})
        context_text += f"PATIENT: {patient.get('name')} (ID: {patient.get('patient_id')})\n"
        context_text += f"Date de Naissance: {patient.get('date_of_birth', 'N/A')}\n"
        context_text += f"Sexe: {patient.get('gender', 'N/A')}\n\n"
        
        # Recent visits (most recent first, limit to max_visits)
        visits = patient_context.get("visits", [])[:max_visits]
        if visits:
            context_text += f"=== CONSULTATIONS ({len(visits)} récentes) ===\n"
            for visit in visits:
                context_text += f"\nConsultation du {visit.get('date')} ({visit.get('type', 'consultation')}):\n"
                if visit.get('chief_complaint'):
                    context_text += f"Motif: {visit.get('chief_complaint')}\n"
                if visit.get('summary'):
                    context_text += f"Résumé: {visit.get('summary')[:500]}\n"
                if visit.get('diagnosis'):
                    context_text += f"Diagnostic: {visit.get('diagnosis')}\n"
                if visit.get('recommendations'):
                    context_text += f"Recommandations: {visit.get('recommendations')[:300]}\n"
        
        # Medications
        medications = patient_context.get("medications", [])
        if medications:
            context_text += f"\n=== MÉDICAMENTS ({len(medications)} total) ===\n"
            active_meds = [m for m in medications if m.get('is_active')]
            if active_meds:
                context_text += "Médicaments actifs:\n"
                for med in active_meds:
                    context_text += f"- {med.get('name')} ({med.get('dosage')}) - {med.get('frequency')}\n"
                    if med.get('start_date'):
                        context_text += f"  Début: {med.get('start_date')}\n"
            
            inactive_meds = [m for m in medications if not m.get('is_active')]
            if inactive_meds:
                context_text += "\nMédicaments arrêtés:\n"
                for med in inactive_meds[:5]:  # Limit to 5 most recent
                    context_text += f"- {med.get('name')} ({med.get('dosage')}) - Arrêté le {med.get('end_date', 'N/A')}\n"
        
        # Test results
        tests = patient_context.get("test_results", [])
        if tests:
            context_text += f"\n=== RÉSULTATS DE TESTS ({len(tests)} total) ===\n"
            for test in tests[:10]:  # Limit to 10 most recent
                context_text += f"\n{test.get('type', 'Test').upper()}: {test.get('name')} ({test.get('date')})\n"
                if test.get('interpretation'):
                    context_text += f"Interprétation: {test.get('interpretation')[:200]}\n"
                if test.get('key_results'):
                    context_text += f"Résultats clés: {json.dumps(test.get('key_results'), ensure_ascii=False)[:200]}\n"
                if test.get('modality'):
                    context_text += f"Modalité: {test.get('modality')} - {test.get('study_description', '')}\n"
        
        return context_text
    
    def chat(
        self,
        patient_id: int,
        user_message: str,
        use_vector_search: bool = True
    ) -> Dict:
        """
        Chat with patient medical records.
        
        Args:
            patient_id: Patient ID
            user_message: User's question
            use_vector_search: Whether to use vector search for additional context
        
        Returns:
            Dictionary with response and metadata
        """
        # Initialize conversation history if needed
        if patient_id not in self.conversation_history:
            self.conversation_history[patient_id] = []
        
        # Load patient context
        patient_context = self._load_patient_context(patient_id)
        if not patient_context:
            return {
                "response": "Erreur: Patient non trouvé.",
                "error": True
            }
        
        # Build system prompt
        system_prompt = self._build_system_prompt(patient_context)
        
        # Format patient context
        context_text = self._format_patient_context_for_llm(patient_context)
        
        # Search for relevant context if enabled
        relevant_context = ""
        if use_vector_search and self.vector_store:
            relevant_context = self._search_relevant_context(user_message, patient_id)
        
        # Build messages for LLM
        messages = []
        
        # Add system message with context
        messages.append({
            "role": "system",
            "content": system_prompt + context_text + relevant_context
        })
        
        # Add conversation history (last 5 exchanges to preserve context)
        history = self.conversation_history[patient_id][-10:]  # Last 10 messages (5 exchanges)
        messages.extend(history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Call LLM
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.3,  # Lower temperature for medical accuracy
                    "num_predict": 500  # Limit response length
                }
            )
            
            assistant_response = response["message"]["content"].strip()
            
            # Check for empty or very short responses
            if not assistant_response or len(assistant_response) < 10:
                assistant_response = "Je n'ai pas pu générer de réponse. Veuillez reformuler votre question ou vérifier que le patient a des données dans son dossier."
            
            # Check for refusal/apology messages and provide fallback
            refusal_phrases = [
                "je suis désolé",
                "je ne peux pas",
                "je ne peux pas répondre",
                "i'm sorry",
                "i cannot",
                "i cannot respond",
                "i'm sorry, but i cannot"
            ]
            
            response_lower = assistant_response.lower()
            has_refusal = any(phrase in response_lower for phrase in refusal_phrases)
            
            if has_refusal and len(assistant_response) < 200:
                # Try to extract useful information from context
                fallback_response = self._generate_fallback_response(
                    user_message, patient_context
                )
                if fallback_response:
                    assistant_response = fallback_response
            
            # Update conversation history
            self.conversation_history[patient_id].append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history[patient_id].append({
                "role": "assistant",
                "content": assistant_response
            })
            
            # Keep history manageable (last 20 messages max)
            if len(self.conversation_history[patient_id]) > 20:
                self.conversation_history[patient_id] = self.conversation_history[patient_id][-20:]
            
            return {
                "response": assistant_response,
                "error": False,
                "context_used": {
                    "visits_count": len(patient_context.get("visits", [])),
                    "medications_count": len(patient_context.get("medications", [])),
                    "tests_count": len(patient_context.get("test_results", [])),
                    "vector_search_used": bool(relevant_context)
                }
            }
            
        except Exception as e:
            print(f"Error in medical chat: {e}")
            return {
                "response": f"Erreur lors de la génération de la réponse: {str(e)}",
                "error": True
            }
    
    def clear_history(self, patient_id: int):
        """Clear conversation history for a patient."""
        if patient_id in self.conversation_history:
            del self.conversation_history[patient_id]
    
    def get_history(self, patient_id: int) -> List[Dict]:
        """Get conversation history for a patient."""
        return self.conversation_history.get(patient_id, [])
    
    def _generate_fallback_response(self, user_message: str, patient_context: Dict) -> Optional[str]:
        """Generate a fallback response based on patient context when LLM refuses."""
        user_lower = user_message.lower()
        
        # Check what data is available
        visits = patient_context.get("visits", [])
        medications = patient_context.get("medications", [])
        tests = patient_context.get("test_results", [])
        
        # Generate simple responses based on question type
        if "médicament" in user_lower or "medication" in user_lower:
            active_meds = [m for m in medications if m.get("is_active")]
            if active_meds:
                med_list = "\n".join([f"- {m.get('name')} ({m.get('dosage')}) - {m.get('frequency')}" 
                                     for m in active_meds[:5]])
                return f"Médicaments actifs:\n{med_list}"
            else:
                return "Aucun médicament actif trouvé dans le dossier."
        
        elif "test" in user_lower or "résultat" in user_lower or "result" in user_lower:
            if tests:
                test_list = "\n".join([f"- {t.get('name')} ({t.get('type', 'test')}) - {t.get('date')}" 
                                      for t in tests[:5]])
                return f"Tests récents:\n{test_list}"
            else:
                return "Aucun résultat de test trouvé dans le dossier."
        
        elif "diagnostic" in user_lower or "diagnosis" in user_lower:
            if visits:
                latest_visit = visits[0]  # Most recent
                diagnosis = latest_visit.get("diagnosis", "")
                if diagnosis:
                    return f"Dernier diagnostic ({latest_visit.get('date', 'N/A')}): {diagnosis}"
                else:
                    return "Aucun diagnostic trouvé dans les consultations récentes."
            else:
                return "Aucune consultation trouvée dans le dossier."
        
        elif "évolution" in user_lower or "evolution" in user_lower or "pattern" in user_lower:
            if len(visits) >= 2:
                return f"Le patient a {len(visits)} consultations dans son dossier. Pour une analyse détaillée de l'évolution, veuillez consulter l'historique complet."
            else:
                return "Pas assez de consultations pour analyser l'évolution (minimum 2 requises)."
        
        # Generic fallback
        if visits or medications or tests:
            return f"Le dossier contient {len(visits)} consultation(s), {len(medications)} médicament(s), et {len(tests)} test(s). Veuillez reformuler votre question de manière plus spécifique."
        else:
            return "Le dossier du patient semble vide. Veuillez ajouter des consultations, médicaments ou tests."


