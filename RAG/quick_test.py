#!/usr/bin/env python3
"""
Quick test to identify issues with the RAG system.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_imports():
    """Test basic imports."""
    print("🧪 Testing imports...")
    
    try:
        from dotenv import load_dotenv
        print("✅ dotenv imported")
        
        # Load environment
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            print("✅ Environment loaded")
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            print("✅ OpenAI API key found")
        else:
            print("❌ No OpenAI API key")
            return False
        
        from character_rag import CharacterRAGEngine
        print("✅ CharacterRAGEngine imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_system():
    """Test minimal system initialization."""
    print("\n🧪 Testing minimal initialization...")
    
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        openai_key = os.getenv('OPENAI_API_KEY')
        data_dir = str(Path(__file__).parent.parent / 'data' / 'translated')
        
        print(f"📁 Data directory: {data_dir}")
        print(f"📚 Files found: {len([f for f in os.listdir(data_dir) if f.endswith('.md')])}")
        
        from character_rag import CharacterRAGEngine
        
        # Initialize with minimal settings
        rag_engine = CharacterRAGEngine(
            openai_api_key=openai_key,
            data_directory=data_dir,
            persist_directory="./test_db"
        )
        
        print("✅ RAG engine created successfully")
        
        # Try to just load documents without building embeddings
        print("📚 Loading documents...")
        docs = rag_engine.document_processor.load_all_documents()
        print(f"✅ Loaded {len(docs)} documents")
        
        if docs:
            sample_doc = docs[0]
            print(f"📄 Sample document title: {sample_doc.metadata.get('title', 'Unknown')}")
            print(f"📄 Character mentions: {len(sample_doc.metadata.get('character_mentions', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Minimal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run quick tests."""
    print("🚀 Quick Test for Infinity Mage RAG System")
    print("=" * 50)
    
    if not test_basic_imports():
        return 1
    
    if not test_minimal_system():
        return 1
    
    print("\n✅ Quick tests passed! The basic system is working.")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)