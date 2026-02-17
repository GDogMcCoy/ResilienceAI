# RDS Configuration for ResilienceAI Multi-Region DR

# Primary RDS Instance
resource "aws_db_instance" "primary" {
  provider = aws.primary
  
  identifier = "resilienceai-primary-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = "resilienceai"
  username = "admin"
  password = var.db_password
  
  multi_az               = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds_primary.id]
  db_subnet_group_name   = aws_db_subnet_group.primary.name
  
  backup_retention_period = 35
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "resilienceai-primary-final"
  
  tags = {
    Name = "resilienceai-primary-db"
  }
}

# DR RDS Instance (read replica)
resource "aws_db_instance" "dr_replica" {
  provider = aws.dr
  
  identifier = "resilienceai-dr-db"
  
  replicate_source_db = aws_db_instance.primary.arn
  
  instance_class = "db.r6g.large"
  
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds_dr.id]
  db_subnet_group_name   = aws_db_subnet_group.dr.name
  
  backup_retention_period = 35
  backup_window          = "03:00-04:00"
  
  auto_minor_version_upgrade = true
  
  tags = {
    Name = "resilienceai-dr-db"
  }
}

# Primary DB Subnet Group
resource "aws_db_subnet_group" "primary" {
  provider = aws.primary
  
  name       = "resilienceai-primary-db-subnet"
  subnet_ids = module.vpc_primary.private_subnets
  
  tags = {
    Name = "resilienceai-primary-db-subnet"
  }
}

# DR DB Subnet Group
resource "aws_db_subnet_group" "dr" {
  provider = aws.dr
  
  name       = "resilienceai-dr-db-subnet"
  subnet_ids = module.vpc_dr.private_subnets
  
  tags = {
    Name = "resilienceai-dr-db-subnet"
  }
}

# Security Groups
resource "aws_security_group" "rds_primary" {
  provider = aws.primary
  
  name_prefix = "rds-primary-"
  vpc_id      = module.vpc_primary.vpc_id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_primary]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "rds-primary-sg"
  }
}

resource "aws_security_group" "rds_dr" {
  provider = aws.dr
  
  name_prefix = "rds-dr-"
  vpc_id      = module.vpc_dr.vpc_id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_dr, var.vpc_cidr_primary]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "rds-dr-sg"
  }
}

# DynamoDB Global Tables
resource "aws_dynamodb_global_table" "sessions" {
  provider = aws.primary
  
  name = "resilienceai-sessions"
  
  replica {
    region_name = var.primary_region
  }
  
  replica {
    region_name = var.dr_region
  }
  
  depends_on = [aws_dynamodb_table.sessions_primary]
}

resource "aws_dynamodb_table" "sessions_primary" {
  provider = aws.primary
  
  name         = "resilienceai-sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "session_id"
  
  attribute {
    name = "session_id"
    type = "S"
  }
  
  attribute {
    name = "user_id"
    type = "S"
  }
  
  global_secondary_index {
    name            = "user_id-index"
    hash_key        = "user_id"
    projection_type = "ALL"
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  server_side_encryption {
    enabled = true
  }
  
  tags = {
    Name = "resilienceai-sessions"
  }
}

# ElastiCache Redis (Global Datastore)
resource "aws_elasticache_replication_group" "primary" {
  provider = aws.primary
  
  replication_group_id = "resilienceai-redis"
  description          = "Redis cluster for ResilienceAI"
  
  node_type            = "cache.r6g.xlarge"
  num_cache_clusters   = 2
  automatic_failover_enabled = true
  multi_az_enabled     = true
  
  engine               = "redis"
  engine_version       = "7.0"
  port                 = 6379
  
  parameter_group_name = "default.redis7"
  
  subnet_group_name  = aws_elasticache_subnet_group.primary.name
  security_group_ids = [aws_security_group.redis_primary.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  snapshot_retention_limit = 35
  snapshot_window         = "05:00-06:00"
  
  tags = {
    Name = "resilienceai-redis-primary"
  }
}

# Global Datastore for cross-region replication
resource "aws_elasticache_global_replication_group" "redis_global" {
  provider = aws.primary
  
  global_replication_group_id_suffix = "resilienceai-redis"
  primary_replication_group_id       = aws_elasticache_replication_group.primary.id
}

resource "aws_elasticache_replication_group" "dr_secondary" {
  provider = aws.dr
  
  replication_group_id = "resilienceai-redis-dr"
  description          = "DR Redis cluster for ResilienceAI"
  
  global_replication_group_id = aws_elasticache_global_replication_group.redis_global.id
  
  num_cache_clusters = 2
  
  subnet_group_name  = aws_elasticache_subnet_group.dr.name
  security_group_ids = [aws_security_group.redis_dr.id]
  
  tags = {
    Name = "resilienceai-redis-dr"
  }
}

# ElastiCache Subnet Groups
resource "aws_elasticache_subnet_group" "primary" {
  provider = aws.primary
  
  name       = "resilienceai-redis-primary"
  subnet_ids = module.vpc_primary.private_subnets
}

resource "aws_elasticache_subnet_group" "dr" {
  provider = aws.dr
  
  name       = "resilienceai-redis-dr"
  subnet_ids = module.vpc_dr.private_subnets
}

# Redis Security Groups
resource "aws_security_group" "redis_primary" {
  provider = aws.primary
  
  name_prefix = "redis-primary-"
  vpc_id      = module.vpc_primary.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_primary]
  }
  
  tags = {
    Name = "redis-primary-sg"
  }
}

resource "aws_security_group" "redis_dr" {
  provider = aws.dr
  
  name_prefix = "redis-dr-"
  vpc_id      = module.vpc_dr.vpc_id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr_dr]
  }
  
  tags = {
    Name = "redis-dr-sg"
  }
}

# Variables
variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# Outputs
output "primary_db_endpoint" {
  description = "Primary RDS endpoint"
  value       = aws_db_instance.primary.endpoint
  sensitive   = true
}

output "dr_db_endpoint" {
  description = "DR RDS endpoint"
  value       = aws_db_instance.dr_replica.endpoint
  sensitive   = true
}

output "redis_primary_endpoint" {
  description = "Primary Redis endpoint"
  value       = aws_elasticache_replication_group.primary.primary_endpoint_address
  sensitive   = true
}

output "redis_dr_endpoint" {
  description = "DR Redis endpoint"
  value       = aws_elasticache_replication_group.dr_secondary.primary_endpoint_address
  sensitive   = true
}
