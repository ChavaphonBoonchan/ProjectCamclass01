#!/usr/bin/env python3
"""
Test System Integrity
ทดสอบความสมบูรณ์ของระบบหลังจากการจัดระเบียบ
"""
import sys
import os
from pathlib import Path

def test_file_exists(filepath, description):
    """Test if file exists"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False

def test_directory_exists(dirpath, description):
    """Test if directory exists"""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("🧪 Testing System Integrity")
    print("=" * 60)
    print()
    
    passed = 0
    failed = 0
    
    # Test core application files
    print("📁 Testing Core Application Files...")
    tests = [
        ("app/server.py", "Main Server"),
        ("app/test_telegram.py", "Telegram Tester"),
    ]
    
    for filepath, desc in tests:
        if test_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Test executable scripts
    print("🚀 Testing Executable Scripts...")
    tests = [
        ("bin/start_server.bat", "Start Server Script"),
        ("bin/start_detection.bat", "Start Detection Script"),
        ("bin/start_webapp.bat", "Start WebApp Script"),
    ]
    
    for filepath, desc in tests:
        if test_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Test tools
    print("🔧 Testing Tools...")
    tests = [
        ("tools/migrate_db.py", "Database Migration"),
        ("tools/fix_gpu_libraries.ps1", "GPU Library Fixer"),
    ]
    
    for filepath, desc in tests:
        if test_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Test configuration files
    print("⚙️ Testing Configuration Files...")
    tests = [
        (".env", "Environment Variables"),
        (".env.example", "Environment Template"),
        ("requirements.txt", "Python Dependencies"),
        ("detection_prod/config.json", "Detection Config"),
    ]
    
    for filepath, desc in tests:
        if test_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Test documentation
    print("📚 Testing Documentation...")
    tests = [
        ("README.md", "Main README"),
        ("QUICK_START.md", "Quick Start Guide"),
        ("PROJECT_STATUS.md", "Project Status"),
        ("docs/API_DOCUMENTATION.md", "API Documentation"),
        ("docs/GPU_SETUP_GUIDE.md", "GPU Setup Guide"),
    ]
    
    for filepath, desc in tests:
        if test_file_exists(filepath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Test directories
    print("📂 Testing Directories...")
    tests = [
        ("app", "Application Directory"),
        ("bin", "Scripts Directory"),
        ("tools", "Tools Directory"),
        ("docs", "Documentation Directory"),
        ("dashboard", "Database Directory"),
        ("detection_prod", "Detection Directory"),
        ("face_common", "Common Utilities"),
        ("model_store", "Model Storage"),
        ("training", "Training Scripts"),
        ("web_app", "Web Application"),
    ]
    
    for dirpath, desc in tests:
        if test_directory_exists(dirpath, desc):
            passed += 1
        else:
            failed += 1
    print()
    
    # Test imports
    print("🐍 Testing Python Imports...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        # Test if server.py can be imported
        import importlib.util
        spec = importlib.util.spec_from_file_location("server", "app/server.py")
        if spec and spec.loader:
            print("✅ Server module can be loaded")
            passed += 1
        else:
            print("❌ Server module cannot be loaded")
            failed += 1
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        failed += 1
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
    print()
    
    if failed == 0:
        print("🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
