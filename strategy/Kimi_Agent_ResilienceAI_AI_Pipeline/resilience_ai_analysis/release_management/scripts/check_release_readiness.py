#!/usr/bin/env python3
"""
Check if the codebase is ready for release
"""

import argparse
import json
import subprocess
import sys
import os
from dataclasses import dataclass
from typing import List


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    severity: str


class ReleaseReadinessChecker:
    def __init__(self, version: str):
        self.version = version
        self.results: List[CheckResult] = []
    
    def run_all_checks(self) -> bool:
        checks = [
            self.check_tests_pass,
            self.check_no_uncommitted_changes,
            self.check_changelog_updated,
            self.check_version_file_updated,
            self.check_security_scans_pass,
            self.check_documentation_updated,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.results.append(CheckResult(
                    name=check.__name__,
                    passed=False,
                    message=str(e),
                    severity='error'
                ))
        
        return all(r.passed for r in self.results if r.severity == 'error')
    
    def check_tests_pass(self):
        try:
            result = subprocess.run(
                ['pytest', '--tb=short', '-q'],
                capture_output=True,
                text=True,
                timeout=300
            )
            passed = result.returncode == 0
            self.results.append(CheckResult(
                name='tests_pass',
                passed=passed,
                message='All tests pass' if passed else f'Tests failed',
                severity='error'
            ))
        except Exception as e:
            self.results.append(CheckResult(
                name='tests_pass',
                passed=False,
                message=f'Could not run tests: {e}',
                severity='error'
            ))
    
    def check_no_uncommitted_changes(self):
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True
        )
        has_changes = bool(result.stdout.strip())
        self.results.append(CheckResult(
            name='no_uncommitted_changes',
            passed=not has_changes,
            message='No uncommitted changes' if not has_changes else 'Uncommitted changes detected',
            severity='error'
        ))
    
    def check_changelog_updated(self):
        try:
            with open('CHANGELOG.md', 'r') as f:
                content = f.read()
            has_version = self.version in content
            self.results.append(CheckResult(
                name='changelog_updated',
                passed=has_version,
                message=f'CHANGELOG.md contains version {self.version}' if has_version else f'CHANGELOG.md missing version',
                severity='warning'
            ))
        except FileNotFoundError:
            self.results.append(CheckResult(
                name='changelog_updated',
                passed=False,
                message='CHANGELOG.md not found',
                severity='warning'
            ))
    
    def check_version_file_updated(self):
        try:
            with open('version.json', 'r') as f:
                data = json.load(f)
            matches = data.get('version') == self.version
            self.results.append(CheckResult(
                name='version_file_updated',
                passed=matches,
                message=f'Version file matches' if matches else f'Version file does not match',
                severity='error'
            ))
        except FileNotFoundError:
            self.results.append(CheckResult(
                name='version_file_updated',
                passed=False,
                message='version.json not found',
                severity='error'
            ))
    
    def check_security_scans_pass(self):
        security_files = ['trivy-results.sarif', 'safety-report.json']
        found_reports = [f for f in security_files if os.path.exists(f)]
        self.results.append(CheckResult(
            name='security_scans',
            passed=len(found_reports) > 0,
            message=f'Security reports found' if found_reports else 'No security reports',
            severity='warning'
        ))
    
    def check_documentation_updated(self):
        docs_exist = os.path.exists('docs') and os.listdir('docs')
        self.results.append(CheckResult(
            name='documentation_updated',
            passed=docs_exist,
            message='Documentation exists' if docs_exist else 'Documentation missing',
            severity='warning'
        ))
    
    def print_report(self):
        print("\n" + "="*70)
        print("RELEASE READINESS REPORT")
        print("="*70)
        print(f"Version: {self.version}")
        print("-"*70)
        
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            icon = " " if result.passed else ""
            print(f"{icon} [{status}] {result.name}")
            print(f"         {result.message}")
        
        print("-"*70)
        errors = sum(1 for r in self.results if not r.passed and r.severity == 'error')
        warnings = sum(1 for r in self.results if not r.passed and r.severity == 'warning')
        print(f"Errors: {errors}, Warnings: {warnings}")
        print("="*70)


def main():
    parser = argparse.ArgumentParser(description='Check release readiness')
    parser.add_argument('--version', required=True, help='Version to check')
    args = parser.parse_args()
    
    checker = ReleaseReadinessChecker(args.version)
    ready = checker.run_all_checks()
    checker.print_report()
    
    print(f"::set-output name=should_release::{str(ready).lower()}")
    print(f"should_release={str(ready).lower()}")
    
    sys.exit(0 if ready else 1)


if __name__ == '__main__':
    main()
