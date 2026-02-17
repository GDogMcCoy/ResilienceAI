#!/bin/bash
# ============================================
# RESILIENCEAI RESTORE SCRIPT
# Database recovery procedures for PostgreSQL, TimescaleDB, and Redis
# ============================================

set -e

# Configuration
S3_BUCKET="${S3_BUCKET:-s3://resilienceai-backups}"
RESTORE_DIR="${RESTORE_DIR:-/tmp/restore}"
DB_NAME="${DB_NAME:-resilienceai}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Logging
LOG_FILE="${RESTORE_DIR}/restore_$(date +%Y%m%d_%H%M%S).log"

# Create restore directory
mkdir -p "$RESTORE_DIR"

# Function to log messages
log() {
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$message"
    echo "$message" >> "$LOG_FILE"
}

# Function to send alert
send_alert() {
    local message="Restore failed: $1"
    log "ERROR: $message"
    
    if command -v aws &> /dev/null && [ -n "${SNS_ALERT_TOPIC:-}" ]; then
        aws sns publish \
            --topic-arn "$SNS_ALERT_TOPIC" \
            --message "$message" \
            --subject "ResilienceAI Restore Failure" 2>/dev/null || true
    fi
}

# ============================================
# LIST AND DOWNLOAD
# ============================================

# List available backups
list_backups() {
    log "Available backups in S3:"
    
    echo ""
    echo "Full Backups:"
    aws s3 ls "$S3_BUCKET/full/" | tail -20
    
    echo ""
    echo "Incremental Backups:"
    aws s3 ls "$S3_BUCKET/incremental/" | tail -10
    
    echo ""
    echo "Schema Backups:"
    aws s3 ls "$S3_BUCKET/schema/" | tail -10
}

# Download backup from S3
download_backup() {
    local backup_type=$1
    local backup_date=$2
    
    log "Downloading $backup_type backup from $backup_date..."
    
    local s3_prefix="$S3_BUCKET/$backup_type/$backup_date/"
    local local_dir="$RESTORE_DIR/$backup_type/$backup_date"
    
    mkdir -p "$local_dir"
    
    # Download all files from the backup date
    aws s3 sync "$s3_prefix" "$local_dir/" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "Backup downloaded to: $local_dir"
        echo "$local_dir"
    else
        send_alert "Failed to download backup from S3"
        return 1
    fi
}

# Download specific backup file
download_backup_file() {
    local s3_path=$1
    local local_path=$2
    
    log "Downloading $s3_path..."
    
    mkdir -p "$(dirname "$local_path")"
    aws s3 cp "$s3_path" "$local_path" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "Downloaded to: $local_path"
        echo "$local_path"
    else
        send_alert "Failed to download $s3_path"
        return 1
    fi
}

# ============================================
# RESTORE FUNCTIONS
# ============================================

# Restore PostgreSQL full backup
restore_postgres_full() {
    local backup_file=$1
    
    log "Restoring PostgreSQL full backup from $backup_file..."
    
    # Verify backup file exists
    if [ ! -f "$backup_file" ]; then
        send_alert "Backup file not found: $backup_file"
        return 1
    fi
    
    # Confirm with user if interactive
    if [ -t 0 ]; then
        read -p "This will DESTROY the existing database. Continue? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            log "Restore cancelled by user"
            exit 0
        fi
    fi
    
    # Stop application connections (optional)
    log "Stopping application connections..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = '$DB_NAME' 
          AND pid <> pg_backend_pid();
    " 2>/dev/null || true
    
    # Drop and recreate database
    log "Dropping and recreating database..."
    dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --if-exists "$DB_NAME" 2>> "$LOG_FILE"
    createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>> "$LOG_FILE"
    
    # Restore from backup
    log "Restoring from backup (this may take a while)..."
    pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --no-owner \
        --no-privileges \
        --jobs=4 \
        "$backup_file" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "PostgreSQL full restore completed successfully"
    else
        send_alert "PostgreSQL restore failed"
        return 1
    fi
}

# Restore specific table
restore_table() {
    local backup_file=$1
    local table_name=$2
    
    log "Restoring table: $table_name from $backup_file"
    
    # Truncate existing table
    log "Truncating existing table..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -c "TRUNCATE TABLE $table_name CASCADE;" 2>> "$LOG_FILE"
    
    # Restore table data
    log "Restoring table data..."
    pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --table="$table_name" \
        --data-only \
        --verbose \
        "$backup_file" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "Table restore completed: $table_name"
    else
        log "WARNING: Table restore may have issues: $table_name"
    fi
}

# Restore schema only
restore_schema() {
    local schema_file=$1
    
    log "Restoring schema from $schema_file..."
    
    # Apply schema
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        -f "$schema_file" 2>> "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "Schema restore completed"
    else
        send_alert "Schema restore failed"
        return 1
    fi
}

# Point-in-time recovery (PITR)
restore_pitr() {
    local target_timestamp=$1
    local base_backup=$2
    
    log "Performing point-in-time recovery to: $target_timestamp"
    
    # Confirm with user
    if [ -t 0 ]; then
        read -p "This will DESTROY the existing database. Continue? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            log "PITR cancelled by user"
            exit 0
        fi
    fi
    
    # Stop PostgreSQL
    log "Stopping PostgreSQL..."
    systemctl stop postgresql || service postgresql stop
    
    # Clean data directory
    log "Cleaning data directory..."
    rm -rf /var/lib/postgresql/data/*
    
    # Restore base backup
    log "Restoring base backup..."
    if [ -f "$base_backup" ]; then
        # Custom format backup
        pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
            --dbname=postgres \
            --create \
            "$base_backup"
    else
        # Directory format backup
        cp -r "$base_backup"/* /var/lib/postgresql/data/
    fi
    
    # Create recovery configuration
    log "Configuring point-in-time recovery..."
    cat > /var/lib/postgresql/data/postgresql.auto.conf << EOF
# Recovery configuration
restore_command = 'aws s3 cp $S3_BUCKET/wal/%f %p 2>/dev/null || exit 0'
recovery_target_time = '$target_timestamp'
recovery_target_action = 'promote'
recovery_target_inclusive = true
EOF
    
    # Create recovery signal file
    touch /var/lib/postgresql/data/recovery.signal
    
    # Set correct ownership
    chown -R postgres:postgres /var/lib/postgresql/data
    chmod 700 /var/lib/postgresql/data
    
    # Start PostgreSQL for recovery
    log "Starting PostgreSQL for recovery..."
    systemctl start postgresql || service postgresql start
    
    # Monitor recovery progress
    log "Monitoring recovery progress..."
    local attempts=0
    while [ $attempts -lt 300 ]; do
        if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
            sleep 1
            attempts=$((attempts + 1))
            continue
        fi
        
        # Check if recovery is complete
        local recovery_status=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            -t -c "SELECT pg_is_in_recovery();" 2>/dev/null | tr -d ' ')
        
        if [ "$recovery_status" = "f" ]; then
            log "Point-in-time recovery completed"
            break
        fi
        
        sleep 2
        attempts=$((attempts + 2))
    done
    
    if [ $attempts -ge 300 ]; then
        send_alert "PITR timed out"
        return 1
    fi
    
    log "Point-in-time recovery completed successfully"
}

# Restore Redis
restore_redis() {
    local backup_file=$1
    
    log "Restoring Redis from $backup_file..."
    
    # Verify backup file
    if [ ! -f "$backup_file" ]; then
        send_alert "Redis backup file not found: $backup_file"
        return 1
    fi
    
    # Stop Redis
    log "Stopping Redis..."
    systemctl stop redis || service redis stop || redis-cli SHUTDOWN
    
    sleep 2
    
    # Restore dump file
    log "Restoring dump file..."
    cp "$backup_file" /var/lib/redis/dump.rdb
    chown redis:redis /var/lib/redis/dump.rdb
    chmod 644 /var/lib/redis/dump.rdb
    
    # Start Redis
    log "Starting Redis..."
    systemctl start redis || service redis start
    
    # Verify Redis is running
    sleep 2
    if redis-cli PING | grep -q "PONG"; then
        log "Redis restore completed successfully"
    else
        send_alert "Redis restore failed - service not responding"
        return 1
    fi
}

# ============================================
# VERIFICATION
# ============================================

verify_restore() {
    log "Verifying restore..."
    
    # Check database connectivity
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
        send_alert "Database not accessible after restore"
        return 1
    fi
    
    # Check table counts
    log "Checking table counts..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << EOF 2>> "$LOG_FILE"
\echo 'Table Counts:'
SELECT 
    'counties' as table_name, COUNT(*) as row_count FROM counties
UNION ALL
SELECT 'county_features', COUNT(*) FROM county_features
UNION ALL
SELECT 'feature_definitions', COUNT(*) FROM feature_definitions
UNION ALL
SELECT 'alert_events', COUNT(*) FROM alert_events
UNION ALL
SELECT 'alert_subscriptions', COUNT(*) FROM alert_subscriptions;
EOF
    
    # Check TimescaleDB
    log "Checking TimescaleDB..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" << EOF 2>> "$LOG_FILE"
\echo 'TimescaleDB Hypertables:'
SELECT hypertable_name, num_dimensions, num_chunks 
FROM timescaledb_information.hypertables;
EOF
    
    # Check Redis
    log "Checking Redis..."
    redis-cli INFO keyspace 2>> "$LOG_FILE"
    
    log "Verification completed"
}

# ============================================
# MAIN EXECUTION
# ============================================

show_usage() {
    cat << EOF
Usage: $0 {list|full|table|schema|pitr|redis|verify} [options]

Commands:
    list                    List available backups
    full <date>             Restore full backup from date (YYYYMMDD)
    table <date> <table>    Restore specific table from backup
    schema <date>           Restore schema only
    pitr <timestamp>        Point-in-time recovery to timestamp
    redis <date>            Restore Redis backup
    verify                  Verify current database state

Examples:
    $0 list
    $0 full 20240217
    $0 table 20240217 county_features
    $0 pitr "2024-02-17 14:30:00"
    $0 redis 20240217
EOF
}

main() {
    local command=$1
    shift
    
    case "$command" in
        list)
            list_backups
            ;;
            
        full)
            local backup_date=$1
            if [ -z "$backup_date" ]; then
                log "Error: Backup date required (YYYYMMDD)"
                show_usage
                exit 1
            fi
            
            local backup_dir=$(download_backup "full" "$backup_date")
            local backup_file=$(find "$backup_dir" -name "*.dump" | head -1)
            
            restore_postgres_full "$backup_file"
            verify_restore
            ;;
            
        table)
            local backup_date=$1
            local table_name=$2
            
            if [ -z "$backup_date" ] || [ -z "$table_name" ]; then
                log "Error: Backup date and table name required"
                show_usage
                exit 1
            fi
            
            local backup_dir=$(download_backup "full" "$backup_date")
            local backup_file=$(find "$backup_dir" -name "*.dump" | head -1)
            
            restore_table "$backup_file" "$table_name"
            verify_restore
            ;;
            
        schema)
            local backup_date=$1
            if [ -z "$backup_date" ]; then
                log "Error: Backup date required"
                show_usage
                exit 1
            fi
            
            local backup_dir=$(download_backup "schema" "$backup_date")
            local schema_file=$(find "$backup_dir" -name "*.sql" | head -1)
            
            restore_schema "$schema_file"
            verify_restore
            ;;
            
        pitr)
            local target_timestamp=$1
            if [ -z "$target_timestamp" ]; then
                log "Error: Target timestamp required (e.g., '2024-02-17 14:30:00')"
                show_usage
                exit 1
            fi
            
            # Find most recent base backup
            log "Finding most recent base backup..."
            local latest_backup=$(aws s3 ls "$S3_BUCKET/full/" | sort | tail -1 | awk '{print $2}')
            local backup_dir=$(download_backup "full" "${latest_backup%/}")
            local backup_file=$(find "$backup_dir" -name "*.dump" | head -1)
            
            restore_pitr "$target_timestamp" "$backup_file"
            verify_restore
            ;;
            
        redis)
            local backup_date=$1
            if [ -z "$backup_date" ]; then
                log "Error: Backup date required"
                show_usage
                exit 1
            fi
            
            local backup_dir=$(download_backup "redis" "$backup_date")
            local backup_file=$(find "$backup_dir" -name "*.rdb" | head -1)
            
            restore_redis "$backup_file"
            ;;
            
        verify)
            verify_restore
            ;;
            
        *)
            show_usage
            exit 1
            ;;
    esac
    
    # Cleanup
    log "Cleaning up restore directory..."
    rm -rf "$RESTORE_DIR"
    
    log "Restore process completed"
}

# Run main function
main "$@"
