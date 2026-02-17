# Terraform Configuration for ResilienceAI Multi-Region DR Infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "resilienceai-terraform-state"
    key            = "dr-infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

# Primary region provider
provider "aws" {
  region = var.primary_region
  alias  = "primary"
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "ResilienceAI"
      ManagedBy   = "Terraform"
    }
  }
}

# DR region provider
provider "aws" {
  region = var.dr_region
  alias  = "dr"
  
  default_tags {
    tags = {
      Environment = var.environment
      Project     = "ResilienceAI"
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "primary_region" {
  description = "Primary AWS region"
  type        = string
  default     = "us-east-1"
}

variable "dr_region" {
  description = "DR AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "vpc_cidr_primary" {
  description = "CIDR block for primary VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_cidr_dr" {
  description = "CIDR block for DR VPC"
  type        = string
  default     = "10.1.0.0/16"
}

# Primary Region VPC
module "vpc_primary" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  providers = {
    aws = aws.primary
  }
  
  name = "resilienceai-primary"
  cidr = var.vpc_cidr_primary
  
  azs             = ["${var.primary_region}a", "${var.primary_region}b", "${var.primary_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway     = true
  single_nat_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true
  enable_vpn_gateway     = true
  
  tags = {
    Region = "primary"
  }
}

# DR Region VPC
module "vpc_dr" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  
  providers = {
    aws = aws.dr
  }
  
  name = "resilienceai-dr"
  cidr = var.vpc_cidr_dr
  
  azs             = ["${var.dr_region}a", "${var.dr_region}b", "${var.dr_region}c"]
  private_subnets = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
  public_subnets  = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]
  
  enable_nat_gateway     = true
  single_nat_gateway     = false
  enable_dns_hostnames   = true
  enable_dns_support     = true
  enable_vpn_gateway     = true
  
  tags = {
    Region = "dr"
  }
}

# VPC Peering between regions
resource "aws_vpc_peering_connection" "primary_to_dr" {
  provider = aws.primary
  
  vpc_id        = module.vpc_primary.vpc_id
  peer_vpc_id   = module.vpc_dr.vpc_id
  peer_region   = var.dr_region
  auto_accept   = false
  
  tags = {
    Name = "primary-to-dr-peering"
  }
}

resource "aws_vpc_peering_connection_accepter" "dr_accept" {
  provider = aws.dr
  
  vpc_peering_connection_id = aws_vpc_peering_connection.primary_to_dr.id
  auto_accept               = true
  
  tags = {
    Name = "dr-accept-peering"
  }
}

# Route table updates for peering
resource "aws_route" "primary_to_dr" {
  provider = aws.primary
  
  route_table_id            = module.vpc_primary.private_route_table_ids[0]
  destination_cidr_block    = var.vpc_cidr_dr
  vpc_peering_connection_id = aws_vpc_peering_connection.primary_to_dr.id
}

resource "aws_route" "dr_to_primary" {
  provider = aws.dr
  
  route_table_id            = module.vpc_dr.private_route_table_ids[0]
  destination_cidr_block    = var.vpc_cidr_primary
  vpc_peering_connection_id = aws_vpc_peering_connection.primary_to_dr.id
}

# Primary EKS Cluster
module "eks_primary" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  providers = {
    aws = aws.primary
  }
  
  cluster_name    = "resilienceai-primary"
  cluster_version = "1.28"
  
  vpc_id                         = module.vpc_primary.vpc_id
  subnet_ids                     = module.vpc_primary.private_subnets
  control_plane_subnet_ids       = module.vpc_primary.private_subnets
  
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true
  
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
  
  eks_managed_node_groups = {
    general = {
      desired_size = 3
      min_size     = 2
      max_size     = 10
      
      instance_types = ["m6i.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        workload = "general"
      }
      
      tags = {
        Region = "primary"
      }
    }
    
    gpu = {
      desired_size = 2
      min_size     = 1
      max_size     = 5
      
      instance_types = ["g5.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        workload = "gpu"
        "nvidia.com/gpu" = "true"
      }
      
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
      
      tags = {
        Region = "primary"
      }
    }
  }
  
  tags = {
    Environment = var.environment
  }
}

# DR EKS Cluster
module "eks_dr" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  providers = {
    aws = aws.dr
  }
  
  cluster_name    = "resilienceai-dr"
  cluster_version = "1.28"
  
  vpc_id                         = module.vpc_dr.vpc_id
  subnet_ids                     = module.vpc_dr.private_subnets
  control_plane_subnet_ids       = module.vpc_dr.private_subnets
  
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true
  
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }
  
  eks_managed_node_groups = {
    general = {
      desired_size = 2
      min_size     = 1
      max_size     = 10
      
      instance_types = ["m6i.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        workload = "general"
      }
      
      tags = {
        Region = "dr"
      }
    }
    
    gpu = {
      desired_size = 1
      min_size     = 0
      max_size     = 5
      
      instance_types = ["g5.xlarge"]
      capacity_type  = "ON_DEMAND"
      
      labels = {
        workload = "gpu"
        "nvidia.com/gpu" = "true"
      }
      
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
      
      tags = {
        Region = "dr"
      }
    }
  }
  
  tags = {
    Environment = var.environment
  }
}

# Outputs
output "primary_vpc_id" {
  description = "Primary VPC ID"
  value       = module.vpc_primary.vpc_id
}

output "dr_vpc_id" {
  description = "DR VPC ID"
  value       = module.vpc_dr.vpc_id
}

output "primary_eks_cluster_endpoint" {
  description = "Primary EKS cluster endpoint"
  value       = module.eks_primary.cluster_endpoint
  sensitive   = true
}

output "dr_eks_cluster_endpoint" {
  description = "DR EKS cluster endpoint"
  value       = module.eks_dr.cluster_endpoint
  sensitive   = true
}

output "vpc_peering_connection_id" {
  description = "VPC peering connection ID"
  value       = aws_vpc_peering_connection.primary_to_dr.id
}
