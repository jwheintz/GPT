"""
Comprehensive Deployment Validation Script
Checks all aspects of the OBS Plugin Manager v2.0 before deployment
"""

import sys
from pathlib import Path
import json

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check(status):
    """Return colored checkmark or X."""
    return f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"

def section(title):
    """Print section header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{title:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

class DeploymentValidator:
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    def test(self, name, condition, critical=True):
        """Record a test result."""
        self.results.append((name, condition, critical))
        if not condition:
            if critical:
                self.errors.append(name)
            else:
                self.warnings.append(name)
        status = check(condition)
        level = "CRITICAL" if critical and not condition else "WARNING" if not condition else "PASSED"
        color = RED if critical and not condition else YELLOW if not condition else GREEN
        print(f"{status} {name:.<60} {color}{level}{RESET}")
        
    def validate_file_structure(self):
        """Validate project file structure."""
        section("FILE STRUCTURE VALIDATION")
        
        # Core Python modules
        core_modules = [
            "__init__.py",
            "database.py",
            "obs_manager.py",
            "plugin_scanner.py",
            "plugin_repository.py",
            "plugin_installer.py",
            "local_repository.py",
            "discovery.py",
            "obs_resources.py",
            "gui.py"
        ]
        
        for module in core_modules:
            path = Path("obs_plugin_manager") / module
            self.test(f"Core module: {module}", path.exists())
        
        # Documentation files
        docs = [
            "README.md",
            "GETTING_STARTED.md",
            "QUICK_REFERENCE.md",
            "TROUBLESHOOTING.md",
            "INSTALLATION_CHECKLIST.md",
            "DISCOVERY_GUIDE.md",
            "OBS_WEBSITE_INTEGRATION.md",
            "WHATS_NEW_V2.md",
            "FILE_INDEX.md",
            "START_HERE.md",
            "ARCHITECTURE.md",
            "CONTRIBUTING.md",
            "PROJECT_SUMMARY.md",
            "DEVELOPERS.md",
            "PERFORMANCE.md",
            "CODE_REVIEW.md",
            "DEPLOYMENT_CHECKLIST.md",
            "VERSION_2_UPDATES.md",
            "FINAL_SUMMARY_V2.md",
            "CHANGELOG.md"
        ]
        
        for doc in docs:
            self.test(f"Documentation: {doc}", Path(doc).exists())
        
        # Launch scripts
        scripts = ["launch.bat", "install.bat", "quick_setup.bat", "obs_plugin_manager.py"]
        for script in scripts:
            self.test(f"Launch script: {script}", Path(script).exists())
        
        # Config files
        configs = ["requirements.txt", "setup.py", "LICENSE", ".gitignore"]
        for config in configs:
            self.test(f"Config file: {config}", Path(config).exists())
        
        # Test files
        tests = ["test_basic.py", "test_v2_features.py"]
        for test in tests:
            self.test(f"Test file: {test}", Path(test).exists(), critical=False)
    
    def validate_version(self):
        """Validate version information."""
        section("VERSION VALIDATION")
        
        init_file = Path("obs_plugin_manager/__init__.py")
        if init_file.exists():
            content = init_file.read_text()
            has_version = '__version__ = "2.0.0"' in content
            self.test("Version is 2.0.0 in __init__.py", has_version)
            has_author = '__author__' in content
            self.test("Author field present", has_author, critical=False)
        else:
            self.test("__init__.py exists", False)
    
    def validate_imports(self):
        """Validate import statements."""
        section("IMPORT VALIDATION")
        
        # Check for relative imports in package
        files_to_check = [
            ("gui.py", [".obs_manager", ".plugin_scanner", ".plugin_repository", 
                       ".plugin_installer", ".database", ".local_repository", ".discovery"]),
            ("discovery.py", [".obs_resources"]),
        ]
        
        for filename, expected_imports in files_to_check:
            filepath = Path("obs_plugin_manager") / filename
            if filepath.exists():
                content = filepath.read_text()
                for imp in expected_imports:
                    has_import = f"from {imp} import" in content
                    self.test(f"Relative import '{imp}' in {filename}", has_import)
            else:
                self.test(f"{filename} exists", False)
    
    def validate_dependencies(self):
        """Validate requirements.txt."""
        section("DEPENDENCY VALIDATION")
        
        req_file = Path("requirements.txt")
        if req_file.exists():
            content = req_file.read_text()
            
            deps = {
                "psutil": "psutil>=5.9.0",
                "requests": "requests>=2.31.0",
                "beautifulsoup4": "beautifulsoup4>=4.12.0",
                "pywin32": "pywin32>=305"
            }
            
            for name, requirement in deps.items():
                has_dep = name in content
                self.test(f"Dependency: {name}", has_dep, critical=(name != "pywin32"))
        else:
            self.test("requirements.txt exists", False)
    
    def validate_code_quality(self):
        """Basic code quality checks."""
        section("CODE QUALITY CHECKS")
        
        # Check for common issues
        files = list(Path("obs_plugin_manager").glob("*.py"))
        
        total_lines = 0
        for file in files:
            if file.name != "__init__.py":
                lines = len(file.read_text().splitlines())
                total_lines += lines
        
        self.test("Total code lines > 4000", total_lines > 4000, critical=False)
        self.test("Total code lines < 10000", total_lines < 10000, critical=False)
        
        # Check for syntax (basic)
        for file in files:
            try:
                compile(file.read_text(), file.name, 'exec')
                has_syntax_error = False
            except SyntaxError:
                has_syntax_error = True
            self.test(f"No syntax errors in {file.name}", not has_syntax_error)
    
    def validate_documentation(self):
        """Validate documentation completeness."""
        section("DOCUMENTATION VALIDATION")
        
        # Check README has key sections
        readme = Path("README.md")
        if readme.exists():
            content = readme.read_text()
            sections = [
                "# OBS Plugin Manager",
                "## Features",
                "Installation",
                "Usage",
                "Discovery",
                "Local Repository"
            ]
            for section_title in sections:
                has_section = section_title in content
                self.test(f"README has '{section_title}'", has_section, critical=False)
        
        # Check START_HERE has navigation
        start_here = Path("START_HERE.md")
        if start_here.exists():
            content = start_here.read_text()
            has_nav = "Documentation Map" in content or "documentation" in content.lower()
            self.test("START_HERE has navigation", has_nav, critical=False)
    
    def validate_git(self):
        """Validate git repository."""
        section("GIT REPOSITORY VALIDATION")
        
        git_dir = Path(".git")
        self.test("Git repository initialized", git_dir.exists(), critical=False)
        
        gitignore = Path(".gitignore")
        if gitignore.exists():
            content = gitignore.read_text()
            ignores = ["__pycache__", "*.pyc", "obs_plugins.db", "plugin_archives"]
            for pattern in ignores:
                has_pattern = pattern in content
                self.test(f".gitignore has '{pattern}'", has_pattern, critical=False)
    
    def print_summary(self):
        """Print validation summary."""
        section("VALIDATION SUMMARY")
        
        total = len(self.results)
        passed = sum(1 for _, result, _ in self.results if result)
        failed = len(self.errors)
        warnings = len(self.warnings)
        
        print(f"\n{BOLD}Results:{RESET}")
        print(f"  Total checks: {total}")
        print(f"  {GREEN}Passed: {passed}{RESET}")
        print(f"  {RED}Failed (Critical): {failed}{RESET}")
        print(f"  {YELLOW}Warnings: {warnings}{RESET}")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        print(f"\n  Pass rate: {pass_rate:.1f}%")
        
        if self.errors:
            print(f"\n{RED}{BOLD}CRITICAL ISSUES:{RESET}")
            for error in self.errors:
                print(f"  {RED}✗{RESET} {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}{BOLD}WARNINGS:{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {warning}")
        
        print("\n" + "="*70)
        
        if not self.errors:
            print(f"{GREEN}{BOLD}{'🎉 DEPLOYMENT VALIDATION PASSED! 🎉':^70}{RESET}")
            print(f"{GREEN}{BOLD}{'Version 2.0 is READY for production!':^70}{RESET}")
            return 0
        else:
            print(f"{RED}{BOLD}{'⚠ DEPLOYMENT VALIDATION FAILED ⚠':^70}{RESET}")
            print(f"{RED}{BOLD}{'Please fix critical issues before deployment':^70}{RESET}")
            return 1
        
        print("="*70 + "\n")
    
    def run_all(self):
        """Run all validation checks."""
        print(f"\n{BOLD}OBS PLUGIN MANAGER v2.0 - DEPLOYMENT VALIDATION{RESET}")
        print(f"{BOLD}Running comprehensive validation suite...{RESET}\n")
        
        self.validate_file_structure()
        self.validate_version()
        self.validate_imports()
        self.validate_dependencies()
        self.validate_code_quality()
        self.validate_documentation()
        self.validate_git()
        
        return self.print_summary()

def main():
    """Main entry point."""
    try:
        validator = DeploymentValidator()
        exit_code = validator.run_all()
        
        if exit_code == 0:
            print(f"\n{BOLD}Next steps:{RESET}")
            print("  1. Review DEPLOYMENT_CHECKLIST.md")
            print("  2. Run manual GUI tests")
            print("  3. Package for distribution")
            print("  4. Deploy to production!")
            print(f"\n{GREEN}Good luck with your deployment! 🚀{RESET}\n")
        else:
            print(f"\n{BOLD}Next steps:{RESET}")
            print("  1. Fix critical issues listed above")
            print("  2. Re-run this validation script")
            print("  3. Review CODE_REVIEW.md for guidance")
            print(f"\n{YELLOW}Almost there! 💪{RESET}\n")
        
        return exit_code
    except Exception as e:
        print(f"\n{RED}{BOLD}Validation script error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())
