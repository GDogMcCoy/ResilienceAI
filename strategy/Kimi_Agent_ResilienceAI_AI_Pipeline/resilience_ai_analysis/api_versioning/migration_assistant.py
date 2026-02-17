"""
Migration Assistant

Provides automated tools to assist with API version migrations.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class MigrationStep:
    """Single migration step."""
    id: str
    description: str
    severity: str  # "info", "warning", "error"
    auto_fixable: bool
    fix_code: str = ""
    documentation_url: str = ""
    line_number: Optional[int] = None
    original_code: str = ""
    suggested_code: str = ""


@dataclass
class MigrationReport:
    """Complete migration analysis report."""
    source_version: str
    target_version: str
    total_issues: int
    auto_fixable: int
    manual_fix_required: int
    steps: List[MigrationStep]
    estimated_effort_hours: float
    breaking_changes: List[str]


class MigrationAssistant:
    """
    Assists with API version migrations.
    
    Provides:
    - Code analysis
    - Automated migration scripts
    - Validation tools
    - Effort estimation
    """
    
    # Migration rules between versions
    MIGRATION_RULES = {
        ("v1", "v2"): {
            "field_mappings": {
                "incident_id": "id",
                "created_at": "created_timestamp",
                "severity_level": "severity",
                "old_status": "status"
            },
            "value_transforms": {
                "severity": {
                    "low": "P4",
                    "medium": "P3",
                    "high": "P2",
                    "critical": "P1"
                }
            },
            "endpoint_changes": {
                "/v1/incidents/list": "/v2/incidents",
                "/v1/incidents/create": "/v2/incidents",
                "/v1/incidents/{id}/details": "/v2/incidents/{id}",
                "/v1/incidents/{id}/update": "/v2/incidents/{id}"
            },
            "removed_fields": ["legacy_field", "old_status"],
            "added_fields": ["updated_timestamp", "assignee", "tags"],
            "breaking_changes": [
                "Field 'incident_id' renamed to 'id'",
                "Field 'created_at' renamed to 'created_timestamp'",
                "Severity values changed from strings ('low', 'medium', 'high', 'critical') to P-levels ('P4', 'P3', 'P2', 'P1')",
                "Timestamp format changed to ISO 8601",
                "Endpoint '/v1/incidents/list' changed to '/v2/incidents'",
                "Response structure changed from 'incidents' array to 'data' array with pagination"
            ]
        }
    }
    
    def __init__(self, source_version: str, target_version: str):
        self.source_version = source_version
        self.target_version = target_version
        self.rules = self._load_migration_rules()
    
    def _load_migration_rules(self) -> Dict[str, Any]:
        """Load migration rules for version pair."""
        return self.MIGRATION_RULES.get(
            (self.source_version, self.target_version),
            {}
        )
    
    def analyze_code(self, code: str, language: str = "python") -> List[MigrationStep]:
        """
        Analyze code for migration issues.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            List of migration steps
        """
        steps = []
        
        # Check for old field names
        for old_name, new_name in self.rules.get("field_mappings", {}).items():
            pattern = rf'\b{re.escape(old_name)}\b'
            for match in re.finditer(pattern, code):
                steps.append(MigrationStep(
                    id=f"FIELD_{old_name.upper()}",
                    description=f"Replace '{old_name}' with '{new_name}'",
                    severity="error",
                    auto_fixable=True,
                    fix_code=f"s/{old_name}/{new_name}/g",
                    documentation_url=f"/docs/migration/{self.source_version}-to-{self.target_version}#{new_name}",
                    line_number=code[:match.start()].count("\n") + 1,
                    original_code=old_name,
                    suggested_code=new_name
                ))
        
        # Check for old endpoints
        for old_endpoint, new_endpoint in self.rules.get("endpoint_changes", {}).items():
            if old_endpoint in code:
                steps.append(MigrationStep(
                    id=f"ENDPOINT_{old_endpoint.replace('/', '_').upper()}",
                    description=f"Update endpoint from '{old_endpoint}' to '{new_endpoint}'",
                    severity="error",
                    auto_fixable=True,
                    fix_code=f"s/{re.escape(old_endpoint)}/{re.escape(new_endpoint)}/g",
                    documentation_url=f"/docs/migration/{self.source_version}-to-{self.target_version}#endpoints",
                    original_code=old_endpoint,
                    suggested_code=new_endpoint
                ))
        
        # Check for old severity values
        severity_transforms = self.rules.get("value_transforms", {}).get("severity", {})
        for old_value, new_value in severity_transforms.items():
            pattern = rf'["\']{re.escape(old_value)}["\']'
            for match in re.finditer(pattern, code, re.IGNORECASE):
                steps.append(MigrationStep(
                    id=f"SEVERITY_{old_value.upper()}",
                    description=f"Update severity value from '{old_value}' to '{new_value}'",
                    severity="error",
                    auto_fixable=True,
                    fix_code=f"s/{old_value}/{new_value}/gi",
                    documentation_url=f"/docs/migration/{self.source_version}-to-{self.target_version}#severity",
                    line_number=code[:match.start()].count("\n") + 1,
                    original_code=old_value,
                    suggested_code=new_value
                ))
        
        # Check for removed fields
        for removed_field in self.rules.get("removed_fields", []):
            if removed_field in code:
                steps.append(MigrationStep(
                    id=f"REMOVED_{removed_field.upper()}",
                    description=f"Remove usage of deprecated field '{removed_field}'",
                    severity="warning",
                    auto_fixable=False,
                    documentation_url=f"/docs/migration/{self.source_version}-to-{self.target_version}#removed-fields",
                    original_code=removed_field,
                    suggested_code="# Remove this field"
                ))
        
        return steps
    
    def generate_migration_script(self, code: str, language: str = "python") -> str:
        """
        Generate automated migration script.
        
        Args:
            code: Source code to migrate
            language: Programming language
            
        Returns:
            Migration script
        """
        steps = self.analyze_code(code, language)
        auto_fixable_steps = [s for s in steps if s.auto_fixable]
        
        script = f"""#!/usr/bin/env python3
# Auto-generated migration script: {self.source_version} -> {self.target_version}
# Generated: {datetime.now().isoformat()}
# Total issues found: {len(steps)}
# Auto-fixable: {len(auto_fixable_steps)}

import re
import sys

def migrate_code(source_code: str) -> str:
    code = source_code
    changes_made = []
    
"""
        
        for step in auto_fixable_steps:
            parts = step.fix_code.split("/")
            if len(parts) >= 3:
                pattern = parts[1]
                replacement = parts[2]
                flags = parts[3] if len(parts) > 3 else ""
                
                script += f"""
    # {step.description}
    # Line {step.line_number or 'unknown'}
    original_code = code
    code = re.sub(r'{pattern}', '{replacement}', code{', flags=re.IGNORECASE' if 'i' in flags else ''})
    if code != original_code:
        changes_made.append("{step.description}")
    
"""
        
        script += """
    return code, changes_made

def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <source_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    with open(filepath, 'r') as f:
        source = f.read()
    
    migrated, changes = migrate_code(source)
    
    output_path = filepath + '.migrated'
    with open(output_path, 'w') as f:
        f.write(migrated)
    
    print(f"Migrated {{filepath}} -> {{output_path}}")
    print(f"Changes made: {{len(changes)}}")
    for change in changes:
        print(f"  - {{change}}")
    
    print("\\nNOTE: Please review the migrated code before deploying.")
    print("Some changes may require manual verification.")

if __name__ == "__main__":
    main()
"""
        
        return script
    
    def validate_migration(
        self,
        old_response: Dict[str, Any],
        new_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that migration produces equivalent results.
        
        Args:
            old_response: Response from old version
            new_response: Response from new version
            
        Returns:
            Validation results
        """
        validation = {
            "passed": True,
            "warnings": [],
            "errors": [],
            "field_checks": []
        }
        
        # Check field presence
        field_mappings = self.rules.get("field_mappings", {})
        for old_field, new_field in field_mappings.items():
            check = {
                "old_field": old_field,
                "new_field": new_field,
                "old_present": old_field in old_response,
                "new_present": new_field in new_response
            }
            
            if old_field in old_response and new_field not in new_response:
                validation["passed"] = False
                validation["errors"].append(
                    f"Expected field '{new_field}' not found in new response"
                )
                check["status"] = "FAILED"
            else:
                check["status"] = "PASSED"
            
            validation["field_checks"].append(check)
        
        # Check response structure
        if "data" in new_response and "incidents" in old_response:
            if len(new_response.get("data", [])) != len(old_response.get("incidents", [])):
                validation["warnings"].append(
                    "Response array lengths differ"
                )
        
        return validation
    
    def estimate_effort(self, code: str) -> Dict[str, Any]:
        """
        Estimate migration effort.
        
        Args:
            code: Source code to analyze
            
        Returns:
            Effort estimation
        """
        steps = self.analyze_code(code)
        
        error_count = len([s for s in steps if s.severity == "error"])
        warning_count = len([s for s in steps if s.severity == "warning"])
        auto_fixable = len([s for s in steps if s.auto_fixable])
        manual_fix = len([s for s in steps if not s.auto_fixable])
        
        # Estimate hours
        base_hours = 2
        error_hours = error_count * 0.5
        warning_hours = warning_count * 0.25
        manual_hours = manual_fix * 1.0
        
        total_hours = base_hours + error_hours + warning_hours + manual_hours
        
        return {
            "total_issues": len(steps),
            "errors": error_count,
            "warnings": warning_count,
            "auto_fixable": auto_fixable,
            "manual_fix_required": manual_fix,
            "estimated_hours": round(total_hours, 1),
            "estimated_days": round(total_hours / 8, 1),
            "complexity": self._calculate_complexity(len(steps), manual_fix)
        }
    
    def _calculate_complexity(self, total_issues: int, manual_fix: int) -> str:
        """Calculate migration complexity."""
        if total_issues < 10 and manual_fix == 0:
            return "low"
        elif total_issues < 50 and manual_fix < 10:
            return "medium"
        return "high"
    
    def generate_report(self, code: str) -> MigrationReport:
        """
        Generate complete migration report.
        
        Args:
            code: Source code to analyze
            
        Returns:
            Migration report
        """
        steps = self.analyze_code(code)
        effort = self.estimate_effort(code)
        
        return MigrationReport(
            source_version=self.source_version,
            target_version=self.target_version,
            total_issues=len(steps),
            auto_fixable=len([s for s in steps if s.auto_fixable]),
            manual_fix_required=len([s for s in steps if not s.auto_fixable]),
            steps=steps,
            estimated_effort_hours=effort["estimated_hours"],
            breaking_changes=self.rules.get("breaking_changes", [])
        )
    
    def print_report(self, report: MigrationReport):
        """Print migration report to console."""
        print("=" * 60)
        print(f"MIGRATION REPORT: {report.source_version} -> {report.target_version}")
        print("=" * 60)
        print()
        print(f"Total Issues: {report.total_issues}")
        print(f"  - Auto-fixable: {report.auto_fixable}")
        print(f"  - Manual fix required: {report.manual_fix_required}")
        print()
        print(f"Estimated Effort: {report.estimated_effort_hours} hours")
        print()
        print("Breaking Changes:")
        for change in report.breaking_changes:
            print(f"  - {change}")
        print()
        print("Migration Steps:")
        for step in report.steps:
            icon = "✓" if step.auto_fixable else "✗"
            print(f"  [{icon}] {step.severity.upper()}: {step.description}")
        print()
        print("=" * 60)


# Usage example
if __name__ == "__main__":
    # Example code to analyze
    example_code = '''
import requests

# Old V1 API calls
response = requests.get("https://api.resilienceai.com/v1/incidents/list")
data = response.json()

for incident in data["incidents"]:
    incident_id = incident["incident_id"]
    created = incident["created_at"]
    severity = incident["severity_level"]  # "high", "medium", etc.
    
    if incident["old_status"] == "open":
        print(f"Open incident: {incident_id}")
'''
    
    # Create migration assistant
    assistant = MigrationAssistant("v1", "v2")
    
    # Generate report
    report = assistant.generate_report(example_code)
    
    # Print report
    assistant.print_report(report)
    
    # Generate migration script
    script = assistant.generate_migration_script(example_code)
    print("\nGenerated Migration Script:")
    print("-" * 60)
    print(script)
