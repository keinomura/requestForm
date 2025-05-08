#!/bin/bash

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/path/to/backups"  # Change this to your preferred backup directory
DB_USER="felddorf_request_db"
DB_PASSWORD="sakura2rental4db"
DB_HOST="mysql3102.db.sakura.ne.jp"
DB_NAME="felddorf_request_db"
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup_log.txt"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Log start of backup
echo "Starting backup at $(date)" >> $LOG_FILE

# Perform the backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE" >> $LOG_FILE
    
    # Compress the backup file
    gzip $BACKUP_FILE
    echo "Backup compressed: ${BACKUP_FILE}.gz" >> $LOG_FILE
    
    # Delete backups older than 30 days
    find $BACKUP_DIR -name "backup_*.sql.gz" -type f -mtime +30 -delete
    echo "Old backups cleaned up" >> $LOG_FILE
else
    echo "Backup failed!" >> $LOG_FILE
fi

echo "Backup process completed at $(date)" >> $LOG_FILE
echo "----------------------------------------" >> $LOG_FILE
