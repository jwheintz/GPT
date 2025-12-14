"""
GUI Code Analysis - Static verification of GUI code without running

This analyzes:
1. Python syntax validity
2. Import statements
3. Method definitions
4. Variable usage
5. Common GUI patterns
"""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

class GUICodeAnalyzer:
    def __init__(self):
        self.results = []
        self.gui_path = Path(__file__).parent / "obs_plugin_manager" / "gui.py"
    
    def test_syntax(self):
        """Test 1: Python syntax is valid"""
        print("\n" + "="*70)
        print("TEST 1: Syntax Validation")
        print("="*70)
        
        try:
            print(f"\n1. Reading {self.gui_path}...")
            code = self.gui_path.read_text()
            print(f"   ✅ File read successfully ({len(code)} bytes)")
            
            print("\n2. Parsing Python AST...")
            tree = ast.parse(code, filename=str(self.gui_path))
            print("   ✅ Syntax is valid (no parse errors)")
            
            print("\n3. Analyzing structure...")
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            print(f"   - Found {len(classes)} class(es)")
            print(f"   - Found {len(functions)} function(s)/method(s)")
            print(f"   - Found {len(imports)} import statement(s)")
            
            self.results.append(("Syntax Validation", True, tree))
            return True, tree
            
        except SyntaxError as e:
            print(f"   ❌ Syntax error: {e}")
            print(f"      Line {e.lineno}: {e.text}")
            self.results.append(("Syntax Validation", False, None))
            return False, None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results.append(("Syntax Validation", False, None))
            return False, None
    
    def test_imports(self, tree):
        """Test 2: All imports are valid"""
        print("\n" + "="*70)
        print("TEST 2: Import Analysis")
        print("="*70)
        
        if not tree:
            print("   ⚠️ Skipping - no AST available")
            self.results.append(("Import Analysis", False))
            return False
        
        try:
            print("\n1. Extracting import statements...")
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            print(f"   Found {len(imports)} imports")
            
            print("\n2. Checking critical imports...")
            critical_imports = [
                'tkinter',
                'threading',
                'messagebox',
                'database',
                'obs_manager',
                'plugin_scanner',
                'plugin_installer',
                'plugin_repository',
                'local_repository',
                'discovery'
            ]
            
            all_found = True
            for imp in critical_imports:
                found = any(imp in i for i in imports)
                if found:
                    print(f"   ✅ {imp} imported")
                else:
                    print(f"   ⚠️ {imp} not found in imports")
                    all_found = False
            
            self.results.append(("Import Analysis", all_found))
            return all_found
            
        except Exception as e:
            print(f"   ❌ Import analysis failed: {e}")
            self.results.append(("Import Analysis", False))
            return False
    
    def test_class_structure(self, tree):
        """Test 3: Main GUI class structure"""
        print("\n" + "="*70)
        print("TEST 3: Class Structure")
        print("="*70)
        
        if not tree:
            print("   ⚠️ Skipping - no AST available")
            self.results.append(("Class Structure", False))
            return False
        
        try:
            print("\n1. Finding main GUI class...")
            gui_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and 'GUI' in node.name:
                    gui_class = node
                    print(f"   ✅ Found class: {node.name}")
                    break
            
            if not gui_class:
                print("   ❌ No GUI class found")
                self.results.append(("Class Structure", False))
                return False
            
            print("\n2. Analyzing methods...")
            methods = [n for n in gui_class.body if isinstance(n, ast.FunctionDef)]
            print(f"   Found {len(methods)} methods")
            
            print("\n3. Checking critical methods...")
            critical_methods = [
                '__init__',
                '_setup_ui',
                '_scan_plugins',
                '_mark_current_as_stable',
                '_rollback_to_stable',
                '_manage_versions'
            ]
            
            method_names = [m.name for m in methods]
            all_found = True
            for method in critical_methods:
                if method in method_names:
                    print(f"   ✅ {method} defined")
                else:
                    print(f"   ❌ {method} missing")
                    all_found = False
            
            self.results.append(("Class Structure", all_found))
            return all_found
            
        except Exception as e:
            print(f"   ❌ Class structure analysis failed: {e}")
            self.results.append(("Class Structure", False))
            return False
    
    def test_defensive_code(self, tree):
        """Test 4: Defensive None checks exist"""
        print("\n" + "="*70)
        print("TEST 4: Defensive Code (Bug #1 fix verification)")
        print("="*70)
        
        if not tree:
            print("   ⚠️ Skipping - no AST available")
            self.results.append(("Defensive Code", False))
            return False
        
        try:
            print("\n1. Searching for None checks...")
            code = self.gui_path.read_text()
            
            # Look for defensive patterns
            defensive_checks = [
                "if self.plugin_scanner is None",
                "if self.plugin_installer is None",
                "if not self.plugin_scanner",
                "if not self.plugin_installer"
            ]
            
            checks_found = []
            for check in defensive_checks:
                if check in code:
                    checks_found.append(check)
                    count = code.count(check)
                    print(f"   ✅ Found: '{check}' ({count} occurrence(s))")
            
            if checks_found:
                print(f"\n   ✅ Total: {len(checks_found)} defensive patterns found")
                self.results.append(("Defensive Code", True))
                return True
            else:
                print("   ⚠️ No defensive None checks found")
                self.results.append(("Defensive Code", False))
                return False
            
        except Exception as e:
            print(f"   ❌ Defensive code check failed: {e}")
            self.results.append(("Defensive Code", False))
            return False
    
    def test_stable_version_code(self, tree):
        """Test 5: Stable version locking code exists"""
        print("\n" + "="*70)
        print("TEST 5: Stable Version Feature")
        print("="*70)
        
        try:
            print("\n1. Checking for stable version methods...")
            code = self.gui_path.read_text()
            
            stable_methods = [
                '_mark_current_as_stable',
                '_rollback_to_stable',
                '_manage_versions'
            ]
            
            all_found = True
            for method in stable_methods:
                if f"def {method}" in code:
                    print(f"   ✅ Method '{method}' defined")
                else:
                    print(f"   ❌ Method '{method}' missing")
                    all_found = False
            
            print("\n2. Checking for stable version UI elements...")
            ui_elements = [
                'Mark Stable',
                'Rollback to Stable', 
                'Manage Versions',
                '⭐',  # Star symbol
                '↩️'   # Rollback arrow
            ]
            
            for element in ui_elements:
                if element in code:
                    print(f"   ✅ UI element '{element}' found")
                else:
                    print(f"   ⚠️ UI element '{element}' not found")
            
            self.results.append(("Stable Version Feature", all_found))
            return all_found
            
        except Exception as e:
            print(f"   ❌ Stable version check failed: {e}")
            self.results.append(("Stable Version Feature", False))
            return False
    
    def test_database_integration(self, tree):
        """Test 6: Database methods are called correctly"""
        print("\n" + "="*70)
        print("TEST 6: Database Integration")
        print("="*70)
        
        try:
            print("\n1. Checking database method calls...")
            code = self.gui_path.read_text()
            
            db_methods = [
                'mark_version_as_stable',
                'get_stable_version',
                'get_all_versions',
                'get_installed_plugins',
                'add_installed_plugin'
            ]
            
            found_count = 0
            for method in db_methods:
                if f"database.{method}" in code or f"self.database.{method}" in code:
                    print(f"   ✅ Calls database.{method}")
                    found_count += 1
                else:
                    print(f"   ⚠️ No calls to database.{method}")
            
            print(f"\n   Found {found_count}/{len(db_methods)} database methods called")
            
            result = found_count >= 3  # At least 3 methods should be called
            self.results.append(("Database Integration", result))
            return result
            
        except Exception as e:
            print(f"   ❌ Database integration check failed: {e}")
            self.results.append(("Database Integration", False))
            return False
    
    def test_initial_backup_integration(self, tree):
        """Test 7: Initial backup passes database (Bug #25 fix)"""
        print("\n" + "="*70)
        print("TEST 7: Initial Backup Integration (Bug #25 fix)")
        print("="*70)
        
        try:
            print("\n1. Checking create_initial_backups call...")
            code = self.gui_path.read_text()
            
            # Look for the fixed call
            if "create_initial_backups(plugins, self.database)" in code:
                print("   ✅ create_initial_backups called WITH database parameter")
                print("   ✅ Bug #25 fix verified in code")
                result = True
            elif "create_initial_backups(plugins)" in code and "self.database" not in code:
                print("   ❌ create_initial_backups called WITHOUT database parameter")
                print("   ❌ Bug #25 NOT fixed!")
                result = False
            else:
                print("   ⚠️ Could not find create_initial_backups call")
                result = False
            
            self.results.append(("Initial Backup Integration", result))
            return result
            
        except Exception as e:
            print(f"   ❌ Initial backup check failed: {e}")
            self.results.append(("Initial Backup Integration", False))
            return False
    
    def run_all(self):
        """Run all GUI code analysis tests"""
        print("="*70)
        print("GUI CODE ANALYSIS (Static Verification)")
        print("="*70)
        print("\nAnalyzing GUI code without running it...\n")
        
        # Run tests
        success, tree = self.test_syntax()
        if success:
            self.test_imports(tree)
            self.test_class_structure(tree)
            self.test_defensive_code(tree)
            self.test_stable_version_code(tree)
            self.test_database_integration(tree)
            self.test_initial_backup_integration(tree)
        
        # Summary
        print("\n" + "="*70)
        print("ANALYSIS SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result, *_ in self.results if result)
        total = len(self.results)
        
        for test_result in self.results:
            test_name = test_result[0]
            result = test_result[1]
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL CODE ANALYSIS TESTS PASSED!")
            print("✅ Syntax is valid")
            print("✅ All critical imports present")
            print("✅ Class structure correct")
            print("✅ Defensive checks in place")
            print("✅ Stable version feature implemented")
            print("✅ Database integration correct")
            print("✅ Bug #25 fix verified")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed - review above")
        
        return passed == total

def main():
    analyzer = GUICodeAnalyzer()
    success = analyzer.run_all()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
