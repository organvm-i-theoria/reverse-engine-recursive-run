#!/usr/bin/env python3
"""
Extract Technology Stack Fingerprint

Analyzes the codebase to identify:
- Programming languages (by file extensions and content)
- Frameworks (from package manifests)
- Tools and utilities (from config files)
- Infrastructure patterns (Docker, K8s, etc.)
- Dependency versions
"""

import os
import json
import re
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any
import hashlib


# Language detection by file extension
LANGUAGE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.jsx': 'JavaScript',
    '.go': 'Go',
    '.java': 'Java',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.c': 'C',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.r': 'R',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.sql': 'SQL',
}

# Package manifest files by ecosystem
PACKAGE_MANIFESTS = {
    'package.json': 'Node.js',
    'requirements.txt': 'Python',
    'Pipfile': 'Python',
    'pyproject.toml': 'Python',
    'setup.py': 'Python',
    'go.mod': 'Go',
    'go.sum': 'Go',
    'Cargo.toml': 'Rust',
    'pom.xml': 'Java',
    'build.gradle': 'Java',
    'Gemfile': 'Ruby',
    'composer.json': 'PHP',
}

# Infrastructure and tool patterns
INFRASTRUCTURE_PATTERNS = {
    'Dockerfile': 'Docker',
    'docker-compose.yml': 'Docker Compose',
    'docker-compose.yaml': 'Docker Compose',
    'kubernetes.yml': 'Kubernetes',
    'kubernetes.yaml': 'Kubernetes',
    '*.k8s.yml': 'Kubernetes',
    '.github/workflows': 'GitHub Actions',
    '.gitlab-ci.yml': 'GitLab CI',
    'Jenkinsfile': 'Jenkins',
    '.circleci': 'CircleCI',
    'terraform': 'Terraform',
    'ansible': 'Ansible',
    'Makefile': 'Make',
}


def scan_directory(root_path: str, exclude_patterns: List[str] = None) -> Dict[str, Any]:
    """Scan directory tree for files and patterns."""
    if exclude_patterns is None:
        exclude_patterns = [
            'node_modules', 'venv', '.venv', '__pycache__',
            '.git', 'dist', 'build', 'target', 'vendor'
        ]

    file_stats = {
        'total_files': 0,
        'total_lines': 0,
        'files_by_extension': Counter(),
        'languages': Counter(),
    }

    found_files = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_patterns and not d.startswith('.')]

        for filename in filenames:
            if filename.startswith('.'):
                continue

            file_path = os.path.join(dirpath, filename)
            file_stats['total_files'] += 1

            # Get extension
            ext = Path(filename).suffix.lower()
            if ext:
                file_stats['files_by_extension'][ext] += 1

                # Map to language
                if ext in LANGUAGE_EXTENSIONS:
                    lang = LANGUAGE_EXTENSIONS[ext]
                    file_stats['languages'][lang] += 1

            # Count lines
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    file_stats['total_lines'] += lines
            except:
                pass

            found_files.append(file_path)

    return file_stats, found_files


def detect_frameworks(root_path: str, files: List[str]) -> Dict[str, List[str]]:
    """Detect frameworks from package manifests."""
    frameworks = defaultdict(list)

    for file_path in files:
        filename = os.path.basename(file_path)

        # Node.js - package.json
        if filename == 'package.json':
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    deps = {}
                    deps.update(data.get('dependencies', {}))
                    deps.update(data.get('devDependencies', {}))

                    # Detect frameworks
                    if 'react' in deps:
                        frameworks['JavaScript'].append(f"React@{deps['react']}")
                    if 'vue' in deps:
                        frameworks['JavaScript'].append(f"Vue@{deps['vue']}")
                    if 'angular' in deps or '@angular/core' in deps:
                        frameworks['JavaScript'].append('Angular')
                    if 'express' in deps:
                        frameworks['JavaScript'].append(f"Express@{deps['express']}")
                    if 'next' in deps:
                        frameworks['JavaScript'].append(f"Next.js@{deps['next']}")
            except:
                pass

        # Python - requirements.txt, pyproject.toml
        elif filename == 'requirements.txt':
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse package==version
                            match = re.match(r'([a-zA-Z0-9\-_]+)([=<>]=?.*)?', line)
                            if match:
                                pkg = match.group(1).lower()
                                if pkg in ['django', 'flask', 'fastapi', 'tornado']:
                                    frameworks['Python'].append(line)
            except:
                pass

        elif filename == 'pyproject.toml':
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'django' in content.lower():
                        frameworks['Python'].append('Django')
                    if 'flask' in content.lower():
                        frameworks['Python'].append('Flask')
                    if 'fastapi' in content.lower():
                        frameworks['Python'].append('FastAPI')
            except:
                pass

        # Go - go.mod
        elif filename == 'go.mod':
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Extract require statements
                    for match in re.finditer(r'require\s+([^\s]+)\s+v([^\s]+)', content):
                        pkg, version = match.groups()
                        if 'gin-gonic/gin' in pkg:
                            frameworks['Go'].append(f"Gin@v{version}")
                        elif 'gorilla/mux' in pkg:
                            frameworks['Go'].append(f"Gorilla Mux@v{version}")
            except:
                pass

    return dict(frameworks)


def detect_tools(root_path: str, files: List[str]) -> Set[str]:
    """Detect development tools and configurations."""
    tools = set()

    for file_path in files:
        filename = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, root_path)

        # CI/CD
        if '.github/workflows' in rel_path:
            tools.add('GitHub Actions')
        if filename == '.gitlab-ci.yml':
            tools.add('GitLab CI')
        if filename == 'Jenkinsfile':
            tools.add('Jenkins')
        if '.circleci' in rel_path:
            tools.add('CircleCI')

        # Containers
        if filename.startswith('Dockerfile'):
            tools.add('Docker')
        if 'docker-compose' in filename:
            tools.add('Docker Compose')

        # IaC
        if filename.endswith('.tf'):
            tools.add('Terraform')
        if 'kubernetes' in rel_path or filename.endswith('.k8s.yml'):
            tools.add('Kubernetes')

        # Build tools
        if filename == 'Makefile':
            tools.add('Make')
        if filename == 'CMakeLists.txt':
            tools.add('CMake')

        # Linters and formatters
        if filename in ['.eslintrc', '.eslintrc.json', '.eslintrc.js']:
            tools.add('ESLint')
        if filename in ['.pylintrc', 'pylint.cfg']:
            tools.add('Pylint')
        if filename in ['.prettierrc', 'prettier.config.js']:
            tools.add('Prettier')
        if filename == '.editorconfig':
            tools.add('EditorConfig')

        # Testing
        if filename in ['jest.config.js', 'jest.config.json']:
            tools.add('Jest')
        if filename in ['pytest.ini', '.pytest.ini']:
            tools.add('Pytest')

        # Code quality
        if filename in ['.codeclimate.yml', '.codeclimate.json']:
            tools.add('Code Climate')
        if filename == 'sonar-project.properties':
            tools.add('SonarQube')

    return tools


def generate_fingerprint(tech_stack: Dict[str, Any]) -> str:
    """Generate a unique fingerprint hash for the tech stack."""
    # Create a canonical representation
    canonical = json.dumps(tech_stack, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def extract_tech_stack(root_path: str, output_path: str):
    """Main function to extract technology stack."""
    print(f"[TECH-STACK] Scanning directory: {root_path}")

    # Scan directory
    file_stats, files = scan_directory(root_path)

    print(f"[TECH-STACK] Found {file_stats['total_files']} files, {file_stats['total_lines']} total lines")

    # Detect frameworks
    frameworks = detect_frameworks(root_path, files)

    # Detect tools
    tools = detect_tools(root_path, files)

    # Compile tech stack
    tech_stack = {
        'metadata': {
            'scanned_path': root_path,
            'total_files': file_stats['total_files'],
            'total_lines': file_stats['total_lines'],
            'scan_timestamp': None,  # TODO: Add timestamp
        },
        'languages': {
            lang: {
                'file_count': count,
                'percentage': round(count / file_stats['total_files'] * 100, 2) if file_stats['total_files'] > 0 else 0
            }
            for lang, count in file_stats['languages'].most_common()
        },
        'frameworks': frameworks,
        'tools': sorted(list(tools)),
        'package_ecosystems': list(set([PACKAGE_MANIFESTS[os.path.basename(f)]
                                         for f in files
                                         if os.path.basename(f) in PACKAGE_MANIFESTS])),
        'infrastructure': {
            'containerization': 'Docker' in tools or 'Docker Compose' in tools,
            'orchestration': 'Kubernetes' in tools,
            'ci_cd': any(ci in tools for ci in ['GitHub Actions', 'GitLab CI', 'Jenkins', 'CircleCI']),
            'iac': 'Terraform' in tools or 'Ansible' in tools,
        }
    }

    # Generate fingerprint
    tech_stack['fingerprint'] = generate_fingerprint(tech_stack)

    # Write output
    with open(output_path, 'w') as f:
        json.dump(tech_stack, f, indent=2)

    print(f"[TECH-STACK] Technology stack extracted to: {output_path}")
    print(f"[TECH-STACK] Fingerprint: {tech_stack['fingerprint']}")
    print(f"[TECH-STACK] Primary languages: {', '.join(list(tech_stack['languages'].keys())[:5])}")
    print(f"[TECH-STACK] Tools detected: {len(tools)}")

    return tech_stack


def main():
    parser = argparse.ArgumentParser(description='Extract technology stack fingerprint')
    parser.add_argument('--path', default='.', help='Path to analyze (default: current directory)')
    parser.add_argument('--out', required=True, help='Output JSON file path')

    args = parser.parse_args()

    extract_tech_stack(args.path, args.out)


if __name__ == '__main__':
    main()
