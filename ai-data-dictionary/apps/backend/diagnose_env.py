"""
Python Environment Diagnostic Script

Run this to diagnose Python environment issues in VS Code.
"""

import sys
import os
from pathlib import Path


def main():
    print("=" * 70)
    print("Python Environment Diagnostic")
    print("=" * 70)
    
    print(f"\n📍 Python Executable:")
    print(f"   {sys.executable}")
    
    print(f"\n🐍 Python Version:")
    print(f"   {sys.version}")
    
    print(f"\n📦 Python Paths (sys.path):")
    for i, path in enumerate(sys.path, 1):
        print(f"   {i}. {path}")
    
    print(f"\n📁 Site Packages:")
    import site
    print(f"   User site: {site.USER_SITE}")
    print(f"   Site packages: {site.getsitepackages()}")
    
    print(f"\n✅ Verifying Key Packages:")
    packages_to_check = [
        "pydantic",
        "pydantic_settings",
        "sqlalchemy",
        "fastapi",
        "cryptography",
        "structlog",
        "sqlparse",
        "sqlglot",
        "pytest",
    ]
    
    for pkg in packages_to_check:
        try:
            module = __import__(pkg)
            location = getattr(module, "__file__", "built-in")
            version = getattr(module, "__version__", "unknown")
            print(f"   ✅ {pkg:20} v{version:15} @ {location}")
        except ImportError:
            print(f"   ❌ {pkg:20} NOT FOUND")
    
    print(f"\n🔧 Environment Variables:")
    print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"   VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
    
    print(f"\n💡 Recommendations for VS Code:")
    print(f"   1. Press Ctrl+Shift+P, type 'Python: Select Interpreter'")
    print(f"   2. Choose: {sys.executable}")
    print(f"   3. Reload VS Code window (Ctrl+Shift+P -> 'Reload Window')")
    print(f"   4. Check .vscode/settings.json is configured correctly")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
