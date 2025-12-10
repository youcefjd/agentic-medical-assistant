"""French translations for the medical assistant application."""
# This file contains all French translations for the UI

TRANSLATIONS = {
    # Navigation
    "navigation": {
        "dashboard": "Tableau de bord",
        "new_patient": "Nouveau Patient",
        "record_visit": "Enregistrer Consultation",
        "view_patient": "Voir Patient",
        "upload_tests": "Télécharger Tests",
        "pattern_analysis": "Analyse de Modèles",
        "semantic_search": "Recherche Sémantique"
    },
    
    # Dashboard
    "dashboard": {
        "title": "Tableau de Bord des Patients",
        "total_patients": "Total Patients",
        "recent_patients": "Patients Récents",
        "dob": "Date de Naissance",
        "phone": "Téléphone",
        "total_visits": "Total Consultations",
        "last_visit": "Dernière Consultation"
    },
    
    # New Patient
    "new_patient": {
        "title": "Enregistrer un Nouveau Patient",
        "patient_id": "ID Patient *",
        "first_name": "Prénom *",
        "last_name": "Nom *",
        "date_of_birth": "Date de Naissance",
        "gender": "Sexe",
        "gender_options": ["", "Homme", "Femme", "Autre"],
        "phone": "Téléphone",
        "email": "Email",
        "address": "Adresse",
        "emergency_contact": "Contact d'Urgence",
        "create_button": "Créer le Patient",
        "success": "Patient {patient_id} créé avec succès !",
        "error": "Erreur lors de la création du patient : {error}",
        "required_fields": "Veuillez remplir les champs obligatoires (*)"
    },
    
    # Record Visit
    "record_visit": {
        "title": "Enregistrer une Consultation",
        "no_patients": "Aucun patient trouvé. Veuillez créer un patient d'abord.",
        "select_patient": "Sélectionner un Patient",
        "visit_type": "Type de Consultation",
        "visit_types": ["Consultation", "Suivi", "Urgence", "Autre"],
        "upload_audio": "Télécharger l'Enregistrement Audio",
        "choose_file": "Choisir un fichier audio",
        "process_button": "Traiter la Consultation",
        "processing": "Traitement en cours...",
        "transcribing": "Transcription de l'audio...",
        "summarizing": "Résumé de la conversation...",
        "success": "Consultation enregistrée avec succès !",
        "visit_summary": "Résumé de la Consultation",
        "generate_pdf": "Générer le PDF",
        "download_pdf": "Télécharger le PDF"
    },
    
    # View Patient
    "view_patient": {
        "title": "Dossiers des Patients",
        "no_patients": "Aucun patient trouvé.",
        "select_patient": "Sélectionner un Patient",
        "patient_info": "Informations Patient",
        "name": "Nom",
        "patient_id": "ID Patient",
        "dob": "Date de Naissance",
        "gender": "Sexe",
        "phone": "Téléphone",
        "total_visits": "Total Consultations",
        "active_medications": "Médicaments Actifs",
        "test_results": "Résultats de Tests",
        "visit_history": "Historique des Consultations",
        "medications": "Médicaments",
        "test_results_title": "Résultats de Tests & Imagerie Médicale",
        "generate_complete_pdf": "Générer l'Historique Complet PDF",
        "download_complete_pdf": "Télécharger l'Historique Complet PDF",
        "no_test_results": "Aucun résultat de test disponible pour ce patient."
    },
    
    # Upload Tests
    "upload_tests": {
        "title": "Télécharger des Résultats de Tests",
        "no_patients": "Aucun patient trouvé.",
        "select_patient": "Sélectionner un Patient",
        "test_type": "Type de Test",
        "test_types": ["IRM", "Scanner CT", "Radiographie", "Analyse de Sang", "Autre"],
        "upload_file": "Télécharger le Fichier de Test",
        "process_button": "Traiter le Test",
        "processing": "Traitement du test...",
        "success": "Résultat de test enregistré !",
        "error": "Erreur lors du traitement : {error}"
    },
    
    # Pattern Analysis
    "pattern_analysis": {
        "title": "Analyse de Modèles",
        "no_patients": "Aucun patient trouvé.",
        "select_patient": "Sélectionner un Patient",
        "analyze_button": "Analyser l'Évolution du Patient",
        "analyzing": "Analyse des modèles...",
        "pathology_evolution": "Évolution de la Pathologie",
        "trend": "Tendance",
        "summary": "Résumé",
        "key_changes": "Changements Clés",
        "medication_changes": "Changements de Médicaments",
        "new_medications": "Nouveaux Médicaments",
        "discontinued_medications": "Médicaments Arrêtés",
        "key_insights": "Insights Clés",
        "insufficient_data": "Données insuffisantes pour l'analyse de modèles. Au moins 2 consultations nécessaires."
    },
    
    # Semantic Search
    "semantic_search": {
        "title": "Recherche Sémantique",
        "description": "Recherchez dans toutes les conversations et notes médicales en utilisant le langage naturel.",
        "search_query": "Entrez votre requête de recherche",
        "filter_patient": "Filtrer par Patient",
        "all_patients": "Tous les Patients",
        "search_type": "Type de Recherche",
        "search_types": ["Tout", "Conversations Seulement", "Notes Médicales Seulement"],
        "num_results": "Nombre de Résultats",
        "search_button": "Rechercher",
        "searching": "Recherche...",
        "matching_conversations": "Conversations Correspondantes",
        "matching_notes": "Notes Médicales Correspondantes",
        "example_queries": "Exemples de Requêtes",
        "visit_id": "ID Consultation",
        "score": "Score"
    }
}

def t(key_path: str, **kwargs) -> str:
    """
    Get translation by key path (e.g., 'dashboard.title').
    Supports string formatting with kwargs.
    """
    keys = key_path.split('.')
    value = TRANSLATIONS
    for key in keys:
        value = value[key]
    
    if isinstance(value, str) and kwargs:
        return value.format(**kwargs)
    return value

