#!/usr/bin/env python3
"""
Simple test script for the Infinity Mage Character RAG system.

This script tests the basic functionality without requiring full system initialization.
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_data_access():
    """Test that we can access the data directory and load documents."""
    print("🧪 Testing data access...")
    
    try:
        from character_loader import CharacterDocumentProcessor, CharacterAwareMarkdownLoader
        
        data_dir = str(Path(__file__).parent.parent / 'data' / 'translated')
        print(f"📁 Data directory: {data_dir}")
        
        if not os.path.exists(data_dir):
            print(f"❌ Data directory not found: {data_dir}")
            return False
        
        # Count files
        files = [f for f in os.listdir(data_dir) if f.endswith('.md')]
        print(f"📚 Found {len(files)} markdown files")
        
        if len(files) == 0:
            print("❌ No markdown files found")
            return False
        
        # Test loading a few documents
        processor = CharacterDocumentProcessor(data_dir)
        
        # Load first 5 documents as a test
        test_files = files[:5]
        test_docs = []
        
        for filename in test_files:
            file_path = os.path.join(data_dir, filename)
            loader = CharacterAwareMarkdownLoader(file_path)
            docs = loader.load()
            test_docs.extend(docs)
        
        print(f"✅ Successfully loaded {len(test_docs)} test documents")
        
        # Analyze first document
        if test_docs:
            doc = test_docs[0]
            print(f"📄 Sample document analysis:")
            print(f"   Title: {doc.metadata.get('title', 'Unknown')}")
            print(f"   Character mentions: {doc.metadata.get('character_mentions', [])}")
            print(f"   Has dialogue: {doc.metadata.get('has_dialogue', False)}")
            print(f"   Chapter themes: {doc.metadata.get('chapter_themes', [])}")
            print(f"   Content preview: {doc.page_content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Data access test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_character_database():
    """Test character database functionality."""
    print("\n🧪 Testing character database...")
    
    try:
        from character_db import CharacterDatabase, CharacterProfile, PhysicalAppearance
        
        # Create test database
        db = CharacterDatabase()
        
        # Create test character
        character = CharacterProfile(name="Test Character")
        character.appearance = PhysicalAppearance(
            height="tall",
            hair_color="brown",
            description="A test character"
        )
        character.background = "This is a test character for system validation."
        
        # Add to database
        db.add_character(character)
        
        # Test retrieval
        retrieved = db.get_character("Test Character")
        if retrieved and retrieved.name == "Test Character":
            print("✅ Character database creation and retrieval works")
        else:
            print("❌ Character database retrieval failed")
            return False
        
        # Test statistics
        stats = db.get_statistics()
        print(f"📊 Database stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Character database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_setup():
    """Test environment variables and API key."""
    print("\n🧪 Testing environment setup...")
    
    try:
        from dotenv import load_dotenv
        
        # Load environment
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Loaded .env from {env_path}")
        else:
            print(f"⚠️  .env file not found at {env_path}")
        
        # Check API key
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.startswith('sk-'):
            print("✅ OPENAI_API_KEY found and appears valid")
            return True
        else:
            print("❌ OPENAI_API_KEY not found or invalid")
            return False
            
    except Exception as e:
        print(f"❌ Environment setup test failed: {e}")
        return False

def test_imports():
    """Test all module imports."""
    print("\n🧪 Testing module imports...")
    
    modules_to_test = [
        ('character_loader', 'CharacterDocumentProcessor'),
        ('character_db', 'CharacterDatabase'),
        ('embeddings', 'CharacterAwareTextSplitter'),
        ('character_rag', 'CharacterRAGEngine'),
        ('query_interface', 'CharacterQueryInterface'),
    ]
    
    all_passed = True
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name} imported successfully")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} import failed: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests."""
    print("🚀 Starting Infinity Mage Character RAG System Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Setup", test_environment_setup),
        ("Data Access", test_data_access),
        ("Character Database", test_character_database),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The RAG system is ready to use.")
        print(f"\n🚀 To get started, run:")
        print(f"   cd {Path(__file__).parent}")
        print(f"   python main.py")
    else:
        print(f"⚠️  Some tests failed. Please fix the issues before using the system.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)