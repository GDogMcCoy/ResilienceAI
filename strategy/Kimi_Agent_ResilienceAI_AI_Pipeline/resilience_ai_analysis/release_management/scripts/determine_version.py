#!/usr/bin/env python3
"""
Determine version bump based on branch and commit messages
"""

import argparse
import re
import subprocess


class ConventionalCommit:
    """Parse conventional commit messages"""
    
    TYPES = {
        'feat': 'minor',
        'fix': 'patch',
        'docs': None,
        'style': None,
        'refactor': None,
        'perf': 'patch',
        'test': None,
        'chore': None,
        'build': None,
        'ci': None,
        'revert': 'patch',
        'BREAKING CHANGE': 'major',
        'BREAKING-CHANGE': 'major'
    }
    
    @classmethod
    def parse(cls, message: str) -> dict:
        pattern = r'^(\w+)(?:\(([^)]+)\))?!?: (.+)$'
        match = re.match(pattern, message)
        
        if not match:
            return {'type': None, 'scope': None, 'message': message}
        
        commit_type = match.group(1)
        scope = match.group(2)
        msg = match.group(3)
        
        is_breaking = '!' in message[:message.find(':')] or \
                      'BREAKING CHANGE' in message or \
                      'BREAKING-CHANGE' in message
        
        return {
            'type': commit_type,
            'scope': scope,
            'message': msg,
            'is_breaking': is_breaking,
            'bump': 'major' if is_breaking else cls.TYPES.get(commit_type)
        }


def get_commits_since_last_tag() -> list:
    try:
        last_tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        commits = subprocess.check_output(
            ['git', 'log', f'{last_tag}..HEAD', '--pretty=format:%s'],
            stderr=subprocess.DEVNULL
        ).decode().strip().split('\n')
        
        return [c for c in commits if c]
    except subprocess.CalledProcessError:
        return []


def determine_bump_type(branch: str, commits: list, manual_type: str = None) -> str:
    if manual_type:
        return manual_type
    
    if branch.startswith('hotfix/'):
        return 'hotfix'
    
    if branch.startswith('release/'):
        match = re.search(r'release/(\d+)\.(\d+)', branch)
        if match:
            return 'minor' if int(match.group(2)) > 0 else 'major'
    
    bumps = []
    for commit in commits:
        parsed = ConventionalCommit.parse(commit)
        if parsed['bump']:
            bumps.append(parsed['bump'])
    
    if 'major' in bumps:
        return 'major'
    elif 'minor' in bumps:
        return 'minor'
    elif 'patch' in bumps:
        return 'patch'
    
    if branch == 'main':
        return 'patch'
    
    return None


def main():
    parser = argparse.ArgumentParser(description='Determine version bump')
    parser.add_argument('--branch', required=True, help='Current branch')
    parser.add_argument('--commit-msg', help='Commit message')
    parser.add_argument('--manual-type', help='Manual version bump type')
    args = parser.parse_args()
    
    commits = get_commits_since_last_tag()
    if args.commit_msg:
        commits.insert(0, args.commit_msg)
    
    bump_type = determine_bump_type(args.branch, commits, args.manual_type)
    
    print(f"::set-output name=release_type::{bump_type}")
    print(f"release_type={bump_type}")


if __name__ == '__main__':
    main()
