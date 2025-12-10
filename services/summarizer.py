"""Medical conversation summarization using Ollama."""
import ollama
import config
import json
from typing import Dict, List, Optional


class MedicalSummarizer:
    """Summarizes medical conversations and extracts structured information."""
    
    def __init__(self, vector_store=None):
        self.model = config.OLLAMA_MODEL
        self.base_url = config.OLLAMA_BASE_URL
        self.vector_store = vector_store
    
    def summarize_conversation(self, transcription: str) -> Dict:
        """
        Summarize a medical conversation and extract key information.
        
        Returns:
            Dictionary with summary, topics, recommendations, etc.
        """
        prompt = f"""Vous êtes un assistant médical professionnel dans un système de gestion de dossiers médicaux pour une clinique. Votre rôle est d'extraire et d'organiser les informations d'une conversation médecin-patient RÉELLE qui a été enregistrée.

CONTEXTE:
- Vous travaillez dans un environnement médical contrôlé pour des professionnels de santé
- La conversation fournie est une transcription RÉELLE d'une consultation médecin-patient
- Votre tâche est d'extraire les informations factuelles de cette conversation existante
- Ces informations seront utilisées pour créer un dossier médical structuré

CONVERSATION RÉELLE (transcription):
{transcription}

Extrayez et organisez les informations suivantes en format JSON à partir de cette conversation RÉELLE:

1. Résumé: Un résumé concis de la conversation (en français)
2. Sujets Discutés: Liste des sujets principaux (ex: ["symptômes", "revue des médicaments", "résultats de tests"])
3. Motif de Consultation: La raison principale de la visite
4. Diagnostic: Tout diagnostic mentionné
5. Recommandations: Les recommandations du médecin et les prochaines étapes
6. Médicaments Mentionnés: Liste des médicaments discutés avec les dosages
7. Suivi: Tout rendez-vous de suivi ou actions nécessaires

Répondez UNIQUEMENT avec un JSON valide dans ce format:
{{
    "summary": "...",
    "topics_discussed": ["sujet1", "sujet2"],
    "chief_complaint": "...",
    "diagnosis": "...",
    "recommendations": "...",
    "medications_mentioned": [{{"name": "...", "dosage": "...", "frequency": "..."}}],
    "follow_up": "..."
}}

IMPORTANT: Tous les textes doivent être en français. Extrayez UNIQUEMENT les informations présentes dans la conversation fournie."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}  # Lower temperature for more consistent medical summaries
            )
            
            content = response["message"]["content"]
            
            # Extract JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback: return basic structure
                return {
                    "summary": content,
                    "topics_discussed": [],
                    "chief_complaint": "",
                    "diagnosis": "",
                    "recommendations": "",
                    "medications_mentioned": [],
                    "follow_up": ""
                }
        except Exception as e:
            print(f"Error in summarization: {e}")
            return {
                "summary": transcription[:500] + "...",  # Fallback to truncated transcription
                "topics_discussed": [],
                "chief_complaint": "",
                "diagnosis": "",
                "recommendations": "",
                "medications_mentioned": [],
                "follow_up": ""
            }
    
    def clean_summary(self, summary: str, context: Optional[Dict] = None) -> str:
        """
        Clean and format the summary for medical records.
        Removes filler words, corrects grammar, and formats professionally.
        """
        prompt = f"""Vous êtes un assistant médical dans un système de gestion de dossiers médicaux pour une clinique. Votre tâche est de nettoyer et formater un résumé médical RÉEL existant pour qu'il soit professionnel et clair.

CONTEXTE:
- Vous travaillez dans un environnement médical contrôlé pour des professionnels de santé
- Le résumé fourni est un résumé RÉEL d'une consultation médecin-patient déjà enregistrée
- Votre tâche est d'améliorer la clarté et le formatage, pas de créer de nouvelles informations

Résumé Original (données réelles):
{summary}

Nettoyez et formatez ce résumé médical pour qu'il soit professionnel et clair. Supprimez les mots de remplissage, corrigez les problèmes de grammaire, et assurez-vous qu'il se lit comme une note médicale appropriée.

Fournissez UNIQUEMENT le résumé nettoyé, sans texte supplémentaire. Le résumé doit être en français:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2}
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"Error cleaning summary: {e}")
            return summary
    
    def extract_medical_entities(self, text: str) -> Dict:
        """Extract medical entities (symptoms, medications, conditions) from text."""
        prompt = f"""Vous êtes un assistant médical dans un système de gestion de dossiers médicaux pour une clinique. Votre tâche est d'extraire les entités médicales d'un texte RÉEL de dossier médical.

CONTEXTE:
- Vous travaillez dans un environnement médical contrôlé pour des professionnels de santé
- Le texte fourni est un texte RÉEL provenant d'un dossier médical existant
- Votre tâche est d'extraire les informations factuelles présentes dans le texte

Texte (données réelles):
{text}

Extrayez les entités médicales de ce texte. Retournez un JSON avec:
- symptoms: Liste des symptômes mentionnés (en français)
- medications: Liste des médicaments avec dosages
- conditions: Liste des conditions médicales (en français)
- vital_signs: Signes vitaux mentionnés (tension artérielle, température, etc.)
- test_results: Résultats de tests mentionnés

Retournez UNIQUEMENT un JSON valide. Tous les textes doivent être en français. Extrayez UNIQUEMENT les informations présentes dans le texte fourni:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.2}
            )
            
            content = response["message"]["content"]
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(content[json_start:json_end])
            return {}
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {}
    
    def generate_patient_overview(
        self,
        patient_name: str,
        visits: List[Dict],
        medications: List[Dict],
        latest_visit: Optional[Dict] = None,
        test_results: Optional[List[Dict]] = None
    ) -> str:
        """
        Génère un résumé global du patient pour rafraîchir la mémoire du médecin.
        
        Args:
            patient_name: Nom du patient
            visits: Liste des consultations (dicts avec date, summary, diagnosis)
            medications: Liste des médicaments actifs
            latest_visit: Dernière consultation avec détails
        
        Returns:
            Résumé en français de l'état global du patient
        """
        # Préparer les informations
        meds_text = ""
        if medications:
            meds_list = []
            for med in medications:
                if isinstance(med, dict):
                    med_name = med.get("name", med.get("medication_name", ""))
                    dosage = med.get("dosage", "")
                    frequency = med.get("frequency", "")
                else:
                    med_name = getattr(med, "medication_name", "")
                    dosage = getattr(med, "dosage", "")
                    frequency = getattr(med, "frequency", "")
                
                if med_name:
                    med_text = med_name
                    if dosage:
                        med_text += f" ({dosage})"
                    if frequency:
                        med_text += f" - {frequency}"
                    meds_list.append(med_text)
            meds_text = ", ".join(meds_list) if meds_list else "Aucun médicament actif"
        else:
            meds_text = "Aucun médicament actif"
        
        # Préparer l'historique des diagnostics
        diagnoses = []
        for visit in visits:
            if isinstance(visit, dict):
                diag = visit.get("diagnosis", "")
            else:
                diag = getattr(visit, "diagnosis", None)
            if diag:
                diagnoses.append(diag)
        
        # Préparer les résultats de tests récents
        recent_tests_info = ""
        if test_results:
            # Trier par date et prendre les 3 plus récents
            sorted_tests = sorted(test_results, key=lambda x: x.get("test_date", "") if isinstance(x, dict) else getattr(x, "test_date", ""), reverse=True)
            recent_tests = sorted_tests[:3]
            
            if recent_tests:
                recent_tests_info = "\n\nRésultats de tests récents:\n"
                for test in recent_tests:
                    if isinstance(test, dict):
                        test_name = test.get("test_name", "")
                        test_type = test.get("test_type", "")
                        test_date = test.get("test_date", "")
                    else:
                        test_name = getattr(test, "test_name", "")
                        test_type = getattr(test, "test_type", "")
                        test_date = getattr(test, "test_date", None)
                    
                    if test_name:
                        if hasattr(test_date, "strftime"):
                            date_str = test_date.strftime("%Y-%m-%d")
                        else:
                            date_str = str(test_date)[:10] if test_date else "Date inconnue"
                        
                        type_label = test_type.replace("_", " ").title() if test_type else "Test"
                        recent_tests_info += f"- {type_label}: {test_name} ({date_str})\n"
        
        # Dernière visite
        last_visit_info = ""
        if latest_visit:
            if isinstance(latest_visit, dict):
                last_date = latest_visit.get("date", latest_visit.get("visit_date", ""))
                last_summary = latest_visit.get("summary", latest_visit.get("cleaned_summary", ""))
                last_diag = latest_visit.get("diagnosis", "")
                last_rec = latest_visit.get("recommendations", "")
            else:
                last_date = getattr(latest_visit, "visit_date", None)
                last_summary = getattr(latest_visit, "cleaned_summary", None) or getattr(latest_visit, "summary", "")
                last_diag = getattr(latest_visit, "diagnosis", None)
                last_rec = getattr(latest_visit, "recommendations", None)
            
            if last_date:
                if hasattr(last_date, "strftime"):
                    last_date_str = last_date.strftime("%Y-%m-%d")
                else:
                    last_date_str = str(last_date)[:10]
                last_visit_info = f"\n\nDernière consultation ({last_date_str}):\n"
                if last_summary:
                    last_visit_info += f"Résumé: {last_summary[:200]}...\n" if len(str(last_summary)) > 200 else f"Résumé: {last_summary}\n"
                if last_diag:
                    last_visit_info += f"Diagnostic: {last_diag}\n"
                if last_rec:
                    last_visit_info += f"Recommandations: {last_rec[:150]}...\n" if len(str(last_rec)) > 150 else f"Recommandations: {last_rec}\n"
        
        prompt = f"""Vous êtes un assistant médical dans un système de dossiers médicaux. Générez un résumé professionnel.

RÈGLE ABSOLUE: Répondez UNIQUEMENT avec le résumé. Aucune excuse, aucun préambule, aucune question.

INFORMATIONS PATIENT:
Nom: {patient_name}
Consultations: {len(visits)}
Médicaments: {meds_text}
Diagnostics: {', '.join(diagnoses) if diagnoses else 'Aucun'}
{recent_tests_info}
{last_visit_info}

Générez maintenant un résumé de 3-5 lignes en français couvrant:
- État de santé général
- Médicaments et leur objectif
- Diagnostic principal
- Résultats de tests récents (si disponibles)
- Points clés dernière consultation

EXEMPLE DE FORMAT ATTENDU:
"Le patient présente [état de santé] avec [diagnostic]. Traitement actuel: [médicaments] pour [objectif]. Dernière consultation: [points clés]."

Générez le résumé maintenant:"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"Error generating patient overview: {e}")
            # Fallback summary
            fallback = f"Patient {patient_name} avec {len(visits)} consultation(s) au total. "
            if medications:
                fallback += f"Médicaments actifs: {meds_text}. "
            if latest_visit:
                fallback += "Dernière consultation récente."
            return fallback

