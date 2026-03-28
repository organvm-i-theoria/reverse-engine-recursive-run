#!/usr/bin/env python3
"""
Organization Profiling Orchestrator

Coordinates all profiling activities to create a comprehensive
machine-readable fingerprint of the organization.

Runs:
1. Technology stack extraction
2. Architecture pattern analysis
3. Baseline metrics collection
4. Challenge identification
"""

import os
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def run_script(script_name: str, args: list) -> Dict[str, Any]:
    """Run a profiling script and return its output."""
    script_path = Path(__file__).parent / script_name
    cmd = ['python3', str(script_path)] + args

    print(f"[PROFILE-ORG] Running: {script_name}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return {'success': True, 'output': result.stdout}
    except subprocess.CalledProcessError as e:
        print(f"[PROFILE-ORG] ERROR running {script_name}: {e.stderr}")
        return {'success': False, 'error': str(e)}


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[PROFILE-ORG] WARNING: Could not load {file_path}: {e}")
        return {}


def aggregate_risk_data(artifacts_dir: str) -> Dict[str, Any]:
    """Aggregate existing risk analysis data."""
    risk_data = {
        'hotspots': [],
        'ownership_risks': [],
        'drift_issues': [],
        'security_findings': []
    }

    # Load existing artifacts if available
    hotspots_file = os.path.join(artifacts_dir, 'hotspots.json')
    if os.path.exists(hotspots_file):
        risk_data['hotspots'] = load_json(hotspots_file).get('hotspots', [])

    ownership_file = os.path.join(artifacts_dir, 'ownership.json')
    if os.path.exists(ownership_file):
        ownership_data = load_json(ownership_file)
        risk_data['ownership_risks'] = ownership_data.get('risks', [])

    drift_file = os.path.join(artifacts_dir, 'drift_report.json')
    if os.path.exists(drift_file):
        drift_data = load_json(drift_file)
        risk_data['drift_issues'] = drift_data.get('summary', {})

    security_file = os.path.join(artifacts_dir, 'security_findings.json')
    if os.path.exists(security_file):
        risk_data['security_findings'] = load_json(security_file)

    return risk_data


def identify_challenges(risk_data: Dict[str, Any], tech_stack: Dict[str, Any]) -> Dict[str, Any]:
    """Identify organizational challenges based on risk and tech stack."""
    challenges = {
        'high_priority': [],
        'medium_priority': [],
        'low_priority': [],
        'research_areas': []
    }

    # Analyze hotspots
    if risk_data.get('hotspots'):
        high_risk_files = [h for h in risk_data['hotspots'] if h.get('risk_score', 0) >= 0.7]
        if len(high_risk_files) > 10:
            challenges['high_priority'].append({
                'category': 'code_quality',
                'issue': 'high_hotspot_count',
                'description': f'{len(high_risk_files)} files with high risk scores',
                'research_focus': ['refactoring', 'testing', 'complexity reduction']
            })

    # Analyze ownership
    if risk_data.get('ownership_risks'):
        single_owner = [r for r in risk_data['ownership_risks'] if 'SINGLE_CONTRIBUTOR' in r.get('flags', [])]
        if len(single_owner) > 5:
            challenges['high_priority'].append({
                'category': 'knowledge_concentration',
                'issue': 'bus_factor_risk',
                'description': f'{len(single_owner)} areas with single contributor',
                'research_focus': ['documentation', 'knowledge_sharing', 'pair_programming']
            })

    # Analyze security
    if risk_data.get('security_findings'):
        critical_vulns = [f for f in risk_data['security_findings'] if f.get('severity') == 'HIGH']
        if len(critical_vulns) > 0:
            challenges['high_priority'].append({
                'category': 'security',
                'issue': 'critical_vulnerabilities',
                'description': f'{len(critical_vulns)} critical security findings',
                'research_focus': ['security', 'dependency_management', 'sast', 'dast']
            })

    # Analyze tech stack gaps
    if not tech_stack.get('infrastructure', {}).get('ci_cd'):
        challenges['medium_priority'].append({
            'category': 'devops',
            'issue': 'no_ci_cd',
            'description': 'No CI/CD pipeline detected',
            'research_focus': ['ci_cd', 'automation', 'testing_automation']
        })

    # Generate research areas
    all_focuses = set()
    for priority_list in [challenges['high_priority'], challenges['medium_priority']]:
        for challenge in priority_list:
            all_focuses.update(challenge.get('research_focus', []))

    challenges['research_areas'] = sorted(list(all_focuses))

    return challenges


def create_org_profile(codebase_path: str, artifacts_dir: str, output_path: str):
    """Create comprehensive organization profile."""
    print("[PROFILE-ORG] Starting organization profiling...")

    # Ensure artifacts directory exists
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. Extract technology stack
    tech_stack_file = os.path.join(artifacts_dir, 'tech_signature.json')
    run_script('extract_tech_stack.py', [
        '--path', codebase_path,
        '--out', tech_stack_file
    ])

    tech_stack = load_json(tech_stack_file)

    # 2. Load/aggregate existing risk data
    print("[PROFILE-ORG] Aggregating existing risk data...")
    risk_data = aggregate_risk_data(artifacts_dir)

    # 3. Identify challenges and research areas
    print("[PROFILE-ORG] Identifying challenges and research areas...")
    challenges = identify_challenges(risk_data, tech_stack)

    # 4. Compile complete profile
    profile = {
        'profile_version': '1.0',
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'organization': {
            'name': os.path.basename(os.path.abspath(codebase_path)),
            'codebase_path': codebase_path,
        },
        'technology': tech_stack,
        'metrics': {
            'total_files': tech_stack.get('metadata', {}).get('total_files', 0),
            'total_lines': tech_stack.get('metadata', {}).get('total_lines', 0),
            'primary_languages': list(tech_stack.get('languages', {}).keys())[:5],
            'risk_summary': {
                'hotspot_count': len(risk_data.get('hotspots', [])),
                'ownership_risks': len(risk_data.get('ownership_risks', [])),
                'security_findings': len(risk_data.get('security_findings', []))
            }
        },
        'challenges': challenges,
        'fingerprint': tech_stack.get('fingerprint', 'unknown')
    }

    # Write profile
    with open(output_path, 'w') as f:
        json.dump(profile, f, indent=2)

    print(f"[PROFILE-ORG] Organization profile created: {output_path}")
    print(f"[PROFILE-ORG] Fingerprint: {profile['fingerprint']}")
    print(f"[PROFILE-ORG] Primary languages: {', '.join(profile['metrics']['primary_languages'])}")
    print(f"[PROFILE-ORG] High priority challenges: {len(challenges['high_priority'])}")
    print(f"[PROFILE-ORG] Research areas: {len(challenges['research_areas'])}")

    return profile


def main():
    parser = argparse.ArgumentParser(description='Create organization profile')
    parser.add_argument('--path', default='.', help='Path to codebase (default: current directory)')
    parser.add_argument('--artifacts', default='./artifacts', help='Artifacts directory')
    parser.add_argument('--out', required=True, help='Output JSON file path')

    args = parser.parse_args()

    create_org_profile(args.path, args.artifacts, args.out)


if __name__ == '__main__':
    main()
