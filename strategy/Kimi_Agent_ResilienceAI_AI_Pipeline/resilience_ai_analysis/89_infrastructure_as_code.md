# Infrastructure as Code (IaC) for ResilienceAI

## Executive Summary

This document provides a comprehensive Infrastructure as Code (IaC) architecture for ResilienceAI, a multi-cloud AI platform requiring high availability, security, and scalability. The design leverages Terraform as the primary IaC tool with support for AWS, GCP, and Azure cloud providers.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Directory Structure](#2-directory-structure)
3. [Terraform Modules](#3-terraform-modules)
4. [State Management](#4-state-management)
5. [Variable Management](#5-variable-management)
6. [Module Composition](#6-module-composition)
7. [CI/CD Integration](#7-cicd-integration)
8. [Drift Detection](#8-drift-detection)
9. [Cost Estimation](#9-cost-estimation)
10. [Security & Compliance](#10-security--compliance)
11. [Implementation Priority](#11-implementation-priority)
12. [Best Practices](#12-best-practices)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESILIENCEAI IAC ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    TERRAFORM WORKSPACE LAYER                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Production  │  │   Staging    │  │ Development  │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│  ┌───────────────────────────▼─────────────────────────────────────────┐   │
│  │                    MODULE COMPOSITION LAYER                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   Network    │  │  Compute     │  │   Storage    │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │  Security    │  │  Database    │  │  Monitoring  │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                              │
│  ┌───────────────────────────▼─────────────────────────────────────────┐   │
│  │                    CLOUD PROVIDER LAYER                             │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       │   │
│  │  │      AWS        │ │       GCP       │ │      Azure      │       │   │
│  │  │  ┌───────────┐  │ │  ┌───────────┐  │ │  ┌───────────┐  │       │   │
│  │  │  │ EKS/EC2   │  │ │  │  GKE/GCE  │  │ │  │  AKS/VM   │  │       │   │
│  │  │  │ S3/RDS    │  │ │  │Cloud SQL  │  │ │  │Blob/DB    │  │       │   │
│  │  │  │ VPC/IAM   │  │ │  │VPC/IAM    │  │ │  │VNet/RBAC  │  │       │   │
│  │  │  └───────────┘  │ │  └───────────┘  │ │  └───────────┘  │       │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    STATE & BACKEND LAYER                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │ S3 Backend   │  │ DynamoDB Lock│  │ Encryption   │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Design Principles

| Principle | Description | Implementation |
|-----------|-------------|----------------|
| **DRY** | Don't Repeat Yourself | Reusable modules with parameterized configurations |
| **Idempotency** | Same input = Same output | Terraform state management and planning |
| **Immutability** | Infrastructure as cattle, not pets | Blue-green deployments, versioned artifacts |
| **Least Privilege** | Minimum required permissions | IAM roles, policy documents, RBAC |
| **Observability** | Full visibility into infrastructure | Comprehensive tagging, logging, monitoring |

---

## 2. Directory Structure

```
resilienceai-iac/
├── README.md
├── Makefile
├── .terraform-version
├── infracost.yml
├── infracost-usage.yml
│
├── global/
│   ├── backend/
│   │   ├── main.tf          # S3 bucket + DynamoDB for state
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── iam/
│       ├── main.tf          # Cross-account IAM roles
│       ├── variables.tf
│       └── outputs.tf
│
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
│
├── modules/
│   ├── aws/
│   │   ├── vpc/
│   │   ├── eks/
│   │   ├── rds/
│   │   ├── s3/
│   │   ├── iam/
│   │   ├── alb/
│   │   ├── cloudwatch/
│   │   └── secrets-manager/
│   ├── gcp/
│   │   ├── vpc/
│   │   ├── gke/
│   │   ├── cloud-sql/
│   │   ├── cloud-storage/
│   │   ├── iam/
│   │   └── cloud-monitoring/
│   └── azure/
│       ├── vnet/
│       ├── aks/
│       ├── postgresql/
│       ├── storage/
│       ├── rbac/
│       └── monitor/
│
├── .github/
│   └── workflows/
│       ├── terraform-plan.yml
│       ├── terraform-apply.yml
│       ├── drift-detection.yml
│       └── security-scan.yml
│
├── policies/
│   ├── checkov/
│   ├── terraform-compliance/
│   └── sentinel/
│
├── scripts/
│   ├── bootstrap.sh
│   ├── cost-estimate.sh
│   └── drift-check.sh
│
└── docs/
    ├── architecture.md
    ├── modules.md
    └── runbooks/
```

---

## 3. Terraform Modules

### 3.1 Module Structure Template

Each module follows a standardized structure:

```
modules/{provider}/{module-name}/
├── README.md              # Module documentation
├── main.tf                # Primary resources
├── variables.tf           # Input variables
├── outputs.tf             # Output values
├── versions.tf            # Provider version constraints
├── data.tf               # Data sources
├── locals.tf             # Local values
└── examples/             # Usage examples
    └── complete/
        ├── main.tf
        └── variables.tf
```

### 3.2 AWS VPC Module

**File: `/modules/aws/vpc/main.tf`**

```hcl
#===============================================================================
# AWS VPC Module for ResilienceAI
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# VPC Resource
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-vpc"
      Environment = var.environment
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-igw"
      Environment = var.environment
    }
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-public-${count.index + 1}"
      Environment = var.environment
      Type        = "public"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 100)
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-private-${count.index + 1}"
      Environment = var.environment
      Type        = "private"
    }
  )
}

# Database Subnets
resource "aws_subnet" "database" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 200)
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-db-${count.index + 1}"
      Environment = var.environment
      Type        = "database"
    }
  )
}

# NAT Gateways (One per AZ for high availability)
resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? length(var.availability_zones) : 0
  domain = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-nat-eip-${count.index + 1}"
      Environment = var.environment
    }
  )

  depends_on = [aws_internet_gateway.main]
}

resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? length(var.availability_zones) : 0

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-nat-${count.index + 1}"
      Environment = var.environment
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-public-rt"
      Environment = var.environment
      Type        = "public"
    }
  )
}

resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = aws_nat_gateway.main[count.index].id
    }
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
      Environment = var.environment
      Type        = "private"
    }
  )
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

resource "aws_route_table_association" "database" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# VPC Flow Logs
resource "aws_flow_log" "main" {
  count = var.enable_flow_logs ? 1 : 0

  vpc_id                   = aws_vpc.main.id
  traffic_type             = "ALL"
  log_destination_type     = "cloud-watch-logs"
  log_destination          = aws_cloudwatch_log_group.flow_logs[0].arn
  iam_role_arn             = aws_iam_role.flow_logs[0].arn
  max_aggregation_interval = 60

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-flow-log"
      Environment = var.environment
    }
  )
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  count = var.enable_flow_logs ? 1 : 0

  name              = "/aws/vpc/${var.project_name}-${var.environment}-flow-logs"
  retention_in_days = var.flow_logs_retention_days

  tags = var.common_tags
}
```

**File: `/modules/aws/vpc/variables.tf`**

```hcl
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "resilienceai"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

variable "flow_logs_retention_days" {
  description = "Flow logs retention in days"
  type        = number
  default     = 30
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "ResilienceAI"
    ManagedBy   = "Terraform"
    CostCenter  = "Engineering"
  }
}
```

**File: `/modules/aws/vpc/outputs.tf`**

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of database subnets"
  value       = aws_subnet.database[*].id
}

output "nat_gateway_ids" {
  description = "IDs of NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}

output "internet_gateway_id" {
  description = "ID of Internet Gateway"
  value       = aws_internet_gateway.main.id
}
```

### 3.3 AWS EKS Module

**File: `/modules/aws/eks/main.tf`**

```hcl
#===============================================================================
# AWS EKS Module for ResilienceAI
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = "${var.project_name}-${var.environment}"
  role_arn = aws_iam_role.cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = var.subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.enable_public_endpoint
    public_access_cidrs     = var.public_access_cidrs
    security_group_ids      = [aws_security_group.cluster.id]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks.arn
    }
    resources = ["secrets"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster_policies,
    aws_cloudwatch_log_group.eks,
  ]

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}"
      Environment = var.environment
    }
  )
}

# KMS Key for EKS Secrets Encryption
resource "aws_kms_key" "eks" {
  description             = "EKS Secret Encryption Key"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-eks-key"
    }
  )
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.project_name}-${var.environment}-eks"
  target_key_id = aws_kms_key.eks.key_id
}

# EKS Managed Node Groups
resource "aws_eks_node_group" "main" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = each.key
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  instance_types = each.value.instance_types
  capacity_type  = each.value.capacity_type
  disk_size      = each.value.disk_size

  scaling_config {
    desired_size = each.value.desired_size
    min_size     = each.value.min_size
    max_size     = each.value.max_size
  }

  update_config {
    max_unavailable_percentage = 25
  }

  labels = merge(
    each.value.labels,
    {
      environment = var.environment
      node_group  = each.key
    }
  )

  dynamic "taint" {
    for_each = each.value.taints
    content {
      key    = taint.value.key
      value  = taint.value.value
      effect = taint.value.effect
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_policies,
  ]

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-${each.key}"
      Environment = var.environment
    }
  )

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

# CloudWatch Log Group for EKS
resource "aws_cloudwatch_log_group" "eks" {
  name              = "/aws/eks/${var.project_name}-${var.environment}/cluster"
  retention_in_days = var.log_retention_days

  tags = var.common_tags
}

# Security Group for EKS Cluster
resource "aws_security_group" "cluster" {
  name_prefix = "${var.project_name}-${var.environment}-cluster-"
  description = "EKS cluster security group"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-cluster-sg"
    }
  )
}

resource "aws_security_group_rule" "cluster_ingress" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  security_group_id        = aws_security_group.cluster.id
  source_security_group_id = aws_security_group.node.id
}

# Security Group for EKS Nodes
resource "aws_security_group" "node" {
  name_prefix = "${var.project_name}-${var.environment}-node-"
  description = "EKS node security group"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-node-sg"
      "kubernetes.io/cluster/${var.project_name}-${var.environment}" = "owned"
    }
  )
}

resource "aws_security_group_rule" "node_ingress_self" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "-1"
  self              = true
  security_group_id = aws_security_group.node.id
}

resource "aws_security_group_rule" "node_ingress_cluster" {
  type                     = "ingress"
  from_port                = 1025
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.node.id
  source_security_group_id = aws_security_group.cluster.id
}
```


### 3.4 AWS RDS Module

**File: `/modules/aws/rds/main.tf`**

```hcl
#===============================================================================
# AWS RDS Module for ResilienceAI
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name        = "${var.project_name}-${var.environment}"
  description = "Database subnet group for ${var.project_name}"
  subnet_ids  = var.subnet_ids

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}"
      Environment = var.environment
    }
  )
}

# KMS Key for RDS Encryption
resource "aws_kms_key" "rds" {
  count = var.storage_encrypted ? 1 : 0

  description             = "RDS encryption key for ${var.project_name}"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-key"
    }
  )
}

# Master Password (Secrets Manager)
resource "random_password" "master" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "master_password" {
  name                    = "${var.project_name}/${var.environment}/rds/master-password"
  description             = "Master password for RDS instance"
  recovery_window_in_days = 7

  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "master_password" {
  secret_id     = aws_secretsmanager_secret.master_password.id
  secret_string = random_password.master.result
}

# RDS Instance (Primary)
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-${var.environment}"

  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = var.storage_type
  storage_encrypted     = var.storage_encrypted
  kms_key_id            = var.storage_encrypted ? aws_kms_key.rds[0].arn : null

  db_name  = var.database_name
  username = var.master_username
  password = random_password.master.result

  multi_az               = var.multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = var.backup_retention_period
  backup_window           = var.backup_window
  maintenance_window      = var.maintenance_window

  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.project_name}-${var.environment}-final-snapshot"
  copy_tags_to_snapshot     = true

  deletion_protection = var.deletion_protection

  performance_insights_enabled          = var.performance_insights_enabled
  performance_insights_kms_key_id       = var.performance_insights_enabled ? aws_kms_key.rds[0].arn : null
  performance_insights_retention_period = var.performance_insights_retention_period

  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports

  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null

  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  apply_immediately          = var.apply_immediately

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}"
      Environment = var.environment
    }
  )
}

# RDS Read Replicas
resource "aws_db_instance" "replica" {
  count = var.read_replica_count

  identifier = "${var.project_name}-${var.environment}-replica-${count.index + 1}"

  replicate_source_db = aws_db_instance.main.arn
  instance_class      = var.replica_instance_class

  storage_encrypted = var.storage_encrypted
  kms_key_id        = var.storage_encrypted ? aws_kms_key.rds[0].arn : null

  multi_az               = false
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 0

  performance_insights_enabled    = var.performance_insights_enabled
  performance_insights_kms_key_id = var.performance_insights_enabled ? aws_kms_key.rds[0].arn : null

  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  apply_immediately          = var.apply_immediately

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-${var.environment}-replica-${count.index + 1}"
      Environment = var.environment
      Type        = "replica"
    }
  )
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  description = "Security group for RDS instance"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.port
    to_port         = var.port
    protocol        = "tcp"
    security_groups = var.allowed_security_groups
    cidr_blocks     = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-rds-sg"
    }
  )
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-${var.environment}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "RDS CPU utilization is high"
  alarm_actions       = var.alarm_actions
  ok_actions          = var.alarm_actions

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.identifier
  }

  tags = var.common_tags
}
```

### 3.5 GCP GKE Module

**File: `/modules/gcp/gke/main.tf`**

```hcl
#===============================================================================
# GCP GKE Module for ResilienceAI
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# GKE Cluster
resource "google_container_cluster" "main" {
  name     = "${var.project_name}-${var.environment}"
  location = var.location

  release_channel {
    channel = var.release_channel
  }

  min_master_version = var.kubernetes_version

  network    = var.network
  subnetwork = var.subnetwork

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block

    master_global_access_config {
      enabled = true
    }
  }

  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.authorized_networks
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  networking_mode = "VPC_NATIVE"

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
    gcp_filestore_csi_driver_config {
      enabled = true
    }
  }

  network_policy {
    enabled = true
  }

  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  datapath_provider = "ADVANCED_DATAPATH"

  resource_labels = merge(
    var.common_labels,
    {
      environment = var.environment
    }
  )

  remove_default_node_pool = true
  initial_node_count       = 1

  depends_on = [google_project_service.container]
}

# Node Pools
resource "google_container_node_pool" "main" {
  for_each = var.node_pools

  name           = each.key
  location       = var.location
  cluster        = google_container_cluster.main.name
  node_locations = var.node_locations

  autoscaling {
    min_node_count  = each.value.min_count
    max_node_count  = each.value.max_count
    location_policy = "BALANCED"
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }

  node_config {
    machine_type    = each.value.machine_type
    disk_size_gb    = each.value.disk_size_gb
    disk_type       = each.value.disk_type
    image_type      = "COS_CONTAINERD"
    service_account = google_service_account.gke_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    labels = merge(
      each.value.labels,
      {
        environment = var.environment
        node_pool   = each.key
      }
    )

    taint = each.value.taints

    tags = ["gke-node", "${var.project_name}-${var.environment}"]

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  lifecycle {
    ignore_changes = [node_config[0].taint]
  }
}

# Service Account for GKE Nodes
resource "google_service_account" "gke_nodes" {
  account_id   = "${var.project_name}-${var.environment}-gke"
  display_name = "GKE Node Service Account"
  description  = "Service account for GKE nodes in ${var.environment}"
  project      = var.project_id
}

resource "google_project_iam_member" "gke_nodes" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer",
    "roles/autoscaling.metricsWriter",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}

# Enable Required APIs
resource "google_project_service" "container" {
  project = var.project_id
  service = "container.googleapis.com"

  disable_on_destroy = false
}
```

### 3.6 Azure AKS Module

**File: `/modules/azure/aks/main.tf`**

```hcl
#===============================================================================
# Azure AKS Module for ResilienceAI
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.75"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.15"
    }
  }
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${var.project_name}-${var.environment}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}-${var.environment}"
  kubernetes_version  = var.kubernetes_version

  private_cluster_enabled = var.private_cluster_enabled
  private_dns_zone_id     = var.private_cluster_enabled ? "System" : null

  automatic_channel_upgrade = "stable"
  node_os_channel_upgrade   = "NodeImage"

  sku_tier = var.sku_tier

  default_node_pool {
    name                = "system"
    node_count          = var.system_node_count
    vm_size             = var.system_node_vm_size
    os_disk_size_gb     = var.system_node_disk_size
    os_disk_type        = "Managed"
    type                = "VirtualMachineScaleSets"
    zones               = var.availability_zones
    vnet_subnet_id      = var.subnet_id
    enable_auto_scaling = false

    node_labels = {
      "node-type" = "system"
    }

    tags = var.common_tags
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin      = "azure"
    network_policy      = "calico"
    load_balancer_sku   = "standard"
    service_cidr        = var.service_cidr
    dns_service_ip      = var.dns_service_ip
    docker_bridge_cidr  = "172.17.0.1/16"
    outbound_type       = "loadBalancer"
  }

  azure_active_directory_role_based_access_control {
    managed                = true
    admin_group_object_ids = var.aad_admin_group_ids
    azure_rbac_enabled     = true
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  microsoft_defender {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
  }

  workload_identity_enabled = true
  oidc_issuer_enabled       = true

  tags = merge(
    var.common_tags,
    {
      environment = var.environment
    }
  )
}

# Additional Node Pools
resource "azurerm_kubernetes_cluster_node_pool" "main" {
  for_each = var.additional_node_pools

  name                  = each.key
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = each.value.vm_size
  node_count            = each.value.node_count
  min_count             = each.value.min_count
  max_count             = each.value.max_count
  enable_auto_scaling   = each.value.enable_auto_scaling
  os_disk_size_gb       = each.value.os_disk_size_gb
  os_type               = "Linux"
  vnet_subnet_id        = var.subnet_id
  zones                 = var.availability_zones
  mode                  = each.value.mode

  node_labels = merge(
    each.value.node_labels,
    {
      "node-pool" = each.key
    }
  )

  node_taints = each.value.node_taints

  tags = var.common_tags
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.project_name}-${var.environment}-logs"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days

  tags = var.common_tags
}

# Container Registry
resource "azurerm_container_registry" "main" {
  name                = replace("${var.project_name}${var.environment}", "-", "")
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.acr_sku
  admin_enabled       = false

  identity {
    type = "SystemAssigned"
  }

  network_rule_set {
    default_action = "Deny"
  }

  tags = var.common_tags
}

# ACR Pull Role Assignment
resource "azurerm_role_assignment" "acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
```

---

## 4. State Management

### 4.1 Backend Configuration

**File: `/environments/prod/backend.tf`**

```hcl
#===============================================================================
# Terraform Backend Configuration for Production
#===============================================================================

terraform {
  backend "s3" {
    bucket         = "resilienceai-terraform-state-prod"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/terraform-state-key"
    dynamodb_table = "resilienceai-terraform-locks"
    use_lockfile   = true
  }
}
```

### 4.2 Backend Infrastructure

**File: `/global/backend/main.tf`**

```hcl
#===============================================================================
# Terraform State Backend Infrastructure
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket for Terraform State
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.project_name}-terraform-state-${var.environment}"

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-terraform-state-${var.environment}"
      Environment = var.environment
    }
  )
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.terraform_state.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB Table for State Locking
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "${var.project_name}-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.terraform_state.arn
  }

  tags = merge(
    var.common_tags,
    {
      Name        = "${var.project_name}-terraform-locks"
      Environment = var.environment
    }
  )
}

# KMS Key for State Encryption
resource "aws_kms_key" "terraform_state" {
  description             = "KMS key for Terraform state encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  multi_region            = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-terraform-state-key"
    }
  )
}

resource "aws_kms_alias" "terraform_state" {
  name          = "alias/${var.project_name}-terraform-state"
  target_key_id = aws_kms_key.terraform_state.key_id
}

data "aws_caller_identity" "current" {}
```

---

## 5. Variable Management

### 5.1 Global Variables

**File: `/environments/prod/variables.tf`**

```hcl
#===============================================================================
# Global Variables for Production Environment
#===============================================================================

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "resilienceai"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# EKS Configuration
variable "eks_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.28"
}

variable "eks_node_groups" {
  description = "EKS node group configuration"
  type = map(object({
    instance_types = list(string)
    capacity_type  = string
    disk_size      = number
    desired_size   = number
    min_size       = number
    max_size       = number
    labels         = map(string)
    taints         = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  default = {
    general = {
      instance_types = ["m6i.xlarge"]
      capacity_type  = "ON_DEMAND"
      disk_size      = 100
      desired_size   = 3
      min_size       = 2
      max_size       = 10
      labels         = {}
      taints         = []
    }
    gpu = {
      instance_types = ["g4dn.xlarge"]
      capacity_type  = "ON_DEMAND"
      disk_size      = 200
      desired_size   = 1
      min_size       = 0
      max_size       = 5
      labels = {
        "nvidia.com/gpu" = "true"
      }
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NoSchedule"
      }]
    }
    spot = {
      instance_types = ["m6i.large", "m5.large", "m5a.large"]
      capacity_type  = "SPOT"
      disk_size      = 50
      desired_size   = 2
      min_size       = 0
      max_size       = 20
      labels = {
        "node-type" = "spot"
      }
      taints = []
    }
  }
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.xlarge"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 100
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_backup_retention" {
  description = "Backup retention period in days"
  type        = number
  default     = 30
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = true
}

# Security Configuration
variable "enable_waf" {
  description = "Enable AWS WAF"
  type        = bool
  default     = true
}

variable "enable_shield_advanced" {
  description = "Enable AWS Shield Advanced"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty"
  type        = bool
  default     = true
}

# Monitoring Configuration
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 90
}

variable "enable_container_insights" {
  description = "Enable Container Insights"
  type        = bool
  default     = true
}

# Cost Management
variable "enable_cost_anomaly_detection" {
  description = "Enable Cost Anomaly Detection"
  type        = bool
  default     = true
}

variable "monthly_budget_limit" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 10000
}

variable "budget_alert_thresholds" {
  description = "Budget alert thresholds as percentages"
  type        = list(number)
  default     = [50, 80, 100]
}

# Common Tags
variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "ResilienceAI"
    ManagedBy   = "Terraform"
    CostCenter  = "Engineering"
    Environment = "prod"
  }
}
```

### 5.2 Environment-Specific Variables

**File: `/environments/prod/terraform.tfvars`**

```hcl
#===============================================================================
# Production Environment Variables
#===============================================================================

environment = "prod"
aws_region  = "us-east-1"

vpc_cidr           = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]

eks_version = "1.28"
eks_node_groups = {
  system = {
    instance_types = ["m6i.2xlarge"]
    capacity_type  = "ON_DEMAND"
    disk_size      = 100
    desired_size   = 3
    min_size       = 3
    max_size       = 10
    labels = {
      "node-type" = "system"
    }
    taints = []
  }
  workload = {
    instance_types = ["m6i.4xlarge"]
    capacity_type  = "ON_DEMAND"
    disk_size      = 200
    desired_size   = 5
    min_size       = 3
    max_size       = 20
    labels = {
      "node-type" = "workload"
    }
    taints = []
  }
  gpu = {
    instance_types = ["g4dn.2xlarge"]
    capacity_type  = "ON_DEMAND"
    disk_size      = 500
    desired_size   = 2
    min_size       = 1
    max_size       = 10
    labels = {
      "nvidia.com/gpu" = "true"
    }
    taints = [{
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NoSchedule"
    }]
  }
  spot = {
    instance_types = ["m6i.2xlarge", "m5.2xlarge", "m5a.2xlarge"]
    capacity_type  = "SPOT"
    disk_size      = 100
    desired_size   = 5
    min_size       = 0
    max_size       = 50
    labels = {
      "node-type" = "spot"
    }
    taints = []
  }
}

db_instance_class    = "db.r6g.2xlarge"
db_allocated_storage = 500
db_engine_version    = "15.4"
db_backup_retention  = 30
db_multi_az          = true

enable_waf             = true
enable_shield_advanced = true
enable_guardduty       = true
enable_security_hub    = true

log_retention_days        = 90
enable_container_insights = true
enable_xray               = true

enable_cost_anomaly_detection = true
monthly_budget_limit          = 25000
budget_alert_thresholds       = [50, 75, 90, 100]

common_tags = {
  Project     = "ResilienceAI"
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
  Environment = "prod"
  Owner       = "platform-team"
  DataClass   = "confidential"
}
```


---

## 6. Module Composition

### 6.1 Root Module Structure

**File: `/environments/prod/main.tf`**

```hcl
#===============================================================================
# ResilienceAI Production Infrastructure
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket         = "resilienceai-terraform-state-prod"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/terraform-state-key"
    dynamodb_table = "resilienceai-terraform-locks"
  }
}

# Provider Configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = var.common_tags
  }
}

# Data Sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

# Local Values
locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name
  
  naming_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = merge(
    var.common_tags,
    {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  )
}

# Networking Module
module "vpc" {
  source = "../../modules/aws/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  
  availability_zones = var.availability_zones
  
  enable_nat_gateway       = true
  enable_flow_logs         = true
  flow_logs_retention_days = var.log_retention_days
  
  common_tags = local.common_tags
}

# Security Module
module "security" {
  source = "../../modules/aws/security"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  
  enable_waf             = var.enable_waf
  enable_shield_advanced = var.enable_shield_advanced
  enable_guardduty       = var.enable_guardduty
  enable_security_hub    = var.enable_security_hub
  
  common_tags = local.common_tags
}

# EKS Cluster Module
module "eks" {
  source = "../../modules/aws/eks"

  project_name = var.project_name
  environment  = var.environment
  
  kubernetes_version = var.eks_version
  
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = concat(module.vpc.public_subnet_ids, module.vpc.private_subnet_ids)
  private_subnet_ids = module.vpc.private_subnet_ids
  
  node_groups = var.eks_node_groups
  
  enable_public_endpoint = false
  public_access_cidrs    = []
  
  log_retention_days = var.log_retention_days
  
  common_tags = local.common_tags

  depends_on = [module.vpc]
}

# Database Module
module "database" {
  source = "../../modules/aws/rds"

  project_name = var.project_name
  environment  = var.environment
  
  engine         = "postgres"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_allocated_storage * 2
  
  database_name    = "resilienceai"
  master_username  = "dbadmin"
  
  multi_az               = var.db_multi_az
  subnet_ids             = module.vpc.database_subnet_ids
  vpc_id                 = module.vpc.vpc_id
  allowed_security_groups = [module.eks.node_security_group_id]
  
  backup_retention_period = var.db_backup_retention
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"
  
  storage_encrypted = true
  deletion_protection = true
  
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  read_replica_count      = 2
  replica_instance_class  = var.db_instance_class
  
  alarm_actions = [module.monitoring.sns_topic_arn]
  
  common_tags = local.common_tags

  depends_on = [module.vpc, module.eks]
}

# Storage Module (S3)
module "storage" {
  source = "../../modules/aws/s3"

  project_name = var.project_name
  environment  = var.environment
  
  buckets = {
    "data" = {
      versioning = true
      encryption = true
      lifecycle_rules = [
        {
          id      = "transition-to-ia"
          enabled = true
          transition = {
            days          = 90
            storage_class = "STANDARD_IA"
          }
        },
        {
          id      = "transition-to-glacier"
          enabled = true
          transition = {
            days          = 365
            storage_class = "GLACIER"
          }
        }
      ]
    }
    "models" = {
      versioning = true
      encryption = true
    }
    "logs" = {
      versioning = false
      encryption = true
      lifecycle_rules = [
        {
          id      = "expire-old-logs"
          enabled = true
          expiration = {
            days = 90
          }
        }
      ]
    }
  }
  
  common_tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/aws/cloudwatch"

  project_name = var.project_name
  environment  = var.environment
  
  log_retention_days        = var.log_retention_days
  enable_container_insights = var.enable_container_insights
  enable_xray               = var.enable_xray
  
  alarm_actions = []
  
  common_tags = local.common_tags
}

# Cost Management Module
module "cost_management" {
  source = "../../modules/aws/cost"

  project_name = var.project_name
  environment  = var.environment
  
  enable_anomaly_detection = var.enable_cost_anomaly_detection
  monthly_budget_limit     = var.monthly_budget_limit
  budget_alert_thresholds  = var.budget_alert_thresholds
  
  notification_emails = [
    "platform-team@resilienceai.com",
    "finance@resilienceai.com"
  ]
  
  common_tags = local.common_tags
}
```

### 6.2 Module Dependencies Graph

```
                    ┌─────────────────────────────────────────┐
                    │           ROOT MODULE                   │
                    │         (environments/prod)             │
                    └─────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│      VPC        │         │    SECURITY     │         │   MONITORING    │
│    Module       │         │    Module       │         │    Module       │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         │         ┌─────────────────┴─────────────────┐         │
         │         │                                   │         │
         ▼         ▼                                   ▼         ▼
┌─────────────────────────┐                 ┌─────────────────────────┐
│         EKS             │                 │        DATABASE         │
│        Module           │◄────────────────│        Module           │
└─────────────────────────┘                 └─────────────────────────┘
         │                                           │
         │         ┌─────────────────┐               │
         │         │                 │               │
         ▼         ▼                 ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        STORAGE MODULE                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. CI/CD Integration

### 7.1 GitHub Actions Workflow - Plan

**File: `/.github/workflows/terraform-plan.yml`**

```yaml
#===============================================================================
# Terraform Plan Workflow
#===============================================================================
name: Terraform Plan

on:
  pull_request:
    paths:
      - '**.tf'
      - '**.tfvars'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to plan'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod

env:
  TF_IN_AUTOMATION: true
  TF_INPUT: false

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Detect Changed Environments
        id: set-matrix
        run: |
          CHANGED_FILES=$(git diff --name-only origin/main...HEAD | grep -E '\.tf$|\.tfvars$' || true)
          
          ENVIRONMENTS=()
          for file in $CHANGED_FILES; do
            if [[ $file == environments/dev/* ]]; then
              ENVIRONMENTS+=("dev")
            elif [[ $file == environments/staging/* ]]; then
              ENVIRONMENTS+=("staging")
            elif [[ $file == environments/prod/* ]]; then
              ENVIRONMENTS+=("prod")
            elif [[ $file == modules/* ]]; then
              ENVIRONMENTS+=("dev" "staging" "prod")
              break
            fi
          done
          
          UNIQUE_ENVS=$(echo "${ENVIRONMENTS[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' ')
          
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            UNIQUE_ENVS="${{ github.event.inputs.environment }}"
          fi
          
          MATRIX="{\"environment\":["
          FIRST=true
          for env in $UNIQUE_ENVS; do
            if [ "$FIRST" = true ]; then
              FIRST=false
            else
              MATRIX="${MATRIX},"
            fi
            MATRIX="${MATRIX}\"$env\""
          done
          MATRIX="${MATRIX}]}"
          
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          output_format: sarif
          soft_fail: true

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: results.sarif

  terraform-plan:
    needs: [detect-changes, security-scan]
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{fromJson(needs.detect-changes.outputs.matrix)}}
      fail-fast: false
    environment:
      name: ${{ matrix.environment }}-plan
    
    permissions:
      contents: read
      id-token: write
      pull-requests: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-terraform-role
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"

      - name: Terraform Format Check
        run: terraform fmt -check -recursive
        continue-on-error: true

      - name: Terraform Init
        working-directory: environments/${{ matrix.environment }}
        run: terraform init

      - name: Terraform Validate
        working-directory: environments/${{ matrix.environment }}
        run: terraform validate

      - name: Terraform Plan
        working-directory: environments/${{ matrix.environment }}
        run: |
          terraform plan \
            -var-file=terraform.tfvars \
            -out=tfplan \
            -input=false

      - name: Generate Plan Summary
        working-directory: environments/${{ matrix.environment }}
        run: |
          echo "## Terraform Plan Summary - ${{ matrix.environment }}" > plan.md
          terraform show -json tfplan | jq -r '
            "Resources to Create: \(.resource_changes | map(select(.change.actions[0] == "create")) | length)",
            "Resources to Update: \(.resource_changes | map(select(.change.actions[0] == "update")) | length)",
            "Resources to Delete: \(.resource_changes | map(select(.change.actions[0] == "delete")) | length)"
          ' >> plan.md

      - name: Upload Plan
        uses: actions/upload-artifact@v4
        with:
          name: tfplan-${{ matrix.environment }}
          path: environments/${{ matrix.environment }}/tfplan
          retention-days: 5

      - name: Cost Estimation
        uses: infracost/actions/setup@v2
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate Cost Estimate
        working-directory: environments/${{ matrix.environment }}
        run: |
          infracost breakdown --path=. --format=json --out-file=/tmp/infracost.json
          infracost output --path=/tmp/infracost.json --format=table --show-skipped
```

### 7.2 GitHub Actions Workflow - Apply

**File: `/.github/workflows/terraform-apply.yml`**

```yaml
#===============================================================================
# Terraform Apply Workflow
#===============================================================================
name: Terraform Apply

on:
  push:
    branches:
      - main
    paths:
      - '**.tf'
      - '**.tfvars'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to apply'
        required: true
        default: 'dev'
        type: choice
        options:
          - dev
          - staging
          - prod

env:
  TF_IN_AUTOMATION: true
  TF_INPUT: false

jobs:
  determine-env:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
    steps:
      - name: Set Environment
        id: set-env
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "environment=dev" >> $GITHUB_OUTPUT
          fi

  terraform-apply:
    needs: determine-env
    runs-on: ubuntu-latest
    environment:
      name: ${{ needs.determine-env.outputs.environment }}
    
    permissions:
      contents: read
      id-token: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-terraform-role
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"

      - name: Terraform Init
        working-directory: environments/${{ needs.determine-env.outputs.environment }}
        run: terraform init

      - name: Terraform Plan
        working-directory: environments/${{ needs.determine-env.outputs.environment }}
        run: |
          terraform plan \
            -var-file=terraform.tfvars \
            -out=tfplan \
            -input=false

      - name: Terraform Apply
        working-directory: environments/${{ needs.determine-env.outputs.environment }}
        run: |
          terraform apply \
            -auto-approve \
            -input=false \
            tfplan

      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#platform-alerts'
          text: |
            Terraform Apply ${{ job.status }} for ${{ needs.determine-env.outputs.environment }}
            Commit: ${{ github.sha }}
            Author: ${{ github.actor }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 7.3 GitHub Actions Workflow - Drift Detection

**File: `/.github/workflows/drift-detection.yml`**

```yaml
#===============================================================================
# Drift Detection Workflow
#===============================================================================
name: Drift Detection

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

env:
  TF_IN_AUTOMATION: true
  TF_INPUT: false

jobs:
  drift-detection:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
      fail-fast: false
    
    permissions:
      contents: read
      id-token: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-terraform-role
          aws-region: us-east-1

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"

      - name: Terraform Init
        working-directory: environments/${{ matrix.environment }}
        run: terraform init

      - name: Detect Drift
        id: drift
        working-directory: environments/${{ matrix.environment }}
        run: |
          terraform plan \
            -var-file=terraform.tfvars \
            -detailed-exitcode \
            -input=false \
            -out=tfplan 2>&1 || EXIT_CODE=$?
          
          if [ "$EXIT_CODE" == "2" ]; then
            echo "drift_detected=true" >> $GITHUB_OUTPUT
            echo "Drift detected!"
            terraform show -json tfplan | jq -r '
              .resource_changes[] | 
              select(.change.actions[0] != "no-op") |
              "Resource: \(.address) Action: \(.change.actions | join(", "))"
            ' > drift-report.txt
          elif [ "$EXIT_CODE" == "0" ]; then
            echo "drift_detected=false" >> $GITHUB_OUTPUT
            echo "No drift detected"
          else
            echo "Error running terraform plan"
            exit 1
          fi
        continue-on-error: true

      - name: Create Issue for Drift
        if: steps.drift.outputs.drift_detected == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const driftReport = fs.readFileSync('environments/${{ matrix.environment }}/drift-report.txt', 'utf8');
            
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Infrastructure Drift Detected: ${{ matrix.environment }}`,
              body: `Drift detected at ${new Date().toISOString()}\n\n${driftReport}`,
              labels: ['drift', '${{ matrix.environment }}', 'infrastructure']
            });

      - name: Notify Slack
        if: steps.drift.outputs.drift_detected == 'true'
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          custom_payload: |
            {
              "channel": "#platform-alerts",
              "attachments": [{
                "color": "danger",
                "title": "Infrastructure Drift Detected",
                "text": "Environment: ${{ matrix.environment }}"
              }]
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## 8. Drift Detection

### 8.1 Drift Detection Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DRIFT DETECTION SYSTEM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  Scheduled      │    │  Manual         │    │  Event-     │ │
│  │  (Every 6h)     │    │  Trigger        │    │  Driven     │ │
│  └────────┬────────┘    └────────┬────────┘    └──────┬──────┘ │
│           │                      │                    │        │
│           └──────────────────────┼────────────────────┘        │
│                                  ▼                             │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              GitHub Actions Workflow                      │ │
│  │  1. terraform plan -detailed-exitcode                    │ │
│  │  2. Parse exit code (0=no drift, 2=drift)                │ │
│  │  3. Generate drift report                                │ │
│  │  4. Create GitHub Issue                                  │ │
│  │  5. Send Slack notification                              │ │
│  └──────────────────────────┬───────────────────────────────┘ │
│                             │                                  │
│                             ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Drift Remediation Options                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │ │
│  │  │  terraform   │  │  Import      │  │  Manual      │   │ │
│  │  │  apply       │  │  Resources   │  │  Revert      │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Drift Detection Script

**File: `/scripts/drift-check.sh`**

```bash
#!/bin/bash
#===============================================================================
# Drift Detection Script for ResilienceAI
#===============================================================================

set -e

ENVIRONMENTS=("dev" "staging" "prod")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DRIFT_DETECTED=false

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_drift() {
    local env=$1
    local env_dir="$PROJECT_ROOT/environments/$env"
    
    log_info "Checking drift for environment: $env"
    
    if [ ! -d "$env_dir" ]; then
        log_error "Environment directory not found: $env_dir"
        return 1
    fi
    
    cd "$env_dir"
    
    log_info "Initializing Terraform..."
    terraform init -backend=false > /dev/null 2>&1
    
    log_info "Running terraform plan..."
    set +e
    terraform plan \
        -var-file=terraform.tfvars \
        -detailed-exitcode \
        -input=false \
        -out=tfplan
    
    local exit_code=$?
    set -e
    
    case $exit_code in
        0)
            log_info "No drift detected in $env"
            return 0
            ;;
        1)
            log_error "Error running terraform plan for $env"
            return 1
            ;;
        2)
            log_warn "DRIFT DETECTED in $env!"
            DRIFT_DETECTED=true
            generate_drift_report "$env"
            return 0
            ;;
        *)
            log_error "Unknown exit code: $exit_code"
            return 1
            ;;
    esac
}

generate_drift_report() {
    local env=$1
    local report_file="drift-report-$env-$(date +%Y%m%d-%H%M%S).json"
    
    log_info "Generating drift report: $report_file"
    
    terraform show -json tfplan > "$report_file"
    
    echo ""
    echo "=== Drift Details ==="
    jq -r '
        .resource_changes[] | 
        select(.change.actions[0] != "no-op") |
        "\nResource: \(.address)
Action: \(.change.actions | join(", "))"
    ' "$report_file" 2>/dev/null || echo "No drift details available"
    
    echo ""
    echo "Full report saved to: $report_file"
}

main() {
    log_info "Starting drift detection for ResilienceAI infrastructure"
    log_info "Timestamp: $(date)"
    echo ""
    
    if [ -n "$1" ]; then
        check_drift "$1"
    else
        for env in "${ENVIRONMENTS[@]}"; do
            echo "=========================================="
            check_drift "$env"
            echo ""
        done
    fi
    
    echo "=========================================="
    echo ""
    if [ "$DRIFT_DETECTED" = true ]; then
        log_warn "Drift was detected in one or more environments!"
        exit 2
    else
        log_info "All environments are in sync with Terraform configuration."
        exit 0
    fi
}

main "$@"
```


---

## 9. Cost Estimation

### 9.1 Cost Management Module

**File: `/modules/aws/cost/main.tf`**

```hcl
#===============================================================================
# Cost Management Module for ResilienceAI
#===============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS Budget
resource "aws_budgets_budget" "monthly" {
  name              = "${var.project_name}-${var.environment}-monthly-budget"
  budget_type       = "COST"
  limit_amount      = var.monthly_budget_limit
  limit_unit        = "USD"
  time_period_start = "2024-01-01_00:00"
  time_unit         = "MONTHLY"

  cost_filter {
    name = "TagKeyValue"
    values = [
      "user:Environment$${var.environment}",
    ]
  }

  dynamic "notification" {
    for_each = var.budget_alert_thresholds
    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = notification.value
      threshold_type             = "PERCENTAGE"
      notification_type          = "ACTUAL"
      subscriber_email_addresses = var.notification_emails
    }
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = var.notification_emails
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-${var.environment}-monthly-budget"
    }
  )
}

# Cost Anomaly Detection
resource "aws_ce_anomaly_monitor" "service_monitor" {
  count = var.enable_anomaly_detection ? 1 : 0

  name              = "${var.project_name}-${var.environment}-service-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"

  tags = var.common_tags
}

resource "aws_ce_anomaly_subscription" "service_subscription" {
  count = var.enable_anomaly_detection ? 1 : 0

  name      = "${var.project_name}-${var.environment}-anomaly-subscription"
  threshold = 100
  frequency = "IMMEDIATE"

  monitor_arn_list = [
    aws_ce_anomaly_monitor.service_monitor[0].arn
  ]

  subscriber {
    type    = "EMAIL"
    address = var.notification_emails[0]
  }

  depends_on = [aws_ce_anomaly_monitor.service_monitor]
}

# Cost Allocation Tags
resource "aws_ce_cost_allocation_tag" "environment" {
  tag_key = "Environment"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "project" {
  tag_key = "Project"
  status  = "Active"
}

resource "aws_ce_cost_allocation_tag" "cost_center" {
  tag_key = "CostCenter"
  status  = "Active"
}
```

### 9.2 Infracost Integration

**File: `/infracost.yml`**

```yaml
# Infracost Configuration for ResilienceAI
version: 0.1

projects:
  - path: environments/dev
    name: ResilienceAI Development
    terraform_workspace: dev
    
  - path: environments/staging
    name: ResilienceAI Staging
    terraform_workspace: staging
    
  - path: environments/prod
    name: ResilienceAI Production
    terraform_workspace: prod

usage_file: infracost-usage.yml

exclude_paths:
  - modules/**/examples/**
  - "**/.terraform/**/*"

aws:
  region: us-east-1
  
gcp:
  region: us-central1
  
azure:
  region: East US
```

**File: `/infracost-usage.yml`**

```yaml
# Usage estimates for ResilienceAI resources
version: 0.1
resource_usage:
  aws_eks_node_group.general:
    operating_system: linux
    reserved_instances: none
    instance_count: 3
    monthly_hours: 730
    
  aws_eks_node_group.gpu:
    operating_system: linux
    reserved_instances: none
    instance_count: 1
    monthly_hours: 730
    
  aws_db_instance.main:
    storage_gb: 500
    monthly_io_operations: 10000000
    backup_storage_gb: 100
    
  aws_s3_bucket.data:
    storage_gb: 1000
    monthly_tier_1_requests: 1000000
    monthly_tier_2_requests: 10000000
    
  aws_lb.main:
    monthly_data_processed_gb: 1000
    monthly_new_connections: 1000000
```

---

## 10. Security & Compliance

### 10.1 Security Scanning Configuration

**File: `/.github/workflows/security-scan.yml`**

```yaml
#===============================================================================
# Security Scanning Workflow
#===============================================================================
name: Security Scan

on:
  pull_request:
    paths:
      - '**.tf'
  push:
    branches:
      - main
  schedule:
    - cron: '0 0 * * *'

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          output_format: cli,sarif
          soft_fail: false
          
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: results.sarif

  tfsec:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run tfsec
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          soft_fail: false
          format: sarif
          out: tfsec.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: tfsec.sarif

  terrascan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Terrascan
        uses: tenable/terrascan-action@main
        with:
          iac_type: 'terraform'
          policy_type: 'aws'
          only_warn: false
```

### 10.2 Checkov Configuration

**File: `/policies/checkov/checkov.yml`**

```yaml
# Checkov Configuration for ResilienceAI
framework:
  - terraform

skip-check:
  - CKV_AWS_18
  - CKV_AWS_144

compact: true
quiet: true

external-checks-dir:
  - policies/checkov/custom/

skip-path:
  - modules/**/examples/**
  - "**/.terraform/**/*"

output: cli

soft-fail-on:
  - LOW
```

### 10.3 Terraform Compliance Policies

**File: `/policies/terraform-compliance/encryption.feature`**

```gherkin
Feature: Encryption must be enabled for all data at rest and in transit

  Scenario: EBS volumes must be encrypted
    Given I have aws_ebs_volume defined
    Then it must contain encrypted
    And its value must be true

  Scenario: RDS instances must be encrypted
    Given I have aws_db_instance defined
    Then it must contain storage_encrypted
    And its value must be true

  Scenario: S3 buckets must have encryption
    Given I have aws_s3_bucket_server_side_encryption_configuration defined
    Then it must contain rule
    And it must contain apply_server_side_encryption_by_default

  Scenario: EKS secrets must be encrypted
    Given I have aws_eks_cluster defined
    Then it must contain encryption_config
```

**File: `/policies/terraform-compliance/tags.feature`**

```gherkin
Feature: All resources must have required tags

  Scenario Outline: Resources must have required tags
    Given I have resource that supports tags defined
    Then it must contain tags
    And its value must contain <tag>

    Examples:
      | tag         |
      | Environment |
      | Project     |
      | ManagedBy   |
      | CostCenter  |
```

**File: `/policies/terraform-compliance/networking.feature`**

```gherkin
Feature: Network security requirements

  Scenario: Security groups should not allow unrestricted SSH access
    Given I have aws_security_group_rule defined
    When its type is ingress
    And its from_port is 22
    Then its cidr_blocks must not contain 0.0.0.0/0

  Scenario: Security groups should not allow unrestricted RDP access
    Given I have aws_security_group_rule defined
    When its type is ingress
    And its from_port is 3389
    Then its cidr_blocks must not contain 0.0.0.0/0

  Scenario: VPC flow logs must be enabled
    Given I have aws_vpc defined
    Then it must contain aws_flow_log
```

### 10.4 Sentinel Policies

**File: `/policies/sentinels/enforce-tags.sentinel`**

```sentinel
#===============================================================================
# Sentinel Policy: Enforce Required Tags
#===============================================================================

import "tfplan"

required_tags = [
  "Environment",
  "Project",
  "ManagedBy",
  "CostCenter",
]

all_resources = filter tfplan.resource_changes as _, rc {
  rc.mode == "managed" and
  rc.change.actions contains "create"
}

resources_with_tags = filter all_resources as _, rc {
  rc.change.after contains "tags"
}

violations = 0
for resources_with_tags as _, resource {
  tags = resource.change.after.tags
  
  for required_tags as tag {
    if not tags contains tag {
      print("Resource", resource.address, "is missing required tag:", tag)
      violations += 1
    }
  }
}

main = rule {
  violations == 0
}
```

**File: `/policies/sentinels/restrict-instance-types.sentinel`**

```sentinel
#===============================================================================
# Sentinel Policy: Restrict EC2 Instance Types
#===============================================================================

import "tfplan"

allowed_instance_types = [
  "t3.micro",
  "t3.small",
  "t3.medium",
  "t3.large",
  "m6i.large",
  "m6i.xlarge",
  "m6i.2xlarge",
  "m6i.4xlarge",
  "c6i.large",
  "c6i.xlarge",
  "c6i.2xlarge",
  "r6i.large",
  "r6i.xlarge",
  "r6i.2xlarge",
  "g4dn.xlarge",
  "g4dn.2xlarge",
]

ec2_instances = filter tfplan.resource_changes as _, rc {
  rc.type is "aws_instance" and
  rc.mode is "managed" and
  (rc.change.actions contains "create" or rc.change.actions contains "update")
}

violations = 0

for ec2_instances as _, instance {
  instance_type = instance.change.after.instance_type
  
  if instance_type not in allowed_instance_types {
    print("EC2 instance", instance.address, "uses disallowed instance type:", instance_type)
    violations += 1
  }
}

main = rule {
  violations == 0
}
```

---

## 11. Implementation Priority

### 11.1 Implementation Roadmap

| Phase | Priority | Components | Timeline | Dependencies |
|-------|----------|------------|----------|--------------|
| **Phase 1** | Critical | State Backend, VPC, IAM | Week 1-2 | None |
| **Phase 2** | Critical | EKS/GKE/AKS, Security Groups | Week 3-4 | Phase 1 |
| **Phase 3** | High | RDS/Cloud SQL/PostgreSQL | Week 5-6 | Phase 2 |
| **Phase 4** | High | S3/Storage, ALB/Ingress | Week 7-8 | Phase 2 |
| **Phase 5** | Medium | Monitoring, Logging | Week 9-10 | Phase 2-4 |
| **Phase 6** | Medium | CI/CD Pipelines | Week 11-12 | Phase 1-5 |
| **Phase 7** | Low | Cost Management, Drift Detection | Week 13-14 | Phase 6 |
| **Phase 8** | Low | Documentation, Runbooks | Week 15-16 | All |

### 11.2 Quick Start Guide

```bash
# 1. Clone repository
git clone https://github.com/resilienceai/infrastructure.git
cd infrastructure

# 2. Install prerequisites
# - Terraform >= 1.5.0
# - AWS CLI
# - kubectl

# 3. Bootstrap backend (one-time)
cd global/backend
terraform init
terraform apply

# 4. Deploy development environment
cd ../../environments/dev
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply

# 5. Verify deployment
aws eks update-kubeconfig --region us-east-1 --name resilienceai-dev
kubectl get nodes
```

---

## 12. Best Practices

### 12.1 Terraform Best Practices

```hcl
#===============================================================================
# Terraform Best Practices for ResilienceAI
#===============================================================================

# 1. Use consistent naming conventions
resource "aws_instance" "web_server" {
  # ...
}

# 2. Tag all resources
tags = {
  Name        = "${var.project_name}-${var.environment}-web"
  Environment = var.environment
  ManagedBy   = "Terraform"
  CostCenter  = "Engineering"
}

# 3. Use locals for repeated values
locals {
  common_tags = {
    Project = var.project_name
    Environment = var.environment
  }
  naming_prefix = "${var.project_name}-${var.environment}"
}

# 4. Use data sources for existing resources
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 5. Use modules for reusable components
module "vpc" {
  source = "../../modules/aws/vpc"
  
  project_name = var.project_name
  environment  = var.environment
}

# 6. Use remote state with locking
terraform {
  backend "s3" {
    bucket         = "resilienceai-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "resilienceai-terraform-locks"
  }
}

# 7. Use variable validation
variable "environment" {
  type = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# 8. Use lifecycle rules
resource "aws_instance" "example" {
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [ami]
  }
}

# 9. Use depends_on for explicit dependencies
resource "aws_instance" "example" {
  depends_on = [aws_security_group.example]
}
```

### 12.2 Security Best Practices

| Practice | Implementation |
|----------|----------------|
| **State Encryption** | Use S3 SSE-KMS for state files |
| **State Locking** | Use DynamoDB for state locking |
| **Least Privilege** | Use IAM roles with minimal permissions |
| **Secrets Management** | Use AWS Secrets Manager, never hardcode |
| **Network Segmentation** | Use VPCs, private subnets, security groups |
| **Encryption at Rest** | Enable encryption for all storage |
| **Encryption in Transit** | Use TLS 1.2+ for all communications |
| **Audit Logging** | Enable CloudTrail, VPC Flow Logs |
| **Regular Scanning** | Run Checkov, tfsec on every PR |
| **Drift Detection** | Automated drift detection every 6 hours |

### 12.3 Cost Optimization Best Practices

```hcl
# 1. Use Spot Instances where possible
resource "aws_eks_node_group" "spot" {
  capacity_type = "SPOT"
}

# 2. Enable autoscaling
resource "aws_eks_node_group" "main" {
  scaling_config {
    desired_size = 3
    min_size     = 1
    max_size     = 10
  }
}

# 3. Enable S3 lifecycle policies
resource "aws_s3_bucket_lifecycle_configuration" "example" {
  rule {
    id     = "transition-to-ia"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
    
    transition {
      days          = 365
      storage_class = "GLACIER"
    }
  }
}

# 4. Use Graviton instances for better price/performance
resource "aws_instance" "example" {
  instance_type = "m6g.large"
}
```

---

## 13. File Structure Summary

```
resilienceai-iac/
├── README.md
├── Makefile
├── .terraform-version
├── infracost.yml
├── infracost-usage.yml
│
├── global/
│   ├── backend/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── iam/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
│
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── prod/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── backend.tf
│
├── modules/
│   ├── aws/
│   │   ├── vpc/
│   │   ├── eks/
│   │   ├── rds/
│   │   ├── s3/
│   │   ├── iam/
│   │   ├── alb/
│   │   ├── cloudwatch/
│   │   ├── cost/
│   │   └── secrets-manager/
│   ├── gcp/
│   │   ├── vpc/
│   │   ├── gke/
│   │   ├── cloud-sql/
│   │   ├── cloud-storage/
│   │   ├── iam/
│   │   └── cloud-monitoring/
│   └── azure/
│       ├── vnet/
│       ├── aks/
│       ├── postgresql/
│       ├── storage/
│       ├── rbac/
│       └── monitor/
│
├── .github/
│   └── workflows/
│       ├── terraform-plan.yml
│       ├── terraform-apply.yml
│       ├── drift-detection.yml
│       └── security-scan.yml
│
├── policies/
│   ├── checkov/
│   │   ├── checkov.yml
│   │   └── custom/
│   ├── terraform-compliance/
│   │   ├── encryption.feature
│   │   ├── tags.feature
│   │   └── networking.feature
│   └── sentinel/
│       ├── enforce-tags.sentinel
│       └── restrict-instance-types.sentinel
│
├── scripts/
│   ├── bootstrap.sh
│   ├── cost-estimate.sh
│   └── drift-check.sh
│
└── docs/
    ├── architecture.md
    ├── modules.md
    └── runbooks/
        ├── incident-response.md
        └── disaster-recovery.md
```

---

## 14. Conclusion

This comprehensive Infrastructure as Code architecture provides ResilienceAI with:

1. **Multi-Cloud Support**: AWS, GCP, and Azure modules for flexibility
2. **Security-First Design**: Encryption, least privilege, continuous scanning
3. **Cost Optimization**: Budgets, anomaly detection, right-sizing
4. **Operational Excellence**: Drift detection, monitoring, automated remediation
5. **Compliance**: Policy as code with Checkov, tfsec, Sentinel
6. **Scalability**: Modular design for easy extension
7. **Collaboration**: GitOps workflow with PR reviews and approvals

### Next Steps

1. **Week 1**: Set up state backend and bootstrap infrastructure
2. **Week 2**: Deploy VPC and network foundation
3. **Week 3-4**: Deploy EKS cluster with security hardening
4. **Week 5-6**: Deploy database and storage resources
5. **Week 7-8**: Implement CI/CD pipelines
6. **Week 9-10**: Configure monitoring and alerting
7. **Week 11-12**: Security hardening and compliance validation

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: Platform Engineering Team*
