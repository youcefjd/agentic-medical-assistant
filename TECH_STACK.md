# Stack Technique - Mini-Jarvis Medical Assistant

## Vue d'Ensemble

Mini-Jarvis est une application **agentic** (agentive) de gestion de dossiers médicaux qui utilise l'IA pour automatiser la transcription, la résuméisation et l'analyse des conversations médecin-patient. L'application fonctionne entièrement en local, garantissant la confidentialité des données médicales.

---

## 🏗️ Architecture Générale

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit UI (Interface)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│  Services    │ │  Database   │ │ Integrations│
│  Layer       │ │  Layer      │ │  Layer      │
└───────┬──────┘ └──────┬──────┘ └─────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │    LLM (Ollama + Llama 3.1)  │
        │    Vector DB (ChromaDB)       │
        └───────────────────────────────┘
```

---

## 📦 Composants Principaux

### 1. **Interface Utilisateur (UI)**
**Technologie**: Streamlit
- **Rôle**: Interface web interactive pour les médecins
- **Fonctionnalités**:
  - Gestion des patients (création, consultation)
  - Upload et traitement d'audio
  - Visualisation de l'historique médical
  - Recherche sémantique
  - Génération de PDFs
- **Avantages**: Développement rapide, pas besoin de frontend complexe

### 2. **Base de Données Relationnelle**
**Technologie**: SQLite + SQLAlchemy ORM
- **Rôle**: Stockage structuré des données médicales
- **Tables principales**:
  - `patients`: Informations démographiques des patients
  - `visits`: Consultations avec transcriptions et résumés
  - `medications`: Historique des médicaments prescrits
  - `test_results`: Résultats de tests (IRM, analyses de sang, etc.)
  - `pattern_analyses`: Analyses de patterns stockées
- **Avantages**: Local, rapide, pas de serveur requis

### 3. **Base de Données Vectorielle**
**Technologie**: ChromaDB
- **Rôle**: Recherche sémantique dans les conversations et notes médicales
- **Collections**:
  - `conversations`: Transcripts et résumés de consultations (embeddings)
  - `medical_notes`: Notes structurées (diagnostics, recommandations)
- **Fonctionnalités**:
  - Recherche par similarité sémantique
  - Filtrage par patient
  - Recherche cross-collection
- **Avantages**: Recherche naturelle en langage libre, pas besoin de mots-clés exacts

### 4. **Transcription Audio**
**Technologie**: Faster-Whisper
- **Rôle**: Conversion audio → texte
- **Modèle**: Whisper (base/small/medium/large-v2)
- **Fonctionnalités**:
  - Détection automatique de langue
  - Voice Activity Detection (VAD)
  - Transcription segmentée avec timestamps
- **Avantages**: Local, privé, support multilingue (FR/EN)

### 5. **LLM (Large Language Model)**
**Technologie**: Ollama + Llama 3.1 8B
- **Rôle**: Cerveau de l'application - compréhension et génération de texte
- **Modèle**: Llama 3.1 8B (8 milliards de paramètres)
- **Utilisations**:
  1. **Résuméisation de conversations** (`MedicalSummarizer`)
     - Extraction d'informations structurées (diagnostic, recommandations, médicaments)
     - Génération de résumés professionnels
     - Nettoyage et formatage de texte
  2. **Analyse de patterns** (`PatternAnalyzer`)
     - Évolution de la pathologie dans le temps
     - Changements de médicaments
     - Identification de tendances
  3. **Résumé global patient** (`generate_patient_overview`)
     - Synthèse de l'état de santé
     - Vue d'ensemble pour rafraîchir la mémoire du médecin
- **Configuration**:
  - Temperature: 0.3 (cohérence médicale)
  - Format de réponse: JSON structuré
  - Langue: Français (prompts traduits)
- **Avantages**: Local, gratuit, pas de transmission de données sensibles

### 6. **Génération de PDF**
**Technologie**: ReportLab + WeasyPrint
- **Rôle**: Création de documents médicaux professionnels
- **Types de PDF**:
  - Résumé de consultation individuelle
  - Historique médical complet du patient
- **Contenu**: Informations patient, consultations, médicaments, résultats de tests

### 7. **Intégrations Médicales**
**Technologies**: pydicom, LabResultsParser
- **DICOM Parser** (`DICOMParser`):
  - Parsing de fichiers DICOM (IRM, Scanner CT, Radiographie)
  - Extraction de métadonnées (modalité, description, dimensions)
- **Lab Results Parser** (`LabResultsParser`):
  - Parsing de résultats d'analyses (JSON, texte)
  - Normalisation des valeurs et unités
  - Extraction de plages de référence

---

## 🤖 Ce qui Rend l'Application "Agentic"

L'application est **agentic** car elle:

### 1. **Autonomie dans le Traitement**
- **Pipeline automatique**: Audio → Transcription → Résumé → Extraction → Stockage
- **Pas d'intervention manuelle** nécessaire pour structurer les données
- **Décisions automatiques**: Extraction d'entités, catégorisation, organisation

### 2. **Compréhension Contextuelle**
- **Utilise ChromaDB** pour retrouver des contextes similaires
- **Analyse temporelle**: Compare les visites pour identifier des patterns
- **Synthèse intelligente**: Combine informations de multiples sources (visites, tests, médicaments)

### 3. **Apprentissage et Adaptation**
- **Vector Store** apprend des patterns dans les conversations
- **Pattern Analyzer** identifie des tendances dans l'historique
- **Résumés contextuels** qui s'améliorent avec plus de données

### 4. **Actions Proactives**
- **Génération automatique** de résumés et analyses
- **Détection de changements** (nouveaux médicaments, évolution pathologie)
- **Suggestions** basées sur l'historique (via Pattern Analyzer)

### 5. **Intégration Multi-Modalité**
- **Audio** (transcription)
- **Texte** (résumés, notes)
- **Images médicales** (DICOM)
- **Données structurées** (analyses de sang)
- **Tout combiné** dans une vue holistique

---

## 🔄 Flux de Données (Workflow)

### Enregistrement d'une Consultation

```
1. Upload Audio
   ↓
2. Faster-Whisper (Transcription)
   ↓
3. Ollama/Llama (Résuméisation + Extraction)
   ├─→ Résumé structuré (JSON)
   ├─→ Diagnostic
   ├─→ Recommandations
   └─→ Médicaments mentionnés
   ↓
4. Stockage
   ├─→ SQLite (données structurées)
   └─→ ChromaDB (embeddings pour recherche)
   ↓
5. Génération PDF (optionnel)
```

### Recherche Sémantique

```
1. Requête utilisateur (langage naturel)
   ↓
2. ChromaDB (recherche vectorielle)
   ├─→ Similarité sémantique
   └─→ Filtrage par patient
   ↓
3. Résultats contextuels
   └─→ Conversations + Notes médicales
```

### Analyse de Patterns

```
1. Récupération historique patient
   ├─→ Visites (SQLite)
   ├─→ Médicaments (SQLite)
   └─→ Contextes similaires (ChromaDB)
   ↓
2. Ollama/Llama (Analyse)
   ├─→ Évolution pathologie
   ├─→ Changements médicaments
   └─→ Insights
   ↓
3. Stockage analyse (SQLite)
```

---

## 🛠️ Stack Technique Détaillée

### Core Dependencies
- **streamlit** (1.28+): Interface web
- **ollama** (0.1+): Client pour LLM local
- **faster-whisper** (0.10+): Transcription audio optimisée
- **chromadb** (0.4.15+): Base de données vectorielle
- **sqlalchemy** (2.0.23+): ORM pour SQLite
- **pydantic** (2.5+): Validation de données

### Database
- **aiosqlite** (0.19+): SQLite asynchrone

### PDF Generation
- **reportlab** (4.0.7+): Génération PDF
- **weasyprint** (60.1+): Alternative PDF (HTML→PDF)

### Medical Imaging
- **pydicom** (2.4.4+): Parsing DICOM
- **pillow** (10.1+): Traitement d'images

### NLP & Processing
- **spacy** (3.7.2+): Extraction d'entités (optionnel)
- **pandas** (2.1.3+): Manipulation de données
- **numpy** (1.26.2+): Calculs numériques

### Audio Processing
- **pyaudio** (0.2.14+): Enregistrement audio
- **soundfile** (0.12.1+): Lecture/écriture audio

---

## 🔗 Interactions LLM

### Comment Ollama/Llama est Utilisé

1. **Communication**:
   - Via bibliothèque `ollama` (API REST locale)
   - URL: `http://localhost:11434` (par défaut)
   - Modèle: `llama3.1:latest` (8B)

2. **Format des Prompts**:
   - Instructions contextuelles (environnement médical contrôlé)
   - Données réelles du patient
   - Format de réponse attendu (JSON)
   - Langue: Français

3. **Exemples de Prompts**:
   - **Résuméisation**: "Extrayez les informations de cette conversation..."
   - **Analyse**: "Analysez l'évolution de ce patient..."
   - **Résumé global**: "Générez un résumé de 3-5 lignes..."

4. **Post-Traitement**:
   - Extraction JSON depuis réponse texte
   - Validation et nettoyage
   - Stockage structuré

### Pourquoi Agentic?

- **Compréhension sémantique**: Le LLM comprend le contexte médical
- **Extraction intelligente**: Identifie automatiquement les entités importantes
- **Génération contextuelle**: Crée des résumés adaptés au contexte
- **Analyse temporelle**: Compare et identifie des patterns
- **Adaptation**: S'adapte au style et aux besoins du médecin

---

## 🎯 Points Clés de l'Architecture

1. **Local-First**: Tout fonctionne en local, pas de cloud
2. **Privacy-Preserving**: Aucune transmission de données sensibles
3. **Modulaire**: Services séparés, facilement extensibles
4. **Hybrid Storage**: SQLite (structuré) + ChromaDB (sémantique)
5. **Agentic**: Automatisation intelligente avec compréhension contextuelle
6. **Multilingue**: Support FR/EN (transcription + LLM)

---

## 📊 Flux de Données Complet

```
┌─────────────┐
│   Audio     │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│ Faster-     │─────▶│ Transcription│
│ Whisper     │      └──────┬───────┘
└─────────────┘             │
                            ▼
                    ┌──────────────┐
                    │   Ollama/    │
                    │   Llama 3.1  │
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Résumé     │   │  Diagnostic │   │ Recommand.   │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SQLite     │  │  ChromaDB    │  │    PDF       │
│ (Structuré)  │  │ (Vecteurs)   │  │  Generator   │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🚀 Avantages de cette Architecture

1. **Confidentialité**: Données médicales restent locales
2. **Performance**: Pas de latence réseau, traitement rapide
3. **Coût**: Gratuit (pas de coûts cloud/API)
4. **Extensibilité**: Facile d'ajouter de nouveaux services
5. **Intelligence**: Recherche sémantique + analyse de patterns
6. **Autonomie**: Pipeline automatique de bout en bout

---

## 📝 Notes Techniques

- **Temperature LLM**: 0.3 (cohérence médicale importante)
- **Embeddings ChromaDB**: Générés automatiquement (modèle par défaut)
- **Format Audio**: WAV, MP3, M4A, FLAC supportés
- **Langue**: Principalement français (interface + prompts)
- **Stockage**: Tous les fichiers dans `data/` directory

---

*Dernière mise à jour: 2024*

