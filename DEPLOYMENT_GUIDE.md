# Guide de Déploiement - Agentic Medical Assistant

## Options de Déploiement

### Option 1: SaaS Centralisé (Serveur Local)

#### Architecture
```
┌─────────────────────────────────────────┐
│  Serveur Central (Votre Machine)       │
│  - Streamlit (port 8501)               │
│  - Ollama (port 11434)                 │
│  - SQLite + ChromaDB                   │
│  - Faster-Whisper                      │
└──────────────┬──────────────────────────┘
               │
               │ Réseau Local/VPN
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│ Doc 1 │  │ Doc 2 │  │ Doc 3 │
│ PC    │  │ PC    │  │ PC    │
└───────┘  └───────┘  └───────┘
```

#### Avantages ✅
- **Maintenance centralisée**: Une seule installation à maintenir
- **Mises à jour faciles**: Mettre à jour une fois, tous les médecins bénéficient
- **Pas d'installation client**: Accès via navigateur web
- **Gestion centralisée des données**: Backup unique, monitoring centralisé
- **Ressources partagées**: Un seul serveur avec GPU/CPU puissant

#### Inconvénients ❌
- **Dépendance réseau**: Nécessite connexion stable
- **Sécurité réseau**: Doit configurer firewall, VPN, HTTPS
- **Latence**: Si serveur distant, peut être lent
- **Point de défaillance unique**: Si serveur tombe, tous affectés
- **Conformité HIPAA**: Plus complexe (données transitent sur réseau)

#### Configuration Requise

**1. Configuration Streamlit pour accès réseau:**

Créer `streamlit_config.toml`:
```toml
[server]
port = 8501
address = "0.0.0.0"  # Écoute sur toutes les interfaces
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

**2. Lancer avec accès réseau:**
```bash
streamlit run ui/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

**3. Configuration Firewall:**
```bash
# macOS
sudo pfctl -f /etc/pf.conf

# Linux
sudo ufw allow 8501/tcp
```

**4. Accès via IP:**
- Médecins accèdent via: `http://VOTRE_IP:8501`
- Ou configurer un nom de domaine local: `http://medical-assistant.local:8501`

**5. Sécurité (IMPORTANT):**
```bash
# Option 1: VPN (Recommandé)
# Configurer un VPN (WireGuard, OpenVPN) pour accès sécurisé

# Option 2: HTTPS avec reverse proxy
# Utiliser nginx + Let's Encrypt pour HTTPS

# Option 3: Authentification Streamlit
# Ajouter authentification dans streamlit_app.py
```

---

### Option 2: Installation Locale (Chaque Machine)

#### Architecture
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PC Doc 1    │  │  PC Doc 2    │  │  PC Doc 3    │
│  - Streamlit │  │  - Streamlit │  │  - Streamlit │
│  - Ollama    │  │  - Ollama    │  │  - Ollama    │
│  - DB Local  │  │  - DB Local  │  │  - DB Local  │
└──────────────┘  └──────────────┘  └──────────────┘
```

#### Avantages ✅
- **Confidentialité maximale**: Données jamais sur réseau
- **Performance optimale**: Pas de latence réseau
- **Indépendance**: Chaque médecin indépendant
- **Conformité HIPAA**: Plus simple (données restent locales)
- **Pas de dépendance réseau**: Fonctionne offline

#### Inconvénients ❌
- **Maintenance distribuée**: Mettre à jour chaque machine
- **Installation requise**: Sur chaque PC
- **Ressources dupliquées**: Chaque PC doit avoir GPU/CPU
- **Backup complexe**: Gérer backups de chaque machine
- **Synchronisation**: Pas de partage de données entre médecins

#### Installation Simplifiée

**1. Script d'installation automatique:**

Créer `install.sh`:
```bash
#!/bin/bash
echo "Installation de Agentic Medical Assistant..."

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Installer Ollama (si pas déjà installé)
if ! command -v ollama &> /dev/null; then
    echo "Installation d'Ollama..."
    # macOS
    brew install ollama
    # Linux
    # curl -fsSL https://ollama.ai/install.sh | sh
fi

# Télécharger modèle Llama
ollama pull llama3.1:latest

echo "Installation terminée!"
echo "Lancez avec: python main.py"
```

**2. Package distributable:**

Créer un installer avec PyInstaller:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

---

## Recommandation: Approche Hybride

### Architecture Recommandée

```
┌─────────────────────────────────────────┐
│  Serveur Central (Backup/Sync)         │
│  - Base de données de backup           │
│  - Synchronisation (optionnelle)       │
└──────────────┬──────────────────────────┘
               │
               │ Sync périodique (chiffré)
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐  ┌───▼───┐  ┌───▼───┐
│ Doc 1 │  │ Doc 2 │  │ Doc 3 │
│ Local │  │ Local │  │ Local │
└───────┘  └───────┘  └───────┘
```

### Pourquoi Hybride?

1. **Installation locale** pour:
   - Confidentialité maximale
   - Performance
   - Conformité HIPAA simplifiée

2. **Serveur central** pour:
   - Backups automatiques
   - Mises à jour centralisées (optionnel)
   - Monitoring

---

## Comparaison Détaillée

| Critère | SaaS Centralisé | Installation Locale | Hybride |
|---------|----------------|---------------------|---------|
| **Confidentialité** | ⚠️ Moyenne | ✅ Excellente | ✅ Excellente |
| **Performance** | ⚠️ Dépend du réseau | ✅ Optimale | ✅ Optimale |
| **Maintenance** | ✅ Facile | ❌ Complexe | ⚠️ Moyenne |
| **Mises à jour** | ✅ Centralisées | ❌ Manuelles | ⚠️ Semi-auto |
| **Coût serveur** | ❌ Élevé | ✅ Aucun | ⚠️ Modéré |
| **Conformité HIPAA** | ⚠️ Complexe | ✅ Simple | ✅ Simple |
| **Dépendance réseau** | ❌ Oui | ✅ Non | ⚠️ Partielle |
| **Scalabilité** | ✅ Facile | ❌ Limitée | ⚠️ Moyenne |

---

## Recommandation Finale

### Pour une Clinique Petite/Moyenne (< 10 médecins):

**✅ Installation Locale** avec script d'installation automatique

**Raisons:**
- Données médicales sensibles → confidentialité prioritaire
- Conformité HIPAA plus simple
- Performance optimale
- Pas de coût serveur

**Script d'installation:**
- Automatise l'installation sur chaque PC
- Mises à jour via script également

### Pour une Grande Clinique (> 10 médecins):

**✅ SaaS Centralisé** avec VPN/HTTPS

**Raisons:**
- Maintenance centralisée plus importante
- Gestion centralisée des données
- Monitoring centralisé

**Sécurité requise:**
- VPN obligatoire
- HTTPS avec certificat
- Authentification forte
- Audit logs

---

## Configuration SaaS (Si Choisi)

### 1. Fichier de configuration réseau

Créer `.streamlit/config.toml`:
```toml
[server]
headless = true
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
serverAddress = "VOTRE_IP_OU_DOMAINE"
```

### 2. Script de démarrage serveur

Créer `start_server.sh`:
```bash
#!/bin/bash

# Démarrer Ollama
ollama serve &

# Attendre qu'Ollama soit prêt
sleep 5

# Démarrer Streamlit
streamlit run ui/streamlit_app.py \
    --server.address=0.0.0.0 \
    --server.port=8501 \
    --server.headless=true
```

### 3. Service Systemd (Linux)

Créer `/etc/systemd/system/medical-assistant.service`:
```ini
[Unit]
Description=Agentic Medical Assistant
After=network.target

[Service]
Type=simple
User=medical
WorkingDirectory=/opt/medical-assistant
ExecStart=/opt/medical-assistant/venv/bin/streamlit run ui/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Reverse Proxy Nginx (HTTPS)

Créer `/etc/nginx/sites-available/medical-assistant`:
```nginx
server {
    listen 443 ssl;
    server_name medical-assistant.votre-domaine.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Sécurité pour SaaS

### Checklist Sécurité

- [ ] **VPN configuré** pour accès réseau
- [ ] **HTTPS activé** (Let's Encrypt)
- [ ] **Firewall configuré** (port 8501 uniquement depuis VPN)
- [ ] **Authentification** dans l'application
- [ ] **Audit logs** activés
- [ ] **Backups automatiques** configurés
- [ ] **Chiffrement au repos** (disque chiffré)
- [ ] **Mises à jour de sécurité** régulières

### Ajout d'Authentification

Modifier `ui/streamlit_app.py`:
```python
import streamlit_authenticator as stauth

# Configuration utilisateurs
users = {
    "docteur1": {
        "name": "Dr. Martin",
        "password": stauth.Hasher(["motdepasse"]).generate()[0]
    }
}

authenticator = stauth.Authenticate(
    users,
    "medical_cookie",
    "medical_key",
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password incorrect")
    st.stop()
elif authentication_status == None:
    st.warning("Please enter your username and password")
    st.stop()

# Reste de l'application...
```

---

## Conclusion

**Pour votre cas (clinique médicale):**

1. **< 5 médecins**: Installation locale avec script auto
2. **5-10 médecins**: Installation locale + serveur backup
3. **> 10 médecins**: SaaS centralisé avec VPN/HTTPS

**Priorité absolue**: Confidentialité des données médicales → Installation locale recommandée sauf si infrastructure réseau sécurisée en place.


