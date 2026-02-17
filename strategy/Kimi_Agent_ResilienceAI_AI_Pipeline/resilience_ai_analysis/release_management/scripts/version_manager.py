#!/usr/bin/env python3
"""
Semantic Version Manager for ResilienceAI
"""

import re
import json
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


class VersionBumpType(Enum):
    MAJOR = "major"      # Breaking changes
    MINOR = "minor"      # New features (backward compatible)
    PATCH = "patch"      # Bug fixes (backward compatible)
    HOTFIX = "hotfix"    # Emergency fixes
    PRERELEASE = "prerelease"  # Alpha, beta, rc


@dataclass
class SemanticVersion:
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    @classmethod
    def parse(cls, version_string: str) -> "SemanticVersion":
        """Parse semantic version string"""
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$'
        match = re.match(pattern, version_string)
        
        if not match:
            raise ValueError(f"Invalid semantic version: {version_string}")
        
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4),
            build=match.group(5)
        )
    
    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version
    
    def bump(self, bump_type: VersionBumpType, prerelease_id: Optional[str] = None) -> "SemanticVersion":
        """Bump version based on type"""
        if bump_type == VersionBumpType.MAJOR:
            return SemanticVersion(
                major=self.major + 1,
                minor=0,
                patch=0,
                prerelease=prerelease_id
            )
        elif bump_type == VersionBumpType.MINOR:
            return SemanticVersion(
                major=self.major,
                minor=self.minor + 1,
                patch=0,
                prerelease=prerelease_id
            )
        elif bump_type == VersionBumpType.PATCH:
            return SemanticVersion(
                major=self.major,
                minor=self.minor,
                patch=self.patch + 1,
                prerelease=prerelease_id
            )
        elif bump_type == VersionBumpType.HOTFIX:
            return SemanticVersion(
                major=self.major,
                minor=self.minor,
                patch=self.patch + 1,
                prerelease=None
            )
        elif bump_type == VersionBumpType.PRERELEASE:
            return SemanticVersion(
                major=self.major,
                minor=self.minor,
                patch=self.patch,
                prerelease=prerelease_id or "alpha.1"
            )
        else:
            raise ValueError(f"Unknown bump type: {bump_type}")
    
    def is_prerelease(self) -> bool:
        return self.prerelease is not None
    
    def compare(self, other: "SemanticVersion") -> int:
        """Compare two versions. Returns: -1, 0, 1"""
        for attr in ['major', 'minor', 'patch']:
            self_val = getattr(self, attr)
            other_val = getattr(other, attr)
            if self_val < other_val:
                return -1
            elif self_val > other_val:
                return 1
        
        if self.prerelease is None and other.prerelease is not None:
            return 1
        elif self.prerelease is not None and other.prerelease is None:
            return -1
        elif self.prerelease and other.prerelease:
            if self.prerelease < other.prerelease:
                return -1
            elif self.prerelease > other.prerelease:
                return 1
        
        return 0


class VersionManager:
    """Manages versioning across ResilienceAI components"""
    
    def __init__(self, version_file: str = "version.json"):
        self.version_file = version_file
        self._version = self._load_version()
    
    def _load_version(self) -> SemanticVersion:
        try:
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                return SemanticVersion.parse(data['version'])
        except FileNotFoundError:
            return SemanticVersion(0, 1, 0)
    
    def save_version(self):
        with open(self.version_file, 'w') as f:
            json.dump({
                'version': str(self._version),
                'timestamp': datetime.utcnow().isoformat()
            }, f, indent=2)
    
    @property
    def current_version(self) -> SemanticVersion:
        return self._version
    
    def bump(self, bump_type: VersionBumpType, prerelease_id: Optional[str] = None) -> SemanticVersion:
        self._version = self._version.bump(bump_type, prerelease_id)
        self.save_version()
        return self._version


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Version manager')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch', 'hotfix'])
    parser.add_argument('--prerelease', help='Prerelease identifier')
    parser.add_argument('--get', action='store_true', help='Get current version')
    args = parser.parse_args()
    
    manager = VersionManager()
    
    if args.get:
        print(manager.current_version)
    elif args.bump:
        bump_type = VersionBumpType(args.bump)
        new_version = manager.bump(bump_type, args.prerelease)
        print(f"Bumped to: {new_version}")
