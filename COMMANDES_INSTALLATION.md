# 🚀 Commandes d'Installation - Fonctionnalité Rapport PDF

## Installation Rapide

### 1. Installer la dépendance reportlab
```bash
pip install reportlab
```

### 2. Tester la fonctionnalité
```bash
python test_report.py
```

### 3. Lancer l'application
```bash
streamlit run Src/app.py
```

---

## Installation Complète (Si Nécessaire)

### Étape 1 : Mettre à jour pip
```bash
python -m pip install --upgrade pip
```

### Étape 2 : Installer toutes les dépendances
```bash
pip install -r requirements.txt
pip install reportlab
```

### Étape 3 : Vérifier l'installation
```bash
python -c "import reportlab; print('reportlab version:', reportlab.Version)"
```

### Étape 4 : Tester le générateur
```bash
python test_report.py
```

### Étape 5 : Lancer l'application
```bash
streamlit run Src/app.py
```

---

## Vérification de l'Installation

### Vérifier reportlab
```bash
python -c "from reportlab.lib.pagesizes import A4; print('✅ reportlab OK')"
```

### Vérifier le module report_generator
```bash
python -c "from Src.report_generator import MedicalReportGenerator; print('✅ report_generator OK')"
```

### Test complet
```bash
python test_report.py
```

**Résultat attendu :**
```
🧪 Testing Report Generator...
📄 Generating report...
✅ Report generated successfully!
📁 Saved to: C:\...\test_report.pdf
📊 File size: 5773 bytes

🎉 All tests passed!
```

---

## Commandes de Dépannage

### Si reportlab ne s'installe pas
```bash
# Essayer avec --upgrade
pip install --upgrade reportlab

# Ou avec --force-reinstall
pip install --force-reinstall reportlab

# Ou avec une version spécifique
pip install reportlab==4.0.0
```

### Si l'import échoue
```bash
# Vérifier le chemin Python
python -c "import sys; print(sys.path)"

# Réinstaller
pip uninstall reportlab
pip install reportlab
```

### Si le test échoue
```bash
# Vérifier les permissions
python test_report.py

# Vérifier les logs
python test_report.py 2>&1 | tee test_log.txt
```

---

## Commandes Utiles

### Voir la version de reportlab
```bash
pip show reportlab
```

### Lister toutes les dépendances
```bash
pip list
```

### Créer un environnement virtuel (recommandé)
```bash
# Créer
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install reportlab
```

---

## Workflow Complet

```bash
# 1. Naviguer vers le projet
cd Alzheimer_Detection

# 2. (Optionnel) Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt
pip install reportlab

# 4. Tester
python test_report.py

# 5. Lancer l'application
streamlit run Src/app.py
```

---

## Vérification Post-Installation

### Dans l'application Streamlit

1. **Ouvrir l'application**
   ```
   http://localhost:8501
   ```

2. **Se connecter**
   - Créer un compte ou utiliser un compte existant

3. **Tester la fonctionnalité**
   - Aller dans l'onglet "Analyze"
   - Uploader une image ou utiliser un échantillon
   - Attendre l'analyse
   - Cliquer sur "Generate Report"
   - Vérifier que le bouton "Download PDF" s'active

4. **Télécharger et vérifier**
   - Cliquer sur "Download PDF"
   - Ouvrir le PDF téléchargé
   - Vérifier le contenu

---

## Commandes de Maintenance

### Mettre à jour reportlab
```bash
pip install --upgrade reportlab
```

### Nettoyer les fichiers de test
```bash
# Windows
del test_report.pdf

# Linux/Mac
rm test_report.pdf
```

### Réinstaller tout
```bash
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
pip install reportlab
```

---

## Résolution de Problèmes Courants

### Erreur : "No module named 'reportlab'"
```bash
Solution: pip install reportlab
```

### Erreur : "Permission denied"
```bash
Solution: pip install --user reportlab
```

### Erreur : "Cannot import name 'MedicalReportGenerator'"
```bash
Solution: Vérifier que Src/report_generator.py existe
```

### Erreur : "PDF generation failed"
```bash
Solution: 
1. Vérifier les logs
2. Tester avec test_report.py
3. Vérifier les permissions d'écriture
```

---

## Support

Si vous rencontrez des problèmes :

1. **Vérifier les logs**
   ```bash
   streamlit run Src/app.py 2>&1 | tee app_log.txt
   ```

2. **Tester le générateur isolément**
   ```bash
   python test_report.py
   ```

3. **Vérifier les versions**
   ```bash
   python --version
   pip --version
   pip show reportlab
   ```

4. **Consulter la documentation**
   - REPORT_FEATURE.md
   - GUIDE_RAPIDE_RAPPORT.md
   - DEMO_RAPPORT.md

---

**Dernière mise à jour :** Janvier 2026  
**Version :** 1.0.0
