#!/usr/bin/env python3
"""
Setup script for Infinity Mage Character RAG
"""

import os
import sys
from pathlib import Path


def check_requirements():
    """Check if all requirements are met."""
    print("Checking requirements...")

    # Check .env file
    env_path = Path("../.env")
    if not env_path.exists():
        print("ERROR: .env file not found in parent directory")
        print("Please create a .env file with OPENAI_API_KEY=your_key_here")
        return False

    # Check for API key
    from dotenv import load_dotenv
    load_dotenv(env_path)

    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in .env file")
        return False

    if not api_key.startswith('sk-'):
        print("ERROR: OPENAI_API_KEY appears invalid (should start with 'sk-')")
        return False

    print("API key found and valid")

    # Check data directory
    data_dir = Path("../data/translated")
    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        return False

    md_files = list(data_dir.glob("*.md"))
    if not md_files:
        print("ERROR: No markdown files found in data directory")
        return False

    print(f"Found {len(md_files)} chapter files")

    # Check dependencies
    try:
        import langchain
        import langchain_openai
        import langchain_community
        import chromadb
        import dotenv
        print("All dependencies available")
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("Run: pip install -r ../requirements.txt")
        return False

    return True


def test_system():
    """Test the RAG system quickly."""
    print("\nTesting RAG system...")

    try:
        from simple_character_rag import SimpleCharacterRAG

        rag = SimpleCharacterRAG()
        docs = rag.load_documents(max_chapters=3)
        characters = rag.list_characters()

        print(f"System working! Found characters: {', '.join(characters)}")
        return True

    except Exception as e:
        print(f"ERROR: System test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("Infinity Mage Character RAG Setup")
    print("=" * 40)

    if not check_requirements():
        print("\nERROR: Setup failed. Please fix the issues above.")
        return 1

    if not test_system():
        print("\nERROR: System test failed.")
        return 1

    print("\n" + "=" * 40)
    print("Setup complete! Your RAG system is ready to use.")
    print("\nTo get started:")
    print("  python rag.py")
    print('  python rag.py "Who is Shirone?"')

    return 0


if __name__ == "__main__":
    sys.exit(main())