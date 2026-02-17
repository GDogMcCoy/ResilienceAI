# /mnt/okcomputer/output/resilience_ai_analysis/code/cold_storage.py
"""
Cold Storage Manager for ResilienceAI
Manages cold storage operations using AWS S3 Glacier and similar services.
"""

import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import logging
import json


class ColdStorageManager:
    """Manages cold storage operations for ResilienceAI."""
    
    def __init__(self, region: str = 'us-east-1'):
        self.s3 = boto3.client('s3', region_name=region)
        self.glacier = boto3.client('glacier', region_name=region)
        self.logger = logging.getLogger(__name__)
        
        # Storage tier configuration
        self.tier_config = {
            'STANDARD_IA': {
                'min_storage_days': 30,
                'retrieval_time': 'milliseconds',
                'cost_per_gb': 0.0125,
                'retrieval_cost_per_gb': 0.01
            },
            'GLACIER_IR': {
                'min_storage_days': 90,
                'retrieval_time': 'milliseconds',
                'cost_per_gb': 0.004,
                'retrieval_cost_per_gb': 0.0025
            },
            'GLACIER': {
                'min_storage_days': 90,
                'retrieval_time': '1-5 minutes',
                'cost_per_gb': 0.0036,
                'retrieval_cost_per_gb': 0.0025
            },
            'DEEP_ARCHIVE': {
                'min_storage_days': 180,
                'retrieval_time': '12-48 hours',
                'cost_per_gb': 0.00099,
                'retrieval_cost_per_gb': 0.0025
            }
        }
    
    def transition_to_cold_storage(self, bucket: str, key: str, 
                                   target_tier: str = 'GLACIER') -> Dict:
        """Transition an object to cold storage tier."""
        try:
            # Get current object metadata
            response = self.s3.head_object(Bucket=bucket, Key=key)
            current_storage_class = response.get('StorageClass', 'STANDARD')
            
            # Copy object to same location with new storage class
            self.s3.copy_object(
                Bucket=bucket,
                Key=key,
                CopySource={'Bucket': bucket, 'Key': key},
                StorageClass=target_tier,
                MetadataDirective='COPY'
            )
            
            self.logger.info(f"Transitioned {key} to {target_tier}")
            
            return {
                'status': 'success',
                'object_key': key,
                'previous_tier': current_storage_class,
                'new_tier': target_tier,
                'transition_time': datetime.now().isoformat()
            }
            
        except ClientError as e:
            self.logger.error(f"Failed to transition {key}: {str(e)}")
            return {
                'status': 'error',
                'object_key': key,
                'error': str(e)
            }
    
    def initiate_retrieval(self, bucket: str, key: str, 
                          tier: str = 'Standard') -> Dict:
        """Initiate retrieval of object from Glacier/Deep Archive."""
        try:
            response = self.s3.restore_object(
                Bucket=bucket,
                Key=key,
                RestoreRequest={
                    'Days': 7,
                    'GlacierJobParameters': {
                        'Tier': tier  # Expedited, Standard, or Bulk
                    }
                }
            )
            
            self.logger.info(f"Initiated retrieval for {key} with tier {tier}")
            
            return {
                'status': 'retrieval_initiated',
                'object_key': key,
                'retrieval_tier': tier,
                'restore_duration_days': 7,
                'request_id': response.get('RequestId')
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'RestoreAlreadyInProgress':
                return {
                    'status': 'retrieval_in_progress',
                    'object_key': key
                }
            self.logger.error(f"Failed to initiate retrieval for {key}: {str(e)}")
            return {
                'status': 'error',
                'object_key': key,
                'error': str(e)
            }
    
    def check_restore_status(self, bucket: str, key: str) -> Dict:
        """Check if an object has been restored from Glacier."""
        try:
            response = self.s3.head_object(Bucket=bucket, Key=key)
            
            restore_status = response.get('Restore', '')
            is_ongoing = 'ongoing-request="true"' in restore_status
            is_completed = 'ongoing-request="false"' in restore_status
            
            if is_completed:
                expiry = restore_status.split('expiry-date="')[1].split('"')[0]
                return {
                    'status': 'restored',
                    'object_key': key,
                    'restore_expiry': expiry,
                    'can_access': True
                }
            elif is_ongoing:
                return {
                    'status': 'in_progress',
                    'object_key': key,
                    'can_access': False
                }
            else:
                return {
                    'status': 'not_initiated',
                    'object_key': key,
                    'can_access': False
                }
                
        except ClientError as e:
            return {
                'status': 'error',
                'object_key': key,
                'error': str(e)
            }
    
    def batch_transition(self, bucket: str, prefix: str, 
                        target_tier: str = 'GLACIER',
                        max_objects: int = 1000) -> Dict:
        """Batch transition objects to cold storage."""
        transitioned = []
        failed = []
        
        paginator = self.s3.get_paginator('list_objects_v2')
        
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get('Contents', []):
                if len(transitioned) >= max_objects:
                    break
                
                result = self.transition_to_cold_storage(bucket, obj['Key'], target_tier)
                
                if result['status'] == 'success':
                    transitioned.append(result)
                else:
                    failed.append(result)
        
        return {
            'total_processed': len(transitioned) + len(failed),
            'transitioned': len(transitioned),
            'failed': len(failed),
            'target_tier': target_tier,
            'transitioned_objects': transitioned,
            'failed_objects': failed
        }
    
    def calculate_storage_cost(self, storage_gb: float, tier: str, 
                              months: int = 12) -> Dict:
        """Calculate storage costs for a given tier."""
        config = self.tier_config.get(tier, self.tier_config['GLACIER'])
        
        storage_cost = storage_gb * config['cost_per_gb'] * months
        
        return {
            'tier': tier,
            'storage_gb': storage_gb,
            'duration_months': months,
            'cost_per_gb_month': config['cost_per_gb'],
            'estimated_storage_cost': round(storage_cost, 2),
            'retrieval_time': config['retrieval_time'],
            'min_storage_days': config['min_storage_days']
        }


if __name__ == "__main__":
    # Example usage (requires AWS credentials)
    print("Cold Storage Manager Example")
    print("=" * 50)
    
    manager = ColdStorageManager()
    
    # Calculate costs for different tiers
    for tier in ['STANDARD_IA', 'GLACIER_IR', 'GLACIER', 'DEEP_ARCHIVE']:
        cost = manager.calculate_storage_cost(1000, tier, 12)  # 1TB for 12 months
        print(f"\n{tier}:")
        print(f"  Cost: ${cost['estimated_storage_cost']}/year for 1TB")
        print(f"  Retrieval time: {cost['retrieval_time']}")
