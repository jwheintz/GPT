#!/bin/bash
# Create distribution package for OBS Plugin Manager

echo "Creating distribution package..."

# Create distribution directory
DIST_DIR="obs-plugin-manager-v2.0.0"
mkdir -p "$DIST_DIR"

echo "Copying core application files..."
cp -r obs_plugin_manager "$DIST_DIR/"
cp obs_plugin_manager.py "$DIST_DIR/"
cp requirements.txt "$DIST_DIR/"
cp quick_setup.bat "$DIST_DIR/"

echo "Copying essential documentation..."
cp START_HERE.md "$DIST_DIR/"
cp README.md "$DIST_DIR/"
cp GETTING_STARTED.md "$DIST_DIR/"
cp MISSION_ACCOMPLISHED.md "$DIST_DIR/"
cp THE_FINAL_WORD.md "$DIST_DIR/"
cp DEPLOYMENT_CHECKLIST.md "$DIST_DIR/"
cp TROUBLESHOOTING.md "$DIST_DIR/"

echo "Copying test files (optional)..."
mkdir -p "$DIST_DIR/tests"
cp *_test.py "$DIST_DIR/tests/" 2>/dev/null || true
cp validate_deployment.py "$DIST_DIR/tests/" 2>/dev/null || true
cp health_check.py "$DIST_DIR/tests/" 2>/dev/null || true

echo "Creating comprehensive documentation package..."
mkdir -p "$DIST_DIR/docs"
cp SESSION_*.md "$DIST_DIR/docs/" 2>/dev/null || true
cp FINAL_TEST_REPORT.md "$DIST_DIR/docs/" 2>/dev/null || true
cp TESTING_COMPLETE.md "$DIST_DIR/docs/" 2>/dev/null || true

echo "Creating zip file..."
zip -r obs-plugin-manager-v2.0.0.zip "$DIST_DIR"

echo "Creating tar.gz file..."
tar -czf obs-plugin-manager-v2.0.0.tar.gz "$DIST_DIR"

echo ""
echo "✅ Distribution packages created:"
echo "   - obs-plugin-manager-v2.0.0.zip"
echo "   - obs-plugin-manager-v2.0.0.tar.gz"
echo ""
echo "Package includes:"
echo "   - Core application (13 modules)"
echo "   - Main executable"
echo "   - Dependencies list"
echo "   - Quick setup script"
echo "   - Essential documentation"
echo "   - Test suites"
echo "   - Complete documentation"
echo ""
echo "To install on Windows:"
echo "   1. Extract the zip file"
echo "   2. Run quick_setup.bat"
echo "   3. Run obs_plugin_manager.py"
echo ""

# Cleanup
rm -rf "$DIST_DIR"

echo "✅ Done!"
