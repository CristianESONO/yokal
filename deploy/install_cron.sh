#!/bin/bash
# Script d'installation des cron jobs Yokalma
# Usage: bash deploy/install_cron.sh

set -e

# Configuration - MODIFIEZ CES VALEURS
PROJECT_DIR="/path/to/yokal"  # Chemin absolu vers votre projet
PYTHON_VENV="/path/to/python/venv/bin/python"  # Chemin vers votre venv python
LOG_DIR="/var/log/yokal"  # Répertoire de logs

# Créer le répertoire de logs s'il n'existe pas
sudo mkdir -p "$LOG_DIR"
sudo chown $USER:$USER "$LOG_DIR"

# Créer le fichier crontab temporaire
TEMP_CRON=$(mktemp)

# Copier le fichier crontab en remplaçant les variables
sed "s|/path/to/yokal|$PROJECT_DIR|g; s|/path/to/python/venv/bin/python|$PYTHON_VENV|g" deploy/crontab.txt > "$TEMP_CRON"

# Installer le crontab
crontab "$TEMP_CRON"

# Nettoyer
rm "$TEMP_CRON"

echo "✅ Cron jobs installés avec succès !"
echo "📝 Logs disponibles dans: $LOG_DIR/cron.log"
echo "🔍 Vérifiez avec: crontab -l"
