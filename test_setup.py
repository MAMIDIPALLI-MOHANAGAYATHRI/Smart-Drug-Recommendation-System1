"""
Quick Test Script - Verify Setup
Tests data files, imports, and basic functionality
"""

import os
import sys

def test_folder_structure():
    """Test if all required folders exist"""
    print("📁 Testing Folder Structure...")
    
    required_folders = ['data', 'models', 'notebooks', 'templates', 'static/css', 'static/js']
    missing = []
    
    for folder in required_folders:
        if os.path.exists(folder):
            print(f"  ✓ {folder}")
        else:
            print(f"  ✗ {folder} - MISSING")
            missing.append(folder)
    
    return len(missing) == 0


def test_data_files():
    """Test if data files exist and can be loaded"""
    print("\n📊 Testing Data Files...")
    
    try:
        import pandas as pd
        
        # Test medicines.csv
        medicines = pd.read_csv('data/medicines.csv')
        print(f"  ✓ medicines.csv - {len(medicines)} drugs loaded")
        print(f"    Columns: {', '.join(medicines.columns.tolist())}")
        
        # Test interactions.csv
        interactions = pd.read_csv('data/interactions.csv')
        print(f"  ✓ interactions.csv - {len(interactions)} interactions loaded")
        
        # Test training_data.csv
        training = pd.read_csv('data/training_data.csv')
        print(f"  ✓ training_data.csv - {len(training)} records loaded")
        
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False


def test_imports():
    """Test if all required packages are installed"""
    print("\n📦 Testing Python Packages...")
    
    packages = {
        'flask': 'Flask',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'joblib': 'joblib'
    }
    
    missing = []
    
    for module, package_name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {package_name}")
        except ImportError:
            print(f"  ✗ {package_name} - NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def test_templates():
    """Test if HTML templates exist"""
    print("\n🎨 Testing Templates...")
    
    templates = ['base.html', 'index.html', 'patient_form.html']
    missing = []
    
    for template in templates:
        path = f'templates/{template}'
        if os.path.exists(path):
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} - MISSING")
            missing.append(template)
    
    return len(missing) == 0


def test_static_files():
    """Test if CSS and JS files exist"""
    print("\n🎭 Testing Static Files...")
    
    static_files = ['static/css/style.css', 'static/js/script.js']
    missing = []
    
    for file in static_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0


def main():
    """Run all tests"""
    print("="*60)
    print("🧪 SMART DRUG RECOMMENDATION SYSTEM - SETUP TEST")
    print("="*60)
    
    tests = [
        test_folder_structure,
        test_data_files,
        test_imports,
        test_templates,
        test_static_files
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    if all(results):
        print("✅ ALL TESTS PASSED - Ready to run Flask app!")
        print("\nNext steps:")
        print("  1. python app.py")
        print("  2. Open http://localhost:5000 in browser")
    else:
        print("❌ SOME TESTS FAILED - Please fix issues above")
        print("\nMissing files? Run:")
        print("  git status")
        print("  (Check if all files are created)")
    print("="*60)


if __name__ == '__main__':
    main()
