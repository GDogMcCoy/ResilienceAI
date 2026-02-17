#!/usr/bin/env python3
"""
Hotfix management for ResilienceAI
"""

import argparse
import re
import subprocess
import json
from datetime import datetime


class HotfixManager:
    def __init__(self):
        self.current_version = self._get_current_version()
    
    def _get_current_version(self) -> str:
        try:
            with open('version.json', 'r') as f:
                data = json.load(f)
                return data['version']
        except FileNotFoundError:
            return "0.0.0"
    
    def create_hotfix_branch(self, issue_id: str, description: str) -> str:
        subprocess.run(['git', 'checkout', 'main'], check=True)
        subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
        
        branch_name = f"hotfix/{issue_id}-{self._sanitize_branch_name(description)}"
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
        
        print(f"Created hotfix branch: {branch_name}")
        print(f"Base version: {self.current_version}")
        return branch_name
    
    def _sanitize_branch_name(self, description: str) -> str:
        sanitized = re.sub(r'[^\w\s-]', '', description.lower())
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        return sanitized[:50]
    
    def prepare_release(self) -> str:
        version_parts = self.current_version.split('.')
        version_parts[2] = str(int(version_parts[2]) + 1)
        new_version = '.'.join(version_parts)
        
        with open('version.json', 'r') as f:
            data = json.load(f)
        
        data['version'] = new_version
        data['release'] = {
            'type': 'hotfix',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        with open('version.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        self._update_changelog(new_version)
        
        subprocess.run(['git', 'add', 'version.json', 'CHANGELOG.md'], check=True)
        subprocess.run(
            ['git', 'commit', '-m', f"chore(release): prepare hotfix v{new_version}"],
            check=True
        )
        
        print(f"Prepared hotfix release v{new_version}")
        return new_version
    
    def _update_changelog(self, version: str):
        entry = f"""## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### Security
- Hotfix release

### Fixed
- Critical bug fix (see linked issues)

"""
        try:
            with open('CHANGELOG.md', 'r') as f:
                content = f.read()
            header_end = content.find('## [')
            if header_end == -1:
                header_end = len(content)
            updated = content[:header_end] + entry + content[header_end:]
            with open('CHANGELOG.md', 'w') as f:
                f.write(updated)
        except FileNotFoundError:
            pass
    
    def merge_to_main(self, version: str):
        subprocess.run(['git', 'checkout', 'main'], check=True)
        branch = subprocess.check_output(
            ['git', 'branch', '--show-current']
        ).decode().strip()
        subprocess.run(['git', 'merge', '--no-ff', branch, '-m', f"Merge hotfix v{version}"], check=True)
        subprocess.run(
            ['git', 'tag', '-a', f'v{version}', '-m', f'Hotfix v{version}'],
            check=True
        )
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)
        print(f"Merged hotfix v{version} to main")
    
    def merge_to_develop(self, version: str):
        subprocess.run(['git', 'checkout', 'develop'], check=True)
        subprocess.run(['git', 'pull', 'origin', 'develop'], check=True)
        subprocess.run(
            ['git', 'merge', '--no-ff', 'main', '-m', f"Merge hotfix v{version} to develop"],
            check=True
        )
        subprocess.run(['git', 'push', 'origin', 'develop'], check=True)
        print(f"Merged hotfix v{version} to develop")


def main():
    parser = argparse.ArgumentParser(description='Manage hotfixes')
    subparsers = parser.add_subparsers(dest='command')
    
    create_parser = subparsers.add_parser('create', help='Create hotfix branch')
    create_parser.add_argument('--issue', required=True, help='Issue ID')
    create_parser.add_argument('--description', required=True, help='Hotfix description')
    
    prepare_parser = subparsers.add_parser('prepare', help='Prepare hotfix release')
    
    merge_parser = subparsers.add_parser('merge', help='Merge hotfix')
    merge_parser.add_argument('--version', required=True, help='Hotfix version')
    merge_parser.add_argument('--target', choices=['main', 'develop'], default='main')
    
    args = parser.parse_args()
    
    manager = HotfixManager()
    
    if args.command == 'create':
        manager.create_hotfix_branch(args.issue, args.description)
    elif args.command == 'prepare':
        manager.prepare_release()
    elif args.command == 'merge':
        if args.target == 'main':
            manager.merge_to_main(args.version)
        else:
            manager.merge_to_develop(args.version)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
