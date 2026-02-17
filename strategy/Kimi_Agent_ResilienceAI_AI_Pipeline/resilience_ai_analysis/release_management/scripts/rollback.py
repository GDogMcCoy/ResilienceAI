#!/usr/bin/env python3
"""
Automated rollback system for ResilienceAI
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, Optional


class RollbackManager:
    """Manage production rollbacks"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.kubeconfig = f"k8s/{environment}/kubeconfig"
        self.namespace = environment
    
    def get_current_version(self) -> str:
        try:
            result = subprocess.run(
                ['kubectl', '--kubeconfig', self.kubeconfig,
                 'get', 'deployment', 'api', '-n', self.namespace,
                 '-o', 'jsonpath={.spec.template.spec.containers[0].image}'],
                capture_output=True, text=True, check=True
            )
            image = result.stdout.strip()
            if ':' in image:
                return image.split(':')[-1].lstrip('v')
            return "unknown"
        except subprocess.CalledProcessError:
            return "unknown"
    
    def get_previous_version(self) -> Optional[str]:
        try:
            result = subprocess.run(
                ['kubectl', '--kubeconfig', self.kubeconfig,
                 'rollout', 'history', 'deployment/api', '-n', self.namespace],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                prev_revision = lines[-2].split()[0]
                result = subprocess.run(
                    ['kubectl', '--kubeconfig', self.kubeconfig,
                     'rollout', 'history', 'deployment/api', '-n', self.namespace,
                     '--revision', prev_revision],
                    capture_output=True, text=True, check=True
                )
                for line in result.stdout.split('\n'):
                    if 'Image:' in line:
                        image = line.split(':')[-1].strip()
                        return image.split(':')[-1].lstrip('v')
            return None
        except subprocess.CalledProcessError:
            return None
    
    def rollback(self, target_version: Optional[str] = None, reason: str = "manual") -> bool:
        current = self.get_current_version()
        
        if target_version is None:
            target = self.get_previous_version()
            if target is None:
                print("Error: Could not determine previous version")
                return False
        else:
            target = target_version
        
        print(f"Rolling back from v{current} to v{target}")
        print(f"Reason: {reason}")
        
        rollback_id = self._record_rollback_start(current, target, reason)
        
        try:
            services = ['api', 'ml-worker', 'frontend', 'scheduler']
            for service in services:
                print(f"Rolling back {service}...")
                self._rollback_service(service, target)
            
            if self._verify_rollback(target):
                self._record_rollback_complete(rollback_id, 'success')
                print(f"Rollback to v{target} completed successfully")
                return True
            else:
                self._record_rollback_complete(rollback_id, 'verification_failed')
                print("Rollback verification failed!")
                return False
        except Exception as e:
            self._record_rollback_complete(rollback_id, 'failed', str(e))
            print(f"Rollback failed: {e}")
            return False
    
    def _rollback_service(self, service: str, version: str):
        image = f"ghcr.io/resilienceai/{service}:v{version}"
        subprocess.run(
            ['kubectl', '--kubeconfig', self.kubeconfig,
             'set', 'image', f'deployment/{service}',
             f'{service}={image}', '-n', self.namespace],
            check=True
        )
        subprocess.run(
            ['kubectl', '--kubeconfig', self.kubeconfig,
             'rollout', 'status', f'deployment/{service}',
             '-n', self.namespace, '--timeout', '300s'],
            check=True
        )
    
    def _verify_rollback(self, expected_version: str) -> bool:
        print("Verifying rollback...")
        services = ['api', 'ml-worker', 'frontend', 'scheduler']
        
        for service in services:
            result = subprocess.run(
                ['kubectl', '--kubeconfig', self.kubeconfig,
                 'get', 'deployment', service, '-n', self.namespace,
                 '-o', 'jsonpath={.spec.template.spec.containers[0].image}'],
                capture_output=True, text=True, check=True
            )
            if f':v{expected_version}' not in result.stdout:
                print(f"Verification failed for {service}")
                return False
        return self._run_health_checks()
    
    def _run_health_checks(self) -> bool:
        print("Running health checks...")
        try:
            result = subprocess.run(
                ['kubectl', '--kubeconfig', self.kubeconfig,
                 'exec', '-n', self.namespace, 'deployment/api', '--',
                 'curl', '-sf', 'http://localhost:8080/health'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                print("API health check failed")
                return False
            health = json.loads(result.stdout)
            if health.get('status') != 'healthy':
                print(f"API unhealthy: {health}")
                return False
        except Exception as e:
            print(f"Health check error: {e}")
            return False
        return True
    
    def _record_rollback_start(self, from_version: str, to_version: str, reason: str) -> str:
        rollback_id = f"rollback-{int(time.time())}"
        record = {
            'id': rollback_id,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': self.environment,
            'from_version': from_version,
            'to_version': to_version,
            'reason': reason,
            'status': 'in_progress'
        }
        self._append_rollback_log(record)
        self._notify_rollback_started(record)
        return rollback_id
    
    def _record_rollback_complete(self, rollback_id: str, status: str, error: str = None):
        record = {
            'id': rollback_id,
            'completed_at': datetime.utcnow().isoformat(),
            'status': status,
            'error': error
        }
        self._append_rollback_log(record)
        self._notify_rollback_completed(record)
    
    def _append_rollback_log(self, record: dict):
        import os
        os.makedirs('logs', exist_ok=True)
        log_file = f"logs/rollbacks-{self.environment}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def _notify_rollback_started(self, record: dict):
        print(f"Rollback Started: {record}")
    
    def _notify_rollback_completed(self, record: dict):
        print(f"Rollback {record['status'].upper()}: {record['id']}")


def main():
    parser = argparse.ArgumentParser(description='Rollback ResilienceAI deployment')
    parser.add_argument('--environment', required=True, choices=['staging', 'production'])
    parser.add_argument('--version', help='Target version to rollback to')
    parser.add_argument('--reason', default='manual', help='Rollback reason')
    args = parser.parse_args()
    
    manager = RollbackManager(args.environment)
    success = manager.rollback(target_version=args.version, reason=args.reason)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
