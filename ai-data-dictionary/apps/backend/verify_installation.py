"""
Verification script to test installed dependencies.

Run this to confirm that the core packages are working correctly.
"""

import sys

def test_imports():
    """Test importing key packages."""
    results = []
    packages = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("alembic", "Alembic"),
        ("pydantic", "Pydantic"),
        ("openai", "OpenAI"),
        ("tiktoken", "Tiktoken"),
        ("langchain", "LangChain"),
        ("langchain_core", "LangChain Core"),
        ("langchain_openai", "LangChain OpenAI"),
        ("celery", "Celery"),
        ("redis", "Redis"),
        ("pytest", "Pytest"),
        ("asyncpg", "AsyncPG"),
        ("psycopg2", "Psycopg2"),
        ("structlog", "Structlog"),
        ("sqlparse", "SQLParse"),
        ("sqlglot", "SQLGlot"),
        ("pandera", "Pandera"),
    ]
    
    print("=" * 70)
    print("Testing Package Imports")
    print("=" * 70)
    
    for module_name, display_name in packages:
        try:
            module = __import__(module_name)
            version = getattr(module, "__version__", "unknown")
            results.append((display_name, "✅ OK", version))
            print(f"✅ {display_name:25} {version}")
        except ImportError as e:
            results.append((display_name, "❌ FAILED", str(e)))
            print(f"❌ {display_name:25} Import failed: {e}")
        except Exception as e:
            results.append((display_name, "⚠️  ERROR", str(e)))
            print(f"⚠️  {display_name:25} Error: {e}")
    
    print("\n" + "=" * 70)
    print("Known Issues")
    print("=" * 70)
    
    # Test ChromaDB separately
    try:
        import chromadb
        print("⚠️  ChromaDB: Installed but has Python 3.14 compatibility issues")
    except ImportError:
        print("ℹ️  ChromaDB: Not installed (expected - Python 3.14 compatibility)")
    except Exception as e:
        print(f"⚠️  ChromaDB: Installed but not working: {e}")
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    successful = sum(1 for _, status, _ in results if "OK" in status)
    total = len(results)
    
    print(f"Successful: {successful}/{total}")
    print(f"Python Version: {sys.version}")
    
    if successful == total:
        print("\n✅ All core packages installed successfully!")
        return 0
    else:
        print(f"\n⚠️  {total - successful} packages failed to import")
        return 1


if __name__ == "__main__":
    sys.exit(test_imports())
