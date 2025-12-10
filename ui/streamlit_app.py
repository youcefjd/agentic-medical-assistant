"""Main Streamlit application."""
import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from database import db_manager, Patient, Visit
from services import Transcriber, MedicalSummarizer, PatternAnalyzer, PDFGenerator, VectorStore
from integrations import DICOMParser, LabResultsParser

# Page configuration
st.set_page_config(
    page_title="Assistant Médical",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services (cached)
@st.cache_resource
def get_services():
    """Initialize and cache services."""
    vector_store = VectorStore()
    return {
        "transcriber": Transcriber(),
        "summarizer": MedicalSummarizer(vector_store=vector_store),
        "pattern_analyzer": PatternAnalyzer(vector_store=vector_store),
        "pdf_generator": PDFGenerator(),
        "dicom_parser": DICOMParser(),
        "lab_parser": LabResultsParser(),
        "vector_store": vector_store
    }

services = get_services()

# Sidebar navigation
st.sidebar.title("🏥 Assistant Médical")
page = st.sidebar.selectbox(
    "Navigation",
    ["Tableau de bord", "Nouveau Patient", "Enregistrer Consultation", "Voir Patient", "Télécharger Tests", "Analyse de Modèles", "Recherche Sémantique"]
)

# Dashboard
if page == "Tableau de bord":
    st.title("Tableau de Bord des Patients")
    
    # Get all patients
    patients = db_manager.get_all_patients()
    
    st.metric("Total Patients", len(patients))
    
    # Patient list
    if patients:
        st.subheader("Patients Récents")
        for patient in patients[:10]:
            with st.expander(f"{patient.first_name} {patient.last_name} - {patient.patient_id}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Date de Naissance:** {patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else 'N/A'}")
                    st.write(f"**Téléphone:** {patient.phone or 'N/A'}")
                with col2:
                    visits = db_manager.get_patient_visits(patient.id)
                    st.write(f"**Total Consultations:** {len(visits)}")
                    if visits:
                        st.write(f"**Dernière Consultation:** {visits[0].visit_date.strftime('%Y-%m-%d')}")

# New Patient
elif page == "Nouveau Patient":
    st.title("Enregistrer un Nouveau Patient")
    
    with st.form("new_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("ID Patient *", placeholder="P001")
            first_name = st.text_input("Prénom *")
            last_name = st.text_input("Nom *")
            date_of_birth = st.date_input("Date de Naissance")
            gender = st.selectbox("Sexe", ["", "Homme", "Femme", "Autre"])
        
        with col2:
            phone = st.text_input("Téléphone")
            email = st.text_input("Email")
            address = st.text_area("Adresse")
            emergency_contact = st.text_area("Contact d'Urgence")
        
        submitted = st.form_submit_button("Créer le Patient")
        
        if submitted:
            if patient_id and first_name and last_name:
                try:
                    patient = db_manager.create_patient({
                        "patient_id": patient_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "date_of_birth": datetime.combine(date_of_birth, datetime.min.time()) if date_of_birth else None,
                        "gender": gender if gender else None,
                        "phone": phone if phone else None,
                        "email": email if email else None,
                        "address": address if address else None,
                        "emergency_contact": emergency_contact if emergency_contact else None,
                    })
                    st.success(f"Patient {patient.patient_id} créé avec succès !")
                except Exception as e:
                    st.error(f"Erreur lors de la création du patient : {e}")
            else:
                st.error("Veuillez remplir les champs obligatoires (*)")

# Record Visit
elif page == "Enregistrer Consultation":
    st.title("Enregistrer une Consultation")
    
    # Select patient
    patients = db_manager.get_all_patients()
    
    if not patients:
        st.warning("Aucun patient trouvé. Veuillez créer un patient d'abord.")
    else:
        patient_options = {f"{p.first_name} {p.last_name} ({p.patient_id})": p.id for p in patients}
        selected_patient_name = st.selectbox("Sélectionner un Patient", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_name]
        
        visit_type = st.selectbox("Type de Consultation", ["Consultation", "Suivi", "Urgence", "Autre"])
        
        # Audio upload
        st.subheader("Télécharger l'Enregistrement Audio")
        audio_file = st.file_uploader("Choisir un fichier audio", type=["wav", "mp3", "m4a", "flac"])
        
        if audio_file and st.button("Traiter la Consultation"):
            with st.spinner("Traitement en cours..."):
                # Save audio file
                audio_path = f"data/conversations/{selected_patient_id}_{datetime.now().timestamp()}.wav"
                os.makedirs("data/conversations", exist_ok=True)
                
                with open(audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())
                
                # Transcribe
                st.info("Transcription de l'audio...")
                transcription_result = services["transcriber"].transcribe(audio_path)
                transcription = transcription_result["text"]
                
                # Summarize
                st.info("Résumé de la conversation...")
                summary_data = services["summarizer"].summarize_conversation(transcription)
                
                # Clean summary
                cleaned_summary = services["summarizer"].clean_summary(summary_data.get("summary", ""))
                
                # Convert recommendations list to string if needed
                recommendations = summary_data.get("recommendations", "")
                if isinstance(recommendations, list):
                    recommendations = "\n".join(recommendations) if recommendations else ""
                
                # Create visit record
                visit = db_manager.create_visit({
                    "patient_id": selected_patient_id,
                    "visit_type": visit_type,
                    "audio_file_path": audio_path,
                    "transcription": transcription,
                    "summary": summary_data.get("summary", ""),
                    "cleaned_summary": cleaned_summary,
                    "topics_discussed": summary_data.get("topics_discussed", []),
                    "chief_complaint": summary_data.get("chief_complaint", ""),
                    "diagnosis": summary_data.get("diagnosis", ""),
                    "recommendations": recommendations,
                    "duration_minutes": transcription_result.get("duration", 0) / 60,
                })
                
                # Add medications if mentioned
                for med in summary_data.get("medications_mentioned", []):
                    db_manager.add_medication({
                        "patient_id": selected_patient_id,
                        "visit_id": visit.id,
                        "medication_name": med.get("name", ""),
                        "dosage": med.get("dosage", ""),
                        "frequency": med.get("frequency", ""),
                    })
                
                # Add to vector store for semantic search
                services["vector_store"].add_conversation(
                    visit_id=visit.id,
                    patient_id=selected_patient_id,
                    transcription=transcription,
                    summary=summary_data.get("summary", ""),
                    metadata={
                        "visit_date": visit.visit_date.isoformat(),
                        "visit_type": visit_type,
                        "topics": str(summary_data.get("topics_discussed", []))
                    }
                )
                
                # Also add structured notes
                if summary_data.get("diagnosis"):
                    services["vector_store"].add_medical_note(
                        note_id=f"diagnosis_{visit.id}",
                        patient_id=selected_patient_id,
                        note_text=summary_data.get("diagnosis", ""),
                        note_type="diagnosis",
                        metadata={"visit_id": visit.id}
                    )
                
                if recommendations:  # Use the converted string variable
                    services["vector_store"].add_medical_note(
                        note_id=f"recommendations_{visit.id}",
                        patient_id=selected_patient_id,
                        note_text=recommendations,  # Use the converted string
                        note_type="recommendations",
                        metadata={"visit_id": visit.id}
                    )
                
                st.success("Consultation enregistrée avec succès !")
                
                # Display results
                st.subheader("Résumé de la Consultation")
                st.json(summary_data)
                
                # Generate PDF
                if st.button("Générer le PDF"):
                    patient = db_manager.get_patient(patient_id=selected_patient_id)
                    pdf_path = services["pdf_generator"].generate_visit_summary(visit, patient)
                    st.success(f"PDF généré : {pdf_path}")
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button("Télécharger le PDF", pdf_file, file_name=Path(pdf_path).name)

# View Patient
elif page == "Voir Patient":
    st.title("Dossiers des Patients")
    
    patients = db_manager.get_all_patients()
    
    if not patients:
        st.warning("Aucun patient trouvé.")
    else:
        patient_options = {f"{p.first_name} {p.last_name} ({p.patient_id})": p.id for p in patients}
        selected_patient_name = st.selectbox("Sélectionner un Patient", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_name]
        
        patient = db_manager.get_patient(patient_id=selected_patient_id)
        
        if patient:
            # Get all data first
            visits = db_manager.get_patient_visits(selected_patient_id)
            medications = db_manager.get_patient_medications(selected_patient_id)
            test_results = db_manager.get_patient_test_results(selected_patient_id)
            
            # Generate patient overview summary
            st.subheader("📋 Résumé Global du Patient")
            
            if visits or medications:
                # Prepare data for summary
                latest_visit = visits[0] if visits else None
                visits_data = []
                for v in visits:
                    visits_data.append({
                        "date": v.visit_date,
                        "summary": v.cleaned_summary or v.summary or "",
                        "diagnosis": v.diagnosis or "",
                        "recommendations": v.recommendations or ""
                    })
                
                meds_data = []
                for m in medications:
                    if m.is_active:
                        meds_data.append({
                            "medication_name": m.medication_name,
                            "dosage": m.dosage or "",
                            "frequency": m.frequency or ""
                        })
                
                # Extract diagnoses for fallback
                diagnoses_list = []
                for v in visits_data:
                    diag = v.get("diagnosis", "")
                    if diag:
                        diagnoses_list.append(diag)
                
                with st.spinner("Génération du résumé..."):
                    latest_visit_dict = None
                    if latest_visit:
                        latest_visit_dict = {
                            "visit_date": latest_visit.visit_date,
                            "summary": latest_visit.cleaned_summary or latest_visit.summary or "",
                            "diagnosis": latest_visit.diagnosis or "",
                            "recommendations": latest_visit.recommendations or ""
                        }
                    
                    # Prepare test results data
                    test_results_data = []
                    for test in test_results:
                        test_results_data.append({
                            "test_name": test.test_name,
                            "test_type": test.test_type,
                            "test_date": test.test_date,
                            "results_data": test.results_data
                        })
                    
                    overview = services["summarizer"].generate_patient_overview(
                        patient_name=f"{patient.first_name} {patient.last_name}",
                        visits=visits_data,
                        medications=meds_data,
                        latest_visit=latest_visit_dict,
                        test_results=test_results_data
                    )
                    
                    # Clean up any apologies, disclaimers, or refusals from the LLM response
                    overview_lower = overview.lower()
                    if any(phrase in overview_lower for phrase in ["je suis désolé", "je ne peux pas", "si vous fournissez", "j'aurai plaisir", "fournissez les informations"]):
                        # Try to extract actual content
                        lines = overview.split('\n')
                        summary_lines = []
                        found_content = False
                        
                        for line in lines:
                            line_lower = line.lower()
                            # Skip apology lines
                            if any(phrase in line_lower for phrase in ["désolé", "ne peux pas", "si vous", "j'aurai", "fournissez", "plaisir"]):
                                continue
                            # Look for content after colons or in substantive sentences
                            if ':' in line or (len(line.strip()) > 30 and not line.strip().startswith('-')):
                                if ':' in line:
                                    # Take content after colon
                                    parts = line.split(':', 1)
                                    if len(parts) > 1 and len(parts[1].strip()) > 10:
                                        summary_lines.append(parts[1].strip())
                                        found_content = True
                                else:
                                    summary_lines.append(line.strip())
                                    found_content = True
                        
                        # If we found content, use it; otherwise generate a fallback
                        if summary_lines:
                            overview = ' '.join(summary_lines)
                        else:
                            # Fallback: generate a simple summary from available data
                            overview_parts = []
                            if diagnoses_list:
                                overview_parts.append(f"Diagnostic principal: {diagnoses_list[0]}")
                            if meds_data:
                                med_names = [m.get("medication_name", "") for m in meds_data if m.get("medication_name")]
                                if med_names:
                                    overview_parts.append(f"Médicaments: {', '.join(med_names[:3])}")
                            if test_results_data:
                                recent_test_names = [t.get("test_name", "") for t in sorted(test_results_data, key=lambda x: x.get("test_date", ""), reverse=True)[:2] if t.get("test_name")]
                                if recent_test_names:
                                    overview_parts.append(f"Tests récents: {', '.join(recent_test_names)}")
                            if latest_visit_dict and latest_visit_dict.get("summary"):
                                summary = latest_visit_dict["summary"][:150]
                                overview_parts.append(f"Dernière consultation: {summary}...")
                            
                            overview = '. '.join(overview_parts) if overview_parts else "Résumé non disponible pour le moment."
                    
                    # Display overview in a modern styled box
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 24px;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        margin: 16px 0;
                        border-left: 5px solid #fff;
                    ">
                        <p style="
                            font-size: 15px;
                            line-height: 1.8;
                            color: #ffffff;
                            margin: 0;
                            font-weight: 400;
                            letter-spacing: 0.3px;
                        ">{overview}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucune donnée disponible pour générer un résumé. Enregistrez une consultation pour voir le résumé du patient.")
            
            st.divider()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Informations Patient")
                st.write(f"**Nom:** {patient.first_name} {patient.last_name}")
                st.write(f"**ID Patient:** {patient.patient_id}")
                st.write(f"**Date de Naissance:** {patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else 'N/A'}")
                st.write(f"**Sexe:** {patient.gender or 'N/A'}")
                st.write(f"**Téléphone:** {patient.phone or 'N/A'}")
            
            with col2:
                st.metric("Total Consultations", len(visits))
                st.metric("Médicaments Actifs", len([m for m in medications if m.is_active]))
                st.metric("Résultats de Tests", len(test_results))
            
            # Visit History
            st.subheader("Historique des Consultations")
            for visit in visits:
                with st.expander(f"Consultation: {visit.visit_date.strftime('%Y-%m-%d %H:%M')} - {visit.visit_type}"):
                    if visit.cleaned_summary:
                        st.write("**Résumé:**")
                        st.write(visit.cleaned_summary)
                    if visit.diagnosis:
                        st.write(f"**Diagnostic:** {visit.diagnosis}")
                    if visit.recommendations:
                        st.write(f"**Recommandations:** {visit.recommendations}")
                    
                    # Generate PDF for this visit
                    if st.button(f"Générer le PDF", key=f"pdf_{visit.id}"):
                        pdf_path = services["pdf_generator"].generate_visit_summary(visit, patient)
                        st.success(f"PDF généré : {pdf_path}")
            
            # Medications
            st.subheader("Médicaments")
            for med in medications:
                st.write(f"**{med.medication_name}** - {med.dosage} - {med.frequency}")
            
            # Generate Complete Patient History PDF
            st.divider()
            if st.button("📄 Generate Complete Patient History PDF", type="primary"):
                with st.spinner("Generating comprehensive PDF..."):
                    pdf_path = services["pdf_generator"].generate_patient_history(
                        patient=patient,
                        visits=visits,
                        medications=medications,
                        test_results=test_results
                    )
                    st.success(f"✅ Complete history PDF generated!")
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            "📥 Download Complete History PDF",
                            pdf_file,
                            file_name=Path(pdf_path).name,
                            mime="application/pdf"
                        )
            
            # Test Results - Enhanced View
            test_results = db_manager.get_patient_test_results(selected_patient_id)
            if test_results:
                st.subheader("📊 Test Results & Medical Imaging")
                
                # Group by test type
                by_type = {}
                for test in test_results:
                    test_type = test.test_type or "other"
                    if test_type not in by_type:
                        by_type[test_type] = []
                    by_type[test_type].append(test)
                
                for test_type, tests in by_type.items():
                    type_label = test_type.replace("_", " ").title()
                    # Translate test type labels
                    type_translations = {
                        "blood_test": "Analyses de Sang",
                        "mri": "IRM",
                        "ct_scan": "Scanner CT",
                        "x-ray": "Radiographie"
                    }
                    type_label = type_translations.get(test_type, type_label)
                    
                    with st.expander(f"{type_label} ({len(tests)} tests)", expanded=False):
                        for test in sorted(tests, key=lambda x: x.test_date, reverse=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{test.test_name}**")
                                st.write(f"*Date: {test.test_date.strftime('%Y-%m-%d')}*")
                                
                                # Display results based on type
                                if test.results_data:
                                    if isinstance(test.results_data, dict):
                                        # Lab test results
                                        if "values" in test.results_data or "results" in test.results_data:
                                            values = test.results_data.get("values") or test.results_data.get("results", {})
                                            if values:
                                                st.write("**Résultats:**")
                                                for param, value in list(values.items())[:10]:  # Show first 10
                                                    unit = ""
                                                    if "reference_ranges" in test.results_data:
                                                        ref = test.results_data["reference_ranges"].get(param, {})
                                                        if isinstance(ref, dict):
                                                            unit = ref.get("unit", "")
                                                    st.write(f"  • {param}: {value} {unit}")
                                                if len(values) > 10:
                                                    st.write(f"  ... et {len(values) - 10} paramètres supplémentaires")
                                        
                                        # DICOM metadata
                                        elif "modality" in test.results_data:
                                            st.write("**Détails de l'Étude:**")
                                            st.write(f"  • Modalité: {test.results_data.get('modality', 'N/A')}")
                                            st.write(f"  • Étude: {test.results_data.get('study_description', 'N/A')}")
                                            st.write(f"  • Fabricant: {test.results_data.get('manufacturer', 'N/A')}")
                                            if "image_dimensions" in test.results_data:
                                                dims = test.results_data["image_dimensions"]
                                                st.write(f"  • Taille Image: {dims.get('rows', 'N/A')} x {dims.get('columns', 'N/A')}")
                                
                                if test.interpretation:
                                    st.write(f"**Interprétation:** {test.interpretation}")
                                
                                if test.notes:
                                    st.write(f"**Notes:** {test.notes}")
                            
                            with col2:
                                if test.results_file_path:
                                    file_path = Path(test.results_file_path)
                                    if file_path.exists():
                                        file_size = file_path.stat().st_size / 1024
                                        st.write(f"📄 {file_size:.1f} KB")
                                        if test.test_type in ["mri", "ct_scan", "x-ray"]:
                                            st.write("🖼️ DICOM")
                                        else:
                                            st.write("📋 Rapport")
                            
                            st.divider()
            else:
                st.info("Aucun résultat de test disponible pour ce patient.")

# Upload Tests
elif page == "Télécharger Tests":
    st.title("Télécharger des Résultats de Tests")
    
    patients = db_manager.get_all_patients()
    
    if not patients:
        st.warning("Aucun patient trouvé.")
    else:
        patient_options = {f"{p.first_name} {p.last_name} ({p.patient_id})": p.id for p in patients}
        selected_patient_name = st.selectbox("Sélectionner un Patient", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_name]
        
        test_type = st.selectbox("Type de Test", ["IRM", "Scanner CT", "Radiographie", "Analyse de Sang", "Autre"])
        
        uploaded_file = st.file_uploader("Télécharger le Fichier de Test", type=["dcm", "dicom", "json", "txt", "pdf"])
        
        if uploaded_file and st.button("Traiter le Test"):
            with st.spinner("Traitement du test..."):
                # Save file
                file_path = f"data/tests/{selected_patient_id}_{datetime.now().timestamp()}.{uploaded_file.name.split('.')[-1]}"
                os.makedirs("data/tests", exist_ok=True)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse based on type - Map French UI names to database keys
                test_type_map = {
                    "IRM": "mri",
                    "Scanner CT": "ct_scan",
                    "Radiographie": "x-ray",
                    "Analyse de Sang": "blood_test"
                }
                db_test_type = test_type_map.get(test_type, test_type.lower().replace(" ", "_"))
                
                if test_type in ["IRM", "Scanner CT", "Radiographie"]:
                    try:
                        dicom_data = services["dicom_parser"].parse_dicom_file(file_path)
                        st.json(dicom_data)
                        
                        # Save to database
                        db_manager.add_test_result({
                            "patient_id": selected_patient_id,
                            "test_type": db_test_type,
                            "test_name": dicom_data.get("study_description", test_type),
                            "test_date": datetime.now(),
                            "results_data": dicom_data,
                            "results_file_path": file_path,
                            "source": "local_upload"
                        })
                        st.success("Résultat de test enregistré !")
                    except Exception as e:
                        st.error(f"Erreur lors du traitement DICOM : {e}")
                elif test_type == "Analyse de Sang":
                    # Parse lab results
                    if file_path.endswith(".json"):
                        results = services["lab_parser"].parse_json_results(file_path)
                    else:
                        text = uploaded_file.read().decode("utf-8")
                        results = services["lab_parser"].parse_text_results(text)
                    
                    normalized = services["lab_parser"].normalize_results(results)
                    st.json(normalized)
                    
                    db_manager.add_test_result({
                        "patient_id": selected_patient_id,
                        "test_type": db_test_type,
                        "test_name": normalized.get("test_name", "Analyse de Sang"),
                        "test_date": datetime.now(),
                        "results_data": normalized,
                        "results_file_path": file_path,
                        "source": "local_upload"
                    })
                    st.success("Résultat de test enregistré !")

# Pattern Analysis
elif page == "Analyse de Modèles":
    st.title("Analyse de Modèles")
    
    patients = db_manager.get_all_patients()
    
    if not patients:
        st.warning("Aucun patient trouvé.")
    else:
        patient_options = {f"{p.first_name} {p.last_name} ({p.patient_id})": p.id for p in patients}
        selected_patient_name = st.selectbox("Sélectionner un Patient", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_name]
        
        if st.button("Analyser l'Évolution du Patient"):
            with st.spinner("Analyse des modèles..."):
                analysis = services["pattern_analyzer"].analyze_patient_evolution(selected_patient_id)
                
                if analysis:
                    st.subheader("Évolution de la Pathologie")
                    if "pathology_evolution" in analysis:
                        evo = analysis["pathology_evolution"]
                        st.write(f"**Tendance:** {evo.get('trend', 'N/A')}")
                        st.write(f"**Résumé:** {evo.get('summary', 'N/A')}")
                        st.write("**Changements Clés:**")
                        for change in evo.get("key_changes", []):
                            st.write(f"- {change}")
                    
                    st.subheader("Changements de Médicaments")
                    if "medication_changes" in analysis:
                        med_changes = analysis["medication_changes"]
                        st.write("**Nouveaux Médicaments:**")
                        for med in med_changes.get("new_medications", []):
                            st.write(f"- {med}")
                        st.write("**Médicaments Arrêtés:**")
                        for med in med_changes.get("discontinued_medications", []):
                            st.write(f"- {med}")
                    
                    st.subheader("Insights Clés")
                    for insight in analysis.get("key_insights", []):
                        st.write(f"- {insight}")
                else:
                    st.info("Données insuffisantes pour l'analyse de modèles. Au moins 2 consultations nécessaires.")

# Semantic Search
elif page == "Recherche Sémantique":
    st.title("🔍 Recherche Sémantique")
    st.markdown("Recherchez dans toutes les conversations et notes médicales en utilisant le langage naturel.")
    
    # Search input
    search_query = st.text_input("Entrez votre requête de recherche", placeholder="ex: 'patient se plaint de douleur thoracique' ou 'changements de dosage de médicament'")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        patients = db_manager.get_all_patients()
        patient_options = {f"{p.first_name} {p.last_name} ({p.patient_id})": p.id for p in patients}
        patient_options["Tous les Patients"] = None
        selected_patient_name = st.selectbox("Filtrer par Patient", list(patient_options.keys()))
        selected_patient_id = patient_options[selected_patient_name]
    
    with col2:
        search_type = st.selectbox("Type de Recherche", ["Tout", "Conversations Seulement", "Notes Médicales Seulement"])
    
    n_results = st.slider("Nombre de Résultats", 5, 50, 10)
    
    if search_query and st.button("Rechercher"):
        with st.spinner("Recherche..."):
            if search_type == "Tout":
                results = services["vector_store"].search_all(
                    query=search_query,
                    patient_id=selected_patient_id,
                    n_results=n_results
                )
                
                # Display conversations
                if results["conversations"]:
                    st.subheader("📝 Conversations Correspondantes")
                    for result in results["conversations"]:
                        with st.expander(f"ID Consultation: {result['metadata'].get('visit_id', 'N/A')} - Score: {1 - result.get('distance', 0):.2f}"):
                            st.write("**Document:**")
                            st.write(result["document"][:500] + "..." if len(result["document"]) > 500 else result["document"])
                            st.write("**Métadonnées:**")
                            st.json(result["metadata"])
                            
                            # Link to visit
                            visit_id = result["metadata"].get("visit_id")
                            if visit_id:
                                if st.button(f"Voir Détails Consultation", key=f"view_{visit_id}"):
                                    st.session_state["view_visit_id"] = visit_id
                                    st.rerun()
                
                # Display medical notes
                if results["medical_notes"]:
                    st.subheader("🏥 Notes Médicales Correspondantes")
                    for result in results["medical_notes"]:
                        with st.expander(f"{result['metadata'].get('note_type', 'Note').title()} - Score: {1 - result.get('distance', 0):.2f}"):
                            st.write("**Contenu:**")
                            st.write(result["document"])
                            st.write("**Métadonnées:**")
                            st.json(result["metadata"])
            
            elif search_type == "Conversations Seulement":
                results = services["vector_store"].search_conversations(
                    query=search_query,
                    patient_id=selected_patient_id,
                    n_results=n_results
                )
                
                st.subheader(f"📝 {len(results)} Conversations Trouvées")
                for result in results:
                    with st.expander(f"ID Consultation: {result['metadata'].get('visit_id', 'N/A')} - Score: {1 - result.get('distance', 0):.2f}"):
                        st.write("**Document:**")
                        st.write(result["document"][:500] + "..." if len(result["document"]) > 500 else result["document"])
                        st.write("**Métadonnées:**")
                        st.json(result["metadata"])
            
            elif search_type == "Notes Médicales Seulement":
                results = services["vector_store"].search_medical_notes(
                    query=search_query,
                    patient_id=selected_patient_id,
                    note_type=None,
                    n_results=n_results
                )
                
                st.subheader(f"🏥 {len(results)} Notes Médicales Trouvées")
                for result in results:
                    with st.expander(f"{result['metadata'].get('note_type', 'Note').title()} - Score: {1 - result.get('distance', 0):.2f}"):
                        st.write("**Content:**")
                        st.write(result["document"])
                        st.write("**Metadata:**")
                        st.json(result["metadata"])
    
    # Example queries
    st.sidebar.markdown("### 💡 Example Queries")
    example_queries = [
        "chest pain symptoms",
        "medication side effects",
        "blood pressure changes",
        "follow-up recommendations",
        "diabetes management",
        "allergy reactions"
    ]
    for example in example_queries:
        if st.sidebar.button(example, key=f"example_{example}"):
            st.session_state["search_query"] = example
            st.rerun()

