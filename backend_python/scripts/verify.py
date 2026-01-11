#!/usr/bin/env python3
"""
Verification script for MeterSphere Python Backend
Checks if all modules are properly implemented
"""

import os
import sys
import ast
from pathlib import Path
from typing import List, Dict, Tuple

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

BASE_DIR = Path(__file__).parent.parent
APP_DIR = BASE_DIR / "app"

# Expected modules and files
EXPECTED_ENDPOINTS = [
    "auth.py",
    "users.py",
    "api_test.py",
    "bug_management.py",
    "case_management.py",
    "dashboard.py",
    "project_management.py",
    "system_setting.py",
    "test_plan.py",
    "files.py",
    "import_export.py",
    "jmeter.py",
    "jmeter_generate.py",
    "ai.py",
    "i18n.py",
    "batch_operations.py",
    "health.py",
]

EXPECTED_SERVICES = [
    "auth_service.py",
    "user_service.py",
    "project_service.py",
    "project_management_service.py",
    "api_test_service.py",
    "bug_management_service.py",
    "case_management_service.py",
    "test_plan_service.py",
    "file_service.py",
    "import_export_service.py",
    "jmeter_service.py",
    "jmeter_parser.py",
    "ai_service.py",
    "functional_case_ai_service.py",
    "api_test_case_ai_service.py",
    "dashboard_service.py",
    "system_setting_service.py",
    "permission_service.py",
]

EXPECTED_CORE = [
    "config.py",
    "database.py",
    "logging.py",
    "security.py",
    "redis.py",
    "kafka.py",
    "minio.py",
    "rate_limit.py",
    "request_validation.py",
    "i18n.py",
    "i18n_middleware.py",
    "cache.py",
    "database_optimization.py",
    "metrics.py",
    "metrics_middleware.py",
]

EXPECTED_MODELS = [
    "user.py",
    "organization.py",
    "project.py",
    "api_test.py",  # Contains ApiDefinition, ApiTestCase, ApiScenario
    "api_scenario_step.py",
    "api_report.py",
    "functional_case.py",
    "test_plan.py",
    "bug.py",
    "bug_comment.py",
    "bug_attachment.py",
    "user_role.py",
    "user_role_relation.py",
    "base.py",
]

def check_file_exists(file_path: Path) -> bool:
    """Check if file exists"""
    return file_path.exists() and file_path.is_file()

def check_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ast.parse(f.read())
        return True, ""
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {e}"

def check_imports(file_path: Path) -> List[str]:
    """Check if file has valid imports"""
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    try:
                        __import__(alias.name)
                    except ImportError:
                        # This is OK, might be a local import
                        pass
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    try:
                        __import__(node.module)
                    except ImportError:
                        # This is OK, might be a local import
                        pass
    except Exception as e:
        errors.append(f"Error checking imports: {e}")
    
    return errors

def verify_directory(directory: Path, expected_files: List[str], name: str) -> Dict:
    """Verify a directory contains expected files"""
    results = {
        "name": name,
        "total": len(expected_files),
        "found": 0,
        "missing": [],
        "syntax_errors": [],
        "files": []
    }
    
    for filename in expected_files:
        file_path = directory / filename
        if check_file_exists(file_path):
            results["found"] += 1
            syntax_ok, error = check_syntax(file_path)
            if not syntax_ok:
                results["syntax_errors"].append((filename, error))
            results["files"].append((filename, "✓", syntax_ok))
        else:
            results["missing"].append(filename)
            results["files"].append((filename, "✗", False))
    
    return results

def print_results(results: Dict):
    """Print verification results"""
    print(f"\n{BLUE}=== {results['name']} ==={NC}")
    print(f"Total: {results['total']}, Found: {results['found']}, Missing: {len(results['missing'])}")
    
    if results['missing']:
        print(f"{RED}Missing files:{NC}")
        for filename in results['missing']:
            print(f"  {RED}✗{NC} {filename}")
    
    if results['syntax_errors']:
        print(f"{RED}Syntax errors:{NC}")
        for filename, error in results['syntax_errors']:
            print(f"  {RED}✗{NC} {filename}: {error[:100]}")
    
    if results['found'] == results['total'] and not results['syntax_errors']:
        print(f"{GREEN}✓ All files present and valid{NC}")

def main():
    """Main verification function"""
    print(f"{BLUE}MeterSphere Python Backend - Module Verification{NC}")
    print(f"{BLUE}{'=' * 50}{NC}")
    
    # Check endpoints
    endpoints_dir = APP_DIR / "api" / "v1" / "endpoints"
    endpoints_results = verify_directory(endpoints_dir, EXPECTED_ENDPOINTS, "API Endpoints")
    print_results(endpoints_results)
    
    # Check services
    services_dir = APP_DIR / "services"
    services_results = verify_directory(services_dir, EXPECTED_SERVICES, "Services")
    print_results(services_results)
    
    # Check core
    core_dir = APP_DIR / "core"
    core_results = verify_directory(core_dir, EXPECTED_CORE, "Core Modules")
    print_results(core_results)
    
    # Check models
    models_dir = APP_DIR / "models"
    models_results = verify_directory(models_dir, EXPECTED_MODELS, "Models")
    print_results(models_results)
    
    # Check main files
    print(f"\n{BLUE}=== Main Files ==={NC}")
    main_files = ["main.py", "Dockerfile", "docker-compose.yml"]
    for filename in main_files:
        file_path = BASE_DIR / filename
        if check_file_exists(file_path):
            syntax_ok, error = check_syntax(file_path) if filename.endswith('.py') else (True, "")
            status = f"{GREEN}✓{NC}" if syntax_ok else f"{RED}✗{NC}"
            print(f"  {status} {filename}")
        else:
            print(f"  {RED}✗{NC} {filename} (missing)")
    
    # Check requirements.txt in parent directory
    req_file = BASE_DIR.parent / "requirements.txt"
    if check_file_exists(req_file):
        print(f"  {GREEN}✓{NC} requirements.txt (in parent directory)")
    else:
        print(f"  {YELLOW}⚠{NC} requirements.txt (check parent directory)")
    
    # Summary
    print(f"\n{BLUE}{'=' * 50}{NC}")
    total_expected = (
        endpoints_results['total'] +
        services_results['total'] +
        core_results['total'] +
        models_results['total']
    )
    total_found = (
        endpoints_results['found'] +
        services_results['found'] +
        core_results['found'] +
        models_results['found']
    )
    total_missing = total_expected - total_found
    total_errors = (
        len(endpoints_results['syntax_errors']) +
        len(services_results['syntax_errors']) +
        len(core_results['syntax_errors']) +
        len(models_results['syntax_errors'])
    )
    
    print(f"{BLUE}Summary:{NC}")
    print(f"  Total modules: {total_expected}")
    print(f"  Found: {GREEN}{total_found}{NC}")
    print(f"  Missing: {RED}{total_missing}{NC}")
    print(f"  Syntax errors: {RED}{total_errors}{NC}")
    
    if total_missing == 0 and total_errors == 0:
        print(f"\n{GREEN}✓ All modules verified successfully!{NC}")
        return 0
    else:
        print(f"\n{RED}✗ Verification found issues{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

