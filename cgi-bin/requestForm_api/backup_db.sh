#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Configuration
# バックアップディレクトリの設定
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Database connection info from environment variables
# 環境変数からデータベース接続情報を読み込む
# DATABASE_URLの形式: mysql+pymysql://user:password@host/dbname
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL is not set in .env file"
    exit 1
fi

# Parse DATABASE_URL to extract credentials
# DATABASE_URLをパースして認証情報を抽出
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^\/]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"
LOG_FILE="${BACKUP_DIR}/backup_log.txt"

# Log start of backup
echo "Starting backup at $(date)" >> $LOG_FILE

# 接続情報を表示
echo "=== mysqldump 接続情報 ==="
echo "HOST: $DB_HOST"
echo "USER: $DB_USER"
echo "PASS: $DB_PASSWORD"
echo "DB  : $DB_NAME"
echo "========================="


# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Log start of backup
echo "Starting backup at $(date)" >> $LOG_FILE

# Perform the backup
mysqldump --no-tablespaces -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_FILE

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
