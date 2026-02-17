#!/bin/bash
# ============================================
# RESILIENCEAI BACKUP SCRIPT
# Automated backup for PostgreSQL, TimescaleDB, and Redis
# ============================================

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup/resilienceai}"
S3_BUCKET="${S3_BUCKET:-s3://resilienceai-backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DATE=$(date +%Y%m%d_%H%M%S)
DATE_SHORT=$(date +%Y%m%d)

# Database credentials
DB_NAME="${DB_NAME:-resilienceai}"
DB_USER="${DB_USER:-backup_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Redis configuration
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Logging
LOG_FILE="${BACKUP_DIR}/logs/backup_${DATE}.log"

# Create directories
mkdir -p "$BACKUP_DIR"/{full,incremental,schema,redis,logs}

# Function to log messages
log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$message"
    echo "$message" >> "$LOG_FILE"
}

# Function to send alert on failure
send_alert() {
    local message="Backup failed: $1"
    log "ERROR: $message"
    
    # Send to CloudWatch or other monitoring
    if command -v aws &> /dev/null; then
        aws sns publish \
            --topic-arn "${SNS_ALERT_TOPIC:-}" \
            --message "$message" \
            --subject "ResilienceAI Backup Failure" 2>/dev/null || true
    fi
}

# ============================================
# BACKUP FUNCTIONS
# ============================================

# 1. PostgreSQL Full Backup (Weekly)
backup_postgres_full() {
    log "Starting PostgreSQL full backup..."
    
    local backup_file="$BACKUP_DIR/full/postgres_${DATE}.dump"
    
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$backup_file" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "PostgreSQL full backup completed: $backup_file"
        echo "$backup_file"
    else
        send_alert "PostgreSQL full backup failed"
        return 1
    fi
}

# 2. PostgreSQL Incremental (Daily - using WAL archiving)
backup_postgres_incremental() {
    log "Starting PostgreSQL incremental backup..."
    
    # Trigger WAL switch to ensure all changes are archived
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "SELECT pg_switch_wal();" 2>> "$LOG_FILE"
    
    # Backup WAL files
    local wal_backup="$BACKUP_DIR/incremental/wal_${DATE}.tar.gz"
    
    if [ -d "/var/lib/postgresql/wal_archive/" ]; then
        tar -czf "$wal_backup" /var/lib/postgresql/wal_archive/ 2>> "$LOG_FILE"
        log "WAL backup completed: $wal_backup"
        echo "$wal_backup"
    else
        log "WAL archive directory not found, skipping"
    fi
}

# 3. Schema-only backup
backup_schema() {
    log "Starting schema backup..."
    
    local schema_file="$BACKUP_DIR/schema/schema_${DATE}.sql"
    
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --schema-only \
        --verbose \
        --file="$schema_file" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "Schema backup completed: $schema_file"
        echo "$schema_file"
    else
        send_alert "Schema backup failed"
        return 1
    fi
}

# 4. Specific table backups (high-value tables)
backup_critical_tables() {
    log "Starting critical table backups..."
    
    local tables_dir="$BACKUP_DIR/tables_${DATE}"
    mkdir -p "$tables_dir"
    
    local tables=("counties" "county_features" "alert_events" "feature_definitions" "alert_subscriptions")
    
    for table in "${tables[@]}"; do
        local table_file="$tables_dir/${table}.dump"
        
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            --table="$table" \
            --format=custom \
            --verbose \
            --file="$table_file" 2>> "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            log "Backed up table: $table"
        else
            log "WARNING: Failed to backup table: $table"
        fi
    done
    
    echo "$tables_dir"
}

# 5. TimescaleDB backup
backup_timescaledb() {
    log "Starting TimescaleDB backup..."
    
    local ts_backup="$BACKUP_DIR/full/timescaledb_${DATE}.dump"
    
    # Use timescaledb-backup tool if available
    if command -v timescaledb-backup &> /dev/null; then
        timescaledb-backup dump \
            --db-name="$DB_NAME" \
            --output="$ts_backup" 2>> "$LOG_FILE"
    else
        # Fallback to regular pg_dump with TimescaleDB options
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            --format=custom \
            --verbose \
            --file="$ts_backup" \
            --exclude-table='_timescaledb_internal.*' 2>> "$LOG_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        log "TimescaleDB backup completed: $ts_backup"
        echo "$ts_backup"
    else
        send_alert "TimescaleDB backup failed"
        return 1
    fi
}

# 6. Redis backup
backup_redis() {
    log "Starting Redis backup..."
    
    local redis_backup="$BACKUP_DIR/redis/redis_${DATE}.rdb"
    
    # Trigger BGSAVE
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" BGSAVE 2>> "$LOG_FILE"
    
    # Wait for background save to complete
    local attempts=0
    while [ $attempts -lt 30 ]; do
        if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO persistence | grep -q "rdb_bgsave_in_progress:1"; then
            break
        fi
        sleep 1
        attempts=$((attempts + 1))
    done
    
    # Copy dump file
    if [ -f "/var/lib/redis/dump.rdb" ]; then
        cp /var/lib/redis/dump.rdb "$redis_backup"
        log "Redis backup completed: $redis_backup"
        echo "$redis_backup"
    else
        log "WARNING: Redis dump file not found"
        return 1
    fi
}

# 7. Configuration backup
backup_config() {
    log "Starting configuration backup..."
    
    local config_dir="$BACKUP_DIR/config_${DATE}"
    mkdir -p "$config_dir"
    
    # Backup PostgreSQL configuration
    if [ -d "/etc/postgresql" ]; then
        cp -r /etc/postgresql "$config_dir/" 2>/dev/null || true
    fi
    
    # Backup PgBouncer configuration
    if [ -f "/etc/pgbouncer/pgbouncer.ini" ]; then
        cp /etc/pgbouncer/pgbouncer.ini "$config_dir/" 2>/dev/null || true
    fi
    
    # Backup Redis configuration
    if [ -f "/etc/redis/redis.conf" ]; then
        cp /etc/redis/redis.conf "$config_dir/" 2>/dev/null || true
    fi
    
    log "Configuration backup completed"
    echo "$config_dir"
}

# ============================================
# UPLOAD AND CLEANUP
# ============================================

# Compress and upload to S3
upload_to_s3() {
    local backup_type=$1
    local source_dir=$2
    
    log "Uploading $backup_type backup to S3..."
    
    local s3_key="$backup_type/${DATE_SHORT}/"
    
    # Upload individual files
    if [ -d "$source_dir" ]; then
        aws s3 sync "$source_dir" "$S3_BUCKET/$s3_key" --storage-class STANDARD_IA 2>> "$LOG_FILE"
    elif [ -f "$source_dir" ]; then
        aws s3 cp "$source_dir" "$S3_BUCKET/$s3_key" --storage-class STANDARD_IA 2>> "$LOG_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        log "Upload to S3 completed: $s3_key"
    else
        send_alert "S3 upload failed for $backup_type"
        return 1
    fi
}

# Create backup manifest
create_manifest() {
    local manifest_file="$BACKUP_DIR/backup_manifest_${DATE}.json"
    
    cat > "$manifest_file" << EOF
{
    "backup_date": "$DATE",
    "backup_type": "$1",
    "database": "$DB_NAME",
    "host": "$DB_HOST",
    "files": [
$(find "$BACKUP_DIR" -name "*${DATE}*" -type f | sed 's/^/        "/;s/$/",/' | sed '$ s/,$//')
    ],
    "retention_days": $RETENTION_DAYS
}
EOF
    
    log "Manifest created: $manifest_file"
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
    
    # Local cleanup
    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
    find "$BACKUP_DIR" -type d -empty -delete 2>/dev/null || true
    
    # S3 cleanup
    if command -v aws &> /dev/null; then
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" +%Y-%m-%d)
        
        aws s3 ls "$S3_BUCKET/" | while read -r line; do
            local dir_name=$(echo "$line" | awk '{print $2}')
            local dir_date=$(echo "$dir_name" | grep -oP '^\d{8}' || echo "")
            
            if [ -n "$dir_date" ]; then
                local dir_date_formatted="${dir_date:0:4}-${dir_date:4:2}-${dir_date:6:2}"
                if [[ "$dir_date_formatted" < "$cutoff_date" ]]; then
                    aws s3 rm "$S3_BUCKET/$dir_name" --recursive 2>> "$LOG_FILE"
                    log "Deleted old S3 backup: $dir_name"
                fi
            fi
        done
    fi
    
    log "Cleanup completed"
}

# ============================================
# MAIN EXECUTION
# ============================================

main() {
    local backup_type="${1:-full}"
    
    log "=========================================="
    log "Starting backup process (type: $backup_type)"
    log "=========================================="
    
    case "$backup_type" in
        full)
            log "Running full backup..."
            
            # Run all backup types
            backup_postgres_full
            backup_schema
            backup_critical_tables
            backup_timescaledb
            backup_redis
            backup_config
            
            # Upload to S3
            upload_to_s3 "full" "$BACKUP_DIR/full/"
            upload_to_s3 "schema" "$BACKUP_DIR/schema/"
            upload_to_s3 "redis" "$BACKUP_DIR/redis/"
            
            # Create manifest
            create_manifest "full"
            
            # Cleanup
            cleanup_old_backups
            ;;
            
        incremental)
            log "Running incremental backup..."
            
            backup_postgres_incremental
            upload_to_s3 "incremental" "$BACKUP_DIR/incremental/"
            
            create_manifest "incremental"
            ;;
            
        schema)
            log "Running schema backup..."
            
            backup_schema
            upload_to_s3 "schema" "$BACKUP_DIR/schema/"
            
            create_manifest "schema"
            ;;
            
        redis)
            log "Running Redis backup..."
            
            backup_redis
            upload_to_s3 "redis" "$BACKUP_DIR/redis/"
            
            create_manifest "redis"
            ;;
            
        *)
            echo "Usage: $0 {full|incremental|schema|redis}"
            exit 1
            ;;
    esac
    
    log "=========================================="
    log "Backup process completed successfully"
    log "=========================================="
}

# Run main function
main "$@"
