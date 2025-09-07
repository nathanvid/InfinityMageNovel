#!/usr/bin/env python3
"""
Working main entry point for the Infinity Mage Character RAG system.

This version fixes the metadata issues and provides a reliable working system.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import argparse

from simple_rag import SimpleCharacterRAG

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Infinity Mage Character RAG System (Working Version)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🧙 Infinity Mage Character RAG System - Working Version

This is a streamlined version that reliably works with your data.

EXAMPLES:
  python working_main.py                    # Interactive mode
  python working_main.py --query "Who is Shirone?"  # Single query
  python working_main.py --list             # List characters
        """
    )
    
    parser.add_argument(
        "--query", "-q",
        help="Ask a question about the characters"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all found characters"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Load environment
    print("🔧 Loading environment...")
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment loaded")
    else:
        print("❌ .env file not found")
        return 1
    
    # Get API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return 1
    
    # Set data directory
    data_dir = str(Path(__file__).parent.parent / 'data' / 'translated')
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return 1
    
    # Initialize RAG system
    print("🚀 Initializing RAG system...")
    rag = SimpleCharacterRAG(openai_key, data_dir)
    
    # Load documents
    docs = rag.load_documents()
    if not docs:
        print("❌ No documents loaded")
        return 1
    
    # Handle commands
    if args.list:
        characters = rag.list_characters()
        print(f"\n📋 Found Characters ({len(characters)}):")
        for i, char in enumerate(characters, 1):
            print(f"{i:2d}. {char}")
        return 0
    
    if args.query:
        print(f"\n🔍 Query: {args.query}")
        try:
            answer = rag.query(args.query)
            print(f"\n📝 Answer:\n{answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
        return 0
    
    # Interactive mode
    if args.interactive or (not args.query and not args.list):
        print("\n🧙 Welcome to the Infinity Mage Character RAG System!")
        print("Ask questions about the characters. Type 'quit' to exit.")
        print("=" * 60)
        
        characters = rag.list_characters()
        print(f"📋 Available characters: {', '.join(characters)}")
        
        while True:
            try:
                query = input("\n🔍 Your question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if query.lower() in ['help', 'h']:
                    print("\n📚 Example questions:")
                    print("• Who is Shirone?")
                    print("• Tell me about Amy's abilities")
                    print("• What is the relationship between Shirone and Rian?")
                    print("• Describe Vincent's background")
                    print("• List characters - shows all found characters")
                    continue
                
                if query.lower() in ['list', 'characters']:
                    print(f"📋 Characters: {', '.join(characters)}")
                    continue
                
                print("🔄 Processing...")
                answer = rag.query(query)
                print(f"\n📝 Answer:\n{answer}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)