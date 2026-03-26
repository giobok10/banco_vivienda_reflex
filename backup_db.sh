#!/bin/bash
# Backup automatizado - Banco de Vivienda
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# En lugar de hardcodearla, la tomamos del entorno o fallamos
if [ -z "$DB_PASSWORD" ]; then
    echo "Error: Variable DB_PASSWORD no definida."
    # export PGPASSWORD='PasswordSeguro123' # Solo para pruebas locales
fi

pg_dump -h $DB_HOST -U $DB_USER -d neondb > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "Backup completado."