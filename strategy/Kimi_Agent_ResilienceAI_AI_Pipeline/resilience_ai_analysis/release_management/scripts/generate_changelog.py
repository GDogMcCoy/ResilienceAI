#!/usr/bin/env python3
"""
Generate changelog from git commits using conventional commits
"""

import argparse
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChangelogEntry:
    type: str
    scope: Optional[str]
    message: str
    commit_hash: str
    is_breaking: bool
    pull_request: Optional[str]


class ChangelogGenerator:
    CATEGORIES = {
        'feat': 'Features',
        'fix': 'Bug Fixes',
        'docs': 'Documentation',
        'style': 'Styles',
        'refactor': 'Code Refactoring',
        'perf': 'Performance Improvements',
        'test': 'Tests',
        'build': 'Build System',
        'ci': 'CI/CD',
        'chore': 'Chores',
        'revert': 'Reverts'
    }
    
    def __init__(self, version: str):
        self.version = version
        self.entries: List[ChangelogEntry] = []
    
    def get_last_tag(self) -> Optional[str]:
        try:
            result = subprocess.check_output(
                ['git', 'describe', '--tags', '--abbrev=0'],
                stderr=subprocess.DEVNULL
            )
            return result.decode().strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_commits(self, since_tag: Optional[str] = None) -> List[Dict]:
        format_str = '%H|%s'
        range_spec = f'{since_tag}..HEAD' if since_tag else 'HEAD'
        
        try:
            result = subprocess.check_output(
                ['git', 'log', range_spec, f'--pretty=format:{format_str}'],
                stderr=subprocess.DEVNULL
            )
            
            commits = []
            for line in result.decode().strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    commits.append({'hash': parts[0][:7], 'subject': parts[1]})
            return commits
        except subprocess.CalledProcessError:
            return []
    
    def parse_conventional_commit(self, commit: Dict) -> Optional[ChangelogEntry]:
        subject = commit['subject']
        pattern = r'^(\w+)(?:\(([^)]+)\))?(!)?: (.+)$'
        match = re.match(pattern, subject)
        
        if not match:
            return None
        
        commit_type = match.group(1)
        scope = match.group(2)
        breaking_indicator = match.group(3)
        message = match.group(4)
        is_breaking = bool(breaking_indicator)
        
        pr_match = re.search(r'\(#(\d+)\)', subject)
        pull_request = pr_match.group(1) if pr_match else None
        
        return ChangelogEntry(
            type=commit_type,
            scope=scope,
            message=message,
            commit_hash=commit['hash'],
            is_breaking=is_breaking,
            pull_request=pull_request
        )
    
    def generate(self, since_tag: Optional[str] = None) -> str:
        commits = self.get_commits(since_tag)
        
        self.entries = []
        for commit in commits:
            entry = self.parse_conventional_commit(commit)
            if entry:
                self.entries.append(entry)
        
        categorized = self._categorize_entries()
        return self._generate_markdown(categorized)
    
    def _categorize_entries(self) -> Dict[str, List[ChangelogEntry]]:
        categorized: Dict[str, List[ChangelogEntry]] = {}
        for entry in self.entries:
            category = self.CATEGORIES.get(entry.type, 'Other')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(entry)
        return categorized
    
    def _generate_markdown(self, categorized: Dict[str, List[ChangelogEntry]]) -> str:
        lines = []
        date_str = datetime.now().strftime('%Y-%m-%d')
        lines.append(f"## [{self.version}] - {date_str}")
        lines.append("")
        
        priority = ['Features', 'Bug Fixes', 'Performance Improvements', 'Documentation']
        
        for category in priority:
            if category in categorized and categorized[category]:
                lines.append(f"### {category}")
                lines.append("")
                for entry in categorized[category]:
                    scope = f"**{entry.scope}**: " if entry.scope else ""
                    pr_ref = f" (#{entry.pull_request})" if entry.pull_request else ""
                    lines.append(f"- {scope}{entry.message}{pr_ref}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def update_changelog_file(self, output_file: str = 'CHANGELOG.md'):
        last_tag = self.get_last_tag()
        new_entry = self.generate(last_tag)
        
        try:
            with open(output_file, 'r') as f:
                existing = f.read()
        except FileNotFoundError:
            existing = self._generate_header()
        
        header_end = existing.find('## [')
        if header_end == -1:
            header_end = len(existing)
        
        updated = existing[:header_end] + new_entry + '\n' + existing[header_end:]
        
        with open(output_file, 'w') as f:
            f.write(updated)
        
        return new_entry
    
    def _generate_header(self) -> str:
        return """# Changelog

All notable changes to ResilienceAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""


def main():
    parser = argparse.ArgumentParser(description='Generate changelog')
    parser.add_argument('--version', required=True, help='Version for changelog entry')
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--update', action='store_true', help='Update CHANGELOG.md')
    args = parser.parse_args()
    
    generator = ChangelogGenerator(args.version)
    
    if args.update:
        content = generator.update_changelog_file()
    else:
        last_tag = generator.get_last_tag()
        content = generator.generate(last_tag)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(content)
        print(f"Changelog written to {args.output}")
    else:
        print(content)


if __name__ == '__main__':
    main()
